# sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/versioning_test.go

## Purpose
Tests version label parsing, enum stringification, version lookup, advertised known versions, and v1 xattr selection rules for TarSum.

## Important APIs, Types, And Functions
Targets `VersionLabelForChecksum`, `Version.String`, `GetVersionFromTarsum`, `GetVersions`, helper `containsVersion`, and internal `v1TarHeaderSelect`. Uses `slices.Contains`, `errors.Is`, and `gotest.tools` deep equality.

## Control Flow
The tests feed valid labels with and without hash suffixes and one invalid label. `GetVersions` is checked by membership rather than order. The xattr test builds a tar header containing both `PAXRecords` and `Xattrs`, renders selected headers into test logs, and asserts the last three fields are sorted xattrs with `Xattrs` taking precedence over PAX for the duplicate key.

## State And Persistence
No file or persistent state. The test reflects static version maps and selector behavior.

## Dependencies And Integration Points
This is the direct unit coverage for `versioning.go`; broader checksum consequences are covered by `tarsum_test.go`.

## Risks And Test Signals
The tests intentionally accept unordered `GetVersions` output. Failure indicates label compatibility breakage, missing version registration, or xattr ordering/precedence drift that would alter v1/dev TarSum output.
