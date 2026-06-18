# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_module.c

Purpose: owns KFD module-level initialization and shutdown sequencing and exposes `kgd2kfd_init`/`kgd2kfd_exit` for amdgpu-to-KFD integration.

Important APIs/types/functions: `kfd_init` validates module parameters, initializes char device, topology, process workqueue, procfs, and debugfs. `kfd_exit` tears them down. `kgd2kfd_init` and `kgd2kfd_exit` are the external wrappers.

Control flow: init first validates `sched_policy` bounds and `max_num_of_queues_per_device`. It then calls `kfd_chardev_init`, `kfd_topology_init`, and `kfd_process_create_wq` with reverse-order cleanup on failure. `kfd_procfs_init` failure is intentionally ignored, while debugfs init is attempted unconditionally after procfs. Exit cleans up processes, destroys process workqueue, finalizes debugfs/procfs, shuts topology down, and exits char device.

State and persistence: module state includes char device registration, topology data, process workqueue, procfs/debugfs entries, and live KFD process state. No local static mutable state is declared here beyond module parameters defined elsewhere.

Dependencies/integration: depends on KFD core subsystems and amdgpu calling the `kgd2kfd_*` wrappers during driver init/exit.

Risks: init ordering is a contract; adding subsystems must include correct unwind. Procfs failures are non-fatal by design. Exit assumes process cleanup precedes workqueue destruction. Test signals include invalid module parameter rejection, failure injection for char/topology/workqueue init, unload with live processes, and debugfs/procfs optional availability.
