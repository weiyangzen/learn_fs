# sources/distributed-fs/ceph-client/arch/arm/kernel/isa.c

Purpose: exposes legacy ISA memory and I/O port base information through sysctl for ARM platforms that emulate or support ISA-style userspace port access.

Important APIs/types/functions: `register_isa_ports` stores `membase`, `portbase`, and `portshift`, then registers the `bus/isa` sysctl table. The table exposes read-only integer proc entries.

Control flow: platform code calls `register_isa_ports` during initialization; sysctl handlers serve the stored values.

State and persistence: static globals keep base/shift values for the system lifetime; `isa_sysctl_header` tracks the registration.

Dependencies and integration: depends on sysctl, proc integer handlers, and platform-specific ISA setup.

Risks: wrong values break glibc/userspace emulation of `iopl`, `inb`, and `outb`; values are read-only after registration. Test signals include presence and correctness of `/proc/sys/bus/isa/*` entries and userspace port I/O compatibility tests on affected boards.
