# sources/distributed-fs/ceph-client/arch/mips/include/asm/sync.h

## Purpose

`sync.h` centralizes MIPS `sync` instruction types, reasons, and assembly emission macros for memory ordering.

## Important APIs, Types, And Functions

Important APIs are `__SYNC_full`, `__SYNC_rmb`, `__SYNC_wmb`, `__SYNC_ginv`, reason bits such as `__SYNC_weak_ordering`, and emitters `__SYNC()`/`__SYNC_ELSE()`. Macros/constants: `__MIPS_ASM_SYNC_H__`, `__SYNC_none`, `__SYNC_full`, `__SYNC_aq`, `__SYNC_rl`, `__SYNC_mb`, `__SYNC_rmb`, `__SYNC_wmb`, `__SYNC_ginv`, `__SYNC_always`, `__SYNC_weak_ordering`, `__SYNC_weak_llsc`, `__SYNC_loongson3_war`, `__SYNC_rpt`, `____SYNC`, `___SYNC`, `__SYNC`, `__SYNC_ELSE`. Functions/prototypes/helpers: `__SYNC_rpt`.

## Control Flow

The macros expand in C inline asm or assembly files to conditionally emit the correct `sync` subtype, including Octeon double-WMB behavior and Loongson3 LL/SC errata barriers.

## State And Persistence

No kernel state is stored; state is hardware memory-ordering effects and instruction stream selection.

## Dependencies And Integration Points

It integrates with barriers, atomics, LL/SC loops, cache/TLB global invalidation, and CPU errata workarounds.

## Risks

Risks are under-barriering SMP/device interactions, over-barriering performance regressions, or bad assembler-time expression behavior.

## Test Signals

Test signals are LKMM/atomic litmus tests, locktorture, DMA ordering tests, Octeon and Loongson builds, and objdump validation of emitted syncs.
Static review signal: this source currently has 210 lines and 7824 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
