# sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/ocs-hcu.c

## Purpose
This file implements low-level register, DMA, interrupt, and hash/HMAC sequencing for the Keem Bay OCS Hash Control Unit. It is the hardware primitive layer consumed by `keembay-ocs-hcu-core.c`.

## Important APIs, Types, And Functions
- Register definitions cover HCU mode, chain, operation, key, interrupt/status, message length, DMA, and MSI registers.
- `struct ocs_hcu_dma_entry` and `struct ocs_hcu_dma_list` implement the coherent linked-list format for source DMA.
- Utility helpers: `ocs_hcu_num_chains()`, `ocs_hcu_digest_size()`, `ocs_hcu_wait_busy()`, interrupt enable/disable/wait helpers, and intermediate digest get/set helpers.
- Hardware configuration: `ocs_hcu_hw_cfg()` selects algorithm, endianness, and hardware HMAC mode.
- Key handling: `ocs_hcu_write_key()` writes and byte-swaps/pads the hardware HMAC key; `ocs_hcu_clear_key()` clears key registers.
- DMA operations: `ocs_hcu_ll_dma_start()` runs linked-list DMA and waits on either DMA or HCU completion depending on finality.
- Public DMA-list APIs: `ocs_hcu_dma_list_alloc()`, `ocs_hcu_dma_list_free()`, and `ocs_hcu_dma_list_add_tail()`.
- Public hash APIs: `ocs_hcu_hash_init()`, `ocs_hcu_hash_update()`, `ocs_hcu_hash_finup()`, `ocs_hcu_hash_final()`, `ocs_hcu_digest()`, and `ocs_hcu_hmac()`.
- IRQ handling: `ocs_hcu_irq_handler()` reads and clears HCU and DMA interrupt status, records error state, and completes waiters.

## Control Flow
Hash update configures hardware, restores intermediate state if present, starts linked-list DMA without termination, then reads back intermediate state. Finup configures/restores state, starts linked-list DMA with termination, waits for HCU completion, and reads the digest. Final without new data configures/restores state, writes terminate, waits, and reads digest. One-shot digest maps a linear buffer and starts direct DMA. Hardware HMAC configures HMAC mode, writes the key, runs final linked-list DMA, clears hardware key registers, and reads digest.

## State And Persistence
Persistent runtime state exists in hardware chain/message-length registers during an active operation and in `struct ocs_hcu_hash_ctx` between updates. `hcu_dev->irq_err` records whether the IRQ handler saw an error before the wait returns. DMA list memory is coherent and caller-owned. Hardware HMAC keys are cleared after use.

## Dependencies And Integration Points
The file depends on `ocs-hcu.h`, Linux MMIO and polling helpers, DMA mapping/coherent allocation, completions, IRQ handling, SHA2 constants, and front-end request code that supplies mapped data through DMA lists.

## Risks
- `ocs_hcu_digest()` returns immediately on `ocs_hcu_wait_and_disable_irq()` error without unmapping the direct DMA buffer, creating a DMA mapping leak on that error path.
- `kmalloc_obj(*dma_list)` is nonstandard-looking; build coverage should confirm the local tree provides this macro/helper.
- `ocs_hcu_dma_list_add_tail()` truncates DMA addresses to 32 bits after checking against `OCS_HCU_DMA_BIT_MASK`, so correct 32-bit DMA mask setup is mandatory.
- Interruptible waits can return early while hardware may still be active.
- Direct one-shot digest does not check `data`/`dgst` for NULL before DMA/register use; callers are expected to validate.

## Test Signals
- Front-end hash/HMAC Crypto API vectors exercising update, finup, final, digest, and HMAC.
- DMA API debug with injected interrupt errors to catch the one-shot digest unmap leak.
- Tests for DMA list append capacity, zero-length entries, and invalid high DMA addresses.
- IRQ error-bit injection to verify `irq_err` propagation and clearing.
