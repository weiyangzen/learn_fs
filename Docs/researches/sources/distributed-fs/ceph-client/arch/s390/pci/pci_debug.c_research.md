<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_debug.c -->
# sources/distributed-fs/ceph-client/arch/s390/pci/pci_debug.c

Purpose: This file provides s390 zPCI debug buffers and per-device debugfs statistics for firmware measurement blocks and software IOMMU counters.

Important APIs/types/functions: It exports `pci_debug_msg_id` and `pci_debug_err_id`. Public lifecycle hooks are `zpci_debug_init`, `zpci_debug_exit`, `zpci_debug_init_device`, and `zpci_debug_exit_device`. Debugfs file operations are built around `pci_perf_show`, `pci_perf_seq_write`, and `pci_perf_seq_open`; display helpers include `pci_fmb_show` and `pci_sw_counter_show`.

Control flow: Global initialization registers two s390 debug feature buffers, installs sprintf/hex-ascii views, sets debug level, and creates `/sys/kernel/debug/pci`. Per-device initialization creates a device directory and `statistics` file. Reads lock `zdev->fmb_lock`, print FMB header/common counters, dispatch on FMB format-specific counter layout, then append software IOMMU counters under `dom_lock`. Writes parse `0` or `1` to disable or enable FMB collection.

State and persistence: Persistent state is the debug feature handles, debugfs root and per-device dentries, active FMB pointer/data in each zdev, and IOMMU counter atomics. Debugfs state is runtime-only and disappears at module/arch teardown or device exit.

Dependencies and integration points: It depends on Linux debugfs, seq_file, s390 `debug.h`, zPCI FMB enable/disable APIs, and `zpci_get_iommu_ctrs` from PCI DMA support. It integrates with diagnostic tooling and zPCI error/event logging.

Risks and test signals: Locking must prevent FMB teardown while statistics are read or toggled. Counter format interpretation must match firmware-provided FMB format bits, and missing FMB state should report disabled rather than dereferencing NULL. Tests include reading and toggling debugfs statistics, device hot-unplug while statistics are open, FMB formats 0-3, and debug feature registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_debug.c -->
