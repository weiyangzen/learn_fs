# sources/distributed-fs/ceph-client/arch/nios2/include/asm/switch_to.h

Purpose: wraps the assembly resume entry as the Nios II switch_to primitive and feeds the previous/current
task pointers expected by scheduler context switching.

Important APIs/types/functions: prototypes: `__volatile__`; macros: `_ASM_NIOS2_SWITCH_TO_H`, `switch_to(prev, next, last)`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
