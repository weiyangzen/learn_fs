# sources/cloud-native/buildkit/frontend/gateway/container/util.go

## Purpose

This file provides small utility functions for gateway containers: parsing extra host IPs and identifying `os.Root` path escape errors.

## Important APIs, Types, And Functions

- `ParseExtraHosts` converts protobuf host/IP records to executor host/IP records using `net.ParseIP`.
- `isPathEscapesRootError` checks whether an error is an `*os.PathError` whose wrapped error text contains `path escapes`.

## Control Flow

`ParseExtraHosts` allocates an output slice of the same length as input, parses each IP, returns an error on the first invalid IP, and copies host names through. `isPathEscapesRootError` first uses `errors.As` to verify `*os.PathError`, then checks the error string.

## State And Persistence Behavior

No state is stored. Output slices are newly allocated.

## Dependencies And Integration Points

`ParseExtraHosts` feeds `executor.ProcessInfo.Meta.ExtraHosts` from gateway new-container requests. `isPathEscapesRootError` is used by `gatewayContainer.StatFile` to decide when to fall back from stat to lstat for symlink escapes.

## Risks And Edge Cases

The path escape detector depends on error text, which is less stable than a sentinel error. It is scoped by requiring `*os.PathError`, reducing false positives. `ParseExtraHosts` accepts any `net.ParseIP` output, including IPv4 and IPv6.

## Test Signals

`util_test.go` creates a symlink escaping an opened root and asserts the detector returns true for the resulting `fs.Stat` error.
