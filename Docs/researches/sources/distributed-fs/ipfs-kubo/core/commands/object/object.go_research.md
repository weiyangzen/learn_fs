# sources/distributed-fs/ipfs-kubo/core/commands/object/object.go

## Purpose

`object/object.go` defines the deprecated `ipfs object` command tree for legacy dag-pb plumbing commands. Most subcommands are now removed and point users to `ipfs dag` or `ipfs files`.

## Important APIs, Types, and Functions

The file defines legacy output structs `Link` and `Object`, the unused/general `ErrDataEncoding`, `ObjectCmd`, and `RemovedObjectCmd`. `ObjectCmd` registers `diff` and `patch` as remaining deprecated subcommands while `data`, `get`, `links`, `new`, `put`, and `stat` route to `RemovedObjectCmd`.

## Control Flow

Invoking a removed subcommand returns `errors.New("removed, use 'ipfs dag' or 'ipfs files' instead")`. `ObjectCmd` itself has no run logic; behavior is delegated to subcommands.

## State and Persistence Behavior

Removed commands perform no repo or DAG mutation. `diff` is read-only; `patch` creates new DAG objects through its own file. This file itself only wires command state.

## Dependencies and Integration Points

Dependencies are minimal: Go `errors` and `go-ipfs-cmds`. It integrates with `object/diff.go` and `object/patch.go` and preserves command names for compatibility and deprecation messaging.

## Risks and Test Signals

Risks are compatibility and documentation-related: removed commands should fail consistently while deprecated commands remain accessible. Tests should assert command statuses, subcommand routing, removed command error text, and that object output struct JSON shapes remain compatible for `patch` results.
