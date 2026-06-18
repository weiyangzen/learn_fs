<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cmd/networkdb-test/dbserver/ndbServer.go -->
# sources/cloud-native/moby/daemon/libnetwork/cmd/networkdb-test/dbserver/ndbServer.go

## Purpose
Runs a networkdb test node with an embedded diagnostic HTTP server. It binds networkdb to the task's `eth0` IPv4 address, exposes built-in networkdb diagnostics, and registers dummy-client watch endpoints.

## Important APIs, Types, And Functions
`Server(args []string)` is the entry point. It reads `TASK_ID`, resolves `eth0` via `getIPInterface`, initializes `networkdb.DefaultConfig`, creates `networkdb.New`, registers handlers with `diagnostic.New`, and starts `server.Enable`. `/myip` is handled by `ipaddress`.

## Control Flow
Startup parses the port, validates the task ID environment, finds the container IP, creates the networkdb instance, registers diagnostics, starts the HTTP server on the requested port, then blocks forever with `select {}`.

## State And Persistence
Package globals hold the networkdb instance, diagnostic server, and selected IP. Networkdb itself owns gossip/table state; this file does not persist local files.

## Dependencies And Integration Points
Depends on Docker/Swarm task environment, an up `eth0` with IPv4, `networkdb`, diagnostic server, and dummy-client handlers. It is launched by `testMain.go` in the `networkdb-test` command image.

## Risks And Edge Cases
Port parsing ignores conversion errors and can silently use port zero. The server requires interface name `eth0`, so nonstandard container networking breaks startup. Binding with empty IP in `server.Enable("", port)` listens broadly, which is suitable for test containers but not hardened diagnostics.

## Test Signals
Useful signals are successful `/ready`, `/myip`, networkdb diagnostic responses, and client workloads converging without fatal logs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cmd/networkdb-test/dbserver/ndbServer.go -->
