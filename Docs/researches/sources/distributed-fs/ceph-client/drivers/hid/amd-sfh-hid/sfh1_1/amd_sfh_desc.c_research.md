# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/sfh1_1/amd_sfh_desc.c

## Purpose

`sfh1_1/amd_sfh_desc.c` provides descriptor and report callbacks for SFH 1.1 firmware. Unlike the legacy descriptor path, it reads sensor data from an SFH firmware memory window and converts firmware float encodings to integer HID values.

## Important APIs, Types, and Functions

`amd_sfh1_1_set_desc_ops()` installs `get_report_desc()`, `get_feature_rep()`, `get_desc_size()`, and `get_input_rep()` into `amd_mp2_ops`. `amd_sfh_float_to_int()` converts IEEE-like 32-bit firmware float values with rounding. `get_input_rep()` reads `sfh_accel_data`, `sfh_gyro_data`, `sfh_mag_data`, `sfh_als_data`, and HPD status and emits packed HID reports.

## Control Flow

SFH 1.1 client init installs these ops, copies static descriptors, starts sensors, then periodic work requests input reports. For accelerometer, gyro, magnetometer, and ALS, the code computes a sensor memory address from `vsbase`, sensor index, `SENSOR_DATA_MEM_SIZE_DEFAULT`, and `OFFSET_SENSOR_DATA_DEFAULT`. HPD uses a C2P/P2C register selected by revision helper.

## State and Persistence Behavior

The file is mostly stateless. It reads persistent firmware memory and writes caller-owned report buffers. ALS color fields are conditional on firmware feature bits in `sfh_base_info`.

## Dependencies and Integration Points

It depends on `amd_sfh_interface.h` for SFH 1.1 memory layouts, shared descriptor arrays, and packed report structs. It integrates with the generic AMD SFH HID client through `amd_mp2_ops`.

## Risks and Test Signals

Risks include float conversion corner cases, stale firmware memory reads, scale divisors differing by sensor, and feature-bit handling for ALS color data. Test signals include SFH 1.1 devices exposing correct hid-sensor values, ALS color feature validation, HPD reports, and unit tests for `amd_sfh_float_to_int()` edge values.
