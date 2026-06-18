<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_marvel.c -->
## sources/distributed-fs/ceph-client/arch/alpha/kernel/core_marvel.c

**Purpose:** Implements Marvel IO7 core logic support for discovering IO7s, creating PCI hoses per enabled IO7 port, setting DMA windows, config access, RTC callbacks, MMIO/port mapping, VGA hose detection, and AGP support. This is platform hardware glue rather than Ceph client logic; it makes Linux PCI, DMA, I/O mapping, and machine-check paths work on Marvel/EV7 IO7 Alpha systems.

**Important APIs/types/functions:** `marvel_next_io7`, `marvel_find_io7`, `io7_clear_errors`, `marvel_init_arch`, `marvel_pci_ops`, `marvel_pci_tbi`, `marvel_ioremap`, `marvel_iounmap`, `marvel_is_mmio`, `marvel_ioportmap`, `marvel_ioread8`, `marvel_iowrite8`, `marvel_agp_ops`, and `marvel_agp_info`, plus static helpers for config-address construction, controller register access, DMA-window programming, and error clearing/decoding.

**Control flow:** boot parses the GCT for IO7 nodes or accepts `io7=` overrides, allocates IO7s, initializes enabled ports as PCI hoses, configures SG/direct DMA windows, disables the AGP monster window, and locates console VGA. Config access builds hose-relative addresses and rejects disabled ports or oversized primary-bus IDs.

**State and persistence behavior:** sorted `io7_head` list, per-IO7 port enable state, hose resources and saved DMA windows, direct map at 2 GiB/1 GiB, ISA and PCI SG arenas, RTC index shadow, and AGP aperture reservations. None of this is filesystem-persistent, but it persists for the lifetime of the booted kernel and controls all PCI/DMA behavior on the platform.

**Dependencies and integration points:** Depends on Alpha core-specific register headers, `asm/io.h`, `asm/ptrace.h`, `pci_impl.h`, `proto.h`, Linux PCI/resource/memblock APIs, IOMMU arena helpers, PAL machine-check state, and generic PCI enumeration.

**Risks:** These paths intentionally handle absent devices and bad PCI cycles with expected machine checks. Barrier ordering, readbacks that force posted writes, DMA window masks, and firmware restoration are all high-risk. Wrong hose resources or SG TLB invalidation can corrupt DMA or make PCI devices disappear.

**Test signals:** Boot a Marvel/EV7 IO7 kernel or emulator target, enumerate PCI, exercise config reads/writes to present and absent devices, run DMA through ISA and PCI windows, test ioremap/legacy I/O, and inject or observe machine checks during config probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_marvel.c -->
