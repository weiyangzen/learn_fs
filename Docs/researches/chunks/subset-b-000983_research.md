# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_objs_regs.h lines 27141-36256

## Scope

This chunk is an auto-generated Gaudi2 ASIC register-address header slice for the DCORE0 sync-manager objects block. It contains only C preprocessor `#define` constants and blank separator lines. There are no functions, types, executable statements, comments, conditionals, or local control flow inside the assigned line range.

The source file itself is guarded by `ASIC_REG_DCORE0_SYNC_MNGR_OBJS_REGS_H_`, carries a GPL-2.0 SPDX tag, and identifies the register block as `DCORE0_SYNC_MNGR_OBJS` with prototype `SOB_OBJS`. The chunk covers register families used by monitor programming:

- `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_DATA_1271` through `_2047`, addresses `0x410D3DC` through `0x410DFFC`.
- `mmDCORE0_SYNC_MNGR_OBJS_MON_ARM_0` through `_2047`, addresses `0x410E000` through `0x410FFFC`.
- `mmDCORE0_SYNC_MNGR_OBJS_MON_CONFIG_0` through `_1732`, addresses `0x4110000` through `0x4111B10`.

The assigned range has 4,558 register defines. Every define is a 32-bit MMIO address spaced by 4 bytes from the previous index in the same family. The range begins in the middle of the `MON_PAY_DATA` array because earlier chunk coverage contains `MON_PAY_DATA_0` through `_1270`; it ends in the middle of `MON_CONFIG`, with `_1733` through `_2047` continuing after this chunk.

## Purpose

The header gives the Gaudi2 driver symbolic names for DCORE0 sync-manager monitor MMIO locations. The sync manager is used to connect hardware sync objects (SOBs), monitors, completion queues, and MSI-X signaling. These constants let C code write monitor payload data, arm monitors against SOB groups, and configure monitor behavior without embedding raw offsets.

Within this chunk:

- `MON_PAY_DATA_n` is the 32-bit payload value written by monitor `n` when its trigger condition fires. Consumers use it for values such as SOB decrement payloads, monitor re-arm words, completion queue payloads, fence writes, or interrupt IDs.
- `MON_ARM_n` is the 32-bit arm/control register for monitor `n`. It binds the monitor to a sync-object group, mask, comparison operation, and sync-object data threshold/value.
- `MON_CONFIG_n` is the 32-bit configuration register for monitor `n`. It controls options such as CQ mode, LBW write enablement, number of writes in a multi-message monitor, long-SOB handling, high SID bits, and high-group selection.

The chunk is hardware-description data, not a policy layer. The driver behavior comes from code that combines these base addresses with indexes and field masks from the companion masks header.

## Important APIs, Types, And Register Families

There are no APIs, structs, enums, or functions declared by this chunk. Its public interface is the macro namespace consumed by Gaudi2 driver code and by any generated register/mask tooling.

Important macro families:

- `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_DATA_*`: contiguous payload-data MMIO array. In this chunk the visible subset is index `1271..2047`, completing the 2,048-monitor payload-data region that starts at `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_DATA_0` on earlier lines. Driver code usually computes `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_DATA_0 + mon_id * 4`; individual high-index symbols are mainly generated-map completeness.
- `mmDCORE0_SYNC_MNGR_OBJS_MON_ARM_*`: full contiguous monitor-arm MMIO array for indexes `0..2047`. The companion masks define fields `SID`, `MASK`, `SOP`, and `SOD`. `SID` selects the SOB group, `MASK` selects participating SOBs within the group, `SOP` selects comparison mode, and `SOD` carries comparison data.
- `mmDCORE0_SYNC_MNGR_OBJS_MON_CONFIG_*`: contiguous monitor-config MMIO array. This chunk covers `0..1732`, while the rest of the file continues through `_2047`. The companion masks define `LONG_SOB`, `CQ_EN`, `WR_NUM`, `LBW_EN`, `MSB_SID`, and `LONG_HIGH_GROUP`.

Related constants outside this chunk are part of the same contract:

- `mmDCORE0_SYNC_MNGR_OBJS_MON_PAY_ADDRL_0` and `_ADDRH_0` hold the low/high destination address for monitor writes.
- `mmDCORE0_SYNC_MNGR_OBJS_MON_STATUS_0` is used by driver code to size and reset monitor state.
- `mmDCORE0_SYNC_MNGR_OBJS_SOB_OBJ_0` is the sync-object base used with monitor arm fields.
- `mmDCORE0_SYNC_MNGR_OBJS_SM_SEC_0` bounds the user-accessible sync-manager object block in reset/restore paths.
- `DCORE_NUM_OF_MONITORS` in `gaudi2P.h` computes the monitor count from `MON_STATUS_2047 - MON_STATUS_0`, matching the 2,048-entry monitor arrays represented here.

## Control Flow

This chunk has no direct control flow. Its values enter driver control flow through MMIO reads/writes and generated command buffers.

Primary runtime flows using these register families include:

- Virtual MSI-X doorbell preparation in `gaudi2_arm_monitors_for_virt_msix_db()`: resets a SOB, programs three consecutive monitors, writes `MON_PAY_DATA` entries for a SOB decrement payload, a re-arm payload, and an interrupt ID, writes `MON_CONFIG` with `WR_NUM=2` to request three monitor writes, and finally writes `MON_ARM` to arm the master monitor.
- Sync-manager initialization in `gaudi2_init_sm()`: writes `MON_CONFIG_0 + i * 4` for reserved completion monitors, enabling CQ behavior and, for completion monitors, LBW completion support. The KDMA completion monitor is configured with CQ only.
- Command-submission completion monitoring in `gaudi2_arm_cq_monitor()`: resets a SOB, writes CQ ID and CS-index payload data into monitor payload registers, builds the arm word with `SID`, `MASK`, `SOP`, and `SOD`, and writes it to `MON_ARM`.
- Context/user-state restore paths around `gaudi2_restore_user_sm_registers()`: use `MON_CONFIG_0`, `MON_STATUS_0`, and sync-manager block boundaries to clear and protect user monitor state across DCOREs.
- Generated wait command buffers in `gaudi2_gen_wait_cb()`: compute message-short offsets from a monitor base to `MON_PAY_ADDRL`, `MON_PAY_ADDRH`, `MON_PAY_DATA`, and `MON_ARM` for a selected monitor ID, then emit packets that configure a monitor to write a fence value when the sync condition is met.

Most consumers use the base-plus-offset convention rather than the high-index macro names directly. That makes the contiguous layout and 4-byte stride the critical control-flow contract.

## State And Persistence Behavior

The macros themselves are compile-time constants and do not store state. They map to volatile hardware state in the Gaudi2 sync-manager block.

Hardware state affected through this address range includes:

- Per-monitor payload data, retained in the sync-manager register file until overwritten or reset.
- Per-monitor arm state, which determines whether and how a monitor waits on SOB values and dispatches writes.
- Per-monitor configuration, including CQ/LBW behavior and multi-write sequencing.

This state is runtime device state, not filesystem state. It is generally reset-sensitive and context-sensitive. Driver initialization programs reserved monitors for completion and KDMA paths. Context setup and restore paths clear or protect user-available monitor state. Command-buffer generation and queue submission paths may program monitor entries repeatedly for waits, fences, and interrupt redirection.

Persistence risks are mostly hardware lifetime concerns: stale `MON_ARM` state can leave a monitor armed against the wrong SOB, stale `MON_PAY_DATA` can write an old payload when a monitor fires, and stale `MON_CONFIG` can change whether the write is interpreted as CQ/LBW/multi-write behavior. The driver mitigates this by resetting SOBs, configuring payload/address registers before arm writes, and bulk-clearing user monitor config/status state during context restoration.

## Dependencies

This generated header depends on the Gaudi2 hardware register map. It does not include other files directly in the chunk, but it is normally included alongside:

- `dcore0_sync_mngr_objs_masks.h`, which defines field shifts and masks for the register families named here.
- `gaudi2P.h`, which derives sync-manager counts and block sizes from generated register addresses, including monitor and SOB ranges.
- Gaudi2 implementation code in `gaudi2.c`, which uses `WREG32`, `RREG32`, `FIELD_PREP`, `lower_32_bits`, `upper_32_bits`, queue IDs, SOB IDs, monitor IDs, and completion queue structures.
- Common Habana Labs driver infrastructure for MMIO access, command-buffer submission, contexts, completion queues, firmware interrupt handling, and debug/reset flows.

The address values are DCORE0-specific. Other DCOREs are addressed either through corresponding generated headers/register bases or by adding the architectural `DCORE_OFFSET` where code intentionally walks the same block layout across DCORE instances.

## Integration Points

Key integration points are in `sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi2/gaudi2.c`:

- `gaudi2_arm_monitors_for_virt_msix_db()` uses `MON_PAY_DATA_0`, `MON_ARM_0`, and `MON_CONFIG_0` to build a three-monitor sequence that redirects LBW sync-object completions into HBW virtual MSI-X doorbell writes.
- `gaudi2_prepare_sm_for_virt_msix_db()` allocates specific reserved SOB and monitor IDs for decoder normal/abnormal interrupts, then delegates the actual programming to the monitor-arm helper.
- `gaudi2_init_sm()` programs reserved completion monitors by writing `MON_CONFIG` entries, then initializes global completion queue base/size registers outside this chunk.
- `gaudi2_arm_cq_monitor()` configures monitor payload and arm state for command-submission completion queue notifications.
- User sync-manager restore logic clears monitor status/config windows based on `first_available_user_mon`, `MON_CONFIG_0`, `MON_STATUS_0`, `SM_SEC_0`, and `DCORE_OFFSET`.
- Wait command-buffer generation computes offsets from a monitor MMIO base to `MON_PAY_DATA` and `MON_ARM`, so packet contents remain independent of absolute BAR placement.

The chunk also integrates with security and mmap policy indirectly. Sync-manager objects are part of the Gaudi2 block map and user-visible hardware resources, but this slice only supplies addresses; access control is enforced in driver setup, security register programming, context state clearing, and user block-mapping code elsewhere.

## Risks And Edge Cases

Register-map correctness is the central risk. A wrong address, missing index, duplicate macro, or broken 4-byte progression would route monitor writes to the wrong hardware register. Because driver code often uses `*_0 + mon_id * 4`, an incorrect base macro can corrupt every indexed access even when individual high-index defines look correct.

The chunk boundaries are easy to misread. `MON_PAY_DATA` starts before this chunk, while `MON_CONFIG` continues after it. Research or tooling that treats this chunk as a complete definition of either array would undercount or misclassify the hardware surface.

Monitor programming order matters in consumers. Payload address/data/config should be valid before `MON_ARM` is written; otherwise a monitor might fire with stale or partially configured state. The header cannot enforce that ordering.

Field width and index limits must match the masks and hardware topology. `MON_ARM_SID` is 8 bits and the local mask selects SOBs within a group, so helper code must keep SOB group and SOB mask derivation aligned with the sync-object layout. `MON_CONFIG_WR_NUM` has a small encoded width; callers such as the virtual MSI-X path rely on `"2"` meaning three writes.

Cross-DCORE reuse must preserve block stride. Code that adds `DCORE_OFFSET` assumes each DCORE sync-manager object block has an identical layout. Any per-DCORE generation drift would invalidate bulk reset/restore loops.

User-context cleanup is sensitive to first-available monitor/SOB boundaries. Clearing too little can leave stale user monitor state; clearing too much can disturb reserved completion, KDMA, decoder interrupt, or firmware-owned monitors.

Because the file is auto-generated and marked "DO NOT EDIT", hand edits are risky. The safer maintenance path is regenerating the register header from the authoritative hardware database and verifying consumers still compile.

## Test Signals

Useful validation signals include:

- Build coverage that includes Gaudi2 headers and verifies all consumed macros and mask names resolve.
- Static checks that `MON_PAY_DATA`, `MON_ARM`, and `MON_CONFIG` addresses are contiguous 4-byte arrays and align with documented counts of 2,048 monitors.
- Probe/init logs showing successful sync-manager initialization and no MMIO faults when programming reserved completion monitors.
- Command submissions completing through CQ monitors, including correct CS index payloads and no SOB timeout in completion paths.
- KDMA jobs completing through the reserved KDMA monitor after `MON_CONFIG` CQ enablement.
- Decoder normal/abnormal interrupts routed through virtual MSI-X doorbell monitor sequences, with the expected interrupt IDs written.
- Wait/fence command buffers completing under workloads that use monitor arm/payload programming.
- Context create/destroy or device-release tests showing user monitor state is cleared and protected without disturbing reserved monitor entries.
- Fault-injection or debug traces confirming monitor IDs near array boundaries, especially high `MON_PAY_DATA` indexes and later `MON_CONFIG` indexes, map to the expected MMIO addresses.

Failure signals include SOB or CQ completion timeouts, missing MSI-X interrupts after decoder/KDMA/completion events, repeated stale fence values, monitor writes to unexpected addresses, off-by-one behavior around monitor `2047`, and regressions after generated-register updates where `*_0 + id * 4` no longer matches the generated per-index macros.
