<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_irongate.c -->
## sources/distributed-fs/ceph-client/arch/alpha/kernel/core_irongate.c

**Purpose:** Implements IRONGATE/AMD 751-761 core logic support for PCI config space, Albacore memory reservation, AGP aperture ioremap, and error clearing. This is platform hardware glue rather than Ceph client logic; it makes Linux PCI, DMA, I/O mapping, and machine-check paths work on IRONGATE Alpha systems.

**Important APIs/types/functions:** `irongate_pci_ops`, `irongate_pci_clr_err`, `irongate_init_arch`, `irongate_ioremap`, and `irongate_iounmap`, plus static helpers for config-address construction, controller register access, DMA-window programming, and error clearing/decoding.

**Control flow:** config reads/writes access IRONGATE config addresses directly with byte/word helpers and readbacks. Initialization clears errors, warns about old PALcode on Albacore, reserves memory above PCI space when needed, disables AGP GART by default, and sets direct-map DMA.

**State and persistence behavior:** single hose, dense I/O and memory bases with 43-bit user bias, direct-map DMA state, optional AGP GATT mappings, global `IronECC`, and temporarily reserved memory above PCI aperture. None of this is filesystem-persistent, but it persists for the lifetime of the booted kernel and controls all PCI/DMA behavior on the platform.

**Dependencies and integration points:** Depends on Alpha core-specific register headers, `asm/io.h`, `asm/ptrace.h`, `pci_impl.h`, `proto.h`, Linux PCI/resource/memblock APIs, IOMMU arena helpers, PAL machine-check state, and generic PCI enumeration.

**Risks:** These paths intentionally handle absent devices and bad PCI cycles with expected machine checks. Barrier ordering, readbacks that force posted writes, DMA window masks, and firmware restoration are all high-risk. Wrong hose resources or SG TLB invalidation can corrupt DMA or make PCI devices disappear.

**Test signals:** Boot a IRONGATE kernel or emulator target, enumerate PCI, exercise config reads/writes to present and absent devices, run DMA through ISA and PCI windows, test ioremap/legacy I/O, and inject or observe machine checks during config probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_irongate.c -->
