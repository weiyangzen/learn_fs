# sources/cloud-native/moby/hack/dockerfile/install/install.sh

## Purpose
Generic installer dispatcher used by Dockerfile build stages.

## Important APIs and Types
Uses `PREFIX`, optional `TMP_GOPATH`, computed `GO_BUILDMODE`, and sourced `<bin>.installer` files that define `install_<bin>`.

## Control Flow, State, and Persistence
The script creates a temporary GOPATH unless provided, chooses PIE build mode except on mips and ppc64, resolves the installer directory, shifts the binary name argument, sources the matching installer, and calls its install function with remaining arguments.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on Go, installer files in the same directory, and shell sourcing. It writes installed binaries under `PREFIX` by convention and may create temporary GOPATH state. Risks include missing installer files, function-name injection from `bin`, unremoved temp GOPATH in this snippet, and architecture buildmode mismatches. Dockerfile build jobs validate it.
