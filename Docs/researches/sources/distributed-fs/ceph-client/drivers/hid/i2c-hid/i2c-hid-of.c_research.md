<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-of.c -->
# sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-of.c

## Purpose
`i2c-hid-of.c` is the generic firmware-property/Device Tree I2C-HID wrapper. It handles common supplies, reset GPIO, descriptor-address property parsing, timing properties, and simple touchscreen axis inversion quirks before calling the common core.

## Important APIs, Types, and Functions
`struct i2c_hid_of` stores embedded `i2chid_ops`, the I2C client, optional reset GPIO, two bulk supplies (`vdd`, `vddl`), and post-power/reset delays. `i2c_hid_of_power_up` and `i2c_hid_of_power_down` are passed to the core. `i2c_hid_of_probe` parses `hid-descr-addr`, optional timing properties, reset GPIO, supplies, and inversion properties.

## Control Flow
Probe requires `hid-descr-addr` and rejects values that do not fit in 16 bits. It reads optional `post-power-on-delay-ms` and kernel-internal `post-reset-deassert-delay-ms`, requests reset asserted, obtains `vdd`/`vddl`, maps `touchscreen-inverted-x/y` to HID quirk bits, then calls `i2c_hid_core_probe`. Power-up enables both regulators, waits post-power delay, deasserts reset, and waits post-reset delay. Power-down asserts reset and disables both regulators.

## State and Persistence Behavior
The wrapper is devm-managed. Persistent hardware state is limited to rail enables and reset GPIO. The HID protocol, buffers, and PM behavior are owned by the common core. The timing properties are copied once at probe and reused for every power-up.

## Dependencies and Integration Points
It depends on device properties usable from OF or platform-created property sets, regulator bulk APIs, GPIO consumer APIs, HID quirk definitions, and `i2c_hid_core_pm/remove/shutdown`. It matches OF compatible `hid-over-i2c` and I2C IDs `hid`/`hid-over-i2c`.

## Risks and Edge Cases
Missing `hid-descr-addr` prevents binding. The `post-reset-deassert-delay-ms` property is explicitly kernel-internal and must not be treated as a generic DT binding without documentation. Boards that need vendor-specific rail ordering, optional rails, or reset behavior should use a vendor wrapper instead. Bulk regulator failure is returned cleanly, but incorrect supply names cause probe failure.

## Test Signals
Validate descriptor reads from the configured address, regulator and reset ordering, axis inversion quirk behavior, suspend/resume, and compatibility with ACPI/platform property injection paths that use the generic wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-of.c -->
