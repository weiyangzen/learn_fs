# sources/distributed-fs/beegfs-go/common/logger/badgerlog.go

Purpose: bridges BadgerDB logging to the repository's zap-based logging system. Badger expects an interface with `Errorf`, `Warningf`, `Infof`, and `Debugf`; this type adapts those formatted calls to zap levels.

Important APIs are `BadgerLoggerBridge`, `NewBadgerLoggerBridge(subComponent string, logger *zap.Logger)`, and the four level methods. The constructor adds a `database=<subComponent>` field so Badger messages can be attributed to a logical database.

Control flow is direct: each Badger callback trims a trailing newline from the format string, calls `fmt.Sprintf`, and emits one zap message at the corresponding level. There is no buffering, persistence, or retry behavior in the bridge itself.

State is limited to the wrapped `*zap.Logger`. Dependencies are `fmt`, `strings`, and `go.uber.org/zap`. Integration points are Badger's `Logger` interface and any package that wants Badger logs to share application logging configuration.

Risks: formatting every message eagerly can be expensive if Badger debug logs are high volume. Format-string mismatches are not type checked. The bridge assumes newline trimming is enough to normalize Badger messages.

Test signals: no direct test in this subset, but it is exercised indirectly wherever `MapStore` configures Badger logging.
