# sources/distributed-fs/ipfs-kubo/core/commands/log.go

## Purpose

`log.go` implements `ipfs log`, giving operators runtime control over go-log subsystem levels, subsystem discovery, and streaming daemon log output. It complements environment-variable logging configuration with RPC-visible commands.

## Important APIs, Types, and Functions

`LogCmd` exposes `level`, `ls`, and `tail`. `logLevelOutput` carries either a `Levels` map or a human message. Constants model the wildcard subsystem (`*`), convenient alias (`all`), current default keyword, default subsystem display key, and tail log-level option. The implementation uses `logging.SetLogLevel`, `logging.DefaultLevel`, `logging.SubsystemLevelNames`, `logging.SubsystemLevelName`, `logging.GetSubsystems`, and `logging.NewPipeReader`.

## Control Flow

`log level` parses optional subsystem and level arguments. The `all` alias is normalized to `*` for setting. When a level is supplied, `default` is resolved to the current default level and `SetLogLevel` mutates runtime state. Without a level, no subsystem returns only the default fallback, wildcard/all returns all configured subsystem levels with `(default)` substituted for the internal default key, and a named subsystem returns a single entry. The text encoder prints messages directly, then sorts map output. It shows subsystem names only for JSON/RPC-like calls or multi-entry output. `log ls` emits known subsystem names. `log tail` creates a pipe reader, optionally filtered by parsed level, closes it on request cancellation, and emits the reader as a streaming response.

## State and Persistence Behavior

Level changes are process-local runtime logging state and do not persist to config. `tail` holds a live pipe reader until cancellation. `ls` and level queries are read-only. There is no repo mutation.

## Dependencies and Integration Points

The command depends on `go-ipfs-cmds`, `go-log/v2`, and shared `stringList` formatting defined elsewhere in the commands package. It is `NoLocal` for `level`, reflecting daemon-side logging state, and integrates with RPC encodings where JSON consumers need structured subsystem names.

## Risks and Test Signals

Risks include ambiguity between default fallback and wildcard all-subsystem updates, shell escaping of `*`, and long-lived tail streams that must close when contexts cancel. Tests should cover `all`/`*` equivalence, `default` level reset semantics, querying no subsystem versus a single subsystem versus all subsystems, text encoder sorting and name suppression, invalid levels, tail log-level parse failures, and cancellation of pipe readers.
