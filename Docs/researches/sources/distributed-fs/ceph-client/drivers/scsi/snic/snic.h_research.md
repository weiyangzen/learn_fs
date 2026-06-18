# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic.h

Purpose: this is the central SNIC driver header. It defines driver identity, limits, command flag bits, state enums, debug macros, interrupt indexes, firmware info, per-adapter state, global state, and cross-file function prototypes.

Important APIs, types, and functions: the most important types are `struct snic`, `struct snic_global`, `struct snic_fw_info`, `struct snic_work`, and MSI-X entry/state enums. Macros such as `CMD_SP`, `CMD_STATE`, `CMD_FLAGS`, `CMD_ABTS_STATUS`, and `CMD_LR_STATUS` access per-command private state allocated through `scsi_host_template.cmd_size`. Tag high bits `SNIC_TAG_ABORT`, `SNIC_TAG_DEV_RST`, and `SNIC_TAG_IOCTL_DEV_RST` multiplex task-management completions. Logging, soft-assert, and trace macros are also defined here.

Control flow: all SNIC implementation files include this header to share the adapter state. Probe initializes `struct snic`, resources fill its `vdev`, WQ/CQ/INTR arrays, discovery fills `disc`, SCSI queueing uses request pools and hashed locks, and ISR/completion handlers dispatch through prototypes declared here.

State and persistence: runtime state includes adapter online/offline/reset state, firmware capabilities, discovery target list, vNIC BAR/resources, PCI device, interrupts, mempools, special untagged request list, per-command locks, work items, and debugfs handles. There is no disk persistence.

Dependencies and integration: this header ties the SCSI mid-layer, PCI/vNIC resource layer, discovery layer, stats, trace, and firmware-interface headers together. It is therefore a high-coupling point for the SNIC module.

Risks: command state is spread across private SCSI command memory and `snic_req_info`, so locking discipline around `CMD_SP` is critical. Many `SNIC_BUG_ON` checks become `WARN_ON_ONCE` in non-debug builds, allowing execution to continue after invariant violations. Constants assume one WQ and one firmware CQ lane. Debug macros can emit verbose logs in hot paths.

Test signals: build variants should cover debugfs enabled/disabled, queue depth parameters, and all SCSI EH callbacks. Lockdep and KCSAN are valuable around command state flags, `snic_lock`, host lock, and hashed request locks.
