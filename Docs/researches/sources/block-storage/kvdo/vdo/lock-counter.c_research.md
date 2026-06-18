# File Research: sources/block-storage/kvdo/vdo/lock-counter.c

Shared per-lock reference counter set for recovery journal, logical zones, and physical zones.

Key responsibilities:
- Allocates lock-counter arrays for journal, logical, and physical zone lock references.
- Tracks per-zone per-lock counters in `uint16_t` arrays, grouped by zone to reduce cache-line contention.
- Tracks aggregate logical/physical zone holder counts with `atomic_t` arrays.
- Tracks journal decrements from other zones with atomic decrement counts.
- Tests lock state for logical/physical zones, with journal locks blocking both.
- Initializes journal-zone lock counts.
- Acquires/releases logical and physical zone references.
- Releases journal-zone references from journal or other zones.
- Sends a completion notification when some lock may have become unlocked.
- Supports notification acknowledge, suspend, and resume.

Important behavior:
- Journal-zone lock state is `journal_value != journal_decrement_count`.
- Non-journal zone count increments only when a zone's local counter goes from 0 to 1, and decrements only when it goes from 1 to 0.
- Only one unlock notification can be in flight; state transitions use atomic compare-exchange.
- Suspended counters suppress new notifications until resumed.
- Several operations assert they run on the journal thread or not from the journal zone.

Dependencies:
- VDO completions, VDO thread callback IDs, memory allocation, atomics, barriers, assertions, and VDO zone types.

Notable risks:
- Local `uint16_t` counters are not atomic; correctness depends on zone/thread ownership.
- Notification is edge-style and coalesced; the owner must rescan locks and call `vdo_acknowledge_lock_unlock()`.
- `get_counter()` handles `VDO_ZONE_TYPE_JOURNAL` as a single-zone array but computes `locks * zone_id + lock_number`; journal callers pass zone 0.
