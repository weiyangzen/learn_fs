# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/futex.h

Purpose: implements OpenRISC futex atomic operations on user addresses with exception-table recovery.

Important APIs/types/functions: functions: `arch_futex_atomic_op_inuser`, `futex_atomic_cmpxchg_inatomic`; prototypes:
`__volatile__`, `__futex_atomic_op`; macros: `__ASM_OPENRISC_FUTEX_H`, `__futex_atomic_op(insn, ret,
oldval, uaddr, oparg)`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/futex.h`, `linux/uaccess.h`, `asm/errno.h`. Integration points include
generic asm-generic helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex,
ELF, and Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under
the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
