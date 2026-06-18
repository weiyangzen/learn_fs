<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/config_test.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/config_test.go

## Purpose

Tests focused helper behavior for config scrubbing and `$EDITOR` command parsing.

## Important APIs, Types, and Functions

`TestScrubMapInternalDelete` exercises `scrubMapInternal`. `TestEditorParsing` table-tests `parseEditorCommand` with common editors, flags, quoted paths, and a malformed trailing backslash.

## Control Flow

The scrub test calls `scrubMapInternal(nil, nil, true)` and expects an empty non-nil map. Editor parsing subtests call the parser, branch on expected error, and compare argument slices element by element.

## State and Persistence Behavior

Pure unit tests. They do not open or mutate repo config.

## Dependencies and Integration Points

Coupled to `go-shlex` parsing semantics through `parseEditorCommand`.

## Risks and Edge Cases

The tests do not execute editors or validate config file edits. They cover POSIX-like parsing but not Windows shell quoting.

## Test Signals

Good signal for issue-prone `$EDITOR` values such as VS Code with `--wait`. Missing signal for the core config read/write/replace security paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/config_test.go -->
