# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/amd_sfh_pcie.h

## Purpose

`amd_sfh_pcie.h` defines MP2 PCI register offsets, command/response bit layouts, sensor IDs, memory-type constants, HPD status layout, and public PCI/client function prototypes.

## Important APIs, Types, and Functions

Constants include `AMD_C2P_MSG0..2`, `AMD_P2C_MSG3`, `V2_STATUS`, `HPD_IDX`, `ACS_IDX`, and discovery-status masks. `union sfh_cmd_base`, `union cmd_response`, and `union sfh_cmd_param` encode command register payloads for legacy and v2 firmware. `struct sfh_cmd_reg` groups command fields and physical address. `enum sensor_idx` names accelerometer, gyro, magnetometer, operating mode, and ALS IDs. Prototypes expose `amd_mp2_get_sensor_num()`, `amd_sfh_hid_client_init()`, `amd_sfh_hid_client_deinit()`, and `amd_sfh_set_desc_ops()`.

## Control Flow

The header is consumed by PCI command writers and descriptor code. Command fields written by `amd_sfh_pcie.c` are later interpreted by firmware and response registers polled by callback functions.

## State and Persistence Behavior

The header defines wire-level state layouts rather than storing state. Bitfield definitions must remain consistent with firmware ABI.

## Dependencies and Integration Points

It includes `amd_sfh_common.h` and is included by client, PCI, and descriptor code. Its `HPD_IDX`/`ACS_IDX` constants are shared with descriptor generation and sensor discovery.

## Risks and Test Signals

Bitfield layout mistakes directly break firmware commands. Test signals include command register traces for start/stop, response parsing on v2 devices, ALS C2P-register input, HPD report values, and compile checks for duplicate `hpd_status` definitions across SFH generations.
