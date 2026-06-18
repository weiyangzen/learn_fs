# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/hdp/hdp_4_4_2_sh_mask.h

## Purpose

`hdp_4_4_2_sh_mask.h` defines bit shifts and masks for the HDP 4.4.2 `aid_hdp_hdpdec` register map. It describes how fields inside the 4.4.2 AID HDP registers are packed, including newer surface flags, power-control fields, wider status fields, and split GPU IOV logging relative to HDP 4.0.

## Important APIs, types, and macros

The file is macro-only. Key field groups are:

- Widened traffic-level masks: `HDP_MMHUB_TLVL__HDP_WR_TLVL_MASK`, `HDP_RD_TLVL_MASK`, `XDP_WR_TLVL_MASK`, `XDP_RD_TLVL_MASK`, and `XDP_MBX_WR_TLVL_MASK` are 4-bit fields in this version.
- Surface access flags: `HDP_SURFACE_WRITE_FLAGS__SURF0/1_WRITE_FLAG`, `HDP_SURFACE_READ_FLAGS__SURF0/1_READ_FLAG`, and corresponding clear fields.
- Host path control fields: write/read stall timers, write-combine controls, 64-byte combine enable, and `ALL_SURFACES_DIS`. Unlike HDP 4.0/5.0 masks, this header does not define `WRITE_THROUGH_CACHE_DIS` or `LIN_RD_CACHE_DIS` for `HDP_HOST_PATH_CNTL`.
- `HDP_MISC_CNTL` fields for idle hysteresis, atomic buffer protection, raw address CAM, early write ack, simultaneous reads/writes, syshub priority, read-buffer watermark, SRAM ECC, FED/atomic FED, MMHUB burst, and pending write tag checks.
- `HDP_MEM_POWER_CTRL` fields for IPH and RC memory power control, light sleep, deep sleep, shutdown, idle hysteresis, power-up recovery delay, and power-down LS enter delay.
- `HDP_MMHUB_CNTL` fields with RO/GCC/SNOOP plus override bits.
- `HDP_CLK_CNTL` fields including IPH and RC memory clock soft overrides plus DBUS, dynamic, XDP, and HDP register clock overrides.
- XDP/P2P/mailbox/status fields, including 24-bit `HDP_XDP_BUSY_STS__BUSY_BITS_MASK`, `HDP_XDP_GPU_IOV_VIOLATION_LOG2__INITIATOR_ID`, and MMHUB error FED bits.

## Control flow

There is no executable code. Runtime control is in callers that expand these field macros via register helper macros. The naming convention remains `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`, so consumers can use token-pasting helpers without spelling numeric masks directly.

## State and persistence behavior

The described fields cover persistent hardware state: surface and non-surface access flags, memory power gating modes, clock override state, MEMIO command/status fields, P2P BAR validity, sticky XDP bits, IOV violation status, and MMHUB response/error bits. Some fields are clear-on-write or write-one-to-clear style, so mask correctness matters for avoiding accidental loss of diagnostic state.

## Dependencies and integration points

This header pairs with `hdp_4_4_2_offset.h`. It also mirrors later HDP 5.x concepts such as `MEM_POWER_CTRL`, `GPU_IOV_VIOLATION_LOG2`, and richer clock override fields. Although no direct include of this file was found in the visible C sources, its layout is compatible with the AMDGPU `REG_SET_FIELD()`/`REG_GET_FIELD()` macro scheme and with AID-scoped register access patterns.

## Risks

Version skew is the central risk. HDP 4.4.2 differs from HDP 4.0 in traffic-level field width, host-path cache-disable fields, MEM_POWER register naming/layout, EDC counter width, busy status width, and IOV initiator placement. Reusing 4.0 masks on 4.4.2 would truncate fields or write undefined bits; reusing 4.4.2 masks on 4.0 would target fields not present there. Error and IOV fields are security/debug sensitive, so incorrect masks can misreport SR-IOV violations.

## Test signals

Expected signals include successful compilation of any AID HDP consumer, correct `REG_SET_FIELD()` expansion for `HDP_MEM_POWER_CTRL` and `HDP_CLK_CNTL`, working surface flag set/clear behavior, valid busy/sticky status readings, and IOV violation logs that preserve address/opcode/VF/VFID in `LOG` and initiator ID in `LOG2`. Static comparison against generated register XML or headers for HDP 4.4.2 is especially valuable.
