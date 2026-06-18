# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/vic.h

## Purpose

`vic.h` defines VIC method IDs, register offsets, stream-ID transaction configuration fields, clock-gating fields, and firmware header offsets used by `vic.c`.

## Important APIs, Types, and Definitions

- Methods: `VIC_SET_FCE_UCODE_SIZE` and `VIC_SET_FCE_UCODE_OFFSET` are Falcon method IDs for old firmware FCE setup.
- Registers: `VIC_THI_STREAMID0/1`, `NV_PVIC_MISC_PRI_VIC_CG`, and `VIC_TFBIF_TRANSCFG`.
- Bitfield helpers: `CG_IDLE_CG_DLY_CNT`, `CG_IDLE_CG_EN`, `CG_WAKEUP_DLY_CNT`, and `TRANSCFG_ATT`.
- Stream-ID attributes: `TRANSCFG_SID_HW`, `TRANSCFG_SID_PHY`, and `TRANSCFG_SID_FALCON`.
- Firmware offsets: `VIC_UCODE_FCE_HEADER_OFFSET`, `VIC_UCODE_FCE_DATA_OFFSET`, and `FCE_UCODE_SIZE_OFFSET`.

## Control Flow

The header has no runtime control flow. `vic.c` uses these constants during firmware boot and stream-ID/clock-gating setup.

## State and Persistence Behavior

The constants refer to hardware registers and firmware binary layout. Writes to the registers persist until reset or power loss; firmware offsets are read-only interpretation of loaded firmware data.

## Dependencies and Integration Points

It is consumed by `vic.c` and must match VIC hardware and firmware ABI expectations across Tegra generations.

## Risks and Edge Cases

Incorrect offsets can break firmware boot or memory isolation. Firmware-layout constants are especially sensitive because old/new firmware behavior is inferred from magic offset values in `vic.c`.

## Test Signals

Build coverage plus runtime VIC firmware boot, stream-ID isolation tests, and old firmware FCE setup traces validate these definitions.
