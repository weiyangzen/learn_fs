# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/io-defs.h

Purpose: Provides the macro include-list used by `io.h` to declare and define PCI/ISA port I/O accessors consistently.

Important APIs, types, and functions: Expands `DEF_PCI_AC_RET` or `DEF_PCI_AC_NORET` for `inb/inw/inl`, `outb/outw/outl`, string input operations, and string output operations.

Control flow: `io.h` includes this file twice with different macro definitions: once to build the `ppc_pci_io` hook structure and again to generate inline wrappers that call hooks or default implementations.

State and persistence: No state. It participates in compile-time code generation.

Dependencies and integration points: Tightly coupled to `asm/io.h` and optional indirect PIO hooks.

Risks: Because it is intentionally multiple-included, include guards would break it. Argument tuple order must match both hook declarations and default `__do_*` functions.

Test signals: Compile with and without `CONFIG_PPC_INDIRECT_PIO`, verify all accessors are declared once, and exercise hook override paths for port I/O.
