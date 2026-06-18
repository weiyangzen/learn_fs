<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/parport.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/parport.h

**Purpose:** Provides the Alpha hook used by `drivers/parport/parport_pc.c` to discover PC-style non-PCI parallel ports.

**Important APIs/types/functions:** `parport_pc_find_nonpci_ports(autoirq, autodma)` and the static declaration for `parport_pc_find_isa_ports`.

**Control flow:** The non-PCI discovery function simply delegates to ISA port probing with the caller's IRQ/DMA autodetection flags.

**State and persistence behavior:** No local state. The parport driver owns any registered port state.

**Dependencies and integration points:** Integrated only with `parport_pc.c` and ISA-style I/O probing on Alpha systems.

**Risks:** The header is intended for one driver include path; broader inclusion would expose static prototypes in surprising scopes. Incorrect ISA probing can touch legacy I/O ranges.

**Test signals:** Build with parallel-port support, boot on systems with and without ISA parports, and verify autodetected IRQ/DMA settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/parport.h -->
