# File Research: sources/block-storage/lvm2/tools/lvresize.c

## Purpose
Implements shared logic for `lvextend`, `lvreduce`, and `lvresize` generated command variants.

## Parameter Construction
`_lvresize_params()` initializes `struct lvresize_params` based on `cmd->command->command_enum`:
- Policy extension.
- Pool metadata extension/resize.
- PV-based extension.
- Size/extents-based extend/reduce/resize.
- Sets resize direction, percent mode, sign, pool metadata size, and whether filesystem options apply.

## Filesystem Options
When filesystem handling applies:
- Rejects simultaneous `--resizefs` and `--fs`.
- With blkid fs info support:
  - accepts `--fs checksize`, `resize`, `resize_fsadm`, `ignore`
  - defaults to `checksize`
  - maps `--resizefs` to `--fs resize`
- Without blkid fs info:
  - maps supported resize modes to `resize_fsadm`
  - warns for unsupported `ignore`
- Handles `--nofsck`.
- Rejects `--fsmode` with `resize_fsadm`.
- Accepts `--fsmode nochange`, `offline`, or `manage`, defaulting to `manage`.

## Size/Allocation Options
- Accepts either size or extents, not both.
- Handles pool metadata size and sign.
- Parses allocation policy, yes, force, nosync.
- Handles `--type linear` as striped with an `only_linear` guard.
- Validates mirrors, stripes, and stripe size signs.
- Ignores type/stripe/mirror arguments for reductions with a notice.

## Policy Extension
`_lv_extend_policy()`:
- Supports snapshot COW, thin pool, and VDO pool volumes.
- Requires active volume/layer.
- Computes data and metadata extension percentages from policy settings.
- Skips if no extension is needed.
- Calls `lv_resize()` with policy percentages.

## Command Entry Points
- `lvextend_policy_cmd()`:
  - Builds params.
  - Processes exactly the selected LV with `_lvextend_policy_single()`.
- `lvresize_cmd()`:
  - Builds params.
  - Processes selected LV with `_lvresize_single()`.
  - Retries once if VG changed during filesystem resize.
  - Performs deferred `lockd_lv_refresh()` when needed.
- `lvresize()`:
  - Fails with internal error if a command definition is missing a specific function.

## Important Details
- PV lists after the first LV positional arg are passed to `create_pv_list()`.
- Successful resize is printed when `lv_resize()` succeeds or when filesystem extension reported a special error state.
- Retry logic exists specifically because filesystem resize may unlock VG and allow concurrent VG changes.
