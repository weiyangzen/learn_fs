# File Research: sources/block-storage/lvm2/tools/lvconvert_poll.h

This header declares the polling and merge-finalization helpers implemented in `lvconvert_poll.c` and used by `lvconvert.c`.

Declarations:
- Forward declarations for `cmd_context`, `logical_volume`, and `volume_group`.
- Includes `lib/lvmpolld/polldaemon.h` for `progress_t`, `daemon_parms`, and polling callback types.
- Declares:
  - `lvconvert_mirror_finish()`
  - `swap_lv_identifiers()`
  - `thin_merge_finish()`
  - `lvconvert_merge_finish()`
  - `poll_merge_progress()`
  - `poll_thin_merge_progress()`

Role:
- This is the small public interface between the main `lvconvert` command logic and its polling completion helpers.
- It intentionally exposes only conversion/merge finalization and progress callbacks, not the larger command-dispatch machinery.
