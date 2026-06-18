# sources/distributed-fs/ceph-client/arch/nios2/include/asm/unistd.h

Purpose: connects Nios II to its UAPI syscall numbers and selects legacy stat64 and rlimit syscall wants.

Important APIs/types/functions: macros: `__ASM_UNISTD_H`, `__ARCH_WANT_STAT64`, `__ARCH_WANT_SET_GET_RLIMIT`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `uapi/asm/unistd.h`. Integration points include generic Linux MM, irq, signal,
ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II control-
register assembly. This source is part of the Nios II architecture port under the vendored ceph-
client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
