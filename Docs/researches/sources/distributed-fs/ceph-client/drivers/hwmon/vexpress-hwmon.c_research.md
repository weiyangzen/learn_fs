# sources/distributed-fs/ceph-client/drivers/hwmon/vexpress-hwmon.c

## Purpose
ARM Versatile Express platform hwmon bridge. It exposes firmware/config-bus values as voltage, current, temperature, power, or energy sysfs attributes depending on OF compatible string.

## Important APIs, Types, and Functions
`struct vexpress_hwmon_data` stores the hwmon device and vexpress config regmap. `struct vexpress_hwmon_type` binds a hwmon name to attribute groups. `vexpress_hwmon_u32_show()` reads register 0 and divides by the per-attribute scale factor. `vexpress_hwmon_u64_show()` combines registers 1:0 for energy. `vexpress_hwmon_attr_is_visible()` hides labels when the OF node lacks `label`.

## Control Flow
Probe allocates state, retrieves match data for the compatible type, initializes the vexpress config regmap, and registers a hwmon device with the selected static attribute group. Runtime sysfs reads synchronously read one or two config registers and format scaled values. Label reads return the node's `label` property.

## State and Persistence
The driver keeps no measurement cache and writes no hardware state. All values come from the platform config regmap on demand. Attribute availability is fixed at probe by compatible type and at visibility time by the optional label property.

## Dependencies and Integration Points
Depends on platform OF matching, `devm_regmap_init_vexpress_config()`, legacy hwmon attribute groups, and `linux/vexpress.h`. Compatible strings include `arm,vexpress-amp`, `arm,vexpress-temp`, `arm,vexpress-power`, `arm,vexpress-energy`, and conditionally `arm,vexpress-volt` when the regulator driver is not configured.

## Risks
`vexpress_hwmon_label_show()` assumes visibility has hidden the label attribute when the property is absent; direct misuse would pass NULL to formatting. U64 energy reads are not atomic across low/high registers and can race rollover. Scaling is encoded in attribute indices, so mistakes in static attributes directly affect units. Voltage support is conditionally compiled to avoid conflict with the regulator driver.

## Test Signals
Check each compatible's hwmon name and attributes, label visibility with and without `label`, regmap error propagation, u32 scaling for milli-units, u64 high/low composition, and build coverage with `CONFIG_REGULATOR_VEXPRESS` enabled and disabled.
