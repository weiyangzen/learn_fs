<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_mcpcia.c -->
## sources/distributed-fs/ceph-client/arch/alpha/kernel/core_mcpcia.c

**Purpose:** Implements MCbus-PCI adaptor support for multi-hose Rawhide-style systems: config access, hose probing, DMA window setup, TLB invalidation, and machine-check printing. This is platform hardware glue rather than Ceph client logic; it makes Linux PCI, DMA, I/O mapping, and machine-check paths work on MCPCIA Alpha systems.

**Important APIs/types/functions:** `mcpcia_pci_ops`, `mcpcia_pci_tbi`, `mcpcia_init_arch`, `mcpcia_init_hoses`, and `mcpcia_machine_check`, plus static helpers for config-address construction, controller register access, DMA-window programming, and error clearing/decoding.

**Control flow:** boot creates hose 0 early, then after IRQs probes each possible hose by intentionally allowing expected machine checks on absent hardware. Startup configures abort reporting, SG/direct windows, HBASE/HAE registers, and TBIA. Config access uses type-1 cycles for all buses and marks expected machine checks around sparse loads/stores.

**State and persistence behavior:** multiple `pci_controller` hoses, per-hose sparse/dense resources and HAE window, ISA and PCI SG arenas, 2 GiB direct map, MCPCIA CAP error state, and per-CPU machine-check flags. None of this is filesystem-persistent, but it persists for the lifetime of the booted kernel and controls all PCI/DMA behavior on the platform.

**Dependencies and integration points:** Depends on Alpha core-specific register headers, `asm/io.h`, `asm/ptrace.h`, `pci_impl.h`, `proto.h`, Linux PCI/resource/memblock APIs, IOMMU arena helpers, PAL machine-check state, and generic PCI enumeration.

**Risks:** These paths intentionally handle absent devices and bad PCI cycles with expected machine checks. Barrier ordering, readbacks that force posted writes, DMA window masks, and firmware restoration are all high-risk. Wrong hose resources or SG TLB invalidation can corrupt DMA or make PCI devices disappear.

**Test signals:** Boot a MCPCIA kernel or emulator target, enumerate PCI, exercise config reads/writes to present and absent devices, run DMA through ISA and PCI windows, test ioremap/legacy I/O, and inject or observe machine checks during config probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_mcpcia.c -->
