# sources/distributed-fs/ipfs-kubo/core/commands/root.go

Purpose: defines the root `ipfs` command, global options, command help, shared online errors, and the map of all top-level command implementations.

Important APIs/types/functions: `Root` is the top-level `cmds.Command`. Global option constants include repo/config/debug/offline/API/auth options plus CID base, encoding, stream, and timeout options. `rootSubcommands` wires commands such as add, block, repo, stats, dht, routing, swarm, update, version, and shutdown. `init` calls `Root.ProcessHelp()` and assigns subcommands. `MessageOutput` is a shared simple message struct.

Control flow: command registration is static. The root command itself primarily exposes help and global options; actual behavior delegates to subcommands. `CommandsDaemonCmd = CommandsCmd(Root)` allows the daemon command tree to expose command listing.

State and persistence behavior: no state mutation in this file. Options here affect downstream repo selection, offline mode, API endpoint/auth, output encoding, and command timeout handling.

Dependencies and integration points: central integration point for all core command packages and subpackages (`dag`, `name`, `object`, `pin`). Shared errors `ErrNotOnline` and `ErrSelfUnsupported` are referenced by network/DHT commands.

Risks: any omission or key collision in `rootSubcommands` hides or replaces CLI functionality. Global option naming must remain stable for scripts and RPC clients.

Test signals: `root_test.go` calls `Root.DebugValidate()` to catch malformed command definitions, argument/option conflicts, and encoder/type mismatches.
