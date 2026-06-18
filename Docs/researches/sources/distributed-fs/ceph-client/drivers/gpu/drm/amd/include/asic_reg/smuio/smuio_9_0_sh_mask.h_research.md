<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_9_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_9_0_sh_mask.h

## Purpose
`smuio_9_0_sh_mask.h` is the SMUIO 9.0 companion bitfield header for `smuio_9_0_offset.h`. It defines `__SHIFT` and `_MASK` macros for ROM control/status, ROM software-command registers, ROM payload registers, and two SVI telemetry fields.

## Important APIs, Types, And Macros
The file exports macros only. It defines no functions, types, or storage.

Important fields include:

- `ROM_CNTL__CLOCK_GATING_EN` for ROM clock gating.
- `ROM_STATUS__ROM_BUSY` for ROM busy polling.
- `CGTT_ROM_CLK_CTRL0` fields for clock-gating timing: `ON_DELAY`, `OFF_HYSTERESIS`, `SOFT_OVERRIDE1`, and `SOFT_OVERRIDE0`.
- `ROM_INDEX`, `ROM_DATA`, and `ROM_START` full-address/data fields. Index and start are masked to 24 bits in this generation.
- `ROM_SW_CNTL` fields for software command data size, command size, and return-data enable.
- `ROM_SW_STATUS__ROM_SW_DONE` for command-completion polling.
- `ROM_SW_COMMAND` fields for an 8-bit instruction and upper address bits.
- `ROM_SW_DATA_1` through `ROM_SW_DATA_64` full-width payload fields.
- `SMUSVI0_PLANE0_CURRENTVID__CURRENT_SVI0_PLANE0_VID` at bits `31:24`.
- `SMUSVI0_TEL_PLANE0__SVI0_PLANE0_VDDCOR` at bits `24:16` via mask `0x01FF0000L`.

## Control Flow
There is no executable control flow. Consumers use the macros to implement ROM and telemetry control sequences. A ROM software-command path would set data and command size in `ROM_SW_CNTL`, place an instruction/address in `ROM_SW_COMMAND`, fill or read `ROM_SW_DATA_n`, and poll `ROM_SW_STATUS.ROM_SW_DONE`. A simple indexed ROM read path would program `ROM_INDEX` or `ROM_START`, read `ROM_DATA`, and poll `ROM_STATUS.ROM_BUSY` as needed.

## State And Persistence Behavior
The header itself is stateless. It describes live hardware register fields:

- Clock-gating fields affect ROM block power/clock behavior until changed.
- ROM busy/done bits are hardware status indicators.
- ROM command, address, and data fields are transient payload staging state for firmware/ROM operations.
- SVI fields expose current voltage ID and telemetry data from the SVI plane.

## Dependencies
The macros depend on the offsets from `smuio_9_0_offset.h` and the AMDGPU bitfield-helper naming convention. Any consumer using `REG_GET_FIELD` or `REG_SET_FIELD` requires both `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` to be present and correct.

## Integration Points
This header integrates with AMDGPU support for SMUIO 9.0 ASICs, especially ROM/VBIOS access, SMU firmware loading or command paths, and power telemetry paths that read SVI voltage information. It is part of the generated AMD ASIC register include tree under `include/asic_reg`.

## Risks
- Incorrect `ROM_SW_CNTL` field widths would corrupt software-command packet framing.
- Incorrect `ROM_SW_STATUS` or `ROM_STATUS` masks can create premature completion, stuck polling, or timeout behavior.
- Full-width `ROM_SW_DATA_n` masks do not protect against protocol-level invalid payloads.
- The SVI fields are narrow high-bit slices; using the raw register without mask/shift would report incorrect voltage values.
- SMUIO 9.0 ROM field widths differ from newer SMUIO generations, so cross-generation assumptions are risky.

## Test Signals
- Compile checks catch missing macro names.
- Hardware ROM tests should validate busy/done polling and data returned from indexed and software-command reads.
- Firmware-loading or VBIOS-read smoke tests exercise the ROM command/data fields indirectly.
- Power telemetry tests should confirm decoded SVI current VID and VDDCOR values against SMU-reported values.
- Register-generation validation should compare masks against the official SMUIO 9.0 address map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_9_0_sh_mask.h -->
