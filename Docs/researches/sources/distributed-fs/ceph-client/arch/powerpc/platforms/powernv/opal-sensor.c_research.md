## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-sensor.c

### Purpose
`opal-sensor.c` provides exported helpers for reading OPAL sensor handles and creates the OPAL sensor platform device.

### Important APIs, Types, And Functions
The exported functions are `opal_get_sensor_data()` and `opal_get_sensor_data_u64()`. Initialization is handled by `opal_sensor_init()`.

### Control Flow
Sensor reads allocate an interruptible OPAL async token, call `opal_sensor_read()` or `opal_sensor_read_u64()`, wait for async completion if returned, translate OPAL status, and convert big-endian data to CPU order. The u64 helper falls back to the u32 helper if `OPAL_SENSOR_READ_U64` is unavailable. Initialization finds `/ibm,opal/sensors` and creates an `opal-sensor` OF platform device.

### State, Persistence, And Dependencies
The file keeps no local state. Sensor data is firmware-owned and read on demand. Dependencies include OPAL async completion, OPAL token checks, OF platform-device creation, and exported symbols for other drivers.

### Integration Points
`opal_init()` invokes sensor platform setup. Hardware monitoring or platform drivers can call the exported read helpers using handles from device tree.

### Risks
In async read paths, the data output is assigned after converting the async return code; callers must check the returned error before using it. `OPAL_WRONG_STATE` is specially mapped to `-EIO`. Token acquisition can be interrupted and directly returned.

### Test Signals
Test immediate and async reads, u64 token fallback to u32, wrong-state handling, OPAL error mappings, interrupted token allocation, missing `/ibm,opal/sensors`, and consumers reading handles from DT.
