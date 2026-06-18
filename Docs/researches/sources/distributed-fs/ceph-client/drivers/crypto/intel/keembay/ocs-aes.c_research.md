# sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/ocs-aes.c

## Purpose
This file provides low-level MMIO, DMA, interrupt, and mode sequencing primitives for the Keem Bay OCS AES/SM4 block. It is used by `keembay-ocs-aes-core.c` to perform ECB/CBC/CTR/CTS, GCM, CCM, and DMA bypass operations.

## Important APIs, Types, And Functions
- Register definitions cover AES command/key/IV/status, DMA source/destination/list registers, interrupt registers, tag/MAC registers, payload length, and byte-order configuration.
- `struct ocs_dma_linked_list` is the hardware DMA descriptor layout; public linked-list descriptors are represented by `struct ocs_dll_desc` from the header.
- IRQ helpers: `aes_irq_disable()`, `aes_irq_enable()`, `ocs_aes_irq_enable_and_wait()`, and `ocs_aes_irq_handler()` drive completion and DMA error reporting through `aes_dev->irq_completion` and `dma_err_mask`.
- Key programming: `ocs_aes_set_key()` validates AES/SM4 key sizes and writes key registers plus key-size register.
- Generic operation: `ocs_aes_validate_inputs()`, `set_ocs_aes_command()`, `ocs_aes_init()`, and `ocs_aes_op()` validate, configure, run, and wait for non-AEAD modes.
- GCM: `ocs_aes_gcm_op()` writes J0, tag length, payload/AAD bit lengths, processes AAD then payload, and reads tag registers through `ocs_aes_gcm_read_tag()`.
- CCM: `ocs_aes_ccm_op()` normalizes counter, writes B0 and AAD length encoding, processes AAD and payload, writes encrypted tag for decrypt, and compares tag registers through `ccm_compare_tag_to_yr()`.
- DMA list creation: `ocs_create_linked_list_from_sg()` builds coherent OCS DMA linked lists from already mapped SG entries and supports offsets into SG data.

## Control Flow
All operations initialize hardware by disabling/clearing interrupts, setting byte order, and writing the command register. Non-AEAD modes trigger the AES engine, configure source and destination linked-list DMA, set termination or CTS last-block signaling, wait for AES completion, and read CTR IV back when required. GCM/CCM split AAD and payload phases, using DMA source-done interrupts for AAD/payload feeding and AES-complete interrupts for final authentication/tag completion.

## State And Persistence
State is in hardware registers and `struct ocs_aes_dev` fields. `dma_err_mask` is written by the IRQ handler and consumed by wait helpers. Coherent DMA linked lists are allocated by the caller-facing helper and freed by front-end cleanup. No state persists beyond the operation except updated hardware registers and caller-managed IV/tag data.

## Dependencies And Integration Points
The file depends on Linux MMIO accessors, completions, IRQ handling, DMA coherent allocation, scatterlist DMA metadata, AES/GCM constants, and the public types declared in `ocs-aes.h`.

## Risks
- Many wait loops are busy loops without explicit timeout (`aes_a_wait_last_gcx()`, `aes_a_dma_wait_input_buffer_occupancy()`, performance-counter waits), so hardware hangs can stall the crypto engine worker.
- `ocs_aes_irq_enable_and_wait()` uses interruptible waits; signal interruptions propagate as errors but hardware may still be active.
- `ocs_aes_set_key()` casts arbitrary key pointers to `u32 *`, relying on alignment that may not be guaranteed on all architectures.
- `ocs_aes_ccm_op()` mutates the caller-provided IV by zeroing the counter field.
- `ocs_create_linked_list_from_sg()` assumes `sg_dma_len()`/`sg_dma_address()` are valid because the caller already mapped the SG list; misuse will produce invalid DMA descriptors.
- GCM and CCM tag compares are not constant-time.

## Test Signals
- Low-level mode vectors through the front-end driver for ECB/CBC/CTR/CTS/GCM/CCM and SM4 equivalents.
- Fault-injection around IRQ errors and DMA error bits to verify `-EIO` propagation.
- Hardware hang tests or instrumentation for busy-wait loops.
- SG offset/list tests for `ocs_create_linked_list_from_sg()` with zero data, offset crossing entries, and invalid lengths.
