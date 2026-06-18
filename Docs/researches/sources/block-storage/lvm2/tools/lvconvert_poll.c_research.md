# File Research: sources/block-storage/lvm2/tools/lvconvert_poll.c

This file contains helper routines used by `lvconvert.c` polling and merge completion. It is separated from the large command file but still implements core finalization behavior for mirror conversion and snapshot/thin merge.

Main functions:
- `lvconvert_mirror_finish()` finishes mirror conversion polling. If the LV still has `CONVERTING`, it collapses the temporary mirrored sync layer with `collapse_mirrored_lv()`, clears `CONVERTING`, reloads metadata with `lv_update_and_reload()`, and reports completion.
- `swap_lv_identifiers()` swaps two logical volumes’ identifiers, allocation policy, read-ahead, profile, major/minor numbers, timestamps, hostnames, tags, and names. It uses a temporary rename to `pvmove_tmeta` to avoid name collision, then completes the name swap.
- `thin_merge_finish()` uses `swap_lv_identifiers()` so the merge result takes the intended identity, preserves status, and removes the old merge LV with `lv_remove_single()`.
- `lvconvert_merge_finish()` finalizes snapshot merge polling. For thin snapshots it clears snapshot merge state and calls `thin_merge_finish()`. For classic snapshots it removes the COW LV merged into the origin.
- `poll_merge_progress()` reports classic snapshot merge progress. It treats no-longer-merging origins as complete, checks snapshot percent, handles invalidated/failed merge values, and displays `100 - percent` as progress.
- `poll_thin_merge_progress()` checks thin snapshot merge completion by comparing device IDs and returns finished after a single successful check because thin snapshot merge is immediate from this polling perspective.

Important behavior:
- The code assumes the caller has selected the right poll function set for mirror conversion, classic merge, or thin merge.
- `swap_lv_identifiers()` is a powerful metadata mutation helper used by conversion paths; it swaps more than UUID/name and includes tags and persistent device numbers.
- Thin merge completion removes the previous origin after swapping identities, while classic merge completion removes the COW snapshot.
