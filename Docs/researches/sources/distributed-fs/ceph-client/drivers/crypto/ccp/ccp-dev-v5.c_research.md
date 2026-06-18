# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-dev-v5.c

## Purpose

`ccp-dev-v5.c` implements version 5 CCP hardware operations. It replaces v3 request-register submission with DMA-backed descriptor queues, manages private/shared local storage block allocation, assigns LSB regions to hardware queues, handles v5 per-queue interrupts, initializes queue memory/registers, configures v5 variants, and registers device services.

## Important APIs, Types, And Functions

- `ccp_lsb_alloc()`/`ccp_lsb_free()` allocate contiguous LSB slots from a queue-private region first, then shared regions.
- `union ccp_function` and descriptor field macros encode v5 command function and `struct ccp5_desc` fields.
- `low_address()`, `high_address()`, and `ccp5_get_free_slots()` support descriptor queue addressing.
- `ccp5_do_cmd()` copies a descriptor into the queue ring, advances tail, starts the queue, and waits for completion/error interrupts when requested.
- `ccp5_perform_aes()`, `ccp5_perform_xts_aes()`, `ccp5_perform_sha()`, `ccp5_perform_des3()`, `ccp5_perform_rsa()`, `ccp5_perform_passthru()`, and `ccp5_perform_ecc()` fill v5 descriptors and update per-engine stats.
- `ccp_find_lsb_regions()`, `ccp_find_and_assign_lsb_to_q()`, and `ccp_assign_lsbs()` derive private/shared LSB allocation from hardware masks.
- `ccp5_irq_bh()` and `ccp5_irq_handler()` handle per-queue interrupt status.
- `ccp5_init()` performs v5 device initialization.
- `ccp5_destroy()` tears down v5 services and fails queued commands.
- `ccp5_config()` and `ccp5other_config()` configure public and NTB/other variants.
- `ccp5_actions`, `ccpv5a`, and `ccpv5b` expose v5 operation tables and vdata.

## Control Flow

Init reads `Q_MASK_REG` and treats `0xffffffff` as inaccessible hardware, often due to firmware/BIOS restrictions. For each available queue, it creates a DMA pool, initializes a mutex, allocates coherent descriptor ring memory, computes per-queue register pointers, and clears interrupts. It requests IRQ, optionally initializes a tasklet, copies private LSB masks to public registers, programs queue ring base/tail/head/control, discovers queue LSB access, assigns private/shared LSBs, preallocates key/context LSB slots, starts queue kthreads, enables interrupts, adds the device to the global list, registers RNG and DMAengine, and creates debugfs entries when configured.

Each operation builds a zeroed 8-dword descriptor, fills SOC/IOC/INIT/EOM/protection bits, engine and function fields, source/destination/key addresses and memory types, and optional LSB context ID. `ccp5_do_cmd()` endian-converts descriptor words into coherent ring memory, advances `qidx`, uses `wmb()`, writes the new tail, sets the run bit, and waits for an interrupt if IOC is set. On error it logs the CCP error and flushes by moving the head pointer to the submitted tail.

## State And Persistence Behavior

Driver state includes coherent descriptor queues, per-queue `qidx`, cached `qcontrol`, private LSB assignment, queue-private and device-shared LSB bitmaps, preallocated key/context slots, interrupt status/error fields, kthreads, DMA pools, statistics, and debugfs dentries. Hardware state includes queue control/head/tail/interrupt registers, LSB masks, queue masks/priorities, TRNG/AES mask configuration for v5b, and clock gating settings.

## Dependencies And Integration Points

This file depends on generic CCP scheduling in `ccp-dev.c`, SP IRQ helpers, hwrng/DMAengine registration, debugfs helpers, coherent DMA allocation, and operation setup from `ccp-ops.c`. It provides DES3 and SHA384/SHA512 capability used by crypto provider version gating.

## Risks And Edge Cases

- `ccp_lsb_free()` checks `cmd_q->lsb == start`, but allocated private slots are returned as `start + lsb * LSB_SIZE`; freeing private offsets other than the region base may follow the shared path.
- The LSB assignment algorithm is intentionally brute force and must handle constrained queue masks; bad masks can fail init.
- `ccp5_destroy()` calls `ccp5_debugfs_destroy()` when `ccp_present()` returns nonzero after deletion, which corresponds to no devices present; the condition is subtle.
- Descriptor queue uses one unused slot; free-slot math and qidx/head synchronization are critical under high concurrency.
- BIOS/device inaccessibility returns positive `1`, which the generic init treats as quiet nonfatal failure for the CCP portion.

## Test Signals

Signals include v5 queue discovery and descriptor ring operation, LSB private/shared allocation under concurrent AES/XTS/SHA/DES3/RSA/passthrough/ECC workloads, interrupt/error handling, debugfs stats increments, v5b setup register programming, inaccessible-device quiet failure, DMAengine registration, and clean teardown with queued callbacks.
