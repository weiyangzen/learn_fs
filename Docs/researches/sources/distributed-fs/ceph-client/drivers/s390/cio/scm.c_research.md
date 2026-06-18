# sources/distributed-fs/ceph-client/drivers/s390/cio/scm.c

Purpose: discovers, represents, updates, and dispatches events for s390 storage class memory devices.

Important APIs/types/functions: exports `scm_driver_register()`, `scm_driver_unregister()`, and `scm_irq_handler()`. Defines the `scm` bus type, sysfs attributes for SCM metadata, `scm_update_information()`, `scm_process_availability_information()`, and helpers for setup/update/find/add.

Control flow: subsystem init registers the SCM bus and root device, then queries CHSC SCM information. `scm_update_information()` pages through CHSC SALE entries using a resume token, updating existing devices by storage address or registering new `struct scm_device`s. Attribute reads lock the device and expose current fields. EADM AOB completion calls `scm_irq_handler()`, which unwraps the request header and calls the bound SCM driver completion handler.

State and persistence behavior: devices persist in the Linux device model until removal/reboot. `struct scm_device` stores address, size, max block count, and attributes from SALE entries. Updates modify rank/oper_state and issue driver notify plus userspace `KOBJ_CHANGE` when changed.

Dependencies and integration points: depends on CHSC SCM info, EADM AOB request layout, Linux bus/device/driver model, sysfs, and SCM block/storage drivers that bind to the `scm` bus.

Risks and test signals: CHSC length arithmetic and paged resume-token iteration must match firmware. Update only treats rank and operational state as change signals. Tests should cover empty/multiple CHSC pages, duplicate address update, new device registration failure cleanup, sysfs reads under lock, SCM_AVAIL notifications, SCM_CHANGE notifications, and AOB completion error propagation.
