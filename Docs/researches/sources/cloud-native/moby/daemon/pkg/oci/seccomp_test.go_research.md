<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/seccomp_test.go -->
# sources/cloud-native/moby/daemon/pkg/oci/seccomp_test.go

## Purpose
Linux-only test coverage for loading bundled seccomp profiles into a default OCI Linux spec.

## Important APIs, Types, And Functions
`TestSeccompLoadProfile` reads `default.json`, `default-old-format.json`, and `example.json` and calls `seccomp.LoadProfile`. `TestSeccompLoadDefaultProfile` marshals `seccomp.DefaultProfile()` and loads it the same way.

## Control Flow
Each test creates `rs := DefaultLinuxSpec()` and treats any read, marshal, or load error as fatal.

## State, Dependencies, And Integration Points
No persisted state. It depends on Linux build tags, local fixture files, Moby's profiles/seccomp package, and OCI default-spec creation.

## Risks And Test Signals
The tests validate parse/load compatibility but not the exact generated syscall allowlist. They catch schema regressions, fixture syntax errors, and mismatches between default-profile generation and the loader.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/seccomp_test.go -->
