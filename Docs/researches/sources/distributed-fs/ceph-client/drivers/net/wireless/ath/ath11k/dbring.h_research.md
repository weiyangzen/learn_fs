# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/dbring.h

## Purpose
`dbring.h` declares the generic direct-buffer ring data structures and API used by spectral/CFR-style firmware DMA streams.

## Important APIs, Types, And Functions
`struct ath11k_dbring_element` tracks a payload allocation and DMA address. `struct ath11k_dbring_data` is passed to feature handlers with aligned data, metadata, buffer pointer, and buffer ID. `struct ath11k_dbring_buf_release_event` normalizes WMI release event parts. `struct ath11k_dbring_cap` mirrors firmware capability for pdev, module, element count, size, and alignment. `struct ath11k_dbring` stores the refill SRNG, IDR, locks, head/tail addresses, buffer parameters, response settings, and handler. Prototypes expose setup, WMI config, replenish, release processing, capability lookup, cleanup, and validation.

## Control Flow
Feature modules obtain capabilities, initialize an `ath11k_dbring`, configure it with a callback, fill buffers, inform firmware, then receive release events through the common event handler. The handler callback decides whether a buffer can be replenished immediately or must be held.

## State And Persistence
All declared state is per-feature/per-radio runtime state. The IDR maps firmware cookies to live buffer elements; the handler pointer is the module-specific processing hook.

## Dependencies And Integration Points
The header depends on Linux types, IDR, spinlocks, and `dp.h` for `dp_srng`. It references WMI direct-buffer modules and release metadata through included dependencies. It is consumed by CFR, spectral, WMI event handling, and debug code.

## Risks And Test Signals
The callback contract is subtle: `ATH11K_CORRELATE_STATUS_HOLD` means ownership remains with the feature until later replenish. Misusing that status can leak buffers or race cleanup. Compile tests should cover modules that include this header, and runtime tests should validate capability lookup, IDR cleanup, and handler ownership rules.
