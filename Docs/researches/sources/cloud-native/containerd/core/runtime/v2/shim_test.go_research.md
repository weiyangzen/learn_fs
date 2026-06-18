# sources/cloud-native/containerd/core/runtime/v2/shim_test.go

## Purpose
Tests bootstrap response parsing and legacy bootstrap file migration behavior.

## APIs, Flow, State, Dependencies, Risks, And Tests
`TestParseStartResponse` checks raw address output, JSON bootstrap responses for ttrpc/gRPC, malformed legacy JSON falling back to raw-address ttrpc, and unsupported future versions returning `ErrNotImplemented`. `TestRestoreBootstrapParams` writes a legacy `address` file, calls `restoreBootstrapParams`, and confirms `bootstrap.json` is written and readable with version 2/ttrpc values.

The tests mutate temporary directories only. Dependencies include bootstrap API, errdefs, and testify require.

These tests guard the compatibility surface for old shim binaries and the migration path used during reload. Remaining gaps include protobuf bootstrap parsing, invalid `bootstrap.json` content, and filesystem write failure cases.
