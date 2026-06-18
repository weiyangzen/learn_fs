<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/gen_main.sh -->
# sources/distributed-fs/ipfs-kubo/plugin/plugins/gen_main.sh

## Purpose

This helper generates a wrapper `main.go` for building a plugin package as a Go `.so` plugin.

## Important APIs, Types, and Functions

It requires output dir and package import path parameters, creates `<dir>/main`, writes a `package main` that imports the target package as `uniquepkgname`, exports `var Plugins = uniquepkgname.Plugins`, and defines a panic-only `main`.

## Control Flow, State, and Integration

The script writes generated source under the plugin package's `main` subdirectory. `plugin/plugins/Rules.mk` then formats and builds it with `-buildmode=plugin`.

## Dependencies, Risks, and Test Signals

Dependencies are bash and shell redirection. Risks include unescaped package paths, fixed alias collisions, and generated files left behind. Dynamic plugin build tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/gen_main.sh -->
