# File Research: sources/cow-pools/bcachefs-tools/fs/data/extent_update.c

Implements transaction-size guardrails for atomic extent insertion/update.

Key responsibilities:
- Counts how many alloc/EC/LRU/freespace/discard/reflink iterators an extent update may require.
- Handles direct extent/reflink-v keys and reflink-p indirection into the reflink btree.
- Enforces `EXTENT_ITERS_MAX` of 64.
- `bch2_extent_trim_atomic()` scans existing overlapping keys and whiteouts, estimates iterator requirements, and trims the inserted key’s back edge if the update would exceed the iterator limit.
- Emits `extent_trim_atomic` tracepoint when trimming occurs.

Important interactions:
- Prevents large extent updates from exceeding btree transaction iterator capacity.
- Uses extent pointer accounting from `extents.c` and btree update/interior helpers.

Notable concerns:
- Trimming changes the inserted key size, so callers must handle partial progress.
