# sources/distributed-fs/ceph-client/drivers/macintosh/macio_sysfs.c

Purpose: supplies default sysfs attribute groups for MacIO bus devices. The attributes expose OF identity needed by userspace matching, diagnostics, and modalias-based module loading.

Important APIs and functions: `compatible_show()` emits all NUL-separated strings from the OF `compatible` property as newline-separated text. `modalias_show()` calls `of_device_modalias()`. `devspec_show()` prints the OF full path with `%pOF`. `name_show()` prints `%pOFn`; `type_show()` prints `of_node_get_device_type()`. `macio_dev_groups` exports the attribute group consumed by `macio_bus_type`.

Control flow: the device core attaches `macio_dev_groups` to MacIO devices. Reads translate the `struct device` back to the OF/platform device and format current OF properties into the supplied sysfs buffer.

State and persistence: no mutable state. Output reflects device-tree properties attached to each MacIO device.

Dependencies and integration: depends on `asm/macio.h`, OF helpers, `DEVICE_ATTR_RO`, and `macio_asic.c`'s `extern const struct attribute_group *macio_dev_groups[]`.

Risks: `compatible_show()` updates `buf` by cumulative `length`, which can over-advance the pointer if multiple compatible strings exist; this path should be reviewed before modification. The functions assume `dev->of_node` is valid for all MacIO devices.

Test signals: sysfs files `name`, `type`, `compatible`, `modalias`, and `devspec` exist for MacIO devices; modalias strings trigger expected module autoload; multi-string compatible properties render correctly and within `PAGE_SIZE`.
