# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/lsdma/lsdma_7_1_0_sh_mask.h

## Purpose

`lsdma_7_1_0_sh_mask.h` defines the bit shifts and masks for the small LSDMA 7.1.0 PIO register set. It is the companion to `lsdma_7_1_0_offset.h`: offsets identify the registers, while this header defines how to encode and decode fields in those registers.

## Important APIs, Types, And Macros

The file exports preprocessor constants only.

Register field groups:

- `LSDMA_PIO_STATUS`: command FIFO depth (`CMD_IN_FIFO`), command processing count/state (`CMD_PROCESSING`), error bits for invalid address, zero count, DRAM ECC, SRAM ECC, write/read return NACK general errors, write/read return NACK protection errors, request drop, FIFO empty/full, and PIO idle.
- `LSDMA_PIO_SRC_ADDR_LO` and `LSDMA_PIO_SRC_ADDR_HI`: 64-bit source address split into 32-bit halves.
- `LSDMA_PIO_DST_ADDR_LO` and `LSDMA_PIO_DST_ADDR_HI`: 64-bit destination address split into 32-bit halves.
- `LSDMA_PIO_CONTROL`: VMID plus destination/source memory attributes such as GPA, system memory, GCC, snoop, reuse hint, and compression enable.
- `LSDMA_PIO_COMMAND`: `COUNT` in bits 0-25, `RAW_WAIT` at bit 30, and `CONSTANT_FILL` at bit 31.
- `LSDMA_PIO_CONSTFILL_DATA`: 32-bit fill payload.

The command mask shape matters for callers: the count field is `0x03ffffff`, so any caller-provided size must fit the 26-bit field before `REG_SET_FIELD` is used.

## Control Flow

There is no local control flow. The runtime consumer is `amdgpu/lsdma_v7_1.c`. In copy mode, the driver writes source and destination address registers, sets `LSDMA_PIO_COMMAND.COUNT`, clears `RAW_WAIT`, clears `CONSTANT_FILL`, and writes the command register. In fill mode, it first writes `LSDMA_PIO_CONSTFILL_DATA`, writes the destination address, sets `COUNT`, clears `RAW_WAIT`, sets `CONSTANT_FILL`, and writes the command register. Both paths then poll status for `PIO_IDLE | PIO_FIFO_EMPTY`.

## State And Persistence Behavior

The header has no state. The described hardware registers carry transient command programming and status. Address, command, control, and fill-data values persist only as hardware register contents until overwritten or reset. Status bits reflect queue occupancy, in-flight processing, idle state, and sticky or transient error conditions depending on hardware behavior.

## Dependencies

Consumers require:

- `lsdma_7_1_0_offset.h` for register offsets.
- SOC15 register access helpers.
- AMDGPU bitfield helper naming conventions: `REG_SET_FIELD(tmp, LSDMA_PIO_COMMAND, COUNT, size)` expands using `LSDMA_PIO_COMMAND__COUNT_MASK` and `LSDMA_PIO_COMMAND__COUNT__SHIFT`.

The include guard is `_lsdma_7_1_0_SH_MASK_HEADER`.

## Integration Points

Direct integration found in this tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/lsdma_v7_1.c` includes this file and uses `LSDMA_PIO_STATUS__PIO_IDLE_MASK`, `LSDMA_PIO_STATUS__PIO_FIFO_EMPTY_MASK`, and `LSDMA_PIO_COMMAND` fields `COUNT`, `RAW_WAIT`, and `CONSTANT_FILL`.

The fields are a streamlined 7.1.0 PIO contract. Compared with 7.0.0, source/destination location, address increment, and overlap-disable command fields are absent; status error bits also shift upward for the early error fields and include `ERROR_REQ_DROP`.

## Risks

- Code ported from 7.0.0 must not use `BYTE_COUNT`, `SRC_LOCATION`, `DST_LOCATION`, `SRC_ADDR_INC`, `DST_ADDR_INC`, or `OVERLAP_DISABLE`; those fields are not present in this header.
- `COUNT` is 26 bits. Oversized copy/fill requests can be truncated by field insertion unless callers split or validate sizes.
- Error handling in the current direct consumer only waits for idle/empty and logs a generic failure on wait error; these masks expose more detailed error bits that can be missed if diagnostics do not read status on failure.
- Pairing these masks with a mismatched offset header can produce valid writes to the wrong register layout.

## Test Signals

- Compile coverage for `amdgpu/lsdma_v7_1.c` verifies field names expected by the driver.
- Runtime copy/fill tests should validate both `CONSTANT_FILL=0` and `CONSTANT_FILL=1` command paths.
- Negative or fault-injection testing should inspect `LSDMA_PIO_STATUS` error bits, especially invalid address, zero count, ECC, NACK, and request-drop fields.
- Boundary tests should exercise maximum legal `COUNT` and confirm larger operations are rejected or split by higher layers.
