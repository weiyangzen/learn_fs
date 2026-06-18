# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/lsdma/lsdma_7_1_0_offset.h

## Purpose

`lsdma_7_1_0_offset.h` defines the LSDMA 7.1.0 MMIO register offsets used by the AMDGPU LSDMA PIO copy/fill implementation. It is a compact generated offset header for the PIO register window. The values are consumed by SOC15 register helpers to compute actual MMIO addresses for source address, destination address, command, constant-fill data, control, and status registers.

## Important APIs, Types, And Macros

The file exports only `#define` constants. There are no functions or types.

PIO register offsets:

- `regLSDMA_PIO_SRC_ADDR_LO` at `0x0080` and `regLSDMA_PIO_SRC_ADDR_HI` at `0x0081`.
- `regLSDMA_PIO_DST_ADDR_LO` at `0x0082` and `regLSDMA_PIO_DST_ADDR_HI` at `0x0083`.
- `regLSDMA_PIO_COMMAND` at `0x0084`.
- `regLSDMA_PIO_CONSTFILL_DATA` at `0x0085`.
- `regLSDMA_PIO_CONTROL` at `0x0086`.
- `regLSDMA_PIO_STATUS` at `0x008a`.

Each register has a matching `_BASE_IDX` macro set to `0`, matching the SOC15 helper convention for selecting a register base segment.

## Control Flow

There is no local control flow. At runtime, `amdgpu/lsdma_v7_1.c` passes these constants to `WREG32_SOC15`, `RREG32_SOC15`, and `SOC15_REG_OFFSET`. The typical sequence is: write source and destination address halves, write control, update command fields using the matching 7.1.0 shift/mask header, write the command register, then poll the status register until `PIO_IDLE` and `PIO_FIFO_EMPTY` are set.

## State And Persistence Behavior

The header is stateless. The offsets identify hardware registers whose contents are transient device state. Source/destination address and command/control registers are programmed per PIO operation. Constant-fill data persists in the register until rewritten or reset. Status reports in-flight command/FIFO/error state and is not persisted by this file.

## Dependencies

Consumers require:

- `lsdma_7_1_0_sh_mask.h` for the bit layout inside the registers defined here.
- SOC15 register access macros and base-index conventions.
- Driver code that knows the LSDMA instance and register block name, currently `LSDMA, 0` in `amdgpu/lsdma_v7_1.c`.

The include guard is `_lsdma_7_1_0_OFFSET_HEADER`.

## Integration Points

Direct integration found in this tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v7_1.c` includes this header and uses every defined register except that the copy path does not write `PIO_CONSTFILL_DATA`, while the fill path does.

This file also defines the version boundary between 7.0.0 and 7.1.0: 7.1.0 places the PIO window at offsets `0x80` through `0x8a`, whereas 7.0.0 uses a different offset set.

## Risks

- Any incorrect offset directs MMIO writes to the wrong register, which can corrupt unrelated LSDMA state or leave PIO operations stuck.
- The sparse gap between `regLSDMA_PIO_CONTROL` (`0x0086`) and `regLSDMA_PIO_STATUS` (`0x008a`) must be preserved; code should not infer contiguous register coverage.
- The `_BASE_IDX` values are part of the SOC15 address calculation. Changing them without a matching register-base update would break access.
- Pairing this offset header with the wrong shift/mask header can compile but program incompatible bitfields.

## Test Signals

- Compile `amdgpu/lsdma_v7_1.c` to catch missing register names.
- Runtime smoke tests for 7.1.0 should call copy and fill operations and verify that the wait path sees `PIO_IDLE` and `PIO_FIFO_EMPTY` in `regLSDMA_PIO_STATUS`.
- Hardware register traces can confirm writes land at offsets `0x80` to `0x86` and status reads at `0x8a`.
- Regression comparison against 7.0.0 should verify that each version uses its own offset header and does not share PIO offset constants.
