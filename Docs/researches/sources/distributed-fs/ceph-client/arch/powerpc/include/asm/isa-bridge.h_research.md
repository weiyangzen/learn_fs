# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/isa-bridge.h

Purpose: Declares early ISA bridge discovery and helper logic for recognizing legacy IO-port virtual addresses on PPC64.

Important APIs, types, and functions: On PPC64 exposes `isa_bridge_find_early()`, `isa_bridge_init_non_pci()`, and `isa_vaddr_is_ioport()`. On PPC32, `isa_vaddr_is_ioport()` always returns false.

Control flow: Platform PCI or non-PCI setup identifies an ISA bridge early. Later code can test whether an `__iomem` address falls inside the reserved ISA I/O range.

State and persistence: Bridge state is held externally by PCI/ISA setup code.

Dependencies and integration points: Depends on `pci_controller`, OF device nodes, and ISA I/O base range constants. It integrates legacy port I/O with PPC64 PCI host bridge setup.

Risks: Incorrect early bridge detection can make `arch_has_dev_port()` and legacy I/O probing wrong. Address-range checks are PPC64-specific.

Test signals: PPC64 boot with PCI ISA bridge, non-PCI ISA initialization, legacy serial/i8042 probing, and PPC32 compile behavior.
