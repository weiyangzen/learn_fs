# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_objs_regs.h lines 9405-18572

## Scope

This chunk covers the middle of the auto-generated Gaudi2 DCORE0 sync-manager object register header. The file declares preprocessor constants only; there are no C functions, structs, enums, branches, or storage objects in this slice. Lines 9405-18572 contain 4,584 `#define` entries and no other nonblank content.

The chunk starts inside the sync object array and ends inside the monitor payload low-address array, so the final file-level merge must combine this with adjacent chunks for complete register-family coverage.

## Purpose

The constants in this chunk expose memory-mapped register offsets for the DCORE0 sync-manager object block. Driver code uses these offsets with `RREG32`, `WREG32`, command-packet builders, and LBW memset helpers to program synchronization objects and monitors on Gaudi2 hardware.

The covered register families are:

| Family | Lines | Index range | Address range | Count | Layout |
| --- | ---: | ---: | ---: | ---: | --- |
| `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_n` | 9405-16405 | 4691-8191 | `0x410494C`-`0x4107FFC` | 3501 | contiguous 32-bit words |
| `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_ADDRL_n` | 16407-18571 | 0-1082 | `0x4108000`-`0x41090E8` | 1083 | contiguous 32-bit words |

The `SOB_OBJ` range is the tail of the 8192-entry sync-object array. The `MON_PAY_ADDRL` range is the beginning of the monitor payload low-address array. Both arrays advance by 4 bytes per index, and no gaps were observed inside the assigned line range.

## Important APIs, Types, And Constants

This chunk defines register-address macros, not callable APIs:

- `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_4691` through `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_8191` map sync object registers from `0x410494C` through `0x4107FFC`.
- `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_ADDRL_0` through `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_ADDRL_1082` map monitor payload low-address registers from `0x4108000` through `0x41090E8`.

The most important symbols in this chunk from an integration perspective are the boundary constants:

- `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_8191` is used by `gaudi2P.h` to derive `DCORE_NUM_OF_SOB`.
- `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_ADDRL_0` is used by `gaudi2.c` as the base of the monitor payload low-address array and as the end boundary for the SOB-object region.

Most runtime code does not reference the high numbered `SOB_OBJ_n` or `MON_PAY_ADDRL_n` macros directly. It uses the `_0` macro plus `id * sizeof(u32)` / `id * 4`, relying on the generated per-index macros to document and preserve the same contiguous hardware map.

## Control Flow

There is no executable control flow in this chunk. The effective control flow appears in consumers:

- Queue-manager initialization writes `CFG_BASE + mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_ADDRL_0` and `CFG_BASE + mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_0` into QMAN CP/PQC base registers.
- Monitor setup computes `mon_offset = mon_id * sizeof(u32)` and programs `MON_PAY_ADDRL_0 + mon_offset` for monitor message destination addresses.
- SOB reset and restore paths compute `sob_offset = sob_id * sizeof(u32)` and access `SOB_OBJ_0 + sob_offset`.
- Device initialization clears user-available SOBs by using `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_ADDRL_0 - (mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_0 + offset)` as the byte size of the SOB region to clear.

For this chunk specifically, control-flow relevance is boundary-driven: the transition from `SOB_OBJ_8191` at `0x4107FFC` to `MON_PAY_ADDRL_0` at `0x4108000` is the hardware boundary used by memset sizing and register-array count calculations.

## State And Persistence Behavior

The header itself persists no software state. It names MMIO locations for hardware state:

- `SOB_OBJ` registers hold synchronization object values used by queues, completions, monitor arming, and reset paths.
- `MON_PAY_ADDRL` registers hold the low 32 bits of destination addresses written by monitor-triggered messages.

State is volatile hardware state. The driver initializes, clears, restores, or re-arms these registers during device setup, reset, command submission support, and interrupt/fence programming. Because this chunk only defines DCORE0 offsets, other DCORE instances are reached in consumers by adding `DCORE_OFFSET`.

## Dependencies

Direct dependencies are minimal because this is a generated header:

- The include guard and file context identify the block as `DCORE0_SYNC_MNGR_OBJS` with prototype `SOB_OBJS`.
- Consumers depend on Linux/Habanalabs register helpers such as `RREG32`, `WREG32`, `lower_32_bits`, `upper_32_bits`, `FIELD_PREP`, and device constants such as `CFG_BASE`, `DCORE_OFFSET`, and `sizeof(u32)`.
- Bitfield meaning for SOB and monitor programming is supplied by related generated mask headers, for example `DCORE0_SYNC_MNGR_OBJS_SOB_OBJ_*_MASK`, `DCORE0_SYNC_MNGR_OBJS_MON_ARM_*_MASK`, and monitor config/status masks outside this chunk.

The chunk is coupled to generated register maps for the rest of the same block, especially the preceding `SOB_OBJ_0`-`SOB_OBJ_4690` definitions and later `MON_PAY_ADDRL_1083+`, `MON_PAY_ADDRH`, `MON_PAY_DATA`, `MON_ARM`, `MON_CONFIG`, `MON_STATUS`, and security-region definitions.

## Integration Points

Observed Gaudi2 integration points include:

- `drivers/accel/habanalabs/gaudi2/gaudi2P.h` derives `DCORE_NUM_OF_SOB` from `SOB_OBJ_8191 - SOB_OBJ_0`.
- `drivers/accel/habanalabs/gaudi2/gaudi2.c` initializes QMAN completion and monitor bases using `MON_PAY_ADDRL_0` and `SOB_OBJ_0`.
- `gaudi2_arm_monitors_for_virt_msix_db()` programs `MON_PAY_ADDRL_0 + mon_offset` as part of a three-monitor sequence that writes MSI-X doorbells, decrements a SOB, and re-arms the master monitor.
- user-context reset/restore code clears SOBs up to `MON_PAY_ADDRL_0`, making the address boundary in this chunk part of the clearing contract.
- command buffer construction uses `MON_PAY_ADDRL_0` as the monitor message base and computes short message offsets to `MON_PAY_ADDRL`, `MON_PAY_ADDRH`, `MON_PAY_DATA`, and `MON_ARM` arrays.
- security setup references the sync-manager object block and comments on the 8192 SOB objects, matching the `SOB_OBJ_8191` terminal index covered here.

## Risks

- The generated map is a hardware ABI. A wrong address, skipped index, or changed stride would silently redirect MMIO writes and could break queue completion, monitor programming, resets, or security initialization.
- The boundary at `SOB_OBJ_8191` / `MON_PAY_ADDRL_0` is used as both a count and a byte-size delimiter. Off-by-one changes can cause incomplete SOB clearing or writes into monitor payload registers.
- Consumers assume 32-bit spacing and compute offsets manually. Any future hardware generation with non-4-byte stride would require code changes, not just regenerated macro names.
- This chunk starts and ends mid-file; reviewing it alone cannot validate the full monitor array count or later arrays such as `MON_PAY_ADDRH`, `MON_PAY_DATA`, `MON_ARM`, and `MON_STATUS`.
- The file is marked auto-generated. Manual edits should be avoided because they risk divergence from the authoritative ASIC register database.

## Test And Validation Signals

Useful validation signals for this chunk are structural and integration-oriented:

- Build coverage: compile Gaudi2 Habanalabs driver code that includes this header and references `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_8191` and `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_ADDRL_0`.
- Static map checks: verify each covered family increments index by 1 and address by 4 bytes. This chunk passed that check for `SOB_OBJ_4691`-`8191` and `MON_PAY_ADDRL_0`-`1082`.
- Boundary checks: confirm `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_8191 + 4 == mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_ADDRL_0`.
- Runtime hardware tests: queue completion, monitor-triggered MSI-X doorbell handling, SOB reset, device reset/restore, and user SOB clearing paths exercise the register bases and the SOB-to-monitor boundary.
- Security/init validation: checks that user-available SOB ranges begin after reserved pending command-submission SOBs and that all DCOREs are cleared through `DCORE_OFFSET`-derived addresses.

## Cross-Chunk Notes

The merge lane should join this with earlier and later chunks to recover whole-file semantics:

- Earlier lines define `SOB_OBJ_0` through `SOB_OBJ_4690`, including the base macro most consumers use.
- Later lines continue `MON_PAY_ADDRL` beyond index 1082 and define additional monitor payload, arm, config, status, and security-region arrays.
- Whole-file research should describe the full sync-manager object layout from SOB objects through all monitor and security regions, while this chunk only proves the mid-file SOB tail and start of low-address monitor payload layout.
