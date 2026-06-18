# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/cpuinfo.h

Purpose: defines OpenRISC CPU/cache descriptor structures and exported cpuinfo setup/probing hooks.

Important APIs/types/functions: prototypes: `setup_cpuinfo`; types: `cache_desc`, `cpuinfo_or1k`; macros:
`__ASM_OPENRISC_CPUINFO_H`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `asm/spr.h`, `asm/spr_defs.h`. Integration points include generic asm-generic
helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex, ELF, and
Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under the
vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
