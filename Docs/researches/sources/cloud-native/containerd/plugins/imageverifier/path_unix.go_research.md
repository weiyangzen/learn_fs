# sources/cloud-native/containerd/plugins/imageverifier/path_unix.go

## Purpose
Defines the default image verifier binary directory for non-Windows platforms.

## Important APIs, Types, And Functions
Package variable `defaultPath` is `/opt/containerd/image-verifier/bin`.

## Control Flow
No runtime control flow beyond package initialization.

## State And Persistence
No persistence. The path is consumed by default image verifier configuration.

## Dependencies And Integration Points
Compiled under `!windows` and used by `plugin.go` default config.

## Risks
Hard-coded absolute path may not exist; verifier discovery/runtime behavior must handle missing binaries.

## Test Signals
No direct tests.
