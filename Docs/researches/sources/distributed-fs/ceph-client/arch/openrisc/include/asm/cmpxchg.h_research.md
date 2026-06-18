# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/cmpxchg.h

Purpose: implements OpenRISC xchg and cmpxchg primitives, including byte/halfword masking around 32-bit
atomic operations.

Important APIs/types/functions: functions: `Copyright`, `xchg_u32`, `cmpxchg_small`, `xchg_small`, `__cmpxchg`, `__arch_xchg`;
prototypes: `__volatile__`, `cmpxchg`, `cmpxchg_small`, `__cmpxchg`,
`__xchg_called_with_bad_pointer`, `xchg_small`, `__arch_xchg`; macros: `__ASM_OPENRISC_CMPXCHG_H`,
`__HAVE_ARCH_CMPXCHG`, `arch_cmpxchg(ptr, o, n)`, `arch_xchg(ptr, with)`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/bits.h`, `linux/compiler.h`, `linux/types.h`. Integration points include
generic asm-generic helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex,
ELF, and Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under
the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
