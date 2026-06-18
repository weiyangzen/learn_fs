# sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_aux.c

Purpose: provides zfcp module initialization/exit and core adapter/port allocation helpers, low-memory buffer pools, status-read refill scheduling, initial device configuration, and service-level reporting.

Important APIs and functions: module entry/exit are `zfcp_module_init()` and `zfcp_module_exit()`. Initial device parsing flows through `zfcp_init_device_setup()` and `zfcp_init_device_configure()`. Runtime helpers include `zfcp_get_port_by_wwpn()`, `zfcp_status_read_refill()`, `zfcp_adapter_enqueue()`, `zfcp_adapter_unregister()`, `zfcp_adapter_release()`, and `zfcp_port_enqueue()`.

Control flow: module init creates aligned slab caches, attaches the FC transport, reserves per-device transport data, registers the ccw driver, and optionally configures a boot-specified `device=busid,wwpn,lun`. Adapter enqueue takes a ccw device reference, allocates and initializes all adapter subsystems, creates mempools/workqueues/debugfs/sysfs/Fibre Channel GS state, starts ERP support, and stores adapter drvdata. Failure unwinds broadly through cancellation and subsystem teardown. Port enqueue rejects duplicates under adapter locking, registers a child device, links it into the adapter port list, and marks it running.

State and persistence: allocates the live `struct zfcp_adapter` graph, mempools, request list, debug feature state, FC stats, work items, ERP queues, and `struct zfcp_port` children. Module parameters and runtime objects persist until unregister/remove or module exit.

Dependencies and integration: integrates with ccw driver registration, SCSI FC transport, zfcp FSF/QDIO/ERP/FC/SCSI/sysfs/diag/debug subsystems, kernel device model, mempools, workqueues, and service-level reporting.

Risks: adapter setup has many partial-initialization points; incomplete unwind can leak work, device references, pools, or debug registrations. `zfcp_allocate_low_mem_buffers()` returns immediately on failure and relies on later broad cleanup. Initial device parsing must reject malformed boot parameters without leaving devices online incorrectly. Port list locking and device references protect lookup/enqueue races.

Test signals: module load/unload, failure injection at each allocation/setup step, boot `device=` parsing valid/invalid inputs, adapter online allocation then remove, duplicate port enqueue rejection, status-read refill miss counter and reopen trigger, and sysfs/debug/resource cleanup after failed enqueue.
