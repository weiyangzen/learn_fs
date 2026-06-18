# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/io.h

## Purpose

`io.h` provides low-level MMIO and SRAM access helpers for the Solarflare driver. For Falcon/Siena hardware it encodes the Bus Interface Unit locking rules needed for wide 128-bit CSR and 64-bit SRAM access, while allowing special descriptor and event doorbell writes to avoid unnecessary locking on fast paths.

The file is a safety boundary between higher-level hardware code and raw `__raw_read*()`/`__raw_write*()` operations.

## Important APIs, Types, and Functions

Configuration macros include `EFX_USE_QWORD_IO`, `EFX_USE_PIO`, `EFX_DEFAULT_VI_STRIDE`, and `EF100_DEFAULT_VI_STRIDE`. Raw wrappers `_efx_writeq()`, `_efx_readq()`, `_efx_writed()`, `_efx_readd()`, and `efx_reg()` wrap direct MMIO primitives and base-offset handling.

Locked wide access helpers are `efx_writeo()`, `efx_reado()`, `efx_sram_writeq()`, and `efx_sram_readq()`, all serialized with `efx->biu_lock`. Narrow and special access helpers are `efx_writed()`, `efx_readd()`, `efx_writeo_table()`, `efx_reado_table()`, `efx_paged_reg()`, `efx_writeo_page()`, `efx_writed_page()`, and `efx_writed_page_locked()`.

## Control Flow

The main control-flow decision is whether an operation must serialize with the BIU collector. Normal 128-bit CSR writes, wide CSR reads, and SRAM access take `efx->biu_lock`, emit the raw writes/reads in the correct order, and release the lock. Narrow 32-bit CSR access skips locking.

Page-register helpers compute `page * efx->vi_stride + reg`. Macro wrappers add compile-time `BUILD_BUG_ON_ZERO()` validation so only known-safe register offsets are passed to special no-lock write paths. `efx_writed_page_locked()` locks only TIMER_COMMAND page 0 because of a BIU collector bug.

## State and Persistence Behavior

The header owns no persistent state, but it mutates device register and SRAM state through MMIO. Its driver state dependencies are `efx->biu_lock`, `efx->membase`, `efx->reg_base`, `efx->vi_stride`, and debug logging fields. Correct lock use protects the BIU collector from interleaved wide writes that could lose data.

## Dependencies and Integration Points

`io.h` depends on Linux IO and spinlock APIs and on driver-defined `efx_nic`, `efx_oword_t`, `efx_qword_t`, and `efx_dword_t` types plus debug formatting macros. It is included by `farch.c` and other low-level NIC code that programs registers listed in `farch_regs.h`.

The helper contract is tightly coupled to hardware behavior: Falcon/Siena 128-bit CSRs are not host-atomic, the BIU buffers partial wide writes, descriptor update registers have special high-dword semantics, and TIMER_COMMAND page 0 has a collector invalidation issue.

## Risks and Edge Cases

Using `efx_writed()` against a non-special part of a wide CSR can corrupt or discard BIU collector state. Omitting `biu_lock` for ordinary 128-bit CSR/SRAM access can lose register updates. Incorrect `vi_stride` or illegal page offsets would target the wrong queue/register. Architecture-specific 64-bit IO assumptions affect PIO and write-combining behavior. Callers still need explicit descriptor memory barriers before doorbells.

## Test Signals

Test signals include clean register self-tests, stable queue initialization under concurrent channels, no lost writes during repeated reset, correct TX/RX descriptor doorbell behavior, timer programming on page 0 without corrupting later wide writes, successful operation on both 32-bit and 64-bit builds, and hardware debug logs showing expected register addresses and values.
