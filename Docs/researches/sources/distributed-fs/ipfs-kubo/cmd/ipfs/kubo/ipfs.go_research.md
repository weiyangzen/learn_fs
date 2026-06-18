# sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/ipfs.go

## Purpose
This file assembles the local CLI root command by combining daemon/init/local command overrides with the shared core command tree.

## Important APIs, Types, And Functions
`Root` starts with core root options/help. `commandsClientCmd` exposes local `ipfs commands`. `localCommands` maps `daemon`, `init`, and `commands`. `init` fills `Root.Subcommands` with local overrides plus all non-conflicting core commands.

## Control Flow
Package initialization avoids literal initialization loops by assigning subcommands in `init`.

## State And Persistence Behavior
It mutates the global command tree during process init.

## Dependencies And Integration Points
It integrates `core/commands` with the local-only CLI commands implemented in this package.

## Risks And Test Signals
Risks include subcommand collisions and initialization-order assumptions. Signal is `ipfs` exposing local daemon/init while still exposing normal core commands.
