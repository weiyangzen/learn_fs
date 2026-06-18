# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ta_secureDisplay_if.h

## Purpose

`ta_secureDisplay_if.h` defines the shared-buffer ABI for the Secure Display trusted application. It supports querying TA responsiveness and sending display region-of-interest plus CRC data to an I2C path, including a v2 command that adds a ROI index.

## Important APIs, Types, And Functions

`enum ta_securedisplay_command` includes `QUERY_TA`, `SEND_ROI_CRC`, and `SEND_ROI_CRC_V2`. Status values describe success, generic failure, invalid parameter, null pointer, I2C write/init errors, DIO scratch read errors, and CRC read errors. `enum ta_securedisplay_phy_ID` supports four PHY IDs. Buffer-size constants define 15-byte v1 and 16-byte v2 I2C payloads. Input unions carry `phy_id` and optional `roi_idx`; output unions carry the query sentinel `0xAB` or the generated I2C buffer. `struct ta_securedisplay_cmd` is the 48-byte command layout.

## Control Flow, State, And Dependencies

The driver fills `cmd_id` and command input, invokes the Secure Display TA, and reads `status` plus output payload. The TA reads DIO scratch/CRC state and writes I2C data; the host only observes the output buffer. Persistent state is mostly external to this header: TA session state, display hardware scratch registers, and I2C target state.

## Risks And Test Signals

Risks include strict ABI size/layout expectations, invalid PHY or ROI index values, failure to distinguish v1/v2 buffer sizes, and secure display errors that only surface as TA status codes. Tests should query TA load using the `0xAB` sentinel, send ROI/CRC on each PHY, exercise v2 ROI indices, validate I2C buffer contents, and inject/read DIO, CRC, and I2C failure paths.
