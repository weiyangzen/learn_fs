# sources/distributed-fs/ceph-client/drivers/s390/crypto/vfio_ap_drv.c

Purpose: module-level driver setup for VFIO AP matrix passthrough. It creates the root `vfio_ap` device, `matrix` bus/device, AP queue driver for CEX4 and newer queues, debug feature area, and mediated-device registration.

Important APIs and functions: global `matrix_dev` holds the matrix device. `features_show()` advertises `guest_matrix hotplug ap_config`. `vfio_ap_drv` binds AP queues and delegates probe/remove/resource/config callbacks to `vfio_ap_ops.c`. `vfio_ap_matrix_dev_create()` registers the root device and custom matrix bus, allocates `matrix_dev`, fills AP config via `ap_qci()` when facility 12 exists, initializes locks/lists, registers the matrix device and driver. `vfio_ap_dbf_info_init()` creates the s390 debug area. `vfio_ap_init()` orders debug, AP instruction check, matrix creation, AP driver registration, and mdev registration. `vfio_ap_exit()` reverses that order.

Control flow: module init fails early if debug setup, AP instruction availability, matrix setup, AP driver registration, or mdev registration fails. Error paths unregister only objects created earlier. AP bus callbacks flow from `ap_driver_register()` into VFIO AP operations.

State and persistence: persistent module state includes `matrix_dev`, matrix device sysfs attributes, `matrix_dev->info`, mdev list/locks, AP driver registration, and debug feature registration. No guest assignment is stored here; that state lives in mdev objects managed by `vfio_ap_ops.c`.

Dependencies and integration: depends on AP bus/device model, VFIO/mdev parent registration, s390 facility/AP QCI support, and the VFIO AP private ABI. It exposes AP queue IDs for CEX4-CEX8 queue types.

Risks: init error unwinding must avoid leaking root devices, buses, or debug areas. `ap_qci()` failure during matrix allocation jumps through shared cleanup labels, so release order is important. The global `matrix_dev` is central to every operation and must not be used after destruction.

Test signals: module load/unload, no-AP-instruction systems, `ap_qci()` failure injection, each registration failure path, sysfs `features` content, AP queue driver matching for CEX4-CEX8, and debug feature registration/unregistration.
