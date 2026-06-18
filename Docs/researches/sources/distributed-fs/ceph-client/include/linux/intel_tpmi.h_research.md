<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel_tpmi.h -->
# sources/distributed-fs/ceph-client/include/linux/intel_tpmi.h

Purpose: Declares Intel TPMI version/id helpers, notifications, and auxiliary-device resource accessors.

Important APIs/types/functions: Version macros extract major/minor fields; `enum intel_tpmi_id` identifies TPMI services. Constants `TPMI_CORE_INIT` and `TPMI_CORE_EXIT` label notifier events. APIs register/unregister notifiers, get platform data, resource by index/count, feature status including read/write blocks, and debugfs directory.

Control flow: TPMI core notifies clients about init/exit; auxiliary drivers query resources and feature status before accessing hardware.

State/persistence: Platform data/resources are attached to auxiliary devices; notifier registrations persist until removed.

Dependencies/integration: Depends on bitfield helpers, auxiliary devices, debugfs, Intel VSEC/OOBMSM platform data.

Risks: Feature read/write block flags must be obeyed to avoid illegal MMIO access.

Test signals: Notifier order, resource count/index bounds, version extraction, feature blocked status, and debugfs directory presence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel_tpmi.h -->
