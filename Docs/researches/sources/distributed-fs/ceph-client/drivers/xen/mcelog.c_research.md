# sources/distributed-fs/ceph-client/drivers/xen/mcelog.c

Purpose: provides dom0 machine-check logging by receiving Xen MCA VIRQ notifications, fetching Xen machine-check records, converting them to Linux `/dev/mcelog` records, and exposing them through a misc device.

Important APIs/functions: file operations are `xen_mce_chrdev_open`, `xen_mce_chrdev_release`, `xen_mce_chrdev_read`, `xen_mce_chrdev_poll`, and `xen_mce_chrdev_ioctl`. MCA handling uses `bind_virq_for_mce`, `xen_mce_interrupt`, `xen_mce_work_fn`, `mc_queue_handle`, `convert_log`, and `xen_mce_log`.

Control flow: init only runs in the initial domain, registers `/dev/mcelog`, fetches physical CPU info from `HYPERVISOR_mca`, and binds `VIRQ_MCA`. The interrupt schedules work. Work serializes on `mcelog_lock`, drains urgent then nonurgent Xen MCA queues, converts global and bank records into `struct xen_mce`, acknowledges each fetched record, stores records in `xen_mcelog`, and wakes pollers. Reads require offset zero and enough buffer space for the full log length, copy entries to userspace, then clear the buffer.

State and persistence: global CPU physical info, one scratch `mc_info`, `xen_mcelog` ring-like fixed array, overflow flags, open/exclusive counters, and wait queue persist after init. Records are cleared on read.

Dependencies and integration: depends on Xen MCA hypercalls, VIRQ binding from the event layer, misc mcelog ABI constants, CAP_SYS_ADMIN ioctls, and x86 mcinfo layouts.

Risks: only dom0 logs MCA records; fixed log length drops new records on overflow; conversion requires APIC ID matching against fetched CPU info; open exclusivity is advisory via `O_EXCL`; reads are all-or-nothing and clear records.

Test signals: bind and trigger VIRQ_MCA in dom0, fetch urgent/nonurgent queues, validate `/dev/mcelog` poll/read/ioctls, overflow behavior, exclusive open behavior, CPU info fetch failures, and conversion of multiple bank records.
