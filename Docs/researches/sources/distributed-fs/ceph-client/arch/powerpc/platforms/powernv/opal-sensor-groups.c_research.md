## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-sensor-groups.c

### Purpose
`opal-sensor-groups.c` exposes OPAL sensor group operations, currently group clearing through sysfs and group enable/disable through an exported kernel API.

### Important APIs, Types, And Functions
Key types are `struct sg_attr`, `struct sensor_group`, and `sg_ops_info`. Important functions are exported `sensor_group_enable()`, `sg_store()`, `add_attr_group()`, `get_nr_attrs()`, and `opal_sensor_groups_init()`.

### Control Flow
Initialization finds `ibm,opal-sensor-group`, creates `/sys/firmware/opal/sensor_groups`, and for each child inspects its `ops` array. Supported operations become attributes, currently `clear` for `OPAL_SENSOR_GROUP_CLEAR`. Writes accept only value `1`, allocate an async token, take `sg_mutex`, call `opal_sensor_group_clear()`, wait if needed, and return `count` on success. The exported enable API calls `opal_sensor_group_enable()` with async completion handling.

### State, Persistence, And Dependencies
State is the sensor group array, sysfs kobject, group names, operation handles, and mutex. Sensor group state persists in firmware and affects sensor collection. Dependencies include OPAL async APIs, `opal_error_code()`, DT group IDs/chip IDs/ops arrays, and sysfs.

### Integration Points
`opal_init()` creates the sysfs controls. Other kernel drivers may call `sensor_group_enable()` to control sensor groups before reads.

### Risks
The `ops` property length is passed as bytes but iterated as if it were an element count in `get_nr_attrs()` and `add_attr_group()`, which is a potential over-iteration risk unless firmware/properties are constrained elsewhere. Group names are fixed 20-byte buffers assembled with `sprintf()`. Only clear is exposed despite extensible operation metadata.

### Test Signals
Test supported and unsupported ops arrays, ops length handling, group IDs and chip IDs, clear writes with values other than 1, async/immediate completion, enable/disable API, sysfs cleanup after failures, and long node names for fixed-size group names.
