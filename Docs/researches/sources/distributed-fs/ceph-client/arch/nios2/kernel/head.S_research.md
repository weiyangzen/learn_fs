# sources/distributed-fs/ceph-client/arch/nios2/kernel/head.S

Purpose: contains the Nios II reset entry, cache initialization, kernel relocation, BSS clearing, fast TLB
miss hook, and transition into start_kernel.

Important APIs/types/functions: entry points: `_start`, `exception_handler_hook`, `fast_handler`, `fast_handler_end`.

Control flow: Boot starts at `_start`, disables interrupts, initializes instruction/data caches, relocates the
kernel image when needed, clears BSS, records current_thread, preserves boot arguments, and calls
`start_kernel`; the fast handler performs direct TLB refill from `pgd_current`.

State and persistence: State includes saved exception frames, thread_info flags, interrupt enable masks, current
task/thread pointers, kernel stacks, restart state, and architecture control registers.

Dependencies and integration points: Dependencies include `linux/init.h`, `linux/linkage.h`, `asm/thread_info.h`, `asm/processor.h`,
`asm/cache.h`, `asm/page.h`, `asm/asm-offsets.h`, `asm/asm-macros.h`. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
