# sources/distributed-fs/ceph-client/drivers/firmware/edd.c

Purpose: exports BIOS Enhanced Disk Drive data collected during x86 setup through `/sys/firmware/edd/int13_devXX`, making INT 13h disk parameters, MBR signatures, geometry, and EDD 3.0 path information visible to userspace.

Important APIs/types/functions: defines private `struct edd_device` and `struct edd_attribute`. Attribute show/test helpers include `edd_show_raw_data()`, `edd_show_version()`, `edd_show_extensions()`, `edd_show_info_flags()`, `edd_show_sectors()`, legacy/default geometry show functions, `edd_show_interface()`, `edd_show_host_bus()`, and presence validators such as `edd_has_edd30()`. Device lifecycle is handled by `edd_device_register()`, `edd_populate_dir()`, `edd_device_unregister()`, `edd_release()`, `edd_init()`, and `edd_exit()`.

Control flow: `late_initcall(edd_init)` exits if setup code found no EDD or MBR-signature entries. It creates the `edd` kset below `firmware_kobj`, allocates one `edd_device` per BIOS disk slot, binds it to global `edd` setup data, creates only attributes whose test callbacks pass, optionally links `pci_dev` for PCI/XPRS devices, and emits a kobject add event. Module exit drops kobject refs and unregisters the kset.

State and persistence behavior: per-device state stores the device index, optional MBR signature, pointer into the global `edd.edd_info[]` array, and kobject. The driver does not persist anything itself; it publishes boot-time BIOS data until module removal or shutdown.

Dependencies and integration points: depends on `linux/edd.h` boot-time data, sysfs/kobject APIs, firmware kobject, PCI device lookup for host-bus paths, and block/firmware userspace tooling that consumes EDD metadata.

Risks and test signals: BIOS data is legacy and often imperfect; `edd_has_edd30()` checks key, path length, and checksum before exposing host/interface fields, and raw-data size is clamped to the known structure size. There is limited rollback for partial sysfs file creation. Test signals are correct `int13_dev80+` directories, conditional absence of invalid attributes, PCI symlink creation where applicable, and clean teardown with no leaked kobjects.
