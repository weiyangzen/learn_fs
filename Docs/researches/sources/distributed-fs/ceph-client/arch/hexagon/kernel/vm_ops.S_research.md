# sources/distributed-fs/ceph-client/arch/hexagon/kernel/vm_ops.S

## Purpose

`vm_ops.S` provides assembly wrappers for Hexagon VM operations such as interrupt enable, wait/yield, cache/TLB, and VM control primitives. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The file's symbols are low-level ABI helpers referenced from C and exported for modules where needed. Concrete declarations observed in the file: Includes: `linux/linkage.h`, `asm/hexagon_vm.h`. Assembly entry labels: `__vmrte`, `__vmsetvec`, `__vmsetie`, `__vmgetie`, `__vmintop`, `__vmclrmap`, `__vmnewmap`, `__vmcache`, `__vmgettime`, `__vmsettime`, `__vmwait`, `__vmyield`, `__vmstart`, `__vmstop`, `__vmvpid`, `__vmsetregs`, `__vmgetregs`.

## Control Flow, State, And Persistence

Control flow is direct wrapper execution: move arguments into expected registers, execute HVM instructions, return status/results.

## Dependencies And Integration Points

It integrates with `hexagon_ksyms.c`, IRQ, timer, cache, SMP, and reset code.

## Risks And Test Signals

Risks are wrong calling convention or clobber set around privileged VM operations. Test signals are boot, interrupt enable/disable, cache/TLB flush, idle wait, and SMP stop paths.
 A local static signal for this file is that it has 90 lines and 1647 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
