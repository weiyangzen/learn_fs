<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/Rules.mk -->
# sources/distributed-fs/ipfs-kubo/plugin/plugins/Rules.mk

## Purpose

This Make fragment defines dynamic plugin build scaffolding for plugin packages.

## Important APIs, Types, and Functions

It tracks plugin package lists, generated `main/main.go` files, `.so` outputs, invokes `gen_main.sh`, runs `go fmt`, builds with `-buildmode=plugin` and a dynamic-link pkgdir, marks outputs executable, and wires cleanup/build targets.

## Control Flow, State, and Integration

When plugin packages are listed in `$($(d)_plugins)`, Make generates wrapper mains and builds `.so` artifacts. Current list is empty, so the rules are infrastructure.

## Dependencies, Risks, and Test Signals

Dependencies are GNU Make, Go plugin buildmode, GOPATH pkgdir, and `gen_main.sh`. Risks include Linux amd64-specific pkgdir, dynamic plugin ABI fragility, and generated wrapper cleanup. Dynamic plugin build jobs validate it when plugins are listed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/Rules.mk -->
