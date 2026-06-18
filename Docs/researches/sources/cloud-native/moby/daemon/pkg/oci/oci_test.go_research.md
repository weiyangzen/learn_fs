<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/oci_test.go -->
# sources/cloud-native/moby/daemon/pkg/oci/oci_test.go

## Purpose
Provides deterministic unit coverage for device-cgroup rule parsing.

## Important APIs, Types, And Functions
`TestAppendDevicePermissionsFromCgroupRules` table-drives calls to `AppendDevicePermissionsFromCgroupRules`. It uses `gotest.tools/v3/assert` and compares full `specs.LinuxDeviceCgroup` structs, including major/minor pointers.

## Control Flow
Each subtest calls the parser with one rule. Error cases assert exact error messages; success cases assert a one-entry result slice.

## State, Dependencies, And Integration Points
No state. It depends on the OCI runtime spec package and forms the main regression suite for daemon `--device-cgroup-rule` conversion.

## Risks And Test Signals
The test exercises invalid whitespace, unknown device types, missing colon, non-numeric and negative numbers, overflow, wildcards, all/char/block types, and access strings. It does not cover multiple rules in one call or all permutations of repeated access letters.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/oci_test.go -->
