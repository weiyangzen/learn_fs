# sources/cloud-native/containerd/plugins/snapshots/devmapper/config_test.go

## Purpose
This test file validates devmapper configuration loading, parsing, and field validation.

## Important APIs, Types, And Functions
Tests include `TestLoadConfig`, `TestLoadConfigInvalidPath`, `TestParseInvalidData`, `TestFieldValidation`, and `TestExistingPoolFieldValidation`.

## Control Flow
The loading test writes TOML to a temp file, loads it, and checks parsed values including byte conversion. Validation tests assert missing fields produce four joined errors and that a complete ext4 config succeeds.

## State And Persistence
Only temporary config files are created.

## Dependencies And Integration Points
The tests use `go-toml/v2` encoding and `testify/assert`.

## Risks
The tests do not cover xfs/ext2 validation, async/remove flags, discard flag, or custom filesystem options.

## Test Signals
They give focused confidence in config parsing and required-field error aggregation.
