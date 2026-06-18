
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/node/list.go

- Purpose: implements `node list` with optional NIC and reachability information.
- Important APIs: `newListCmd` and `runListCmd`.
- Control flow/state: obtains management client for display port, fetches nodes, sorts by type then numeric ID, builds NIC and reachable strings, prints selected columns, and optionally returns exit code 5 when any node is unreachable.
- Dependencies/integration: uses backend `GetNodes`, Viper debug mode, `cmdfmt`, global management config, network address parsing, and CTL error codes.
- Risks/tests: management NIC port display assumes gRPC listens on the same interfaces as BeeMsg; `hasUnreachableNode` marks nodes with no reachable NIC. No direct tests found.
