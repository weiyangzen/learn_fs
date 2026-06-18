<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_polaris.c -->
## sources/distributed-fs/ceph-client/arch/alpha/kernel/core_polaris.c

**Purpose:** Implements POLARIS core logic support for straightforward dense PCI config access, single-hose setup, fixed direct-map DMA, and minimal machine-check clearing. This is platform hardware glue rather than Ceph client logic; it makes Linux PCI, DMA, I/O mapping, and machine-check paths work on POLARIS Alpha systems.

**Important APIs/types/functions:** `polaris_pci_ops`, `polaris_init_arch`, and `polaris_machine_check`, plus static helpers for config-address construction, controller register access, DMA-window programming, and error clearing/decoding.

**Control flow:** config-space addresses include bus/devfn/register plus the dense config base; the chip chooses type-0 versus type-1 by bus number. Initialization trusts firmware setup, creates the hose, and sets direct-map DMA.

**State and persistence behavior:** single hose with dense memory/I/O bases, fixed 2 GiB direct-map window, no SG arenas, and POLARIS status register bits. None of this is filesystem-persistent, but it persists for the lifetime of the booted kernel and controls all PCI/DMA behavior on the platform.

**Dependencies and integration points:** Depends on Alpha core-specific register headers, `asm/io.h`, `asm/ptrace.h`, `pci_impl.h`, `proto.h`, Linux PCI/resource/memblock APIs, IOMMU arena helpers, PAL machine-check state, and generic PCI enumeration.

**Risks:** These paths intentionally handle absent devices and bad PCI cycles with expected machine checks. Barrier ordering, readbacks that force posted writes, DMA window masks, and firmware restoration are all high-risk. Wrong hose resources or SG TLB invalidation can corrupt DMA or make PCI devices disappear.

**Test signals:** Boot a POLARIS kernel or emulator target, enumerate PCI, exercise config reads/writes to present and absent devices, run DMA through ISA and PCI windows, test ioremap/legacy I/O, and inject or observe machine checks during config probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_polaris.c -->
