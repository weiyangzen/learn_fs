<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/fixtures/default.json -->
# sources/cloud-native/moby/daemon/pkg/oci/fixtures/default.json

## Purpose
Provides the current default seccomp fixture used to verify profile loading. It defaults to `SCMP_ACT_ERRNO`, uses the newer `archMap` form with seven architecture mappings, and groups allowed syscalls into 26 rule blocks with include/exclude conditions.

## Important APIs, Types, And Functions
This is data consumed by `seccomp.LoadProfile`. Its important fields are `defaultAction`, `archMap`, `syscalls[].names`, `syscalls[].action`, `syscalls[].args`, and optional `includes`/`excludes` filters such as kernel-version or architecture gates.

## Control Flow
The test reads the full file from `fixtures/default.json`, initializes `DefaultLinuxSpec()`, and asks the profile loader to transform the JSON into the spec's seccomp configuration.

## State, Dependencies, And Integration Points
No local state. It depends on libseccomp action/operator naming and the Moby profiles package. It is the realistic fixture for daemon default seccomp behavior.

## Risks And Test Signals
Large grouped syscall lists make accidental syntax or schema drift easy. `TestSeccompLoadProfile` confirms parser compatibility but does not assert individual syscall semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/fixtures/default.json -->
