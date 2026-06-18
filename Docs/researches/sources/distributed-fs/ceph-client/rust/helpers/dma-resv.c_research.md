# sources/distributed-fs/ceph-client/rust/helpers/dma-resv.c

## Purpose
Exposes DMA reservation object locking to Rust graphics/DMA users.

## APIs, Types, and Functions
`rust_helper_dma_resv_lock()` and `rust_helper_dma_resv_unlock()` wrap the reservation lock APIs.

## Control Flow, State, and Persistence
State is the reservation object's ww-mutex lock state; no local state is kept.

## Dependencies and Integration
Depends on `linux/dma-resv.h` and wound-wait acquire contexts.

## Risks and Test Signals
Risks are deadlocks from wrong ww context usage and unbalanced unlocks. Test signals are DRM/GEM Rust tests and lockdep ww-mutex coverage.
