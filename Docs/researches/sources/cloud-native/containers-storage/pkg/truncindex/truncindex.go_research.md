# sources/cloud-native/containers-storage/pkg/truncindex/truncindex.go

Purpose: maintains an index of full string IDs that can be looked up by any unique prefix, used for Docker/container-style shortened IDs.

Important APIs/types/functions: errors `ErrEmptyPrefix`, `ErrIllegalChar`, `ErrNotExist`, and `ErrAmbiguousPrefix`; type `TruncIndex` with mutex, Patricia trie, and ID set; `NewTruncIndex`, `Add`, `Delete`, `Get`, and `Iterate`.

Control flow: construction silently ignores invalid/duplicate input IDs via `addID`. `Add` validates spaces/empty/duplicates, stores the ID in a map, and inserts into the trie. `Get` visits the prefix subtree, returns the sole match, returns `ErrAmbiguousPrefix` for multiple matches, and `ErrNotExist` for none. `Delete` requires exact ID membership. `Iterate` walks all trie entries under a write lock.

State/persistence: in-memory only. The trie and map are protected by `sync.RWMutex`.

Dependencies/integration: depends on `github.com/tchap/go-patricia/v2/patricia`. Used by storage indexes where human-facing IDs can be abbreviated.

Risks: `NewTruncIndex` silently drops invalid IDs, which can hide corrupt inputs. `Iterate` uses an exclusive lock and warns handlers not to call public methods, though the test demonstrates concurrent calls block rather than panic. Error for ambiguity reports the second visited prefix, not necessarily the queried prefix.

Test signals: tests cover add/get/delete, ambiguity, illegal/empty IDs, iteration, and benchmarks for add/get/delete/new combined workloads.
