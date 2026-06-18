<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid.h -->
# sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid.h

## Purpose
`i2c-hid.h` is the small shared contract between the I2C-HID core, DMI quirks, and platform/vendor wrappers. It declares optional DMI descriptor/quirk hooks, the wrapper operations structure, exported core lifecycle functions, and the common PM ops.

## Important APIs, Types, and Functions
Under `CONFIG_DMI`, the header declares `i2c_hid_get_dmi_i2c_hid_desc_override`, `i2c_hid_get_dmi_hid_report_desc_override`, and `i2c_hid_get_dmi_quirks`; otherwise static inline stubs return no overrides. `struct i2chid_ops` provides optional `power_up`, `power_down`, `shutdown_tail`, and `restore_sequence` callbacks. The core exports `i2c_hid_core_probe`, `i2c_hid_core_remove`, `i2c_hid_core_shutdown`, and `i2c_hid_core_pm`.

## Control Flow
Wrapper drivers allocate their private state, fill `i2chid_ops`, obtain the HID descriptor address and initial HID quirks, then call `i2c_hid_core_probe`. The core stores the ops pointer and invokes callbacks during power-up/down, hibernation restore, and shutdown. DMI helpers are called inside descriptor/report parsing and quirk setup.

## State and Persistence Behavior
The header owns no storage. It defines callback ownership: wrapper-private structures typically embed `i2chid_ops`, and callbacks use `container_of` to recover regulator/GPIO state. The core assumes the ops object remains valid until remove/shutdown.

## Dependencies and Integration Points
The header depends on `<linux/i2c.h>` and the kernel type namespace. It is included by `i2c-hid-core.c`, `i2c-hid-dmi-quirks.c`, and the OF/vendor wrapper modules.

## Risks and Edge Cases
Because all callbacks are optional, the core must continue checking for `NULL` before invoking them. The ops lifetime is not reference-counted; wrappers must allocate it with device lifetime at least as long as the core instance. DMI helper stubs keep non-DMI builds compiling, but any code relying on overrides must tolerate absence.

## Test Signals
Build coverage with and without `CONFIG_DMI`, module builds for all wrappers, suspend/resume/shutdown callback exercise, and compile-time detection of signature drift between core and wrappers are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid.h -->
