# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_objs_regs.h lines 1-9404

## Purpose

This chunk is the opening portion of an auto-generated Gaudi2 ASIC register header for the DCORE0 sync-manager objects block. The header identifies the block as `DCORE0_SYNC_MNGR_OBJS`, based on the `SOB_OBJS` prototype, and begins the generated MMIO offset map used by the HabanaLabs driver to address hardware synchronization objects.

Within lines 1-9404, the substantive content is the first contiguous part of the sync object bank: `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_0` through `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_4690`. These macros expose 32-bit register offsets from `0x4100000` through `0x4104948`, with one register every 4 bytes. The overall file continues after this chunk with more `SOB_OBJ` entries and later sync-manager object register families.

## Important APIs, Types, And Functions

This chunk does not define C functions, structs, enums, or executable control logic. Its API surface is the generated preprocessor register namespace:

- `ASIC_REG_DCORE0_SYNC_MNGR_OBJS_REGS_H_`: include guard for the generated register header. The guard begins in this chunk; the closing `#endif` is outside this line range.
- `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_n`: per-sync-object MMIO offset constants for DCORE0. In this chunk, `n` ranges from `0` to `4690`.
- Addressing rule: `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_n == 0x4100000 + (n * 4)` for every entry covered here.

The register bit fields are not described in this file. Consumers combine these offsets with masks from Gaudi2 mask headers, especially `DCORE0_SYNC_MNGR_OBJS_SOB_OBJ_VAL_MASK`, `DCORE0_SYNC_MNGR_OBJS_SOB_OBJ_INC_MASK`, and `DCORE0_SYNC_MNGR_OBJS_SOB_OBJ_SIGN_MASK`, to construct values written to the SOB registers.

## Control Flow

There is no runtime control flow in this chunk. The C preprocessor makes the symbolic offsets available to any translation unit that includes `gaudi2_regs.h`, which includes this generated header.

Runtime control flow appears in the consuming Gaudi2 driver code:

1. Initialization code uses the first SOB offset as an array base, usually `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_0`.
2. Driver paths compute per-object addresses as `base + sob_id * sizeof(u32)` or `base + sob_offset`.
3. MMIO helpers such as `WREG32()` and `RREG32()` read or write those computed offsets.
4. Monitor setup code programs monitor payload addresses to point at SOB registers, allowing hardware monitors to increment, decrement, or test synchronization objects.

Because this header provides literal offsets only, all ordering, bounds checking, and synchronization semantics are imposed by the caller and by the hardware block.

## State And Persistence Behavior

The header itself owns no software state and persists nothing. Its constants name hardware state: each `SOB_OBJ_n` register is a sync object slot in DCORE0's sync-manager object aperture.

Writes to these registers affect device MMIO state. In the observed Gaudi2 consumers, SOB registers are reset by writing zero, incremented with payloads built from the SOB value/increment masks, and used as completion or interrupt synchronization counters. That hardware state persists until overwritten by the driver, modified by hardware monitor activity, or reset by device/firmware initialization.

This chunk covers only a prefix of the SOB array. The full driver-level SOB count is computed elsewhere from `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_8191` and `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_0`, so code that assumes the complete 8192-entry array must include the rest of the generated header, not just this chunk.

## Dependencies

- `gaudi2_regs.h` includes this generated register header and provides the normal aggregation point for Gaudi2 register offsets.
- `gaudi2P.h` derives `DCORE_NUM_OF_SOB` from the first and last SOB register macros and defines `SM_OBJS_BLOCK_SIZE` from the sync-manager object block boundaries.
- `gaudi2_masks.h` supplies bit masks and shifts used when writing values to SOB registers. For example, `GAUDI2_SOB_INCREMENT_BY_ONE` combines SOB value and increment fields rather than using raw literal payloads.
- Driver MMIO accessors such as `WREG32()` and `RREG32()` consume these offsets as low-bandwidth register addresses, often adding `CFG_BASE` when a hardware agent must be programmed with a full physical MMIO address.
- The hardware contract is that the generated offsets match the Gaudi2 register map exactly. The source is marked auto-generated and should be regenerated from the ASIC database rather than hand-edited.

## Integration Points

The main integration point is the Gaudi2 sync-manager and monitor infrastructure:

- Queue-manager initialization programs command processor message bases with `CFG_BASE + mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_0`, allowing queue managers to target the SOB aperture.
- Completion and interrupt flows compute addresses from `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_0 + sob_id * 4` and program monitor payloads or bridge doorbell registers to update those SOBs.
- Device initialization and cleanup paths clear reserved SOB slots with `WREG32(mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_0 + sob_offset, 0)`.
- Security setup uses the SOB object range together with monitor/config/security offsets later in the same generated header to configure protection for exposed sync-manager object regions.

For this chunk specifically, the useful integration invariant is the dense 4-byte stride. Consumers rarely reference individual high-numbered macros directly; instead they use the base macro and derive addresses arithmetically.

## Risks And Edge Cases

- Off-by-one or stride errors are high impact. If a caller computes `sob_id * 4` against the wrong base or allows an out-of-range `sob_id`, it can write the wrong sync object or move into the next sync-manager register family.
- The chunk is incomplete by design. It ends at `SOB_OBJ_4690` while the full file continues; per-file research must reconcile later chunks before making claims about all SOBs, monitor registers, config registers, or security registers.
- Generated headers are fragile to manual edits. Renumbering a macro, changing an address literal, or introducing a gap would break driver assumptions such as `DCORE_NUM_OF_SOB` and array-style MMIO indexing.
- Bit interpretation is external. A raw write to a SOB register is not self-documenting without the masks in `gaudi2_masks.h`; consumers must use the correct value, increment, and sign fields for the intended hardware operation.
- Security and user-mapping code depends on exact range endpoints. An incorrect SOB start or end address could expose sync objects incorrectly or fail to protect registers that affect completion signaling.

## Test Signals

- Compile coverage should include translation units that include `include/gaudi2/asic_reg/gaudi2_regs.h`; missing or renamed macros will fail at build time.
- Static checks can verify the generated arithmetic invariant for this chunk: 4691 macros, `SOB_OBJ_0 == 0x4100000`, `SOB_OBJ_4690 == 0x4104948`, and a constant 4-byte stride with no index gaps.
- Driver smoke tests that initialize Gaudi2 queue managers, monitors, decoder interrupts, and completion paths exercise this register family through `WREG32()` and monitor payload programming.
- Runtime diagnostics around SOB reset/readback and completion signaling are useful integration signals, because failures often appear as hung command submissions, missed interrupts, or stale monitor state rather than as direct errors from this header.
