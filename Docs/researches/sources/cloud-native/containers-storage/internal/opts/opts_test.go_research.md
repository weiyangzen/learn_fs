<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/opts/opts_test.go -->
# sources/cloud-native/containers-storage/internal/opts/opts_test.go

## Purpose
This test file verifies option containers and validators in `internal/opts`.

## Important APIs, Types, And Functions
Tests cover `ValidateIPAddress`, `MapOpts`, `ListOpts` with and without validators, `ValidateLabel`, `NamedListOpts`, and `NamedMapOpts`. `logOptsValidator` is a test validator accepting `max-size` and `max-file`.

## Control Flow
The tests set values, assert string forms and lengths, verify validator rejection, delete values, inspect duplicate handling through `GetMap`, and ensure named wrappers update referenced storage.

## State And Persistence
Tests use in-memory maps and slices only.

## Dependencies And Integration Points
The tests use testify and the public opts package API from an external test package.

## Risks And Test Signals
Coverage does not include `ValidateSysctl`, `FilterOpt`, or the richer `Args` matching behavior in `parse.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/opts/opts_test.go -->
