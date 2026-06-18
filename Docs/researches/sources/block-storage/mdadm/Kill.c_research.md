# File Research: sources/block-storage/mdadm/Kill.c

This file implements destructive metadata removal operations for mdadm: zeroing a component superblock and deleting a subarray from external container metadata.

Functions:
- `Kill()` opens a component device for write, guesses metadata if no `supertype` is supplied, loads the superblock, reinitializes an empty superblock through the metadata backend, and stores it back to the device.
- `Kill_subarray()` opens a container subarray, verifies that the metadata backend supports subarray deletion, rejects deletion while the subarray is active, calls the backend `kill_subarray()` method, and flushes/syncs metadata.

`Kill()` behavior:
- The function is intentionally simple and unsafe by its own comment: it “just zeroes out a superblock.”
- `force` disables exclusive open by setting `noexcl`.
- Return codes distinguish success, write failure, open failure, and unrecognized/no superblock.
- If the supertype was guessed locally, the function frees both backend superblock state and the allocated `supertype`.
- It sets `st->ignore_hw_compat = 1` before loading so metadata can be zeroed even when hardware compatibility checks would otherwise object.
- With `force`, load errors of at least `2` still allow zeroing by reinitializing/storing the metadata area.

`Kill_subarray()` behavior:
- The subarray must be inactive; `is_subarray_active()` blocks deletion of active members.
- `open_subarray()` fills a stack `struct supertype` for the target container/subarray.
- If mdmon is running for the container, metadata updates are queued through `st->update_tail`; otherwise the backend’s `sync_metadata()` is called directly.
- The function warns that UUIDs may have changed after successful deletion.
- Return values distinguish successful deletion, metadata sync failure, and lookup/resource/support failures.

Important implementation notes:
- Actual metadata layout knowledge is delegated to backend callbacks: `load_super`, `free_super`, `init_super`, `store_super`, `kill_subarray`, `sync_metadata`, and mdmon update flushing.
- `Kill.c` does not do policy checks beyond open/load/activity checks; callers must ensure the destructive operation is appropriate.
- The file is used by both `mdadm` and `mdmon` builds according to the project Makefile.
