# sources/distributed-fs/ceph-client/drivers/crypto/intel/iaa/iaa_crypto_main.c Research

## Purpose
`iaa_crypto_main.c` is the main Intel Analytics Accelerator crypto driver. It binds to IDXD IAX workqueues, creates a per-CPU workqueue selection table, registers a Crypto API async compression algorithm named `deflate` with driver name `deflate-iaa`, builds IAA hardware descriptors for compression/decompression, optionally verifies compressed output by hardware decompression and CRC comparison, exposes sysfs controls, and handles module/probe/remove lifecycle.

## Important APIs, Types, and Functions
Global state includes `nr_iaa`, CPU/node counts, `cpus_per_iaa`, per-CPU `wq_table`, global `iaa_devices`, `iaa_devices_lock`, `iaa_crypto_enabled`, `iaa_crypto_registered`, `iaa_verify_compress`, and sync-mode flags `async_mode`/`use_irq`.

Sysfs driver attributes are `verify_compress` and `sync_mode`. They are writable only while IAA crypto is disabled. `set_iaa_sync_mode()` maps strings to operation flags, although the `"async"` branch currently sets the same flags as `"sync"`, making the `async_mode && !use_irq` display branch unreachable from the store path.

Compression mode APIs `add_iaa_compression_mode()` and `remove_iaa_compression_mode()` manage global compression modes before devices exist. `init_device_compression_mode()` allocates per-device DMA-coherent AECS tables and copies mode Huffman tables into them. Workqueue/device helpers include `save_iaa_wq()`, `remove_iaa_wq()`, `iaa_wq_get()`, `iaa_wq_put()`, `alloc_wq_table()`, `rebalance_wq_table()`, and `wq_table_next_wq()`.

The data path is implemented by `iaa_comp_acompress()` and `iaa_comp_adecompress()`. They select a workqueue for the current CPU, take a workqueue reference, map source and destination SG lists, call `iaa_compress()` or `iaa_decompress()`, handle synchronous or asynchronous completion, unmap DMA, and release the workqueue. `check_completion()` polls completion records and maps hardware status to Linux errors. `iaa_desc_complete()` handles interrupt-driven asynchronous completions. `deflate_generic_decompress()` is a software fallback for selected decompression analytics errors.

`iaa_register_compression_device()` registers `iaa_acomp_fixed_deflate`; `iaa_crypto_probe()` binds an IDXD workqueue, initializes global tables on the first workqueue, saves/rebalances workqueues, registers the Crypto API algorithm, and enables the driver. `iaa_crypto_remove()` quiesces and removes a workqueue, waits for references through remove flags, disables the driver on last removal, and frees the per-CPU table.

## Control Flow
Module init counts CPUs and NUMA nodes, registers the fixed compression mode, registers the IDXD subdriver, creates sysfs attributes, and initializes debugfs stats if available. Probe accepts only enabled IAX devices with matching workqueue driver names, enables the IDXD workqueue, creates the global workqueue table on first bind, initializes per-device compression modes, rebalances CPU-to-workqueue mappings, registers the acomp algorithm on first workqueue, and marks `iaa_crypto_enabled`.

Compression requests enter through Crypto API acomp. The driver rejects disabled state or missing source data, selects a workqueue via the per-CPU table, maps a single source and destination SG entry, fills an IAX compress descriptor with source, destination, AECS table, completion address, and flags, submits it to IDXD, and either polls or returns `-EINPROGRESS` depending on context mode. If verification is enabled, it remaps buffers in reverse directions, submits a suppress-output decompression descriptor, and compares CRCs.

Decompression mirrors compression but builds an IAX decompress descriptor. If hardware returns an analytics error, the synchronous and IRQ completion paths can fall back to generic deflate decompression. Remove flow quiesces the workqueue first, then removes it from selection structures while preserving active references until `iaa_wq_put()`.

## State and Persistence
Runtime state is fully in kernel memory: global mode registry, per-device mode DMA tables, per-workqueue reference/remove state, per-CPU workqueue arrays, Crypto API registration state, sysfs-controllable defaults, and optional stats counters. Per-transform `iaa_compression_ctx` snapshots verification and sync-mode defaults at transform init; changing sysfs attributes later does not alter existing transform contexts.

## Dependencies and Integration Points
The file depends on IDXD core APIs for workqueue enable/disable, descriptor allocation/submission/freeing, completion callbacks, and workqueue private data. It depends on `iaa_crypto.h` for structures and flags, `iaa_crypto_comp_fixed.c` for fixed-mode registration, optional `iaa_crypto_stats` for counters/debugfs, Linux DMA mapping and scatterlist APIs, sysfs driver attributes, module lifecycle, and Crypto API `acompress`.

## Risks and Edge Cases
The data path only accepts SG mappings that collapse to one DMA segment; multi-segment inputs return `-EIO`, which is a functional limitation tests must capture. DMA unmap direction changes during verification are delicate. Async mode without IRQ appears unselectable because `set_iaa_sync_mode("async")` sets `async_mode = false`; if intentional, the mode description is stale, and if not, async polling mode is broken. `check_completion()` disables global IAA crypto on completion timeout, affecting all users. Hot-remove safety depends on `iaa_wq_get()`/`iaa_wq_put()` reference ordering and `remove` flags. The compression mode registry refuses add/remove while devices exist, so module ordering is strict. Per-transform contexts snapshot global sysfs settings, which may surprise users expecting live changes.

## Test Signals
Test module load/unload, IDXD workqueue probe/remove, first/last workqueue registration, sysfs writes before and after enable, sync/async_irq behavior, compression/decompression known-answer tests, verification CRC mismatch handling, hardware buffer overflow mapping to `-E2BIG` or `-EOVERFLOW`, software fallback on analytics decompression errors, completion timeout disabling, single-vs-multi-SG behavior, CPU hotplug/NUMA selection assumptions, stats on/off builds, and hot-remove during in-flight async acomp requests.
