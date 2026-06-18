<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_9_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_9_0_offset.h

## Purpose
`smuio_9_0_offset.h` defines SMUIO 9.0 register offsets for the `smuio_smuio_SmuSmuioDec` address block whose documented base address is `0x5a000`. It maps symbolic `mm...` register names to register indices and supplies a matching `..._BASE_IDX` macro for each exported register.

## Important APIs, Types, And Macros
The header exports constants only. There are no functions, structs, enums, or runtime data.

The main register set covers ROM access and ROM software-command staging:

- ROM control/status/index/data/start registers: `mmROM_CNTL`, `mmROM_STATUS`, `mmCGTT_ROM_CLK_CTRL0`, `mmROM_INDEX`, `mmROM_DATA`, and `mmROM_START`.
- ROM software-command registers: `mmROM_SW_CNTL`, `mmROM_SW_STATUS`, `mmROM_SW_COMMAND`, and `mmROM_SW_DATA_1` through `mmROM_SW_DATA_64`, arranged contiguously from offsets `0x002e` through `0x006d`.
- SVI telemetry/current-voltage registers: `mmSMUSVI0_PLANE0_CURRENTVID` at offset `0x0013` and `mmSMUSVI0_TEL_PLANE0` at offset `0x0004`.

Every register is paired with `_BASE_IDX 0`, indicating that consumers should use register base index `0` with the AMDGPU register-access macros for this block.

## Control Flow
There is no local control flow. Consumer flow is data driven: include this offset header, include the matching `smuio_9_0_sh_mask.h`, then use SOC15/MMIO helpers to read or write registers by symbolic name. ROM-read code typically programs `ROM_INDEX` or `ROM_SW_COMMAND`, reads or writes `ROM_DATA`/`ROM_SW_DATA_n`, and polls status fields defined in the shift/mask header.

## State And Persistence Behavior
The header is stateless. It names MMIO locations whose values persist in hardware until changed by firmware, software, or device reset:

- ROM index/data/control state affects firmware or VBIOS ROM access.
- `ROM_SW_DATA_1` through `ROM_SW_DATA_64` provide command payload or return-data staging for software ROM commands.
- SVI registers expose voltage/telemetry information from the SMU/SVI interface.

## Dependencies
This header depends on consumers using the same SMUIO 9.0 address-map generation as the matching shift/mask header. It is normally consumed through AMDGPU register helpers that combine the `mm...` offset with `..._BASE_IDX`. The exact macro spelling is part of the generated AMD register ABI.

## Integration Points
The file integrates with AMDGPU ASIC support for SMUIO 9.0 devices. It is paired with `smuio_9_0_sh_mask.h`, which defines the fields inside the offsets named here. ROM, VBIOS, SMU telemetry, and power-management paths are likely consumers because those paths need ROM data, ROM command status, and SVI voltage fields.

## Risks
- Offset mismatch can cause reads and writes to target the wrong SMUIO register while still compiling.
- The long contiguous `ROM_SW_DATA_n` range is easy to index incorrectly in hand-written loops; consumers must preserve the one-based naming and actual offsets.
- Mixing this 9.0 offset header with a newer mask header is unsafe because newer generations add fields and may alter bit layout.
- Base index is uniformly `0`; any code assuming a nonzero instance or broadcast base would misaddress this block.

## Test Signals
- Build coverage verifies that symbolic offsets exist.
- ROM access tests should confirm `ROM_INDEX`, `ROM_DATA`, `ROM_SW_COMMAND`, and all expected payload registers address the correct hardware locations.
- SVI telemetry tests should compare decoded `CURRENTVID` and `TEL_PLANE0` values against expected SMU telemetry.
- Register dumps from known SMUIO 9.0 hardware should match the base `0x5a000` block layout and listed offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_9_0_offset.h -->
