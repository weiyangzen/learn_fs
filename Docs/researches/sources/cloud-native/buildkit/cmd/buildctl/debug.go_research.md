# Research: sources/cloud-native/buildkit/cmd/buildctl/debug.go

Purpose: defines the `buildctl debug` command namespace and registers all debug subcommands. It is a thin command tree assembly file.

Important APIs and flow: `debugCommand` names the group `debug`, sets usage text, and wires `dump-llb`, `dump-metadata`, `workers`, `info`, `monitor`, `logs`, `ctl`, `get`, and `histories` from `cmd/buildctl/debug`.

State and dependencies: no runtime state or persistence is owned here. It depends on the debug subpackage and urfave/cli command definitions.

Risks and test signals: the risk is primarily command registration drift; missing a subcommand here makes its implementation unreachable from the binary. It is covered only indirectly through CLI help/usage and any integration tests that call debug subcommands.
