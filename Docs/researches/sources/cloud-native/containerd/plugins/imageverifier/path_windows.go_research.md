# sources/cloud-native/containerd/plugins/imageverifier/path_windows.go

## Purpose
Defines the default image verifier binary directory for Windows.

## Important APIs, Types, And Functions
Package variable `defaultPath` joins `defaults.DefaultRootDir`, `opt`, `image-verifier`, and `bin`.

## Control Flow
No runtime control flow beyond package initialization.

## State And Persistence
No persistence. It derives a path from containerd defaults.

## Dependencies And Integration Points
Compiled on Windows and consumed by image verifier plugin defaults.

## Risks
Path semantics depend on `defaults.DefaultRootDir`; missing verifier binaries are handled downstream.

## Test Signals
No direct tests.
