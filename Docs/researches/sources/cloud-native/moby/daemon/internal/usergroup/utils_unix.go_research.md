# sources/cloud-native/moby/daemon/internal/usergroup/utils_unix.go

## Purpose
Safely resolves required Unix helper binaries from `PATH`.

## Important APIs, Types, And Functions
`resolveBinary(binname)` calls `exec.LookPath`, resolves symlinks with `filepath.EvalSymlinks`, and returns success only when the resolved basename still matches the requested binary name.

## Control Flow
Lookup failure or symlink resolution failure is returned. A basename mismatch produces an explicit error mentioning the requested binary and resolved path.

## State And Persistence
No state is mutated.

## Dependencies And Integration Points
Used before invoking `adduser`, `useradd`, and `getent` so daemon account-management code does not accidentally run an alias to another binary.

## Risks And Test Signals
The symlink basename check can reject legitimate alternatives managed through symlinks, trading flexibility for predictability. No tests are listed in this subset for the resolver itself.
