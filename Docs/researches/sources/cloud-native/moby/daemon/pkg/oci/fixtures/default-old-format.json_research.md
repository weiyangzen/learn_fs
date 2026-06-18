<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/fixtures/default-old-format.json -->
# sources/cloud-native/moby/daemon/pkg/oci/fixtures/default-old-format.json

## Purpose
Provides a legacy Docker seccomp fixture for validating that the seccomp loader still accepts the old per-syscall profile format. It defaults to `SCMP_ACT_ERRNO`, declares an `architectures` array instead of the newer `archMap`, and lists 311 individual syscall entries with `name`, `action`, and optional `args`.

## Important APIs, Types, And Functions
The file is data-only but its schema is consumed by `github.com/moby/profiles/seccomp.LoadProfile`. The most important fields are `defaultAction`, `architectures`, and `syscalls[].name/action/args`.

## Control Flow
Runtime code reads this JSON as a string and passes it into the seccomp profile parser. The parser expands each syscall entry into OCI Linux seccomp rules for a default Linux spec.

## State, Dependencies, And Integration Points
No state is persisted. It depends on the historical Docker seccomp JSON shape and integrates with `seccomp_test.go` to prevent compatibility regressions.

## Risks And Test Signals
The risk is silent removal of old-profile support. `TestSeccompLoadProfile` is the direct signal: this fixture must parse without error on Linux.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/fixtures/default-old-format.json -->
