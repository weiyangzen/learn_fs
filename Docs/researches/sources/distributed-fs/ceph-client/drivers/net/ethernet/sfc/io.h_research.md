<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/io.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/io.h

## Purpose
Provides low-level MMIO register access helpers for SFC NICs, including 32-bit and 128-bit CSR reads/writes, table access, page-mapped VI register access, architecture-specific 64-bit I/O, and PIO capability selection.

## Important APIs, types, and functions
- Raw helpers: `_efx_writed`, `_efx_readd`, and optional `_efx_writeq`/`_efx_readq`.
- CSR helpers: `efx_writeo`, `efx_writed`, `efx_reado`, `efx_readd`, `efx_writeo_table`, and `efx_reado_table`.
- VI/page helpers: `efx_paged_reg`, `efx_writeo_page`, and `efx_writed_page`.
- Constants: `EFX_DEFAULT_VI_STRIDE` and `EF100_DEFAULT_VI_STRIDE`.

## Control flow
The helpers calculate offsets from `efx->membase`, `efx->reg_base`, and `efx->vi_stride`, emit verbose hardware traces, and use `efx->biu_lock` around normal 128-bit CSR accesses. Page-mapped write macros use `BUILD_BUG_ON_ZERO` to restrict allowed registers at compile time.

## State and persistence behavior
No persistent state is owned here. The helpers mutate device MMIO state and rely on `efx->biu_lock`, register base, memory base, and VI stride stored in the NIC structure.

## Dependencies and integration points
Depends on Linux `io.h` and spinlocks plus SFC register word types/macros. It is foundational for NIC register programming, descriptor doorbells, event queue pointers, and SRAM/CSR access across EF10/EF100 code.

## Risks and test signals
Risks include incorrect locking around latching 128-bit registers, architecture-specific write-combining assumptions, raw I/O ordering surprises, and invalid page register offsets. Test signals are register read/write smoke tests, descriptor doorbell operation, lockdep coverage, compile-time macro failures for invalid page registers, and platform coverage on 32-bit vs 64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/io.h -->
