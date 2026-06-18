# sources/distributed-fs/ceph-client/arch/hexagon/kernel/Makefile

## Purpose

`Makefile` selects the Hexagon kernel objects that form boot, trap, syscall, signal, process, timer, VM, SMP, KGDB, module, DMA, and stacktrace support. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The build API is the `obj-y` and `obj-$(CONFIG_...)` object list; it controls whether files such as `smp.o`, `kgdb.o`, `module.o`, `dma.o`, and `stacktrace.o` are linked. Concrete declarations observed in the file: Build/script rules: `always-$(KBUILD_BUILTIN) := vmlinux.lds`, `obj-y += head.o`, `obj-$(CONFIG_SMP) += smp.o`, `obj-y += setup.o irq_cpu.o traps.o syscalltab.o signal.o time.o`, `obj-y += process.o trampoline.o reset.o ptrace.o vdso.o`, `obj-$(CONFIG_KGDB)    += kgdb.o`, `obj-$(CONFIG_MODULES) += module.o hexagon_ksyms.o`, `obj-y += vm_entry.o vm_events.o vm_switch.o vm_ops.o vm_init_segtable.o`, `obj-y += vm_vectors.o`, `obj-$(CONFIG_HAS_DMA) += dma.o`, `obj-$(CONFIG_STACKTRACE) += stacktrace.o`.

## Control Flow, State, And Persistence

Build-time only; Kbuild resolves config-dependent object inclusion before link.

## Dependencies And Integration Points

It integrates with `arch/hexagon/Makefile`, generated `vmlinux.lds`, and all Hexagon kernel subsystems.

## Risks And Test Signals

Risks are omitting mandatory boot/VM objects or linking optional objects under the wrong config. Test signals are Hexagon defconfig/allmodconfig links and boot to `start_kernel`.
 A local static signal for this file is that it has 20 lines and 552 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
