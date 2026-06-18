# sources/distributed-fs/ceph-client/drivers/pps/generators/sysfs.c

Purpose: sysfs attributes for PPS generator devices.

Important APIs/functions: `system_show()`, `time_show()`, `enable_store()`, `pps_gen_attrs[]`, `pps_gen_group`, and exported `pps_gen_groups`.

Control flow: class registration in `pps_gen.c` attaches `pps_gen_groups` to each generator device. `system` returns whether the generator uses the system clock, `time` calls the driver `get_time()` callback and prints seconds/nanoseconds, and write-only `enable` parses a boolean, calls the driver `enable()` callback, then updates `pps_gen->enabled`.

State/dependencies: uses device drvdata set by generator core and callback pointers supplied by each generator driver.

Risks: no locking around `enabled`; sysfs and ioctl share enable behavior and can race; missing callbacks would crash, so generator registration must provide them; `time` returns driver errors directly.

Test signals: read `system` and `time`, write valid/invalid booleans to `enable`, concurrent ioctl/sysfs enables, callback error propagation, and device removal while sysfs files are open.
