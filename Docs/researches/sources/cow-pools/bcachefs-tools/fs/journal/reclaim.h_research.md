# File Research: sources/cow-pools/bcachefs-tools/fs/journal/reclaim.h

This header exports journal reclaim, space accounting, pin management, discard, and diagnostics APIs.

Key responsibilities:
- Defines `JOURNAL_PIN`.
- Provides `journal_reclaim_kick()`, which marks reclaim kicked and wakes the reclaim thread.
- Declares space accounting APIs:
  - `bch2_journal_dev_buckets_available()`
  - `bch2_journal_set_watermark()`
  - `bch2_journal_space_available()`
- Initializes pin list entries with `journal_pin_list_init()`.
- Provides pin helpers:
  - `journal_pin_active()`
  - `journal_seq_pin()`
  - `__bch2_journal_pin_put()`
  - `bch2_journal_pin_add()`
  - `bch2_journal_pin_update()`
- Defines `replicas_entry_refs` and a preallocated darray type used when releasing journal replica refs.
- Declares reclaim thread start/stop, direct reclaim, pin flush, device pin flush, discard, and text diagnostic functions.

Important invariants:
- `journal_seq_pin()` asserts the requested sequence is inside the pin FIFO range.
- Pin add only moves a pin to an older sequence if inactive or currently newer.
- Pin update only moves a pin to a newer sequence if inactive or currently older.
- `journal_pin_list_init()` resets unflushed/flushed lists, count, unreplayed state, replica-device count, and byte accounting.

Dependencies:
- Requires `struct journal`, `struct journal_device`, `struct journal_entry_pin_list`, `struct journal_entry_pin`, and journal type definitions from surrounding journal headers.

Research notes:
- The inline helpers encode the public semantics for pin movement and are used by hot btree and key-cache paths.
