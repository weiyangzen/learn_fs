<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_config.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_config.c

**Purpose:** `sclp_config.c` handles SCLP Configuration Management Data events and exposes an "Open for Business" firmware sysfs write path.

**Important APIs and functions:** The receiver `sclp_conf_receiver_fn()` decodes `struct conf_mgm_data` qualifiers for CPU changes and CPU capability changes. Work items `sclp_cpu_change_work` and `sclp_cpu_capability_work` call `smp_rescan_cpus(false)` or update CPU MHz and emit per-CPU `KOBJ_CHANGE`. `sclp_ofb_send_req()` builds an OFB event buffer and sends it synchronously. The sysfs binary attribute is `/sys/firmware/ofb/event_data`.

**Control flow, state, and persistence:** Init registers the event receiver for send and receive masks, then creates the firmware kset and binary file. Inbound events are handled quickly by scheduling work. Outbound OFB writes are capped at 64 bytes, wrapped in a DMA page SCCB, and serialized by a static mutex.

**Dependencies and integration:** It depends on SCLP event masks, CPU hotplug locks, sysfs/ksets, workqueues, and the SMP CPU rescan path.

**Risks and test signals:** Risks include missing receiver availability for OFB, overlength event data, unhandled event qualifiers, and hotplug work racing with other CPU topology updates. Test signals include receiving CPU-change and capability-change events, sysfs OFB writes with boundary lengths, unsupported send mask warnings, and CPU device uevents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_config.c -->
