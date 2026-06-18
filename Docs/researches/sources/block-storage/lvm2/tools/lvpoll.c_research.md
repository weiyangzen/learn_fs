# File Research: sources/block-storage/lvm2/tools/lvpoll.c

## Purpose
Implements `lvpoll`, which waits for and monitors long-running LV operations such as pvmove, mirror conversion, and merges.

## Poll Function Sets
Defines `struct poll_functions` instances for:
- pvmove:
  - progress: `poll_mirror_progress`
  - metadata update: `pvmove_update_metadata`
  - finish: `pvmove_finish`
- convert:
  - progress: `poll_mirror_progress`
  - finish: `lvconvert_mirror_finish`
- snapshot merge:
  - progress: `poll_merge_progress`
  - finish: `lvconvert_merge_finish`
- thin merge:
  - progress: `poll_thin_merge_progress`
  - finish: `lvconvert_merge_finish`

## Main Flow
- `lvpoll()` requires `--polloperation`.
- Rejects negative `--interval`.
- Requires an LV name positional argument.
- `_poll_lv()`:
  - Converts path to display name.
  - Validates VG/LV name parameters.
  - Builds `daemon_parms` with interval, abort flag, progress display, and wait-before-testing behavior.
  - Chooses LV type and function table based on operation string.
  - Calls `wait_for_single_lv()`.

## Important Details
- `cmd->handles_missing_pvs` is controlled by `--handlemissingpvs`.
- `--interval +N` changes wait-before-testing behavior.
- Unknown poll operations are rejected as invalid command-line input.
