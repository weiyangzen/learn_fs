# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/refcounted_kptr.c

## Purpose
Tests refcounted kptr ownership rules, wrong-owner rbtree removal failures, per-CPU hash refcount leak prevention, and expected verifier rejection cases. The source was read as a complete 103-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_refcounted_kptr()`, `test_refcounted_kptr_fail()`, `test_refcounted_kptr_wrong_owner()`, `test_percpu_hash_refcounted_kptr_refcount_leak()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include <network_helpers.h>`, `#include "refcounted_kptr.skel.h"`, `#include "refcounted_kptr_fail.skel.h"`.
- Generated skeletons/objects referenced: `refcounted_kptr`, `refcounted_kptr_fail`.
- Primary APIs and types: `refcounted_kptr__open_and_load()`, `refcounted_kptr_fail` skeleton, `bpf_prog_test_run_opts()`, `bpf_map__update_elem()`, `libbpf_num_possible_cpus()`, and per-CPU value allocation.

## Control Flow
Success tests run programs that manipulate refcounted kptrs and validate return values. Failure tests load invalid variants. The per-CPU hash test allocates per-CPU values, updates the map, runs programs, and confirms no leaked refcount remains.

## State and Persistence Behavior
State lives in BPF maps containing kptrs/rbtree nodes and per-CPU values. User allocates a per-CPU value array and frees it after map updates/runs.

## Dependencies and Integration Points
Depends on generated `refcounted_kptr*.skel.h`, refcounted kptr verifier/kfunc support, rbtree support, and CPU-count helper.

## Risks and Edge Cases
Ownership rules are verifier-sensitive; per-CPU allocation must match possible CPU count exactly; failure tests can break on verifier diagnostic-policy changes.

## Test Signals
Assertions cover skeleton loads/rejections, program run retval, per-CPU allocation/update, and expected failure for wrong-owner remove paths. Named assertion/check labels observed in the source include: `refcounted_kptr__open_and_load`, `rbtree_wrong_owner_remove_fail_a1`, `rbtree_wrong_owner_remove_fail_a1 retval`, `rbtree_wrong_owner_remove_fail_b`, `rbtree_wrong_owner_remove_fail_b retval`, `rbtree_wrong_owner_remove_fail_a2`, `rbtree_wrong_owner_remove_fail_a2 retval`, `libbpf_num_possible_cpus`, `calloc values`, `bpf_map__update_elem`, `opts.retval`, `bpf_prog_test_run_opts`.
