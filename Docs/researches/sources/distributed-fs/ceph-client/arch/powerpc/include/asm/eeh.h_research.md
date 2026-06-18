## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/eeh.h

Purpose: defines PowerPC Enhanced Error Handling state, platform operations, PE/device tracking, and MMIO read wrappers for PCI error isolation and recovery.

Important APIs/types/functions: `struct eeh_pe`, `struct eeh_dev`, `struct eeh_ops`, subsystem flags, PE/device state flags, traversal callbacks, `eeh_enabled()`, serialization helpers, PE tree functions, recovery/configuration APIs, `EEH_POSSIBLE_ERROR()`, `EEH_IO_ERROR_VALUE()`, and PPC64 `eeh_read*()`/string read wrappers.

Control flow: platform code registers `eeh_ops`; PCI probe creates EEH devices and PE hierarchy; MMIO reads returning all ones call `eeh_check_failure()`; events and recovery code freeze, reset, configure, restore, and resume PEs. Inline flag helpers gate EEH checks and serialize confirmation with `confirm_error_lock`.

State and persistence: global `eeh_subsystem_flags`, `eeh_ops`, freeze counters, timestamps, PE trees, per-device config snapshots, and error state persist across PCI device lifetimes and recovery cycles.

Dependencies and integration: depends on PCI, OF PCI device nodes, pseries/PowerNV platform EEH backends, IOMMU groups, debugfs, stacktrace, and UAPI EEH definitions. It integrates with PCI error handlers, hotplug, config-space access, and MMIO accessors.

Risks and test signals: false positives are possible because all-ones MMIO can be valid for some devices. PE hierarchy and config restore must be correct to avoid data loss or permanent removal. Test signals include PCI EEH injection, frozen PE recovery, hotplug remove during recovery, config-space restore, MMIO wrapper reads, and platform-specific pseries/PowerNV EEH tests.
