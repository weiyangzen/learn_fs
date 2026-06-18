# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/asm-prototypes.h

## Purpose

`asm-prototypes.h` declares prototypes needed by LoongArch assembly and modversion tooling, including uaccess, FPU, LBT, MMU context, page, ftrace, and generic asm prototypes. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The API is the included prototype set and forward declarations for task, register, KVM, and FPU types. Concrete declarations observed in the file: Includes: `linux/uaccess.h`, `asm/fpu.h`, `asm/lbt.h`, `asm/mmu_context.h`, `asm/page.h`, `asm/ftrace.h`, `asm-generic/asm-prototypes.h`. Types referenced or declared: `task_struct`, `pt_regs`, `kvm_run`, `kvm_vcpu`, `loongarch_fpu`.

## Control Flow, State, And Persistence

Build-time only; it ensures symbol CRC/prototype visibility for assembly-callable routines.

## Dependencies And Integration Points

It integrates with modversions, ftrace, KVM, FPU/LBT code, and asm-generic prototypes.

## Risks And Test Signals

Risks are missing prototypes causing modversion drift or build warnings. Test signals are `CONFIG_MODVERSIONS`, modules build, and W=1 compile checks.
 A local static signal for this file is that it has 43 lines and 1207 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
