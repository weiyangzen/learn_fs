# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_regs.h

## Purpose

`xe_regs.h` defines miscellaneous top-level Xe and SoC registers used by initialization, force-reset, stolen memory discovery, frequency capability discovery, tile range discovery, and VF capability probing.

## Important APIs, Types, and Definitions

- `SOC_BASE` for SoC-relative register headers.
- Global control/debug: `GU_CNTL_PROTECTED`, `DRIVERINT_FLR_DIS`, `GU_CNTL`, `LMEM_INIT`, `DRIVERFLR`, `GU_DEBUG`, and `DRIVERFLR_STATUS`.
- Tile/memory discovery: `XEHP_MTCFG_ADDR`, `TILE_COUNT`, `GGC`, `GMS_MASK`, `GGMS_MASK`, `DSMBASE`, `BDSM_MASK`, `GSMBASE`, `STOLEN_RESERVED`, and `WOPCM_SIZE_MASK`.
- Tile address and frequency registers: `SG_TILE_ADDR_RANGE(_idx)`, `MTL_*_FREQUENCY`, `MTL_*_STATE_CAP`, `PVC_RP_STATE_CAP`.
- Virtualization: `VIRTUAL_CTRL_REG`, `GUEST_GTT_UPDATE_EN`, `VF_CAP_REG`, and `VF_CAP`.

## Control Flow

There is no executable code. Initialization and reset code reads or writes these registers to discover platform layout, control FLR, initialize local memory, read frequency caps, and determine VF capability.

## State and Persistence Behavior

The registers expose persistent hardware configuration and control state. FLR and LMEM bits are command/control bits, while memory base and capability registers describe platform configuration.

## Dependencies and Integration Points

It includes `regs/xe_reg_defs.h`. It is used by platform bring-up, memory/stolen-memory setup, tile enumeration, power/frequency code, SR-IOV/VF setup, and SoC-specific headers that derive offsets from `SOC_BASE`.

## Risks and Edge Cases

- `SOC_BASE` is reused by multiple headers; changing it has broad address impact.
- FLR control/status bits must be sequenced with reset code and interrupt masking.
- Field masks using 64-bit values require consumers to read the appropriate register width.

## Test Signals

Signals include correct tile count detection, local-memory initialization, stolen memory sizing, VF capability detection, frequency reporting, and reset/FLR recovery.
