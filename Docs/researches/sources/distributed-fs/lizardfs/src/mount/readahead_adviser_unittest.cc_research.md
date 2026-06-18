## sources/distributed-fs/lizardfs/src/mount/readahead_adviser_unittest.cc

Purpose: GoogleTest coverage for `ReadaheadAdviser` behavior under sequential, holey, overlapping, and mixed read streams.

Important tests: `ReadSequential` asserts the window never shrinks for contiguous 64 KiB reads. `ReadHoles` and `ReadOverlapping` verify the window does not grow after enough nonmatching requests. `ReadSequentialThenHolesThenSequential` checks reduction during random-looking reads and renewed expansion when sequentiality resumes.

Dependencies and integration: includes only gtest and the adviser header, so tests are cheap and isolated.

Risks and gaps: tests assert monotonic directions but not exact window sizes, timeout-zero behavior, throughput-based max-window adjustment, random threshold boundary, or history expiry. They also do not address the apparent timestamp unit naming mismatch.
