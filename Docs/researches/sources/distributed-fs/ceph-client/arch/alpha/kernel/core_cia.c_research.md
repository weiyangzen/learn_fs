<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_cia.c -->
## sources/distributed-fs/ceph-client/arch/alpha/kernel/core_cia.c

**Purpose:** Implements CIA/PYXIS core logic support for PCI config access, DMA windows, broken scatter-gather TLB workarounds, SRM restoration, and machine-check decoding. This is platform hardware glue rather than Ceph client logic; it makes Linux PCI, DMA, I/O mapping, and machine-check paths work on CIA/PYXIS Alpha systems.

**Important APIs/types/functions:** `cia_pci_ops`, `cia_pci_tbi`, `cia_init_arch`, `pyxis_init_arch`, `cia_kill_arch`, `cia_init_pci`, and `cia_machine_check`, plus static helpers for config-address construction, controller register access, DMA-window programming, and error clearing/decoding.

**Control flow:** config accesses program CIA CFG for type-1 cycles, clear error registers, mark expected machine checks, perform sparse config-space load/store, then restore CFG. Initialization clears error masks, enables machine checks, sets HAE and DMA windows, prepares or verifies TBIA workarounds, and common PCI init runs after machine checks are available.

**State and persistence behavior:** single hose with ISA SG window, 2 GiB direct map, optional DAC window, HAE resources, CIA/PYXIS controller registers, saved SRM configuration, and machine-check expected/taken flags. None of this is filesystem-persistent, but it persists for the lifetime of the booted kernel and controls all PCI/DMA behavior on the platform.

**Dependencies and integration points:** Depends on Alpha core-specific register headers, `asm/io.h`, `asm/ptrace.h`, `pci_impl.h`, `proto.h`, Linux PCI/resource/memblock APIs, IOMMU arena helpers, PAL machine-check state, and generic PCI enumeration.

**Risks:** These paths intentionally handle absent devices and bad PCI cycles with expected machine checks. Barrier ordering, readbacks that force posted writes, DMA window masks, and firmware restoration are all high-risk. Wrong hose resources or SG TLB invalidation can corrupt DMA or make PCI devices disappear.

**Test signals:** Boot a CIA/PYXIS kernel or emulator target, enumerate PCI, exercise config reads/writes to present and absent devices, run DMA through ISA and PCI windows, test ioremap/legacy I/O, and inject or observe machine checks during config probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_cia.c -->
