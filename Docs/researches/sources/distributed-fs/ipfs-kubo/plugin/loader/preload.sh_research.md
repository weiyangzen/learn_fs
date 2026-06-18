<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/loader/preload.sh -->
# sources/distributed-fs/ipfs-kubo/plugin/loader/preload.sh

## Purpose

This shell script regenerates `plugin/loader/preload.go` from a fixed list of built-in plugin import paths.

## Important APIs, Types, and Functions

It defines a `plugins` list, writes package/import boilerplate to `preload.go`, emits one `Preload(alias.Plugins...)` line per plugin, then runs `go fmt`.

## Control Flow, State, and Integration

The script overwrites `preload.go` in the current directory. It is a build-maintenance tool, not runtime code.

## Dependencies, Risks, and Test Signals

Dependencies are bash, redirection, and `go fmt`. Risks include alias generation mistakes, running from the wrong directory, and plugin list drift relative to `plugin/plugins/Rules.mk`. A clean generated diff and successful build validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/loader/preload.sh -->
