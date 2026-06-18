<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/oci.go -->
# sources/cloud-native/moby/daemon/pkg/oci/oci.go

## Purpose
Parses Docker daemon device-cgroup rule strings into OCI `LinuxDeviceCgroup` entries and appends them to an existing permission list.

## Important APIs, Types, And Functions
`deviceCgroupRuleRegex` accepts exact strings of form `([acb]) ([0-9]+|*):([0-9]+|*) ([rwm]{1,3})`. `AppendDevicePermissionsFromCgroupRules` returns a new slice or a format/parse error.

## Control Flow
For each rule, the regex must produce five groups. The function creates an allow entry, maps wildcard major/minor to `-1` pointers, parses numeric values as signed 64-bit integers, sets access bits from the rule, and appends to the input slice.

## State, Dependencies, And Integration Points
No persistence. It depends on Moby's lazy regexp helper, `strconv`, and OCI runtime-spec types. It feeds OCI specs used by container runtimes.

## Risks And Test Signals
The regex is strict about single spaces and does not deduplicate or sort permission letters. The TODO notes uncertainty around `a` all-device syntax. `oci_test.go` and the fuzz target cover syntax, overflow, wildcard, and permission cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/oci.go -->
