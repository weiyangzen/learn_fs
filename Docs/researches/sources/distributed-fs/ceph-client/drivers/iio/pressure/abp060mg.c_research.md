<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/abp060mg.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/abp060mg.c

Purpose: I2C IIO pressure driver for Honeywell ABP pressure sensors. It supports many gage and differential part variants by mapping I2C IDs to pressure ranges and exposing a single pressure channel.

Important APIs, types, and functions: `enum abp_variant` and `abp_config[]` define supported part ranges in pascals. `struct abp_state` stores the I2C client, mutex, measurement-request length, scale, and offset. `abp060mg_get_measurement()` sends the measurement request, waits 40 ms, reads two 16-bit words, validates status/range bits, and returns raw pressure counts. `abp060mg_read_raw()` serves raw, offset, and scale. `abp060mg_init_device()` derives IIO scale and offset from the selected range.

Control flow: probe allocates the IIO device, detects whether SMBus quick is unavailable and therefore a dummy-byte request is needed, initializes model-specific conversion parameters, and registers the direct-mode device. Reads are serialized by a mutex.

State and persistence: only in-memory model parameters and mutex state are kept. No hardware configuration registers or persistent storage are used. The sensor is triggered per read and returns fresh counts.

Dependencies and integration points: depends on I2C and IIO core. It binds through the I2C ID table, not an OF table in this file. IIO ABI conversion relies on raw count plus offset and fractional scale.

Risks: `msleep_interruptible()` return is ignored, so interrupted sleeps can shorten conversion delay. `i2c_master_send()` and `recv()` positive short transfers are not checked. The psi conversion comments use approximate constants and one gage range appears to use `6985` for 1 psi rather than the usual 6895 pattern, so range table values deserve datasheet review. No device-tree compatible table limits firmware binding.

Test signals: validate each ID table entry maps to the expected min/max, test adapters with and without SMBus quick support, inject short I2C transfers and sensor status error bits, and compare raw/offset/scale conversions for gage and differential variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/abp060mg.c -->
