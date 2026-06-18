<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_t2.c -->
## sources/distributed-fs/ceph-client/arch/alpha/kernel/core_t2.c

**Purpose:** Implements T2/SABLE core logic support for sparse PCI config access, saved SRM DMA-window restoration, direct and ISA SG DMA windows, TLB invalidation, and broadcast-style machine-check filtering. This is platform hardware glue rather than Ceph client logic; it makes Linux PCI, DMA, I/O mapping, and machine-check paths work on T2 Alpha systems.

**Important APIs/types/functions:** `t2_pci_ops`, `t2_init_arch`, `t2_kill_arch`, `t2_pci_tbi`, and `t2_machine_check`, plus static helpers for config-address construction, controller register access, DMA-window programming, and error clearing/decoding.

**Control flow:** config access validates primary-bus device IDs, toggles `T2_HAE_3` for type-1 cycles, marks expected machine checks, performs sparse config load/store, delays for possible broadcast checks, then restores HAE. Init enables SG TLB, saves SRM config, creates resources, sets windows, and zeros HAE registers.

**State and persistence behavior:** single hose, saved T2 window/HAE/HBASE registers, direct map window 1, ISA SG window 2, per-CPU `mcheck_expected/taken`, and global `t2_mcheck_any_expected/last_taken` masks. None of this is filesystem-persistent, but it persists for the lifetime of the booted kernel and controls all PCI/DMA behavior on the platform.

**Dependencies and integration points:** Depends on Alpha core-specific register headers, `asm/io.h`, `asm/ptrace.h`, `pci_impl.h`, `proto.h`, Linux PCI/resource/memblock APIs, IOMMU arena helpers, PAL machine-check state, and generic PCI enumeration.

**Risks:** These paths intentionally handle absent devices and bad PCI cycles with expected machine checks. Barrier ordering, readbacks that force posted writes, DMA window masks, and firmware restoration are all high-risk. Wrong hose resources or SG TLB invalidation can corrupt DMA or make PCI devices disappear.

**Test signals:** Boot a T2 kernel or emulator target, enumerate PCI, exercise config reads/writes to present and absent devices, run DMA through ISA and PCI windows, test ioremap/legacy I/O, and inject or observe machine checks during config probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_t2.c -->
