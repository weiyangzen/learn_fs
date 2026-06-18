# sources/distributed-fs/ceph-client/arch/x86/include/asm/parport.h

Purpose: provides the x86 architecture hook used by the parport PC driver to discover non-PCI parallel ports. On x86, non-PCI probing is just ISA probing.

Important APIs, types, and functions: declares internal `parport_pc_find_isa_ports(int autoirq, int autodma)` and defines `parport_pc_find_nonpci_ports(int autoirq, int autodma)` as a wrapper returning the ISA probe result.

Control flow: callers invoke `parport_pc_find_nonpci_ports()`; it immediately delegates to `parport_pc_find_isa_ports()` with the auto IRQ/DMA policy supplied by the driver.

State and persistence: no state is owned. Detected ports and resource registrations are handled by the parport driver.

Dependencies and integration points: included by the parallel port subsystem's PC driver. It assumes ISA-style legacy port probing is the correct non-PCI path for x86.

Risks: small but ABI-like: if non-PCI discovery semantics change, this wrapper controls what legacy hardware is found. ISA probing can touch legacy I/O ports, so policy must remain in the driver.

Test signals: build parport PC support on x86, boot with legacy parallel port hardware or emulation, verify PCI and non-PCI ports are discovered appropriately, and test `autoirq`/`autodma` module parameters.
