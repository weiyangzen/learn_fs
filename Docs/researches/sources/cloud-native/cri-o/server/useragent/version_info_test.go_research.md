# sources/cloud-native/cri-o/server/useragent/version_info_test.go

## Purpose
Tests `AppendVersions` formatting and invalid-entry skipping.

## Important APIs, Types, And Functions
Ginkgo specs call `useragent.AppendVersions` with normal entries, no entries, invalid name, and invalid version.

## Control Flow
Asserts exact output for `base name/0.1.0 another/0.2.0`, empty result for empty base/no versions, and empty result when newline-containing entries are skipped.

## State And Persistence
Pure unit tests with no persistence.

## Dependencies And Integration Points
Validates the lower-level formatter used by `useragent.Get`.

## Risks And Test Signals
Does not test slash, tab, carriage return, spaces, empty fields, or mixed valid and invalid entries.
