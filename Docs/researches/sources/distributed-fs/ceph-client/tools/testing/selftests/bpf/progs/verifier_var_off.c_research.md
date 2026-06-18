<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_var_off.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_var_off.c

## Purpose
This verifier suite tests variable-offset access to contexts and stack memory, including privileged versus unprivileged policy, initialized stack ranges, out-of-bounds min/max checks, zero-sized helper accesses, and clobbering of spilled registers.

## Important APIs, Types, and Functions
It defines `map_hash_8b` for indirect helper calls and uses `bpf_map_lookup_elem`, `bpf_getsockopt`, and `bpf_probe_read_kernel`. Program types include lwt_in, cgroup/skb, socket, and sockops.

## Control Flow
The tests derive unknown offsets from context fields, mask them to small aligned ranges, add them to context or frame pointer bases, and then read, write, or pass them to helpers. Some tests initialize only part of the stack to verify what ranges are safe. The spill-clobber test writes through a variable stack pointer after spilling a map pointer and then reloads the slot, expecting the verifier to forget pointer provenance. Bounds tests deliberately create unbounded, max-out-of-bound, min-out-of-bound, and zero-sized out-of-bound accesses.

## State and Persistence
No persistent runtime state matters. The target state is verifier stack initialization metadata, variable offset ranges, maximum stack depth calculation, spilled register invalidation, and unprivileged variable-stack-access prohibition.

## Dependencies and Integration Points
The file is part of the verifier selftest corpus and depends on `bpf_misc.h` annotations, helper prototypes, and program-type-specific contexts such as `struct bpf_sock_ops`.

## Risks
Stack range analysis changes can affect success/failure outcomes. Some privileged tests intentionally allow reads from a range after variable writes, so overly conservative verifier changes would regress them. Diagnostic text is exact-match sensitive.

## Test Signals
Signals include `variable ctx access`, `variable stack access prohibited for !root`, `stack depth 16`, invalid variable-offset stack read/write messages, and invalid scalar dereference after spilled pointer clobbering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_var_off.c -->
