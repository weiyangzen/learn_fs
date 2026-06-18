<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/system/system.go -->
## sources/cloud-native/nydus-snapshotter/pkg/system/system.go

Purpose: implements the experimental Unix-socket HTTP system controller for snapshotter maintenance: daemon listing, backend inspection, prefetch configuration, and rolling nydusd hot upgrade.

Important APIs/types: endpoint constants, `Controller`, `upgradeRequest`, JSON error helpers, `daemonInfo`, `rafsInstanceInfo`, `NewSystemController`, `Run`, route handlers (`getBackend`, `setPrefetchConfiguration`, `describeDaemons`, `getDaemonRecords`, `upgradeDaemons`), `upgradeNydusDaemon`, `buildNextAPISocket`, and `upgradeNydusdWithSymlink`.

Control flow and state: construction removes any stale socket, resolves a Unix address, and registers Gorilla mux routes. `Run` listens on the Unix socket, chowns it, and closes on signal. `describeDaemons` walks managers and live daemons, collecting RAFS instances, RSS, fs read metrics, references, sockets, and supervisor paths. Upgrade locks each manager, starts a new daemon with `--upgrade`, asks the supervisor to send state, waits for INIT/READY, calls takeover/start APIs, unsubscribes/exits old daemon, subscribes the new daemon, updates manager state, and finally atomically replaces the configured nydusd binary path with a symlink to the requested source.

Dependencies/integration: depends on filesystem, manager, daemon APIs, metrics, prefetch, signals, and mux. It is started from `snapshot.NewSnapshotter` when system controller config is enabled.

Risks and test signals: `jsonResponse` writes status before setting content type. `getDaemonRecords` is unimplemented. `upgradeDaemons` defers manager unlock inside a loop, so multiple managers stay locked until handler return. `SubscribeDaemonEvent` error handling returns `json.InvalidUnmarshalError{}` rather than wrapping the actual error. Tests only cover socket name incrementation.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/system/system.go -->
