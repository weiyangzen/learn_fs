# sources/distributed-fs/ceph-client/drivers/dio/dio-sysfs.c

Purpose: publishes read-only sysfs attributes for each enumerated DIO device.

Important APIs/types/functions: defines device attributes `id`, `ipl`, `secid`, `name`, and `resource`, and exports the local helper `dio_create_sysfs_dev_files()` to create them for a `struct dio_dev`.

Control flow: each show function converts the generic device to `struct dio_dev` and formats one field. `resource` prints start, end, and flags via DIO resource helpers. `dio_create_sysfs_dev_files()` creates attributes sequentially and stops on the first error.

State and persistence behavior: no independent state. Sysfs files reflect fields stored in the `struct dio_dev` populated by bus scan.

Dependencies and integration points: depends on Linux device attributes and DIO helper macros. Called from `dio_init()` after `device_register()` succeeds.

Risks and test signals: uses `sprintf()` instead of `sysfs_emit()`, though fixed-size simple fields make overflow unlikely. There is no rollback for earlier files if a later `device_create_file()` fails. Test signals are presence and content of `/sys/bus/dio/devices/*/{id,ipl,secid,name,resource}` after enumeration.
