# sources/distributed-fs/ipfs-kubo/bin/Rules.mk

## Purpose
This Make fragment defines helper binaries and path setup for the `bin` directory.

## Important APIs, Types, And Functions
It sets a distribution root, adds `bin` to `PATH`, creates a `bin/protoc` wrapper/symlink target, builds `bin/protoc-gen-gogofaster` via Go, and appends generated files to `CLEAN`/`DISTCLEAN`.

## Control Flow
Included from root `Rules.mk`, it participates in the shared Make target accumulator pattern using `mk/header.mk` and `mk/footer.mk`.

## State And Persistence Behavior
It creates local helper binaries/symlinks under `bin` and temporary distribution cache under `bin/tmp`.

## Dependencies And Integration Points
It integrates Make utility macros, Windows-specific copy behavior, Go build of `github.com/gogo/protobuf/protoc-gen-gogofaster`, and protobuf generation targets.

## Risks And Test Signals
Risks include stale symlinks, Windows executable suffix handling, and external tool version drift. Signals are generated protobuf rules finding `protoc` and `protoc-gen-gogofaster`.
