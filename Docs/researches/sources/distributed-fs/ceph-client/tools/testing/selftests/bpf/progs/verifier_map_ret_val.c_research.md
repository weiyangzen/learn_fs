# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_map_ret_val.c

## Purpose
This file tests verifier validation around map helper arguments and map lookup return values, especially null checks and alignment-sensitive map value access.

## Important APIs, Types, And Functions
It defines a hash map `map_hash_8b` and uses `bpf_map_delete_elem` plus `bpf_map_lookup_elem`. Tests are socket programs with strict alignment annotations where needed.

## Control Flow
The invalid-FD test passes literal zero as a map argument. Lookup-return tests access `r0` without checking for null, access with an intentionally misaligned offset, and branch so one path dereferences a null map value.

## State And Persistence
The hash map is a fixture. Verifier state tracks helper argument type, map-value-or-null return state, null refinement, alignment, and unprivileged pointer-leak restrictions.

## Dependencies And Integration Points
It integrates with generic map helper validation and strict-alignment verifier mode.

## Risks
Missing null checks on map lookups can become runtime null dereferences. Incorrect alignment handling can accept loads/stores that are invalid on strict-alignment architectures.

## Test Signals
Failures assert messages such as `fd 0 is not pointing to valid bpf_map`, `map_value_or_null`, `misaligned value access`, and unprivileged `R0 leaks addr`.
