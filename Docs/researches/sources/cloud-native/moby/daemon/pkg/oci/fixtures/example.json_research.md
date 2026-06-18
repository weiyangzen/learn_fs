<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/fixtures/example.json -->
# sources/cloud-native/moby/daemon/pkg/oci/fixtures/example.json

## Purpose
Provides a minimal seccomp fixture for parser coverage. It denies by default and allows only `clone` with a masked argument comparison plus `open` and `close`.

## Important APIs, Types, And Functions
The relevant fields are `defaultAction`, `syscalls[].name`, `syscalls[].action`, and `syscalls[].args[]` with `SCMP_CMP_MASKED_EQ`.

## Control Flow
`seccomp_test.go` loads the file into a default OCI Linux spec through `seccomp.LoadProfile`. The short profile validates the older single-`name` syscall schema and argument comparator parsing.

## State, Dependencies, And Integration Points
No state is changed. The fixture integrates with Moby's seccomp loader tests and complements the large default fixtures by making comparator coverage easy to inspect.

## Risks And Test Signals
It is intentionally too small to represent production policy. Passing `TestSeccompLoadProfile/example.json` signals only that the minimal schema and masked comparator are accepted.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/fixtures/example.json -->
