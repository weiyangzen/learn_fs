<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/cache-ops.c -->
# sources/distributed-fs/ceph-client/arch/riscv/mm/cache-ops.c

## Purpose
`cache-ops.c` stores and exports nonstandard cache operation callbacks for RISC-V noncoherent DMA support.

## Important APIs, Types, And Functions
`noncoherent_cache_ops` is a `__ro_after_init` global. `riscv_noncoherent_register_cache_ops()` copies a supplied `struct riscv_nonstd_cache_ops` into it and is exported GPL-only.

## Control Flow
Registration is a simple null check followed by structure copy. DMA maintenance paths later call populated callbacks when present.

## State And Persistence
The registered callback table persists after init as read-only kernel data. There is no disk persistence.

## Dependencies And Integration Points
It integrates platform/vendor cache maintenance implementations with `dma-noncoherent.c`.

## Risks
Callbacks must be registered before `__ro_after_init` protection and must implement correct cache semantics. Null ops fall back to standard CMO operations.

## Test Signals
Platform boot on nonstandard-cache systems, DMA correctness tests, and verifying fallback behavior with no registered ops are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/cache-ops.c -->
