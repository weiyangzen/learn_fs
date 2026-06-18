<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cmd/networkdb-test/dummyclient/dummyClient.go -->
# sources/cloud-native/moby/daemon/libnetwork/cmd/networkdb-test/dummyclient/dummyClient.go

## Purpose
Adds lightweight client-side table-watch diagnostics to a networkdb test server. It lets tests watch a table and later compare the locally observed watch state against networkdb server state.

## Important APIs, Types, And Functions
`RegisterDiagnosticHandlers` registers `/watchtable` and `/watchedtableentries`. `watchTable` starts `nDB.Watch(tableName, "")` and records a `tableHandler`. `watchTableEntries` renders the currently observed entries. `handleTableEvents` consumes `networkdb.WatchEvent` values from a `go-events` channel.

## Control Flow
`/watchtable` validates `tname`, returns `OK` if already watched, otherwise starts a watcher goroutine. The goroutine loops until `ch.Done()` or an event arrives, adding entries when `Value` is non-nil and deleting on tombstone events. `/watchedtableentries` dumps the in-memory map size and entries.

## State And Persistence
`clientWatchTable` is a package-global map from table name to watched state. It is in-memory only and is reset when the server process exits.

## Dependencies And Integration Points
Integrates with `networkdb.Watch`, `diagnostic.HTTPReply`, and the test client parser for `total elements`. It intentionally mirrors networkdb table changes from the consumer side.

## Risks And Edge Cases
`clientWatchTable` and nested entry maps are accessed from HTTP handlers and watcher goroutines without locking, creating data-race risk under concurrent calls. The `cancelWatch` function is stored but never exposed or called. A non-`WatchEvent` is fatal, which is fine for tests but abruptly exits the server.

## Test Signals
The main signal is `/watchedtableentries?tname=...` returning the expected entry count after write/delete workloads. Race detector runs would be valuable because of unsynchronized global state.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cmd/networkdb-test/dummyclient/dummyClient.go -->
