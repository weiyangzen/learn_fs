# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/chooser.go

Purpose: selects migration source/destination target or buddy group IDs for an entry during rebalancing/migration planning.

Important APIs/types/functions: errors `ErrEntryHasNoTargets` and `ErrEntryDetailsUnavailable`; `getRandomIDChooser`; `getMigrationForEntry`.

Control flow: `getMigrationForEntry` rejects entries without details or without stripe targets. It creates a lazy shuffled destination chooser, then branches on stripe pattern: buddy-mirror entries compare pattern IDs against source groups and choose replacement destination groups; RAID0 entries compare against source targets and choose replacement targets. IDs not in source sets are returned as unmodified. Insufficient destination IDs produce explanatory errors. The chooser avoids IDs already present in the original stripe pattern and returns each shuffled candidate once.

State and persistence: no persistence. The chooser closure keeps shuffled candidates, index, and in-use map for one migration decision.

Dependencies and integration points: uses BeeGFS stripe pattern types and BeeMsg `RebalanceIDType`. Consumed by entry migration workflows outside this file.

Risks: `math/rand/v2` default randomness makes destination choice nondeterministic, complicating reproducibility. The in-use map is initialized only once from the initial stripe pattern, not updated with IDs chosen earlier; uniqueness still comes from the shuffled index but it does not prevent choosing two destination IDs that were not in the original pattern when multiple sources are migrated. Unsupported stripe patterns fall through to invalid type behavior in the unseen tail and should be handled carefully.

Test signals: `chooser_test.go` covers missing details, empty targets, source/destination selection, insufficient destinations, buddy-vs-RAID behavior, and unmodified IDs.
