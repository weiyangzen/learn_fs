<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/walk_test.go -->
# sources/distributed-fs/beegfs-go/common/filesystem/walk_test.go

Purpose: tests lexicographic walking and resumable/glob path streaming.

Important APIs/types/functions: `TestWalkDirLexicographically` and `TestWalkSortedPathFileAndDirectory`.

Control flow: the first test creates a temp tree and a Badger-backed `MapStore` with matching keys, walks the tree, and compares walk order with expected order and Badger iterator order. The second builds a broader file set, then table-tests directory walks, glob patterns, single-file handling, resume tokens, max-path limits, and deep `**` behavior.

State and persistence: uses temporary directories and a temporary Badger database.

Dependencies and integration points: depends on `badger`, `kvstore`, `BeeGFS` provider, and `testify`. It explicitly validates the filesystem walker against the key order expected by `kvstore.MapStore`.

Risks: the test sorts expected paths with `slices.Sort` for streaming cases, which can hide ordering expectations if custom order differs from standard sort for directories. It does not cover filters, context cancellation, directory emission mode, or readDir error paths.

Test signals: strong coverage for common path streaming and resume/glob combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/walk_test.go -->
