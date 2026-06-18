# sources/distributed-fs/ceph-client/drivers/scsi/snic/Makefile

Purpose: this Makefile defines the object composition for the Cisco SNIC SCSI driver.

Important APIs, types, and functions: it builds `snic.o` when `CONFIG_SCSI_SNIC` is enabled. The base object list includes sysfs attributes, main PCI/SCSI lifecycle, vNIC resource setup, interrupt handling, control/version exchange, request allocation, SCSI command/error handling, discovery, completion queue support, interrupt control, devcmd support, and work queue support. With `CONFIG_SCSI_SNIC_DEBUG_FS`, it also includes debugfs and trace files.

Control flow: Kbuild combines the listed `snic-y` objects into one module or built-in object. Conditional `snic-$(CONFIG_SCSI_SNIC_DEBUG_FS)` keeps trace/debugfs code out when the option is disabled while preserving stubs/macros in headers.

State and persistence: no runtime state is defined here, but build-time selection determines whether debugfs state and trace buffers exist in `struct snic_global` and per-host structures.

Dependencies and integration: this Makefile assumes neighboring vNIC support files such as `vnic_wq.c`, headers, and resource definitions are in the same directory and compiled as part of the SNIC driver.

Risks: object ordering matters only for link completeness, but omitting a core object would surface as unresolved symbols. Debugfs-dependent declarations must remain protected by `CONFIG_SCSI_SNIC_DEBUG_FS` to avoid link failures in non-debug builds.

Test signals: build with `CONFIG_SCSI_SNIC=m/y` and with debugfs enabled and disabled. Module load should expose the same PCI ID support in both builds, with only debugfs files differing.
