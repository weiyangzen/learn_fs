# File Research: sources/block-storage/lvm2/lib/metadata/writecache_manip.c

This file implements writecache identity checks, kernel status reads, clean checks, detach workflows, cleaner setting, and settings serialization.

Main entry points:
- Identification: `lv_is_writecache_origin()`, `lv_is_writecache_cachevol()`.
- Clean/status: `lv_writecache_is_clean()`.
- Detach: `lv_detach_writecache_cachevol()`.
- Cleaner: `lv_writecache_set_cleaner()`.
- Serialization: `writecache_settings_to_str_list()`.

Control flow:
- `_get_writecache_kernel_status()` creates a temporary pool, calls `lv_info_with_seg_status()`, validates `SEG_STATUS_WRITECACHE`, and copies error/total/free/writeback block fields.
- Inactive detach path:
  - Validates writecache segment, finds fast cachevol and origin.
  - Temporarily activates the LV unless `noflush`, sends `flush`, reads kernel error, deactivates, disconnects cachevol/origin layers, removes hidden origin LV, makes cachevol visible, renames it, then writes/commits the VG.
- Active detach path:
  - Optionally sends `flush_on_suspend`.
  - Removes writecache links in metadata, writes precommit metadata, obtains old committed LV, suspends using old mapping, checks old kernel error, commits, resumes new mapping, deactivates old cachevol and old origin layer, removes hidden origin, makes cachevol visible, and writes/commits again.
- `_rename_detached_cvol()` tries to drop `_cvol` suffix or generates `lvol%d`.

Dependencies:
- Activation/suspend/resume, VG write/commit/revert, LV layer removal, LV remove/deactivate, writecache target messaging, and DM status parsing.

Correctness notes:
- `WRITECACHE_ORIGIN` is used as a fallback identity marker after links have already been destroyed.
- Active detach deliberately consults `lv_committed(lv)` because the kernel still contains the old mapping after metadata mutation and before commit/resume.
- Kernel error status after flushing is treated as detach failure.

Risks:
- Active detach has tight ordering requirements across metadata write, suspend, kernel error read, commit, resume, and cleanup.
- `noflush` skips safety flushing, so callers must understand possible dirty cache data implications.
