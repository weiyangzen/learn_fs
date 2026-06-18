# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/fast_list.h

This header defines `struct fast_list` and its public API.

Key structures:
- `struct fast_list`:
  - `GENRADIX(void *) items`
  - `ida slots_allocated`
  - per-CPU slot buffer

Iteration:
- `fast_list_iter_peek()` skips empty radix slots.
- `fast_list_for_each_from()` iterates from a starting index.
- `fast_list_for_each()` iterates from zero.

Mutation/API:
- `fast_list_set()` stores an item at an existing slot.
- `fast_list_get_idx()`
- `fast_list_put_idx()`
- `fast_list_add()`
- `fast_list_remove()`
- `fast_list_exit()`
- `fast_list_init()`

Important behavior:
- Iteration skips NULL entries.
- Callers can reserve slots early with `fast_list_get_idx()` to handle allocation failure before entering non-failing contexts.

Research notes:
- The header is intentionally small; most policy is in `fast_list.c`.
