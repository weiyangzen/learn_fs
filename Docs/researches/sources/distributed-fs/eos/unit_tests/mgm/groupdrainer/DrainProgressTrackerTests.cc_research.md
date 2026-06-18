# sources/distributed-fs/eos/unit_tests/mgm/groupdrainer/DrainProgressTrackerTests.cc

## sources/distributed-fs/eos/unit_tests/mgm/groupdrainer/DrainProgressTrackerTests.cc

Purpose: tests `DrainProgressTracker`, an in-memory tracker for per-filesystem drain progress.

Important APIs and types: `DrainProgressTracker`, `setTotalFiles`, `increment`, `getTotalFiles`, `getFileCounter`, `getDrainStatus`, and `dropFsid`.

Control flow: `SetTotalFiles` verifies initial totals, increments, ignored decreases, accepted increases, and recomputed percentages. `Deletions` checks reset after `dropFsid`. `NullTests` and `InvalidFS` cover zero totals, missing fsids, and transitions from invalid to valid totals.

State and persistence: the tracker holds per-fsid counters and totals in memory. No persistent store or external MGM state is involved.

Dependencies and integration: used by group drainer logic to report drain completion percentage. Tests encode percentage semantics: a single increment against total 100 reports `1`, while counter equal to total reports `100`.

Risks and test signals: lowering totals is intentionally ignored to avoid regressions during evolving scans. This can overstate denominator size if production discovers fewer files later.
