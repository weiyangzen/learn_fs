# sources/control-plane/longhorn-engine/pkg/replica/revision_counter.go

Purpose: persists and caches a replica revision counter used to compare replica write freshness.

Important APIs/types/functions: constants define `revision.counter`, file mode, and 4096-byte block size. `readRevisionCounter`, `writeRevisionCounter`, `openRevisionFile`, `initRevisionCounter`, `IsRevCounterDisabled`, `GetRevisionCounter`, and `SetRevisionCounter` implement counter lifecycle. A package-level aligned buffer `revisionCounterBuf` is reused for direct IO writes.

Control flow: initialization creates or opens the counter file, writes zero if new, reads the current value into `revisionCache`, then launches a goroutine that consumes increment requests and writes `cache+1` to disk before atomically adding one. `WriteAt`/`UnmapAt` send requests and wait for an ack after data IO succeeds.

State and persistence: persists ASCII integer data in a direct-IO file padded with NULs. Caches the value in `atomic.Int64`. Uses channels on the `Replica` for request/ack coordination.

Dependencies and integration points: called during `Replica` construction and IO paths. Depends on sparse-tools direct IO and context cancellation.

Risks: package-level `revisionCounterBuf` is shared across replicas and goroutines, so concurrent `writeRevisionCounter` calls on different replicas can race. If `writeRevisionCounter` fails, the ack channel is closed; later send/receive behavior can panic or return zero values. The counter is intentionally not atomic with data writes and can overcount on failed data writes. `SetRevisionCounter` assumes no pending IO, enforced only by callers.

Test signals: no direct tests here in this subset. Revision counter persistence and concurrency are important untested risk areas.
