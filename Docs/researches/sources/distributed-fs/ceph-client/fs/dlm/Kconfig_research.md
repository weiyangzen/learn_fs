<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/Kconfig -->
# sources/distributed-fs/ceph-client/fs/dlm/Kconfig

Purpose: declares kernel configuration options for the Distributed Lock Manager.

Important APIs/types/functions: `menuconfig DLM` is a tristate option depending on `INET`, `SYSFS`, and `CONFIGFS_FS`; `config DLM_DEBUG` is a bool depending on `DLM`.

Control flow: enabling `DLM` allows the DLM subsystem to be built for kernel or userspace lock clients. Enabling `DLM_DEBUG` adds debugfs support that creates lockspace files under the `dlm` debugfs directory.

State and persistence: no runtime state directly; these options determine which source objects and debug surfaces are compiled.

Dependencies and integration: DLM requires networking, sysfs, and configfs because cluster membership and communication configuration are provided through configfs and lock managers communicate over network transports.

Risks: disabling configfs/sysfs/INET makes DLM unavailable. Debug output can expose lockspace details and depends on debugfs availability.

Test signals: config matrix builds should verify `DLM=n`, `DLM=y/m`, and `DLM_DEBUG=y` combinations, including debugfs object inclusion only when requested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/Kconfig -->
