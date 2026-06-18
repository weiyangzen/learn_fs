
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ioat/registers.h -->
# sources/distributed-fs/ceph-client/drivers/dma/ioat/registers.h

Purpose: defines IOAT PCI configuration offsets, global MMIO offsets, per-channel MMIO offsets, capability bits, status masks, error masks, DCA register offsets, version-dependent register selectors, descriptor prefetch controls, and latency-tolerance registers.

Important APIs and control flow: key macros include global registers such as `IOAT_CHANCNT_OFFSET`, `IOAT_XFERCAP_OFFSET`, `IOAT_INTRCTRL_OFFSET`, `IOAT_ATTNSTATUS_OFFSET`, `IOAT_VER_OFFSET`, `IOAT_DMA_CAP_OFFSET`, and `IOAT_PREFETCH_LIMIT_OFFSET`; channel registers such as `IOAT_CHANCTRL_OFFSET`, `IOAT_CHANSTS_OFFSET`, `IOAT_CHAN_DMACOUNT_OFFSET`, `IOAT_CHANCMD_OFFSET(ver)`, `IOAT_CHANCMP_OFFSET_*`, `IOAT_CHANERR_OFFSET`, and DRS/LTR registers; and capability bits for DCA, XOR, PQ, DWBES, RAID16SS, and DPS. `IOAT_CHANCTRL_RUN` packages the interrupt/error bits normally written by cleanup/resource allocation.

State and persistence behavior: the file has no runtime state, but it defines how persistent hardware register state is read and mutated by the IOAT driver. Version-dependent macros select v1 versus v2 command/chain-address offsets, while newer DPS and LTR macros enable performance and power-management features.

Dependencies and integration points: included by IOAT runtime, init, prep, and sysfs files. It is the binding layer between symbolic driver logic and IOAT silicon, PCI config access, DCA support, interrupt routing, reset, channel error clearing, and sysfs interrupt coalescing.

Risks and test signals: risks include incorrect offsets causing silent MMIO corruption, masks that do not match newer device revisions, typo-prone capability semantics such as `IOAT_INTRDELAY_COALESE_SUPPORT`, DCA register assumptions on unsupported systems, and version macros unused or bypassed by some code paths. Test signals include channel count/xfercap reads matching hardware, interrupts acknowledged correctly, error bits logged/cleared accurately, DRS/LTR writes accepted on v3.4+, reset command polling clearing, and capability-dependent feature exposure matching `IOAT_DMA_CAP_OFFSET`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ioat/registers.h -->
