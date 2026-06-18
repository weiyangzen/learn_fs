# sources/cloud-native/containerd/integration/shim_dial_unix_test.go

## Purpose

`shim_dial_unix_test.go` verifies that shim dialing fails fast on Unix socket errors during restart/recovery rather than waiting for a stale socket to reappear.

## Important APIs, Types, and Functions

- `TestFailFastWhenConnectShim` runs normal Unix socket coverage and Linux abstract socket coverage.
- `dialFunc` abstracts shim dialers.
- `testFailFastWhenConnectShim` sets up a temporary ttrpc server, validates successful dialing, shuts the listener down, and checks `ECONNREFUSED`/`ENOENT` handling.
- `newTestListener` constructs normal `unix://` or abstract-socket addresses and cleanup functions.

## Control Flow

The test starts a ttrpc server on a socket, retries dialing until the server is accepting, disables unlink-on-close for normal sockets, shuts down the server, waits for `ECONNREFUSED`, asserts the dialer returns quickly, removes the socket directory, and asserts abstract sockets still report refused while normal sockets report missing.

## State and Persistence Behavior

Only temporary socket paths and listeners are used. The test models stale shim socket state rather than persisting containerd metadata.

## Dependencies and Integration Points

It depends on containerd shim `AnonDialer`, ttrpc server/client behavior, Unix sockets, Linux abstract sockets, and syscall error matching.

## Risks and Edge Cases

Timing is central: the test uses retries and timeouts to separate slow dials from fail-fast behavior. Abstract socket address compatibility is tied to historic shim address file formats.

## Test Signals

Failures signal regressions in shim dialer error handling that could make task manager restart recovery hang on stale or absent shim sockets.
