# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/rbtree.c

## Purpose
Covers BPF rbtree kfunc API behavior, including add/remove/first/search, nested nodes, array-contained nodes, API aliasing, expected verifier failures, and BTF type mismatch failures. The source was read as a complete 202-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_rbtree_add_nodes()`, `test_rbtree_add_nodes_nested()`, `test_rbtree_add_and_remove()`, `test_rbtree_add_and_remove_array()`, `test_rbtree_first_and_remove()`, `test_rbtree_api_release_aliasing()`, `test_rbtree_success()`, `test_rbtree_btf_fail()`, `test_rbtree_fail()`, `test_rbtree_search()`, `test_rbtree_search_kptr()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include <network_helpers.h>`, `#include "rbtree.skel.h"`, `#include "rbtree_fail.skel.h"`, `#include "rbtree_btf_fail__wrong_node_type.skel.h"`, `#include "rbtree_btf_fail__add_wrong_type.skel.h"`, `#include "rbtree_search.skel.h"`, `#include "rbtree_search_kptr.skel.h"`.
- Generated skeletons/objects referenced: `rbtree`, `rbtree_btf_fail__add_wrong_type`, `rbtree_btf_fail__wrong_node_type`, `rbtree_fail`, `rbtree_search`, `rbtree_search_kptr`.
- Primary APIs and types: Skeletons `rbtree`, `rbtree_fail`, BTF fail skeletons, `rbtree_search`, `rbtree_search_kptr`, `bpf_prog_test_run_opts()`, and BPF-side rbtree kfuncs exercised by programs.

## Control Flow
Success helpers open/load the `rbtree` skeleton and run individual programs, checking return values and BSS result fields. Failure helpers attempt to load invalid skeletons. Search helpers validate lookup behavior for normal and kptr-backed nodes.

## State and Persistence Behavior
BPF maps/globals hold tree roots, removed keys, callback flags, and search results during each skeleton lifetime. No user-space persistence remains.

## Dependencies and Integration Points
Depends on generated skeletons, BPF rbtree kfunc support, BTF type checking, and network helper test-run scaffolding.

## Risks and Edge Cases
Verifier rules for ownership/release/aliasing are precise and can change; BTF fail tests are coupled to diagnostic/load-rejection semantics.

## Test Signals
Assertions cover program run success/retval, less-callback execution, first/removed key values, fail skeleton rejection, and search/kptr outcomes. Named assertion/check labels observed in the source include: `rbtree__open_and_load`, `rbtree_add_nodes run`, `rbtree_add_nodes retval`, `rbtree_add_nodes less_callback_ran`, `rbtree_add_nodes_nested run`, `rbtree_add_nodes_nested retval`, `rbtree_add_nodes_nested less_callback_ran`, `rbtree_add_and_remove`, `rbtree_add_and_remove retval`, `rbtree_add_and_remove first removed key`, `rbtree_add_and_remove_array`, `rbtree_add_and_remove_array retval`.
