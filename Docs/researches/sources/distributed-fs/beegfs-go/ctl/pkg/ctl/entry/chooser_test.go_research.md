# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/chooser_test.go

Purpose: unit tests for entry migration target selection.

Important APIs/types/functions: tests around `getMigrationForEntry`, `ErrEntryDetailsUnavailable`, and `ErrEntryHasNoTargets`.

Control flow: table-driven cases construct `GetEntryCombinedInfo` with stripe pattern variants and source/destination sets, then verify returned rebalance type, source IDs, destination IDs, unmodified IDs, and expected errors. Tests account for random destination ordering by checking membership where appropriate.

State and persistence: no state; pure unit tests.

Dependencies and integration points: uses BeeGFS pattern types, BeeMsg rebalance ID types, and testify assertions.

Risks: random chooser behavior means tests should avoid relying on exact destination order unless constrained. Coverage should continue to include unsupported stripe pattern behavior and multi-source uniqueness.

Test signals: direct coverage of the most important chooser error and selection paths; it is the main safety net for migration planning logic in this subset.
