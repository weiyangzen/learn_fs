# sources/distributed-fs/ceph-client/arch/hexagon/kernel/asm-offsets.c

## Purpose

`asm-offsets.c` emits assembly offsets for Hexagon low-level code. It uses `DEFINE` from `linux/kbuild.h` to publish `pt_regs`, `thread_info`, and `hexagon_switch_stack` field offsets. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The generated constants are consumed by exception entry, context switch, linker, and VM assembly. Concrete declarations observed in the file: Includes: `linux/compat.h`, `linux/types.h`, `linux/sched.h`, `linux/interrupt.h`, `linux/kbuild.h`, `asm/ptrace.h`, `asm/processor.h`. Macros: `COMPILE_OFFSETS`. Types referenced or declared: `pt_regs`, `hexagon_switch_stack`. Functions/syscalls: `main`.

## Control Flow, State, And Persistence

Build-time C is compiled by the offsets generator; no runtime object is linked.

## Dependencies And Integration Points

It integrates with `include/generated/asm-offsets.h`, `vm_entry.S`, `vm_switch.S`, `head.S`, and `vmlinux.lds.S`.

## Risks And Test Signals

Risks are stale offsets after C structure layout changes. Test signals are successful assembly, objdump sanity around save/restore code, and boot through fork/syscall/interrupt paths.
 A local static signal for this file is that it has 93 lines and 3144 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
