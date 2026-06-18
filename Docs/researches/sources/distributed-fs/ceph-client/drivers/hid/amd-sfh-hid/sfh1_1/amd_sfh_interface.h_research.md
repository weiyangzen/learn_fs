# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/sfh1_1/amd_sfh_interface.h

## Purpose

`sfh1_1/amd_sfh_interface.h` defines SFH 1.1 command, firmware, sensor-list, sensor-property, and sensor-data memory layouts.

## Important APIs, Types, and Functions

Constants define default sensor data memory size, static memory size, and offsets. `enum sensor_index` names SFH 1.1 sensor IDs. `struct sfh_cmd_base` and `struct sfh_cmd_response` define register command/response bitfields. `struct sfh_base_info` models the firmware base block with platform, firmware, sensor list, and per-sensor properties. Data structs model common sensor metadata, accel/gyro/mag/ALS payloads, HPD status, and SRA operating mode. Prototypes expose interface init/deinit, descriptor-op installation, and float conversion.

## Control Flow

Implementation files use these layouts to parse the mapped firmware memory, generate HID reports, and export AMD PMF information.

## State and Persistence Behavior

The header defines memory-mapped state owned by firmware. Driver state is derived by copying or reading these structures from `mp2->vsbase`.

## Dependencies and Integration Points

It includes `amd_sfh_common.h` and is shared by SFH 1.1 init, interface, and descriptor files. Its layouts must match firmware and AMD PMF expectations.

## Risks and Test Signals

Risks include bitfield layout drift, duplicate `hpd_status` naming relative to the legacy header, and offset/size assumptions for the 128 KiB virtual sensor memory. Test signals include firmware version/sensor-list parsing, ALS/SRA/HPD exported data, and descriptor reports reading correct offsets.
