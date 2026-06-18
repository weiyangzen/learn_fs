<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/config.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/config.go

## Purpose

Implements `ipfs config` commands for reading, setting, showing, editing, replacing, and applying profile transforms to the repo config while protecting secrets.

## Important APIs, Types, and Functions

`ConfigCmd` handles key get/set with `--bool`, `--json`, and `--expand-auto`. `configShowCmd`, `configEditCmd`, `configReplaceCmd`, and `configProfileApplyCmd` are subcommands. Helpers include `matchesGlobPrefix`, `scrubValue`, `scrubOptionalValue`, `transformConfig`, `getConfigWithAutoExpand`, `setConfig`, `parseEditorCommand`, `replaceConfig`, and `getRemotePinningServices`.

## Control Flow

The main command blocks direct identity private-key and remote-pinning credential access, opens fsrepo, and either writes parsed JSON/bool/string values or reads config values with optional AutoConf expansion. `show` reads the config file, optionally expands auto placeholders through full config methods, scrubs identity, API auth, and pinning secrets, then emits JSON. `profile apply` clones config, applies a named transform, backs up and persists unless dry-run, and emits a scrubbed diff. `replace` decodes a whole config, preserves the existing private key, and refuses remote pinning service API changes or add/remove attempts.

## State and Persistence Behavior

Set operations call `SetConfigKey`; profile apply creates a backup and calls `SetConfig`; replace calls `SetConfig`. `edit` runs `$EDITOR` against the config file directly. Read/show/dry-run paths do not persist changes.

## Dependencies and Integration Points

Uses Kubo config model, profile registry, AutoConf expansion methods, repo/fsrepo, `jsondiff`, `go-shlex`, and command file helpers. Integrates with global `ConfigFileOption` and shared `configExpandAutoName`.

## Risks and Edge Cases

Secret scrubbing is security critical. `replace` must preserve existing secrets while refusing attempts to alter concealed remote-service API info. `$EDITOR` parsing must handle quoted paths and flags. `--expand-auto` is read-only and is rejected for writes.

## Test Signals

`config_test.go` covers scrub deletion behavior and editor parsing cases. Additional tests should cover secret access blocking, remote pinning replace constraints, AutoConf expansion, profile backup behavior, and JSON/bool type persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/config.go -->
