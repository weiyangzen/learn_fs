# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/safexcel.c

## Purpose
Implements the main SafeXcel EIP97/EIP197 crypto engine driver. It handles platform and PCI probing, hardware detection/configuration, EIP197 context cache and firmware setup, descriptor ring setup, request queueing, interrupt-driven result completion, algorithm registration, and module init/exit.

## Important APIs, Types, and Functions
Major initialization functions include `eip197_trc_cache_init()`, `eip197_load_firmwares()`, `safexcel_hw_setup_cdesc_rings()`, `safexcel_hw_setup_rdesc_rings()`, `safexcel_hw_init()`, `safexcel_configure()`, `safexcel_init_register_offsets()`, and `safexcel_probe_generic()`. Runtime queue/completion functions include `safexcel_dequeue()`, `safexcel_try_push_requests()`, `safexcel_rdesc_check_errors()`, `safexcel_complete()`, `safexcel_invalidate_cache()`, and `safexcel_handle_result_descriptor()`. Probe/remove paths are `safexcel_probe()`, `safexcel_remove()`, `safexcel_pci_probe()`, and `safexcel_pci_remove()`.

The static `safexcel_algs[]` array collects skcipher, AEAD, ahash, SHA3, SMx, Chacha/Poly, CCM/GCM, and authenc templates from other driver files. `max_rings` is a module parameter.

## Control Flow
Platform probe maps MMIO, enables optional clocks, sets a 64-bit DMA mask, and calls the generic probe. PCI probe maps BARs, performs dev-board reset/MSI setup when applicable, enables bus mastering, and also calls the generic probe. Generic probe creates the DMA context pool, detects EIP97 versus EIP197 and endianness, probes EIP206/EIP96/EIP201 blocks, records hardware capabilities, configures descriptor sizes/ring counts, allocates rings/workqueues/IRQ data, requests per-ring IRQs, initializes hardware, and registers only algorithms whose `algo_mask` is supported by hardware.

At runtime, algorithm-specific send functions enqueue requests into per-ring crypto queues. `safexcel_dequeue()` pulls requests, calls each context’s `send()` method to emit command/result descriptors, records pending request counts, writes RDR/CDR prepared counts, and programs RDR interrupt coalescing. Ring IRQs acknowledge RDR threshold events and wake a threaded handler. The thread calls `safexcel_handle_result_descriptor()`, which retrieves the request stored for the first result descriptor, dispatches to the algorithm context’s `handle_result()`, completes the crypto request if requested, acknowledges processed descriptors, updates ring busy/request state, and schedules a workqueue refill.

## State and Persistence
Driver instance state is in `struct safexcel_crypto_priv`: MMIO base, clocks, per-device data, register offsets, probed hardware config, flags, DMA context pool, ring selection counter, and ring array. Each ring holds descriptor rings, a request pointer table for RDR entries, a crypto queue, locks, busy/request counters, saved request/backlog when resources run out, IRQ number, and a single-thread workqueue. Firmware is loaded into hardware program memory at probe time but not persisted by the driver.

## Dependencies and Integration Points
Depends on Linux platform/OF, PCI, firmware loader, DMA pool, workqueue, interrupt, and crypto registration APIs. Integrates with sibling SafeXcel algorithm files through `struct safexcel_context` callbacks and `safexcel_alg_template` declarations in `safexcel.h`. Firmware paths include `inside-secure/eip197b`, `inside-secure/eip197d`, `inside-secure/eip197_minifw`, and legacy root names for EIP197B.

## Risks
TRC cache probing writes classification RAM and assumes sane physical RAM sizing. Firmware startup polling has a small bounded poll count and falls back to mini firmware only for supported cases. DSE reset waits in a tight loop for thread status. Fatal RDR errors are logged but the ring is not reinitialized in this path. PCI probe allocates `priv` with `kzalloc_obj()` and several early error paths return without freeing it. The PCI remove path destroys workqueues but does not clear IRQ affinity hints, unlike platform remove. Correct operation depends on algorithm `send()`/`handle_result()` callbacks managing descriptor resources exactly.

## Test Signals
Probe/remove both DT and PCI paths, test EIP97 and EIP197 variants, firmware present/missing/minifw fallback, multiple `max_rings` values, MSI/MSI-X on dev board, crypto self-tests for capability-filtered algorithms, ring saturation and backlog handling, fatal RDR status injection, DMA API debug, and suspend-like remove while queues are active.
