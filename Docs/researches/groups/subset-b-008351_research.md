# subset-b-008351 Research

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_iface.c -->
# sources/security-integrity/selinux/libsemanage/tests/test_iface.c

## Purpose
`test_iface.c` is a CUnit suite for the libsemanage interface-record API and the policy/local backend wrappers for network interfaces. It verifies that interface records can be created, keyed, cloned, compared, read from compiled policy, and written/deleted through the local customization store.

## Important APIs, Types, and Functions
The suite exercises `semanage_iface_t` and `semanage_iface_key_t` plus the `semanage_iface_*` API family. Public record functions covered include `semanage_iface_create`, `semanage_iface_free`, `semanage_iface_key_create`, `semanage_iface_key_extract`, `semanage_iface_compare`, `semanage_iface_compare2`, `semanage_iface_get_name`, `semanage_iface_set_name`, `semanage_iface_get_ifcon`, `semanage_iface_set_ifcon`, `semanage_iface_get_msgcon`, `semanage_iface_set_msgcon`, and `semanage_iface_clone`. Policy-store functions covered include `semanage_iface_query`, `semanage_iface_exists`, `semanage_iface_count`, `semanage_iface_iterate`, and `semanage_iface_list`. Local-store functions covered include `semanage_iface_modify_local`, `semanage_iface_del_local`, `semanage_iface_query_local`, `semanage_iface_exists_local`, `semanage_iface_count_local`, `semanage_iface_iterate_local`, and `semanage_iface_list_local`.

The file defines three expected interface fixtures: `eth0`, `eth1`, and `eth2`, with matching interface and packet/message contexts. Helper functions `get_iface_nth`, `get_iface_key_nth`, `add_local_iface`, and `delete_local_iface` centralize list extraction and local-store mutation.

## Control Flow
`iface_test_init` creates a temporary direct policy store through `create_test_store` and loads `test_iface.policy` as `policy.kern`. `iface_add_tests` registers record, policy, and local tests into a supplied CUnit suite. Most tests call `setup_handle(SH_CONNECT)` to connect to the test store or `setup_handle(SH_TRANS)` to open a transaction, perform assertions, then call `cleanup_handle` at the same level.

Record tests operate on policy records fetched through `semanage_iface_list`. Query/existence/count/list/iterate tests read from the active policy view. Local tests start a transaction, copy policy records into the local customization layer, sometimes commit and reopen the transaction to force persistence to disk, then query, count, iterate, list, and delete those local records.

## State and Persistence Behavior
The test store lives under `test-policy` and is destroyed by `iface_test_cleanup`. Local interface changes are transaction-scoped until `helper_commit`; `test_iface_modify_del_query_local` explicitly commits and begins a new transaction before verifying `semanage_iface_query_local`, so it checks serialized local-file behavior rather than only in-memory mutation. Helpers free all unselected list records to avoid leaking list results.

## Dependencies and Integration Points
The suite depends on CUnit, `utilities.h` test-store helpers, libsemanage public headers, and the binary fixture `test_iface.policy`. It integrates with the larger libsemanage test runner through `iface_test_init`, `iface_test_cleanup`, and `iface_add_tests`.

## Risks and Edge Cases
The iterate counters are static globals and are not reset inside each test, so repeated invocation in a single process could produce false failures. Test registration has two typo-like display names, `"iface_create)"` and `"iface_clone);"`, which do not affect function execution but can confuse reports. The suite assumes policy list ordering is stable enough for `I_FIRST`, `I_SECOND`, and `I_THIRD` to identify the fixture records.

## Test Signals
Primary signals are CUnit assertions that policy count equals `IFACE_COUNT`, compare functions distinguish equal and non-equal keys/records, context setters round-trip through `CU_ASSERT_CONTEXT_EQUAL`, policy queries match expected records, and local mutations survive commit and deletion.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_iface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_iface.h -->
# sources/security-integrity/selinux/libsemanage/tests/test_iface.h

## Purpose
`test_iface.h` declares the interface test-suite entry points used by the libsemanage CUnit runner.

## Important APIs, Types, and Functions
It includes `<CUnit/Basic.h>` for `CU_pSuite` and declares `iface_test_init`, `iface_test_cleanup`, and `iface_add_tests(CU_pSuite suite)`.

## Control Flow
The header has no runtime control flow. The runner includes it, calls the init function before suite execution, calls `iface_add_tests` to register test cases, and calls cleanup after the suite completes.

## State and Persistence Behavior
State is owned by `test_iface.c` and shared helpers; this header exposes only the lifecycle contract.

## Dependencies and Integration Points
The include guard `__TEST_IFACE_H__` prevents duplicate declarations. Its only external dependency is CUnit. It is paired directly with `test_iface.c`.

## Risks and Test Signals
Any signature drift between this header, the implementation, and the test runner would break compilation. The meaningful runtime signals are generated by the implementation suite.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_iface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_node.c -->
# sources/security-integrity/selinux/libsemanage/tests/test_node.c

## Purpose
`test_node.c` validates libsemanage node-context record handling for IPv4 and IPv6 network nodes, including record creation, key extraction, address and mask setters, protocol handling, compiled-policy queries, and local-store mutation.

## Important APIs, Types, and Functions
The suite exercises `semanage_node_t` and `semanage_node_key_t`. Record-level coverage includes `semanage_node_create`, `semanage_node_key_create`, `semanage_node_key_extract`, `semanage_node_compare`, `semanage_node_compare2`, `semanage_node_set_addr`, `semanage_node_get_addr`, `semanage_node_set_addr_bytes`, `semanage_node_get_addr_bytes`, `semanage_node_set_mask`, `semanage_node_get_mask`, `semanage_node_set_mask_bytes`, `semanage_node_get_mask_bytes`, `semanage_node_set_proto`, `semanage_node_get_proto`, `semanage_node_get_proto_str`, `semanage_node_set_con`, `semanage_node_get_con`, and `semanage_node_clone`.

Policy APIs covered are `semanage_node_query`, `semanage_node_exists`, `semanage_node_count`, `semanage_node_iterate`, and `semanage_node_list`. Local APIs covered are `semanage_node_modify_local`, `semanage_node_del_local`, `semanage_node_query_local`, `semanage_node_exists_local`, `semanage_node_count_local`, `semanage_node_iterate_local`, and `semanage_node_list_local`.

## Control Flow
`node_test_init` creates the direct test policy store and loads `test_node.policy`; `node_test_cleanup` destroys that store. `node_add_tests` registers record, policy, and local cases. Helper functions fetch nth records and keys from `semanage_node_list` and use them to seed local-store operations.

The record tests cover both textual and byte-vector address/mask paths. Policy tests query and compare address, mask, protocol, and context data from the compiled policy. Local tests run in transactions, write policy records into the local store, commit where persistence needs to be checked, then verify query, existence, count, iteration, listing, and deletion.

## State and Persistence Behavior
The suite creates and removes `test-policy` via shared utilities. Local node customizations are staged inside libsemanage transactions; `test_node_modify_del_query_local` commits, reopens a transaction, and verifies that local query sees the persisted record. It also adds a temporary second record with a modified IPv4 address to exercise qsort comparison paths for local node serialization.

## Dependencies and Integration Points
Dependencies include CUnit, the shared `utilities.h` handle/store helpers, libsemanage and libsepol protocol constants, and the binary fixture `test_node.policy`. It integrates with the runner through `node_test_init`, `node_test_cleanup`, and `node_add_tests`.

## Risks and Edge Cases
The byte-array tests use `char` values such as 192 and 255, which may be signed on some targets; the test compares byte-for-byte through the same representation and is mainly a round-trip check. Static iterate counters are not reset per invocation. As with other record suites, nth-record selection depends on deterministic list ordering from the fixture policy.

## Test Signals
Expected signals are successful CUnit assertions that protocol strings are `"ipv4"` and `"ipv6"`, text and byte setters round-trip, cloned nodes preserve address/mask/protocol/context, policy count equals `NODE_COUNT`, and local add/delete/count/list operations behave consistently across transactions.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_node.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_node.h -->
# sources/security-integrity/selinux/libsemanage/tests/test_node.h

## Purpose
`test_node.h` exposes the CUnit lifecycle functions for the libsemanage node test suite.

## Important APIs, Types, and Functions
The header includes `<CUnit/Basic.h>` and declares `node_test_init`, `node_test_cleanup`, and `node_add_tests(CU_pSuite suite)`.

## Control Flow
There is no logic in this header; it provides declarations consumed by the central test runner.

## State and Persistence Behavior
State is created, mutated, and cleaned up in `test_node.c` and the shared test utilities. The header does not own state.

## Dependencies and Integration Points
Its include guard is `__TEST_NODE_H__`. It integrates `test_node.c` with the CUnit suite registry.

## Risks and Test Signals
Compile-time consistency with the implementation and runner is the relevant signal for this file. Runtime behavior is validated by the `test_node.c` suite.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_node.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_other.c -->
# sources/security-integrity/selinux/libsemanage/tests/test_other.c

## Purpose
`test_other.c` groups smaller libsemanage tests that do not fit the object-specific suites: SELinux context record manipulation and one debug/error-path check for module priority validation.

## Important APIs, Types, and Functions
`test_semanage_context` exercises `semanage_context_t` with `semanage_context_create`, setters/getters for user, role, type, and MLS, `semanage_context_to_string`, `semanage_context_from_string`, `semanage_context_clone`, and `semanage_context_free`. `test_debug` creates a handle and `semanage_module_info_t`, then verifies that `semanage_module_info_set_priority` rejects a priority cast from `-42` to `uint16_t`.

## Control Flow
`other_test_init` and `other_test_cleanup` are no-ops. `other_add_tests` registers `test_semanage_context` and `test_debug`. The context test uses `setup_handle(SH_CONNECT)`, builds a context, serializes it, parses another context string, clones it, and compares all fields. The debug test constructs its own handle instead of using shared setup, connects, creates module info, exercises the invalid-priority path, then explicitly destroys module info and the handle.

## State and Persistence Behavior
No policy files are created by this suite. The context test uses only heap-allocated context objects plus a libsemanage connection. The debug test allocates a handle and module info object and frees both after the assertion.

## Dependencies and Integration Points
The file depends on CUnit, `utilities.h`, libsemanage context APIs, and module-info APIs. It is registered by the test runner through `other_add_tests`.

## Risks and Edge Cases
`test_debug` calls `semanage_module_info_destroy(sh, modinfo)` and then `free(modinfo)`, which assumes the destroy function only releases internals and not the outer allocation. The priority test is tied to libsemanage's accepted numeric range and unsigned-cast behavior. The context test validates simple four-field MLS contexts but does not cover contexts without MLS or malformed strings.

## Test Signals
Signals include exact field equality for context setters/getters, string serialization to `user_u:role_r:type_t:s0`, parsing and cloning of `my_u:my_r:my_t:s0`, and a negative return from invalid module priority assignment.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_other.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_other.h -->
# sources/security-integrity/selinux/libsemanage/tests/test_other.h

## Purpose
`test_other.h` declares the CUnit lifecycle functions for miscellaneous libsemanage tests.

## Important APIs, Types, and Functions
It includes `<CUnit/Basic.h>` and declares `other_test_init`, `other_test_cleanup`, and `other_add_tests(CU_pSuite suite)`.

## Control Flow
The file contains no executable logic. The central CUnit runner uses these declarations to initialize, register, and clean up the miscellaneous suite.

## State and Persistence Behavior
State is entirely in `test_other.c` and shared libsemanage handles; the header has no persistent behavior.

## Dependencies and Integration Points
The include guard is `__TEST_OTHER_H__`. Its integration point is the suite registry.

## Risks and Test Signals
The header's risk is ordinary declaration drift. Runtime test signals live in `test_other.c`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_other.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_port.c -->
# sources/security-integrity/selinux/libsemanage/tests/test_port.c

## Purpose
`test_port.c` validates libsemanage port-context records, including protocol/range/context record operations, compiled-policy queries, local-store CRUD, and an internal local validation path for port customizations.

## Important APIs, Types, and Functions
The suite targets `semanage_port_t` and `semanage_port_key_t`. Record functions covered include `semanage_port_create`, `semanage_port_key_create`, `semanage_port_key_extract`, `semanage_port_compare`, `semanage_port_compare2`, `semanage_port_set_proto`, `semanage_port_get_proto`, `semanage_port_get_proto_str`, `semanage_port_set_port`, `semanage_port_set_range`, `semanage_port_get_low`, `semanage_port_get_high`, `semanage_port_set_con`, `semanage_port_get_con`, and `semanage_port_clone`.

Policy APIs covered are `semanage_port_query`, `semanage_port_exists`, `semanage_port_count`, `semanage_port_iterate`, and `semanage_port_list`. Local APIs covered are `semanage_port_modify_local`, `semanage_port_del_local`, `semanage_port_query_local`, `semanage_port_exists_local`, `semanage_port_count_local`, `semanage_port_iterate_local`, and `semanage_port_list_local`. The final internal validation group drives commit-time validation through `helper_commit`.

## Control Flow
`port_test_init` creates the direct test store and loads `test_port.policy`; cleanup destroys the store. `port_add_tests` registers record, policy, local, and validation tests. The helper layer fetches nth ports and keys from `semanage_port_list` and provides local add/delete wrappers.

The record tests compare same and different keys/records, check protocol string mapping for invalid and known values, verify range setters, create a default record, and clone a populated record. Policy tests read the compiled policy and compare low/high/protocol/context values. Local tests stage records in a transaction, query before and after deletion, and verify local counts, iteration, and lists. `test_port_validate_local` runs three commit scenarios: deleting an existing local port, committing one local port, and committing two adjacent UDP ranges with different contexts.

## State and Persistence Behavior
The suite persists local port changes through the libsemanage transaction system under `test-policy`. Some tests explicitly commit and then reopen transactions to force file-backed validation. Local validation tests depend on commit side effects and clean up by reopening a transaction and deleting local records.

## Dependencies and Integration Points
Dependencies include CUnit, shared `utilities.h`, libsemanage port/context APIs, libsepol protocol constants, and the `test_port.policy` fixture. The suite is exposed through `port_test_init`, `port_test_cleanup`, and `port_add_tests`.

## Risks and Edge Cases
Static iterate counters are not reset per repeated suite execution. Protocol numeric assumptions are embedded directly: `0` maps to UDP, `1` to TCP, `2` to DCCP, and `3` to SCTP. Some validation helpers delete records during cleanup that may already have been removed, relying on the current local-store behavior and assertion placement. The fixture order must remain stable for nth-record selection.

## Test Signals
Signals include `PORT_COUNT == 3`, correct protocol labels including `"???"` for unknown values, context equality after set/clone/query, local count transitions from 0 to 2 and back to 0, iteration/list counts of 3, and successful commit of local validation scenarios.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_port.h -->
# sources/security-integrity/selinux/libsemanage/tests/test_port.h

## Purpose
`test_port.h` declares the lifecycle hooks for the libsemanage port CUnit suite.

## Important APIs, Types, and Functions
It includes `<CUnit/Basic.h>` and declares `port_test_init`, `port_test_cleanup`, and `port_add_tests(CU_pSuite suite)`.

## Control Flow
The header contains declarations only. The test runner calls these functions to set up a policy fixture, register tests, and clean up after execution.

## State and Persistence Behavior
The header has no state. File-backed test-store state is managed by `test_port.c` and shared utilities.

## Dependencies and Integration Points
The include guard is `__TEST_PORT_H__`; integration is with the central CUnit registry.

## Risks and Test Signals
The header must stay synchronized with `test_port.c`. Runtime validation signals are emitted by the implementation suite.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_semanage_store.c -->
# sources/security-integrity/selinux/libsemanage/tests/test_semanage_store.c

## Purpose
`test_semanage_store.c` tests lower-level libsemanage store behavior: access checks over store paths and locks, active/trans lock acquisition and release, and netfilter-context sorting through `semanage_nc_sort`.

## Important APIs, Types, and Functions
Suite lifecycle functions are `semanage_store_test_init`, `semanage_store_test_cleanup`, and `semanage_store_add_tests`. Test functions are `test_semanage_store_access_check`, `test_semanage_get_lock`, and `test_semanage_nc_sort`.

The implementation reaches into lower-level libsemanage internals via `handle.h` and `semanage_store.h`, using `semanage_check_init`, `semanage_store_access_check`, `semanage_get_active_lock`, `semanage_release_active_lock`, `semanage_get_trans_lock`, `semanage_release_trans_lock`, and `semanage_nc_sort`. It also directly adjusts `sh->conf->store_path` and `sh->msg_callback`.

## Control Flow
Initialization creates `./test-policy/store/active/modules`, creates a handle, suppresses messages, sets the store path to `"store"`, and initializes store paths with `semanage_check_init(sh, rootpath)`. Cleanup removes the empty module, active, store, and root directories and destroys the handle.

The access test creates a read lock file and repeatedly changes permissions on the store path, read lock, and modules path, asserting the reported access level for no access, read, write, and missing-lock combinations. The lock test acquires active and transaction locks twice to verify reentrant or already-held behavior, releases them, reacquires, and removes lock files. The nc-sort test mmaps `nc_sort_unsorted`, `nc_sort_sorted`, and `nc_sort_malformed`, compares sorted output to the expected buffer, and verifies malformed input fails.

## State and Persistence Behavior
This suite manipulates real filesystem permissions and lock files under `./test-policy`. It uses `mknod`, `chmod`, `remove`, `mkdir`, `rmdir`, `open`, `mmap`, and `munmap`. The test assumes cleanup can remove directories directly, so tests must leave no generated children behind except files removed inside the tests.

## Dependencies and Integration Points
Dependencies include CUnit, POSIX filesystem APIs, `handle.h`, `semanage_store.h`, shared test utilities, and fixture files `nc_sort_unsorted`, `nc_sort_sorted`, and `nc_sort_malformed`. It is an integration point between public handle setup and private store implementation details.

## Risks and Edge Cases
Permission checks can behave differently when tests run as root or under unusual filesystem ACL/mount options. The suite directly modifies internal handle fields, so internal structure changes can break it. `test_semanage_store_access_check` does not restore all permissions between every branch except by applying the next mode, so an early fatal exit can leave awkward local state. `CU_ASSERT_STRING_EQUAL(sorted_buf, good_buf)` assumes mmaped expected data is NUL-terminated or at least safe for C string comparison.

## Test Signals
Strong signals are exact access constants (`-1`, `0`, `SEMANAGE_CAN_READ`, `SEMANAGE_CAN_WRITE`), successful repeated lock acquisition/release, byte-equivalent netfilter context sort output for valid input, and `-1` from malformed netfilter context data.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_semanage_store.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_semanage_store.h -->
# sources/security-integrity/selinux/libsemanage/tests/test_semanage_store.h

## Purpose
`test_semanage_store.h` declares the CUnit suite hooks and individual test functions for lower-level semanage store tests.

## Important APIs, Types, and Functions
It includes `<CUnit/Basic.h>` and declares `semanage_store_test_init`, `semanage_store_test_cleanup`, `semanage_store_add_tests`, `test_semanage_store_access_check`, `test_semanage_get_lock`, and `test_semanage_nc_sort`.

## Control Flow
There is no executable flow in the header. Its declarations let the CUnit runner register the suite and optionally reference individual test functions.

## State and Persistence Behavior
The header owns no state. Filesystem state is created and removed by `test_semanage_store.c`.

## Dependencies and Integration Points
The include guard is `__TEST_SEMANAGE_STORE_H__`. It connects the store test implementation to the CUnit registry.

## Risks and Test Signals
The extra individual-test declarations increase the surface for declaration drift if function names change. Runtime signals are in `test_semanage_store.c`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_semanage_store.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_user.c -->
# sources/security-integrity/selinux/libsemanage/tests/test_user.c

## Purpose
`test_user.c` validates libsemanage SELinux user-record behavior, including record fields, role list mutation, compiled-policy queries, and local-store CRUD.

## Important APIs, Types, and Functions
The suite targets `semanage_user_t` and `semanage_user_key_t`. It exercises `semanage_user_create`, `semanage_user_free`, `semanage_user_key_create`, `semanage_user_key_extract`, `semanage_user_compare`, `semanage_user_compare2`, `semanage_user_set_name`, `semanage_user_get_name`, `semanage_user_set_prefix`, `semanage_user_get_prefix`, `semanage_user_set_mlslevel`, `semanage_user_get_mlslevel`, `semanage_user_set_mlsrange`, `semanage_user_get_mlsrange`, `semanage_user_get_num_roles`, `semanage_user_add_role`, `semanage_user_del_role`, `semanage_user_has_role`, `semanage_user_get_roles`, `semanage_user_set_roles`, and `semanage_user_clone`.

Policy APIs covered are `semanage_user_query`, `semanage_user_exists`, `semanage_user_count`, `semanage_user_iterate`, and `semanage_user_list`. Local APIs covered are `semanage_user_modify_local`, `semanage_user_del_local`, `semanage_user_query_local`, `semanage_user_exists_local`, `semanage_user_count_local`, `semanage_user_iterate_local`, and `semanage_user_list_local`.

## Control Flow
`user_test_init` creates a test store and loads `test_user.policy`; cleanup destroys the store. `user_add_tests` registers record, policy, and local cases. Helpers fetch nth users and keys from `semanage_user_list`, then use those fixtures to add and delete local records.

Record tests validate scalar fields and role-list APIs. Query/list tests verify the compiled policy exposes three users and returns non-null records. Local tests add policy users to the local store, commit and reopen for query/delete persistence, and verify existence, count, iteration, and list behavior.

## State and Persistence Behavior
The suite stores temporary policy data under `test-policy`. Local user modifications are staged in transactions and persisted on `helper_commit`; `test_user_modify_del_query_local` explicitly checks query behavior after commit. Role arrays returned by `semanage_user_get_roles` are freed by the test after use.

## Dependencies and Integration Points
Dependencies include CUnit, shared `utilities.h`, libsemanage user APIs, and `test_user.policy`. Integration with the runner is through `user_test_init`, `user_test_cleanup`, and `user_add_tests`.

## Risks and Edge Cases
Several policy query/list assertions are shallow and include TODO comments for checking real field values. `test_user_clone` appears to assert fields on the original record after cloning rather than on `user_clone`, so it only verifies the clone call returned success and not clone content. `test_user_exists_local` declares an unused `user` pointer and frees it as NULL. Static iterate counters are not reset between repeated invocations.

## Test Signals
Primary signals are `USER_COUNT == 3`, successful setter/getter round trips for name/prefix/MLS level/range, role-list add/set/delete behavior, non-null query/list records, local existence/count/list/iterate results, and negative query after local deletion.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_user.h -->
# sources/security-integrity/selinux/libsemanage/tests/test_user.h

## Purpose
`test_user.h` declares lifecycle hooks for the libsemanage user CUnit suite.

## Important APIs, Types, and Functions
It includes `<CUnit/Basic.h>` and declares `user_test_init`, `user_test_cleanup`, and `user_add_tests(CU_pSuite suite)`.

## Control Flow
The file has no executable behavior. The CUnit runner uses it to call into `test_user.c`.

## State and Persistence Behavior
No state is stored here. Test-store state is created, used, and destroyed by the implementation.

## Dependencies and Integration Points
The include guard is `__TEST_USER_H__`; the integration point is the central CUnit suite registration path.

## Risks and Test Signals
Declaration drift is the main risk. Runtime correctness signals come from `test_user.c`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_utilities.c -->
# sources/security-integrity/selinux/libsemanage/tests/test_utilities.c

## Purpose
`test_utilities.c` is the CUnit suite for helper functions implemented in libsemanage's `src/utilities.c`. It validates string splitting, list helpers, trimming, replacement, config-value lookup, file filtering, and basename handling.

## Important APIs, Types, and Functions
Suite hooks are `semanage_utilities_test_init`, `semanage_utilities_test_cleanup`, and `semanage_utilities_add_tests`. Tested APIs include `semanage_is_prefix`, `semanage_split_on_space`, `semanage_split`, `semanage_list_push`, `semanage_list_pop`, `semanage_list_sort`, `semanage_list_find`, `semanage_list_destroy`, `semanage_str_count`, `semanage_rtrim`, `semanage_str_replace`, `semanage_findval`, `semanage_slurp_file_filter`, and `semanage_basename`.

## Control Flow
Initialization creates a temporary file from the template `TEST_TEMP_XXXXXX`, wraps it in a `FILE *`, writes fixture lines including `sigma=foo` and comment lines, and rewinds. Cleanup unlinks the temp file. `semanage_utilities_add_tests` registers each utility test and cleans up the CUnit registry if registration fails.

Individual tests allocate mutable strings where the API consumes or returns heap memory. The file-filter test supplies a predicate that keeps lines beginning with `#`. The basename test checks ordinary paths, trailing slash behavior, dot, empty string, and root slash.

## State and Persistence Behavior
The suite owns process-global `fd` and `fptr` plus the temporary filename buffer mutated by `mkstemp`. Most tests allocate and free returned strings/lists. The temporary file remains open for the suite duration and is rewound before repeated lookup/filter tests.

## Dependencies and Integration Points
Dependencies include CUnit, the installed/internal `<utilities.h>` for libsemanage utility APIs, standard C/POSIX I/O, and shared test `utilities.h`. It integrates with the broader test binary through the declared suite hooks.

## Risks and Edge Cases
The cleanup unlinks but does not explicitly close `fptr` or `fd`, relying on process teardown or external runner behavior. `test_semanage_split_on_space` and `test_semanage_split` repeatedly free the previous input string and assign the returned remainder, so API ownership assumptions are central. The registration function uses `CU_cleanup_registry` on failure, affecting all suites in the registry.

## Test Signals
Signals include expected prefix truth values, exact split remainders, list length/order/find behavior, character counts, trim output, full and limited string replacement, config lookup values, exactly two filtered comment lines, and basename edge-case outputs.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_utilities.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_utilities.h -->
# sources/security-integrity/selinux/libsemanage/tests/test_utilities.h

## Purpose
`test_utilities.h` declares CUnit lifecycle hooks for the libsemanage utilities test suite.

## Important APIs, Types, and Functions
It includes `<CUnit/Basic.h>` and declares `semanage_utilities_test_init`, `semanage_utilities_test_cleanup`, and `semanage_utilities_add_tests(CU_pSuite suite)`.

## Control Flow
The header contains declarations only.

## State and Persistence Behavior
It owns no state. Temporary-file setup and cleanup are implemented in `test_utilities.c`.

## Dependencies and Integration Points
The header intentionally has no include guard in the visible file, but its declarations are small and include CUnit for `CU_pSuite`. It connects the utilities suite to the test runner.

## Risks and Test Signals
Lack of an include guard could cause duplicate declarations if included repeatedly in unusual ways, though identical function declarations are generally harmless in C. Runtime signals are produced by `test_utilities.c`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_utilities.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/utilities.c -->
# sources/security-integrity/selinux/libsemanage/tests/utilities.c

## Purpose
`utilities.c` provides shared fixtures and helper functions for libsemanage CUnit suites. It creates a minimal direct policy store, writes binary or CIL policy fixtures, manages the global semanage handle, and wraps common connect/transaction/commit lifecycle steps.

## Important APIs, Types, and Functions
The file defines the global `semanage_handle_t *sh` and helper functions declared in `utilities.h`: `test_msg_handler`, `create_test_store`, `destroy_test_store`, `enable_test_store`, `disable_test_store`, `write_test_policy_from_file`, `write_test_policy_src`, `helper_handle_create`, `helper_handle_destroy`, `helper_connect`, `helper_disconnect`, `helper_begin_transaction`, `helper_commit`, `setup_handle`, `cleanup_handle`, and `setup_handle_invalid_store`.

Internal helper `write_test_policy` writes `policy.kern`. The file uses libsemanage APIs such as `semanage_set_root`, `semanage_handle_create`, `semanage_msg_set_callback`, `semanage_set_create_store`, `semanage_set_reload`, `semanage_set_store_root`, `semanage_select_store`, `semanage_connect`, `semanage_disconnect`, `semanage_begin_transaction`, and `semanage_commit`.

## Control Flow
`create_test_store` constructs `test-policy/store/active/modules` and `test-policy/etc/selinux`, creates an empty `semanage.conf`, and enables test-store mode. Policy-writing helpers write either `store/active/policy.kern` from a file buffer or `store/active/modules/100/base/cil` plus a `lang_ext` marker of `cil`.

`helper_handle_create` optionally points libsemanage at `test-policy`, creates a handle, installs a silent message callback, and, when the test store is enabled, configures direct access to the `"store"` policy store without reload. `setup_handle` advances through null, handle, connected, and transaction states based on `level_t`; `cleanup_handle` unwinds in reverse, committing transactions when needed.

## State and Persistence Behavior
The global `test_store_enabled` controls whether newly created handles target the local fixture store. `destroy_test_store` uses `fts_open`/`fts_read` to recursively remove `test-policy` and disables test-store mode first. `cleanup_handle(SH_TRANS)` commits by design, so tests that need rollback semantics cannot use it directly without custom cleanup.

## Dependencies and Integration Points
Dependencies include POSIX filesystem APIs, FTS traversal, CUnit assertions, and the libsemanage public API. This file is the central integration point for most libsemanage tests in this subset.

## Risks and Edge Cases
Many `mkdir` calls fail if directories already exist, so stale `test-policy` state can prevent suite setup. `write_test_policy_from_file` does not check the return value of `fread`. `destroy_test_store` continues after remove failures and returns `-1` if any deletion failed. `helper_handle_destroy` does not set `sh` to NULL; callers rely on `cleanup_handle` to do that at the end.

## Test Signals
This helper file is validated indirectly by every suite that can create the store, connect, begin transactions, commit, and cleanly remove `test-policy`. Failures surface as suite initialization errors or fatal CUnit assertions in helper calls.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/utilities.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/utilities.h -->
# sources/security-integrity/selinux/libsemanage/tests/utilities.h

## Purpose
`utilities.h` is the shared test support header for libsemanage CUnit suites. It exposes the global handle, common fixture lifecycle functions, and assertion helpers used across object-specific tests.

## Important APIs, Types, and Functions
The header includes standard C/POSIX headers, CUnit, and `semanage/semanage.h`. It defines `CU_ASSERT_CONTEXT_EQUAL`, index constants `I_NULL`, `I_FIRST`, `I_SECOND`, and `I_THIRD`, the global `extern semanage_handle_t *sh`, and `level_t` with states `SH_NULL`, `SH_HANDLE`, `SH_CONNECT`, and `SH_TRANS`.

It declares `test_msg_handler`, handle setup/cleanup helpers, individual helper actions, and test-store functions: `create_test_store`, `write_test_policy_from_file`, `write_test_policy_src`, `destroy_test_store`, `enable_test_store`, and `disable_test_store`.

## Control Flow
The header has no runtime flow, but its `CU_ASSERT_CONTEXT_EQUAL` macro performs context serialization through `semanage_context_to_string`, compares the resulting strings, and frees both buffers. Under `__CHECKER__`, it overrides selected fatal CUnit macros to also call `assert`, improving static-analysis understanding.

## State and Persistence Behavior
The header exposes the process-global handle and the `level_t` lifecycle contract used by `setup_handle` and `cleanup_handle`. Persistence behavior is implemented in `utilities.c`.

## Dependencies and Integration Points
It is included by all libsemanage tests in this subset. It couples tests to CUnit and the libsemanage public handle/context APIs.

## Risks and Test Signals
`CU_ASSERT_CONTEXT_EQUAL` assumes both context-to-string calls succeed and that `sh` is a valid global handle. Macro arguments are evaluated inside the macro and should be side-effect free. The meaningful test signal is broad compile-time and runtime reuse across suites.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/utilities.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/utils/Makefile -->
# sources/security-integrity/selinux/libsemanage/utils/Makefile

## Purpose
This Makefile installs libsemanage utility scripts, currently the `semanage_migrate_store` Python tool, into the SELinux libexec directory.

## Important Targets and Variables
`PREFIX` defaults to `/usr`, `LIBEXECDIR` defaults to `$(PREFIX)/libexec`, and `SELINUXEXECDIR` defaults to `$(LIBEXECDIR)/selinux/`. Targets are `all`, `install`, `clean`, `distclean`, and `relabel`. Only `install` performs work: it creates `$(DESTDIR)$(SELINUXEXECDIR)` and installs `semanage_migrate_store` mode `755`.

## Control Flow
`all`, `clean`, and `relabel` are empty. `distclean` delegates to `clean`. `install` runs after `all`, creates the destination directory with a leading dash to ignore errors, then copies the script with executable permissions.

## State and Persistence Behavior
The Makefile writes only to the installation tree selected by `DESTDIR`, `PREFIX`, and related variables. It does not build generated artifacts.

## Dependencies and Integration Points
It is invoked by the parent libsemanage build. Runtime behavior of the installed utility depends on Python and SELinux bindings, but this Makefile only requires standard `make`, `mkdir`, and `install`.

## Risks and Test Signals
The ignored `mkdir` failure can hide installation-directory problems until the `install` command fails. There is no uninstall target. The test signal is a successful `make -C utils install DESTDIR=...` producing an executable `libexec/selinux/semanage_migrate_store`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/utils/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/utils/semanage_migrate_store -->
# sources/security-integrity/selinux/libsemanage/utils/semanage_migrate_store

## Purpose
`semanage_migrate_store` is a Python 3 utility for migrating SELinux policy stores from the older `/etc/selinux/<store>/modules/active` module layout to the newer `/var/lib/selinux/<store>/active/modules/<priority>` layout. It can migrate one selected store or every store under the old root, optionally clean old modules, and optionally rebuild policy.

## Important APIs, Types, and Functions
Important functions are `copy_file`, `create_dir`, `create_file`, `copy_module`, `disable_module`, `migrate_store`, `rebuild_policy`, and path helpers such as `oldroot_path`, `oldstore_path`, `oldmodules_path`, `newroot_path`, `newstore_path`, `newmodules_path`, `disabledmodules_path`, and `bottomdir_path`.

The script imports Python `os`, `errno`, `shutil`, `sys`, `optparse.OptionParser`, and the SELinux Python bindings `selinux` and `semanage`. CLI options include `--priority`, `--store`, `--debug`, `--clean`, `--norebuild`, `--path`, and `--root`.

## Control Flow
Startup imports SELinux bindings and exits with a diagnostic if unavailable. Main option parsing initializes global settings: `DEBUG`, `PRIORITY`, `TYPE`, `CLEAN`, `NOREBUILD`, `PATH`, `ROOT`, and `TOPPATHS`. It ensures the new root exists, determines stores either from `--store` or by listing the old root, skips entries without an old modules directory, and skips stores whose new active store already exists.

`migrate_store` creates the new active/module/disabled directories, copies `base.pp` specially from the old active root, then walks old top-level files and module files. Top-level files in `TOPPATHS` are copied to the new active store, with `seusers` renamed to `seusers.local`. Module `.pp` files are copied into priority subdirectories as `hll` with `lang_ext` set to `pp`; `.disabled` markers become files in `active/modules/disabled`; stray non-`.pp` module files produce warnings. After migration, `--clean` removes the old modules directory. Unless `--norebuild` is set, `rebuild_policy` opens a direct semanage handle for the current policy type and commits a rebuild transaction.

## State and Persistence Behavior
The script performs privileged filesystem migration. It creates directories with modes `0755` or `0700`, copies store files, creates module `hll` and `lang_ext` files, creates disabled markers, and may delete the old modules directory with `shutil.rmtree`. Rebuild state is persisted through libsemanage transaction commit.

## Dependencies and Integration Points
It integrates old `/etc/selinux` stores, new `/var/lib/selinux` stores, libselinux policy-type discovery, and libsemanage direct-store rebuild. It is installed by `utils/Makefile` into SELinux libexec.

## Risks and Edge Cases
The script exits on most copy/create failures and does not roll back partially migrated stores. It skips stores if the new active directory already exists, even when the old modules directory remains. It treats `base.pp` name conflicts in the module directory as fatal. `copy_module` opens `lang_ext` with `open(path, "w+", 0o600)`, where the third argument is buffering, not file mode, in Python's built-in `open`; actual file permissions depend on normal creation defaults and umask. Running with `--clean` can remove old modules after partial success.

## Test Signals
Signals include printed migration lines, expected new directory layout under `PATH`, copied top-level local files, module subdirectories under the configured priority containing `hll` and `lang_ext`, disabled marker files, warnings for skipped invalid files, and a successful semanage rebuild unless `--norebuild` is used.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/utils/semanage_migrate_store -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/Makefile -->
# sources/security-integrity/selinux/libsepol/Makefile

## Purpose
This top-level libsepol Makefile orchestrates recursive builds, installs, cleaning, relabeling, and tests for the libsepol source tree.

## Important Targets and Variables
`DISABLE_CIL ?= n` controls whether CIL support is disabled and is exported to sub-makes. Targets are `all`, `install`, `relabel`, `clean`, and `test`. `all` builds `src` and `utils`; `install` descends into `include`, `src`, `utils`, and `man`; `relabel` runs only in `src`; `clean` descends into `src`, `utils`, and `tests`; `test` runs `make -C tests test`.

## Control Flow
The file is a simple recursive make dispatcher. Each target invokes `$(MAKE) -C <dir>` in a fixed order.

## State and Persistence Behavior
This Makefile does not directly create artifacts; subdirectories produce libraries, tools, installed files, cleaned outputs, relabeling effects, or test results. Exporting `DISABLE_CIL` affects subdirectory build configuration.

## Dependencies and Integration Points
It integrates libsepol's include, source, utility, manual, and test subtrees. External dependencies are the platform `make` and whatever each child directory requires.

## Risks and Test Signals
Because commands are sequential, an early sub-make failure stops later directories. There is no `.PHONY` declaration in this file, so files named after targets could interfere on some make implementations. Main signals are successful recursive `make`, `make install`, `make clean`, and `make test` invocations.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/include/cil/cil.h -->
# sources/security-integrity/selinux/libsepol/cil/include/cil/cil.h

## Purpose
`cil.h` is the public C API for libsepol's Common Intermediate Language compiler interface. It exposes an opaque `cil_db_t`, compilation entry points, policy/output serialization helpers, configuration setters, logging hooks, and memory-error hook registration.

## Important APIs, Types, and Functions
The header forward-declares `struct cil_db` and typedefs it as `cil_db_t`. Lifecycle and compilation functions are `cil_db_init`, `cil_db_destroy`, `cil_add_file`, `cil_compile`, and `cil_build_policydb`. Side-output functions are `cil_userprefixes_to_string`, `cil_selinuxusers_to_string`, `cil_filecons_to_string`, `cil_write_policy_conf`, `cil_write_parse_ast`, `cil_write_build_ast`, `cil_write_resolve_ast`, and `cil_write_post_ast`.

Configuration setters include `cil_set_disable_dontaudit`, `cil_set_multiple_decls`, `cil_set_qualified_names`, `cil_set_disable_neverallow`, `cil_set_preserve_tunables`, `cil_set_handle_unknown`, `cil_set_mls`, `cil_set_attrs_expand_generated`, `cil_set_attrs_expand_size`, `cil_set_target_platform`, and `cil_set_policy_version`. Neverallow checking against an external policydb is exposed through `cil_check_neverallows_against_pdb`.

Logging support includes `enum cil_log_level`, `cil_set_log_level`, `cil_set_log_handler`, and printf-annotated `cil_log`. `cil_set_malloc_error_handler` lets callers override allocation failure behavior.

## Control Flow
Clients allocate a database with `cil_db_init`, feed one or more CIL files with `cil_add_file`, call `cil_compile`, optionally build a binary `sepol_policydb_t` or serialized side files, then destroy the database with `cil_db_destroy`. AST write helpers represent different pipeline checkpoints and may run parts of the compile pipeline.

## State and Persistence Behavior
The database is opaque and heap-owned by the library. Setter calls mutate compiler behavior inside `cil_db_t`. String conversion helpers allocate output buffers returned through `char **out` and `size_t *size`; callers must free them according to library convention. `cil_build_policydb` returns a libsepol policy database pointer through `sepol_policydb_t **`.

## Dependencies and Integration Points
The header includes `<sepol/policydb/policydb.h>` for `sepol_policydb_t`/`policydb_t` and supports C++ consumers through `extern "C"`. It is implemented primarily by `cil/src/cil.c` and related compiler modules.

## Risks and Test Signals
Callers must respect pipeline ordering: adding files before compile, compiling before binary or policy output where required, and freeing allocated outputs. `cil_set_handle_unknown` is the only setter here that reports invalid input directly. Test signals include successful parse/compile/build-policy flows, correct side-output strings, logging handler invocation, and invalid handle-unknown rejection.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/include/cil/cil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil.c -->
# sources/security-integrity/selinux/libsepol/cil/src/cil.c

## Purpose
`cil.c` is a central implementation file for the CIL compiler core. It initializes global keyword strings, creates and destroys `cil_db`, runs the major parse/build/resolve/post/binary compile phases, serializes selected compiler outputs, maps AST/data flavors to destructors and symbol tables, and provides constructors for most CIL internal data structures.

## Important APIs, Types, and Functions
Public API implementations include `cil_db_init`, `cil_db_destroy`, `cil_add_file`, `cil_compile`, `cil_write_parse_ast`, `cil_write_build_ast`, `cil_write_resolve_ast`, `cil_write_post_ast`, `cil_build_policydb`, `cil_write_policy_conf`, `cil_userprefixes_to_string`, `cil_selinuxusers_to_string`, `cil_filecons_to_string`, and configuration setters such as `cil_set_disable_dontaudit`, `cil_set_disable_neverallow`, `cil_set_attrs_expand_generated`, `cil_set_attrs_expand_size`, `cil_set_preserve_tunables`, `cil_set_handle_unknown`, `cil_set_mls`, `cil_set_multiple_decls`, `cil_set_qualified_names`, `cil_set_target_platform`, and `cil_set_policy_version`.

Internal support includes `cil_init_keys`, `cil_root_init`, `cil_root_destroy`, `cil_destroy_data`, `cil_flavor_to_symtab_index`, `cil_node_to_string`, `cil_symtab_array_init`, `cil_symtab_array_destroy`, `cil_destroy_ast_symtabs`, `cil_get_symtab`, `cil_string_to_uint32`, `cil_string_to_uint64`, `cil_sort_init`, `cil_sort_destroy`, and many `cil_*_init` constructors for AST records including contexts, users, roles, types, classes, booleans, tunables, rules, file contexts, ports, nodes, genfs, hardware contexts, defaults, MLS, and source-info records.

## Control Flow
`cil_db_init` initializes the string pool, interns all CIL keyword tokens via `cil_init_keys`, creates parse and AST trees, initializes root data, sort buckets, side-output lists, special `self`, `notself`, and `other` type records, value lookup arrays, and default compiler options. `cil_add_file` copies caller data into a NUL-padded buffer, invokes `cil_parser`, and frees the temporary buffer.

`cil_compile` runs the standard pipeline: build AST from parse tree, destroy the parse tree, resolve the AST, qualify names, and post-process. The AST write helpers run subsets of the same pipeline and dump parse/build/resolve/post trees with `cil_write_ast`. `cil_build_policydb` delegates to `cil_binary_create`, while `cil_write_policy_conf` delegates to `cil_gen_policy`.

Destructor and mapping functions provide shared infrastructure for the tree/list layers: `cil_destroy_data` switches on `enum cil_flavor` and calls the correct typed destroy helper, `cil_flavor_to_symtab_index` maps declarative flavors to symbol-table slots, and `cil_get_symtab` walks from an AST node to the nearest appropriate root/block/macro/in/conditional symbol table. Constructor functions allocate and zero/default initialize record fields so later parser/build phases can fill strings, datum pointers, expressions, and values.

## State and Persistence Behavior
`cil_db` owns parse/AST trees, sort arrays for context outputs, ordering lists, side-output lists, declared strings, special type datums, and value lookup arrays. `cil_db_destroy` tears these down, destroys the string pool, frees value arrays, and nulls the caller's pointer. Side-output serialization functions allocate buffers for users/prefixes, seusers, and file contexts; they compute lengths first, allocate with `cil_malloc`, and write textual output into caller-returned buffers.

The file does not directly persist to disk except when callers pass `FILE *` to write functions. It mutates global interned-key pointers and the global CIL string pool during database initialization/destruction.

## Dependencies and Integration Points
Dependencies include libsepol policydb/symtab/ebitmap facilities and CIL modules for logging, memory, tree/list/symtab handling, parser, AST build, resolution, fully-qualified names, post-processing, binary generation, policy.conf generation, string pooling, and AST writing. This file is the hub between the public `cil.h` API and internal compiler phases.

## Risks and Edge Cases
The compile pipeline destroys `db->parse`, so parse-tree write operations must happen before full compile or on a fresh database. AST write helpers also consume/destroy parse state as they progress. Side-output functions assume resolved datum pointers and sorted lists are populated correctly before serialization. Many formatting helpers use `sprintf` after manual length calculation, so length bugs would become memory safety issues. The global string-pool lifecycle means multiple independent databases or unusual init/destroy ordering need scrutiny. A duplicated assignment of `CIL_KEY_CONDFALSE` appears in key initialization; it is harmless but suggests manual keyword lists are easy to desynchronize.

## Test Signals
Useful signals include CIL parser/compiler tests that cover successful compile, parse/build/resolve/post AST dumping, binary policy generation, policy.conf generation, MLS and non-MLS user/file-context serialization, invalid numeric parsing, invalid `handle_unknown` values, symbol table lookup from nested AST nodes, and leak/error-path testing across `cil_db_init`/`cil_db_destroy`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/src/cil.c -->
