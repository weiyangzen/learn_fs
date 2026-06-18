# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_sync_mngr_objs_regs.h lines 36257-43543

## Scope

This chunk is the tail of the auto-generated Gaudi2 `DCORE0_SYNC_MNGR_OBJS` register-address header. It covers four contiguous register families for DCORE0 sync-manager objects:

- `mmDCORE0_SYNC_MNGR_OBJS_MON_CONFIG_1733` through `_2047`, addresses `0x4111B14` to `0x4111FFC`.
- `mmDCORE0_SYNC_MNGR_OBJS_MON_STATUS_0` through `_2047`, addresses `0x4112000` to `0x4113FFC`.
- `mmDCORE0_SYNC_MNGR_OBJS_SM_SEC_0` through `_639`, addresses `0x4114000` to `0x41149FC`.
- `mmDCORE0_SYNC_MNGR_OBJS_SM_PRIV_0` through `_639`, addresses `0x4115000` to `0x41159FC`.

The file is generated hardware-description data, not hand-written control logic. The address pattern is a dense 32-bit register table with 4-byte spacing between indexed entries. The chunk ends the header with `#endif /* ASIC_REG_DCORE0_SYNC_MNGR_OBJS_REGS_H_ */`.

## Purpose

The register aliases let Gaudi2 driver code program and inspect DCORE0 sync-manager monitor state without embedding numeric MMIO offsets in C logic. Sync-manager objects are used by the driver and hardware command streams for SOB/monitor based synchronization, completion-queue notification, low-bandwidth writes, and privilege/security partitioning of sync objects.

Within this chunk, the monitor config tail completes the 2048 monitor configuration register space started earlier in the file. The monitor status table provides one status register per monitor. The secure and privileged tables provide 640 per-object permission words that mark sync-manager objects as secure and/or privileged from the hardware access-control point of view.

## Important APIs, Types, And Macros

This chunk defines only preprocessor constants:

- `mmDCORE0_SYNC_MNGR_OBJS_MON_CONFIG_n`: monitor configuration registers. The driver combines these addresses with masks from `dcore0_sync_mngr_objs_masks.h`, including `DCORE0_SYNC_MNGR_OBJS_MON_CONFIG_CQ_EN_MASK`, `LBW_EN_MASK`, `WR_NUM_MASK`, `MSB_SID_MASK`, and long-SOB fields.
- `mmDCORE0_SYNC_MNGR_OBJS_MON_STATUS_n`: monitor runtime status registers. Related masks include `VALID`, `PENDING`, `PROT`, and `PRIV` fields.
- `mmDCORE0_SYNC_MNGR_OBJS_SM_SEC_n`: secure permission metadata for sync-manager objects.
- `mmDCORE0_SYNC_MNGR_OBJS_SM_PRIV_n`: privileged permission metadata for sync-manager objects.

There are no functions, structs, enums, or storage definitions in this range. The public contract is the macro name-to-address mapping consumed by `RREG32()`, `WREG32()`, `gaudi2_memset_device_lbw()`, and packet-generation code elsewhere in the Habana Labs driver.

## Control Flow

The header itself has no runtime control flow. Its constants are pulled into Gaudi2 control paths by inclusion:

- Context/reset cleanup uses `mmDCORE0_SYNC_MNGR_OBJS_MON_STATUS_0`, `mmDCORE0_SYNC_MNGR_OBJS_MON_CONFIG_0`, and `mmDCORE0_SYNC_MNGR_OBJS_SM_SEC_0` as range anchors in `gaudi2_restore_user_sm_registers()`. The function computes an offset from `first_available_user_mon[0]`, sets user monitor statuses to the monitor `PROT` value, clears monitor configs, and repeats the same operation for other DCOREs by adding `DCORE_OFFSET`.
- Monitor programming paths write config entries as `mmDCORE0_SYNC_MNGR_OBJS_MON_CONFIG_0 + 4 * monitor_id`, using bit masks to enable CQ or LBW behavior and to describe write count and SOB selection.
- Diagnostic and protection paths derive the monitor-status count and block sizes from endpoint macros such as `mmDCORE0_SYNC_MNGR_OBJS_MON_STATUS_2047` and `mmDCORE0_SYNC_MNGR_OBJS_SM_SEC_0`, so the dense 4-byte layout is part of the driver ABI with the generated header.

## State And Persistence Behavior

These macros do not store state in host memory. They identify device MMIO registers whose values persist in Gaudi2 hardware until reset or explicit driver/firmware reprogramming.

Runtime state represented by the address ranges includes:

- Monitor configuration state: whether a monitor sends CQ completions, performs LBW writes, uses long SOB IDs, and how many payload writes are associated with the monitor.
- Monitor status state: valid/pending/protection/privilege bits for each of 2048 monitor slots.
- Secure and privileged access metadata for 640 sync-manager objects.

The state is reset-sensitive and context-sensitive. `gaudi2_restore_user_sm_registers()` deliberately clears user-accessible monitor configuration and re-protects user monitor status during context initialization or release/reset cleanup. Firmware and command submissions can also alter monitor and permission state as part of normal accelerator operation.

## Dependencies And Integration Points

This generated register map depends on the Gaudi2 ASIC register database and must match the hardware layout exactly. It is paired with `dcore0_sync_mngr_objs_masks.h`, which supplies field shifts and masks for the addresses declared here.

Important consumers include:

- `gaudi2.c` monitor setup and command-buffer generation, where monitor config/status registers are used for SOB wait/signal, CQ notification, fences, and LBW payload delivery.
- `gaudi2_restore_user_sm_registers()`, which uses this chunk's monitor status/config and `SM_SEC` boundary macros to compute reset ranges.
- `gaudi2P.h`, which derives monitor counts and sync-manager object block sizes from the first/last register macros.
- Generic Habana Labs MMIO helpers such as `RREG32`, `WREG32`, and LBW memset helpers, which turn these offsets into device register accesses through the PCI BAR/register window.

The file is under a Ceph client source snapshot path, but this content is not Ceph filesystem code. It is Linux kernel accelerator-driver hardware description for Intel/Habana Gaudi2.

## Risks And Edge Cases

The main risk is address drift. Because driver code performs arithmetic from the first macro in each family, a wrong base address, missing index, or unexpected stride would redirect bulk MMIO operations to the wrong hardware registers. This is especially important for ranges that use `SM_SEC_0` as an end boundary for monitor status/config cleanup.

The chunk starts at `MON_CONFIG_1733`, not at the start of the monitor config family. Chunk-level analysis must therefore treat this as a continuation of the earlier `MON_CONFIG_0..1732` range rather than as a separate partial device feature. The full monitor config family is 2048 entries, and this slice only contains the final 315.

Bulk operations assume all indexed entries are 32-bit and densely spaced by 4 bytes. Any future hardware generation with holes, wider registers, or nonuniform security-table layout cannot reuse these arithmetic patterns without changing the generated headers and the C logic that computes ranges.

Permission tables are security-sensitive. Incorrect `SM_SEC` or `SM_PRIV` addresses could accidentally leave sync objects writable by unprivileged contexts or mark legitimate user monitors as protected/private, causing failures in command submission, waits, completion signaling, or firmware security checks.

The monitor status reset path writes the `PROT` bit across a computed range. If `first_available_user_mon[0]` is misconfigured, the driver may either fail to reset user monitors or touch reserved/kernel monitors. The risk is compounded because later DCOREs are addressed by adding `DCORE_OFFSET` rather than by using separate generated headers for each DCORE.

## Test Signals

Useful validation signals include:

- Build coverage that includes this header through Gaudi2 driver compilation, catching missing or renamed generated macros.
- Register-map sanity checks showing `MON_STATUS_2047 - MON_STATUS_0 + 4` equals `2048 * 4`, `SM_SEC_639 - SM_SEC_0 + 4` equals `640 * 4`, and `SM_PRIV_639 - SM_PRIV_0 + 4` equals `640 * 4`.
- Context creation/release paths complete without monitor-reset MMIO faults and leave user monitor statuses protected while monitor configs are zeroed.
- Generated wait/signal command buffers correctly program monitor config entries for CQ and LBW completions and observe expected SOB/monitor completion behavior.
- Security tests confirm privileged and secure sync-manager objects are inaccessible from user contexts while allowed user sync objects remain usable.
- Fault-injection or debug traces show monitor status `VALID`, `PENDING`, `PROT`, and `PRIV` bits changing consistently with armed monitor activity and cleanup.
