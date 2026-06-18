# File Research: sources/cow-pools/bcachefs-tools/fs/journal/read.c

Journal read/recovery scanner: reads journal buckets across devices, deduplicates entries, validates replay windows, handles fast bucket search, missing entry checks, checksum reporting, rewind rereads, and replay start metadata.

Key responsibilities:
- Persists/resumes per-member journal position:
  - `bch2_journal_pos_from_member_info_set()` writes last journal bucket and offset to member info.
  - `bch2_journal_pos_from_member_info_resume()` restores device journal current index and free sectors.
- Formats journal pointers, pointer lists, entry datetime, and sequence datetime text for diagnostics.
- Validates journal checksums with `jset_csum_good()`.
- Frees or marks replay entries ignored through `journal_replay_free()`.
- Optionally strips overwrite/log entries from replay entries when recovery info retention, rewind, and journal scrub are not active.
- Maintains `struct journal_list`, a closure-coordinated shared read accumulator containing last needed sequence, lock, return code, and full-read mode.
- Adds read entries in `journal_entry_add()`:
  - Computes `last_seq`, adjusted for rewind.
  - Tracks oldest sequence found on disk.
  - Drops entries older than the needed range unless reading entire journal.
  - Establishes a base sequence for genradix indexing.
  - Drops no-longer-needed older entries when a newer flush entry advances `last_seq`.
  - Deduplicates same sequence across devices.
  - Tracks all physical pointers for a sequence.
  - Reports duplicate same-device and non-identical-replica fsck errors.
  - Keeps the good checksum copy when duplicates differ by checksum quality.
- Reads full journal buckets in `journal_read_bucket()`:
  - Reads bucket contents.
  - Walks entries until bucket end or empty/invalid boundary.
  - Handles checksum-error size distrust by advancing one block.
  - Updates per-device highest sequence, current index, sectors free, and bucket sequence.
  - Decrypts entry payload.
  - Adds entries to shared journal list.
- Implements large-journal fast scanning:
  - `journal_peek_bucket()` reads only the first block to get a candidate sequence.
  - `journal_anchor_bucket()` finds any non-empty bucket via bisect-stride descent.
  - `journal_bsearch_head()` binary-searches forward from an anchor to find write head.
  - `journal_walk_inuse()` walks backward from head through live buckets with strictly decreasing sequence numbers.
  - `journal_bsearch_collect()` combines fast path and fallback rebuild from all peeked buckets.
- Reads one device in `bch2_journal_read_device()`:
  - Allocates read buffer.
  - Uses fast header-peek path for journals larger than 32 buckets unless full read requested.
  - Reads live buckets sorted by descending sequence and stops after passing `last_seq`.
  - Checks monotonicity and records fsck count on irregular bucket sequence layout.
  - Falls back to full bucket reads when needed.
  - Sets device dirty/discard indices so reclaim can later reclaim unpinned buckets.
  - Releases device READ ref and closure.
- Prints checksum errors only for journal entries that will actually be used.
- Computes missing non-blacklisted ranges with `bch2_journal_entry_missing_range()`.
- Detects missing entries:
  - `journal_has_any_missing()` checks union of all device reads before deciding fast path missed data.
  - `journal_retry_full_read()` rereads all large journals fully when fast path produced gaps.
  - `bch2_journal_check_for_missing()` emits fsck errors with neighboring pointer diagnostics.
- Implements `bch2_journal_reread_for_rewind()`:
  - Finds oldest `last_seq` needed by rewind ranges.
  - Rereads buckets whose known max sequence could contain needed entries.
  - Un-ignores entries previously dropped as not dirty but now needed for rewind replay.
  - Updates `c->journal_replay_seq_start`.
- Implements `bch2_journal_read()`:
  - Launches per-device reads in parallel using closures.
  - Skips devices without journal data unless reading entire journal/fsck.
  - Marks journal degraded if a readable member cannot be referenced.
  - Finds `cur_seq`, `replay_end`, `last_seq`, and clean/empty state from newest usable flush entry.
  - Drops no-flush entries and torn final flush entry.
  - Handles dirty-but-no-journal after dropping nonflushes.
  - Applies journal rewind constraints and drop-before calculation.
  - Marks blacklisted entries ignored and reports unexpected blacklisted flush entries.
  - Retries full read if bsearch fast path left missing entries.
  - Validates missing sequence coverage.
  - Prints checksum errors, validates each replayed `jset`, builds journal replica device sets, and extracts rewind-limit/rewind entries.

Important interactions:
- Feeds `recovery.c` with populated `c->journal_entries` and `journal_start_info`.
- Uses blacklist helpers to ignore or skip blacklisted sequences.
- Uses validate code to check early and full `jset` structure.
- Uses allocator/replicas code to verify journal entry replication.
- Uses member device refs so journal reads are safe during startup.

Notable invariants:
- The union of all device journal reads must cover every non-blacklisted sequence in the replay window.
- New journal writes must start strictly after every on-disk entry, including no-flush entries that will be blacklisted.
- Fast bsearch is only an optimization; missing-range detection forces full reread before reporting gaps.
- Rewind cannot target entries older than the persisted rewind discard limit.
