# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/hid_descriptor/amd_sfh_hid_desc.c

## Purpose

`amd_sfh_hid_desc.c` supplies legacy MP2 descriptor operations. It returns HID report descriptors, descriptor sizes, feature reports, and input reports for accelerometer, gyroscope, magnetometer, ambient light/color sensors, and HPD.

## Important APIs, Types, and Functions

`amd_sfh_set_desc_ops()` installs callbacks into `amd_mp2_ops`: `get_report_descriptor()`, `get_feature_report()`, `get_input_report()`, and `get_descr_sz()`. Helpers `get_common_features()` and `get_common_inputs()` populate shared HID sensor fields. `get_input_report()` converts raw DMA or register values into packed report structures from `amd_sfh_hid_desc.h`.

## Control Flow

Client initialization calls `amd_sfh_set_desc_ops()` before requesting descriptor sizes and report descriptors. HID requests and periodic polling later call the installed report callbacks. Input reports read from `in_data->sensor_virt_addr[current_index]` for most sensors; ALS on v2 can read illuminance from `AMD_C2P_MSG(5)`, and HPD reads from `AMD_C2P_MSG(4)`.

## State and Persistence Behavior

The file is stateless aside from writing into caller-provided buffers. Generated reports are stored by the client in per-sensor feature/input buffers. Raw sensor values persist in coherent DMA buffers owned by the client.

## Dependencies and Integration Points

It depends on HID descriptor byte arrays from `amd_sfh_hid_report_desc.h`, packed report structures from `amd_sfh_hid_desc.h`, sensor IDs from `amd_sfh_pcie.h`, and MP2 status/register data from `amd_sfh_common.h`.

## Risks and Test Signals

Risks include size mismatches between descriptors and packed report structs, unit conversion truncation by `AMD_SFH_FW_MULTIPLIER`, and special cases for ACS/HPD/ALS registers. Test signals include `hid_parse_report()` success for every descriptor, expected hid-sensor attributes in userspace, ALS/ACS color fields, and HPD presence changes.
