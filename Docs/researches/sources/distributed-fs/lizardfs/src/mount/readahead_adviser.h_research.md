## sources/distributed-fs/lizardfs/src/mount/readahead_adviser.h

Purpose: header-only adaptive read-ahead predictor for the mount read path.

Important APIs/types: `ReadaheadAdviser::feed(offset, size)` observes original FUSE reads; `window()` returns the suggested extra read size. `HistoryEntry` stores timestamp and request size. Constants define initial window, default max, random threshold, history lifespan/capacity, and validity threshold.

Control flow: zero timeout disables read-ahead. Sequential reads matching `current_offset_` reset random-candidate count and expand the window. Nonmatching reads increment random candidates; once enough random candidates accumulate, the window is reduced and the current offset resets. Recent history estimates throughput and caps max window to roughly twice the observed throughput times timeout.

State and dependencies: maintains current offset, current/max window, random counter, ring-buffered recent request sizes, total requested bytes, and a timer. Used per `readrec` in `readdata.cc`.

Risks and tests: history lifespan constant is named `_ns` but uses `Timer::elapsed_us`, so units deserve review. Overlapping or holey sequential-ish reads can reduce read-ahead. Unit tests in `readahead_adviser_unittest.cc` cover monotonic expansion and reduction patterns.
