# sources/distributed-fs/ceph-client/arch/nios2/kernel/vmlinux.lds.S

Purpose: defines the Nios II kernel link layout, sections, init areas, exception tables, BSS, and discard
rules.

Important APIs/types/functions: entry points: `_start`; prototypes: `EXCEPTION_TABLE`.

Control flow: Assembly labels are reached from reset, exception, or linker-defined entry points and transfer into
C helpers after saving the architecture register state.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `asm/page.h`, `asm-generic/vmlinux.lds.h`, `asm/cache.h`, `asm/thread_info.h`.
Integration points include generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree,
syscall, and cache/TLB subsystems plus Nios II control-register assembly. This source is part of the
Nios II architecture port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
