<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/wq_failures.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/wq_failures.c

## Purpose
This verifier rejection suite checks invalid `struct bpf_wq` helper usage, including wrong map argument, mismatched owner map, invalid workqueue pointer, invalid offset, and non-constant workqueue offsets.

## Important APIs, Types, and Functions
It defines `struct elem { struct bpf_wq w; }`, array and LRU maps, callbacks `wq_callback` and `wq_cb_sleepable`, and uses `bpf_wq_init`, `bpf_wq_set_callback`, `bpf_get_prandom_u32`, plus test kfuncs.

## Control Flow
Each tc program looks up an array value and then intentionally violates a workqueue rule: passing `&key` instead of a map, initializing a workqueue from one map with another map, passing the address of the local workqueue pointer rather than the embedded field, adding offset 1 to the field, or computing the field address with an unknown offset. All are annotated verifier failures with anchor messages around the helper call.

## State and Persistence
There is no intended runtime persistence. Map declarations provide typed values for verifier pointer checks.

## Dependencies and Integration Points
The file integrates with the verifier selftest harness and depends on helper-specific verifier diagnostics for `bpf_wq_init` and `bpf_wq_set_callback`.

## Risks
Verifier diagnostics include map UID text and helper numbers, which can be brittle. Any change in workqueue helper contract or BTF field-offset validation can alter expectations.

## Test Signals
Expected failures include `pointer in R2 isn't map pointer`, workqueue/map UID mismatch, argument not pointing to map value, bad offset to `struct bpf_wq`, and non-constant offset rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/wq_failures.c -->
