<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/transfer/plugin_test.go -->
# sources/cloud-native/containerd/plugins/transfer/plugin_test.go

## Purpose
Unit tests for transfer unpack platform configuration and diff applier selection.

## Important APIs, Types, And Functions
`TestConfigureUnpackPlatforms`, `newTestInitContext`, `newTestDiffPlugin`, `testApplier`, and `testSnapshotter`.

## Control Flow
Table cases cover optional explicit differ skip, required explicit differ skip, optional explicit differ missing, and auto differ selection that skips unavailable candidates and uses a later usable candidate. Helpers create a local content store, bbolt metadata DB, plugin set with snapshotter registrations, and diff plugin registrations.

## State And Persistence
Creates temporary content stores and bbolt metadata DBs, closing the DB through `t.Cleanup`.

## Dependencies And Integration Points
Uses containerd metadata DB, local transfer config, plugin set/context APIs, diff and snapshotter interfaces, errdefs, and platform matching.

## Risks And Edge Cases
Tests use minimal stubs and do not instantiate the full transfer service. Ambiguous multi-differ default preference is not explicitly asserted here.

## Test Signals
Provides focused coverage for optional vs required unpack configuration failures and auto applier selection with skipped plugins.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/transfer/plugin_test.go -->
