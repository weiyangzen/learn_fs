# sources/distributed-fs/ceph-client/arch/sparc/kernel/psycho_common.c

Purpose: provides common support for PSYCHO-family SPARC PCI controllers: streaming-buffer diagnostics, IOMMU error reporting, PCI error interrupt handling, IOMMU initialization, and PBM common initialization.

Important APIs/functions: exported/common functions are `psycho_check_iommu_error()`, `psycho_pcierr_intr()`, `psycho_iommu_init()`, and `psycho_pbm_init_common()`. Internal helpers include `psycho_check_stc_error()`, `psycho_record_iommu_tags_and_data()`, `psycho_dump_iommu_tags_and_data()`, `psycho_pcierr_intr_other()`, and `psycho_iommu_flush()`.

Control flow: PCI error IRQ handling reads AFSR/AFAR, clears primary error bits, logs primary/secondary PCI error types, scans PCI buses for abort/parity sources, and calls IOMMU/STC diagnostics for target aborts. IOMMU diagnostics lock the IOMMU, clear translation error state, snapshot and clear tag/data entries, dump entries with error bits, and inspect streaming-buffer diagnostic tags/lines. IOMMU init enables diagnostic mode, clears old tags/data, allocates and installs the IOMMU page table, sets TSB size, and enables translation.

State and persistence: modifies controller registers, IOMMU fields (`iommu_control`, `iommu_tsbbase`, `iommu_flush`, `iommu_tags`, `write_complete_reg`, page table), and PBM metadata. Static diagnostic buffers are protected by `stc_buf_lock`. All state is hardware/runtime only.

Dependencies and integration points: depends on `pci_pbm_info`, `iommu`/`strbuf` structures, UPA register accessors, PCI config helpers, `iommu_table_init()`, PCI bus error scan helpers, NUMA metadata, and PSYCHO-derived controller drivers that call the common routines.

Risks: diagnostic-mode streaming-buffer probing is explicitly dangerous because dirty STC data can be invalidated if tags are cleared incorrectly. Error handling runs after severe bus faults, so concurrent DVMA may already be corrupting state. TSB size validation only accepts supported sizes. Register bit definitions must match controller manuals.

Test signals: PSYCHO PCI probe, IOMMU table setup for 64K/128K TSBs, DMA through IOMMU, injected/observed PCI parity/abort/SERR conditions, IOMMU translation errors, streaming-buffer error logs, and PBM metadata/resource reporting.
