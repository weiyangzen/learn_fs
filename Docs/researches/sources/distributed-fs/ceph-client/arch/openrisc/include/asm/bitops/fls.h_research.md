# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/bitops/fls.h

Purpose: implements or selects the OpenRISC `fls` bit-operation helper used by generic bitmap, scheduler,
filesystem, and atomic bit APIs.

Important APIs/types/functions: functions: `Copyright`; prototypes: `__asm__`; macros: `__ASM_OPENRISC_FLS_H`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `asm-generic/bitops/fls.h`. Integration points include generic asm-generic
helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex, ELF, and
Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under the
vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
