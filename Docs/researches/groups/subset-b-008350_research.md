# subset-b-008350 research

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/semanage_store.c -->
# sources/security-integrity/selinux/libsemanage/src/semanage_store.c

## Purpose
Implements local SELinux semanage module-store filesystem handling: path initialization, store creation, sandbox/final directory construction, commit promotion, lock management, module path discovery, policydb file I/O, external verifier execution, and file/netfilter context sorting.

## APIs, control flow, and state
`semanage_check_init()` lazily fills global path tables for active, previous, tmp, and final policy locations. `semanage_create_store()`, `semanage_make_sandbox()`, and `semanage_make_final()` prepare persistent and temporary trees. `semanage_install_sandbox()` validates/compiles contexts, calls `semanage_commit_sandbox()`, increments `commit_num`, syncs the sandbox, takes the active lock, renames active to previous, tmp to active, installs final files, optionally reloads policy, and may remove the previous store. File helpers copy via `*.tmp` plus rename, recurse directories, remove directories, and restore SELinux labels/ownership through `semanage_setfiles()`.

## Dependencies and integration
Depends on libselinux paths/restorecon/reload semantics, libsepol policydb/CIL loaders, `database_policydb`, compressed-file mapping, configured external programs (`load_policy`, `setfiles`, `sefcontext_compile`, module/link/kernel verifiers), and handle configuration. `semanage_get_active_modules()` integrates module metadata and selects highest-priority enabled modules.

## Risks and test signals
Global path initialization is explicitly not thread-safe. Cross-device rename fallback is non-atomic. Recursive removal has early-return leak risk on error paths. Context sorting discards comments/blank lines and uses heuristic specificity. Commit rollback can leave an inconsistent store if nested renames/copies fail. Tests in the broader suite cover store access, locking, and netfilter sorting through `test_semanage_store`, but this work item includes only consumers in handle/fcontext tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/semanage_store.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/semanage_store.h -->
# sources/security-integrity/selinux/libsemanage/src/semanage_store.h

## Purpose
Declares the internal module-store contract used by libsemanage direct connections.

## APIs, types, and state
Defines `enum semanage_store_defs` for active/previous/tmp stores, `enum semanage_sandbox_defs` for store-relative artifacts, and final-path enums for installed SELinux policy outputs. Exposes path accessors, store creation/access checks, sandbox/final creation, lock acquisition/release, commit serial lookup, CIL/policydb loading/writing, verifier hooks, context sorting, file copy, and `semanage_setfiles()` configuration.

## Dependencies and integration
Includes `handle.h`, sepol module/CIL types, and public bool/time headers. It is the bridge between handle/direct transaction logic and concrete filesystem paths.

## Risks and test signals
The enum ordering is a persistence ABI for `semanage_store.c` path arrays; adding entries requires synchronized updates to relative-path tables. Callers rely on `semanage_check_init()` before accessing returned const paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/semanage_store.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/seuser_internal.h -->
# sources/security-integrity/selinux/libsemanage/src/seuser_internal.h

## Purpose
Provides private declarations for Unix-login-to-SELinux-user records.

## APIs and integration
Exports `SEMANAGE_SEUSER_RTABLE`, file database init/release functions, and `semanage_seuser_validate_local()`. It ties public `seuser_record`, local/policy APIs, database plumbing, and sepol policydb validation together.

## State and risks
No persistent state is defined here, but declarations couple file-backed local seuser records to policy-backed user validation. `semanage_seuser_validate_local()` requires a transaction-safe context because its implementation performs nested database lookups while iterating.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/seuser_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/seuser_record.c -->
# sources/security-integrity/selinux/libsemanage/src/seuser_record.c

## Purpose
Implements `semanage_seuser_t` and key records for Unix login mappings.

## APIs and control flow
Records contain `name`, `sename`, and optional `mls_range`; keys contain `name`. The file provides key create/extract/free, compare/compare2/qsort comparator, getters/setters for all fields, create/clone/free, and the `SEMANAGE_SEUSER_RTABLE` database method table.

## State and dependencies
All fields are heap strings owned by the record. Setters replace old strings after successful `strdup()`. Clone deep-copies mandatory name and SELinux user plus optional MLS range.

## Risks and test signals
Setters do not accept NULL safely because they call `strdup()`. Cloning assumes source records are fully initialized except for optional MLS. Local seuser tests are indirect in this subset through validation and user deletion dependencies.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/seuser_record.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/seusers_file.c -->
# sources/security-integrity/selinux/libsemanage/src/seusers_file.c

## Purpose
Adds file-backed parsing and printing for seuser mappings.

## APIs and persistence
`seuser_print()` emits `name:sename[:mls]`. `seuser_parse()` consumes colon-separated fields with optional MLS range, skipping blank/end lines and disposing malformed lines. `seuser_file_dbase_init()` binds the generic seuser record table to `SEMANAGE_FILE_DTABLE`.

## Dependencies and integration
Uses `database_file`, `parse_utils`, and `seuser_internal` accessors. The backend persists local login mappings in files such as `seusers.local`.

## Risks and test signals
The MLS parser is noted as not allowing spaces/multiline. Error recovery disposes the current parse line. Formatting has no escaping, so field delimiters in names or ranges are not representable.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/seusers_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/seusers_local.c -->
# sources/security-integrity/selinux/libsemanage/src/seusers_local.c

## Purpose
Implements local CRUD, auditing, and validation for Unix login mappings.

## APIs and control flow
`semanage_seuser_modify_local()` clones incoming data, fills missing MLS range from the target SELinux user when MLS is enabled, queries the previous record with message callbacks muted, writes through `dbase_modify()`, and emits audit records. Delete/query/exists/count/iterate/list are thin local database wrappers. `semanage_seuser_validate_local()` iterates local records and checks referenced SELinux users and MLS containment.

## Dependencies and state
Uses libaudit, sepol MLS checks, policy user APIs, and local/policy databases from the handle. Audit messages include changed sename, role set, and MLS range fields.

## Risks and test signals
Delete audits after `dbase_del()` but then queries the deleted key, which may reduce previous-record detail. Validation comments warn it must run inside a transaction to avoid deadlock/races. MLS fallback depends on a policy user query succeeding.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/seusers_local.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/seusers_policy.c -->
# sources/security-integrity/selinux/libsemanage/src/seusers_policy.c

## Purpose
Provides read-only public policy-view operations for seuser mappings.

## APIs and integration
`semanage_seuser_query`, `exists`, `count`, `iterate`, and `list` all fetch `semanage_seuser_dbase_policy(handle)` and delegate to generic `dbase_*` operations.

## State, risks, and tests
No local persistence is mutated. Correctness depends on the handle selecting a policy database configured by connection setup. Errors and invalid-handle behavior are inherited from the dbase layer.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/seusers_policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/sha256.c -->
# sources/security-integrity/selinux/libsemanage/src/sha256.c

## Purpose
Implements a standalone public-domain SHA-256 hash routine.

## APIs and control flow
`Sha256Initialise()` sets initial constants. `Sha256Update()` buffers input, transforms full 64-byte blocks, and tracks bit length. `Sha256Finalise()` applies padding, appends big-endian bit length, runs the final transform, and writes 32 digest bytes. `Sha256Calculate()` wraps the three-step flow.

## Dependencies and state
Uses only `sha256.h` and memory operations. State lives in caller-owned `Sha256Context`; digest output is caller-owned.

## Risks and test signals
No null-pointer checks are present. The implementation silently returns when `curlen` is invalid rather than reporting failure. It is suitable for checksums/integrity but exposes no constant-time or HMAC features.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/sha256.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/sha256.h -->
# sources/security-integrity/selinux/libsemanage/src/sha256.h

## Purpose
Declares SHA-256 context and digest types plus public hashing functions.

## APIs and state
`Sha256Context` stores total bit length, eight state words, current buffer length, and a 64-byte block buffer. `SHA256_HASH` wraps the 32-byte digest. Exposes initialize/update/finalize and one-shot calculate.

## Dependencies and risks
Includes `stdint.h` and `stdio.h`. The header uses `#pragma once` rather than a traditional include guard. Callers must reinitialize after finalization and provide valid pointers.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/sha256.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/user_base_record.c -->
# sources/security-integrity/selinux/libsemanage/src/user_base_record.c

## Purpose
Adapts sepol user records as the base policy portion of libsemanage users.

## APIs and integration
Defines `semanage_user_base_t` as `sepol_user_t` and wraps sepol key extraction, comparison, name, MLS level/range, role management, create/clone/free. Exports `SEMANAGE_USER_BASE_RTABLE` for generic databases.

## State and risks
State ownership and validation are delegated to libsepol. The method table uses the public `semanage_user_key_free()` from the joined user layer, so key ownership must remain compatible with sepol keys.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/user_base_record.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/user_extra_record.c -->
# sources/security-integrity/selinux/libsemanage/src/user_extra_record.c

## Purpose
Implements the extra, file-backed part of an SELinux user: name plus labeling prefix.

## APIs and state
Provides key extraction via shared user key creation, comparisons, getters/setters, create/clone/free, and `SEMANAGE_USER_EXTRA_RTABLE`. Records own heap strings for `name` and `prefix`.

## Dependencies and risks
Depends on `user_internal` and sepol key compatibility. Setters require non-NULL input. Clone logs source `name` on error, so malformed partially initialized records can affect diagnostics.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/user_extra_record.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/user_internal.h -->
# sources/security-integrity/selinux/libsemanage/src/user_internal.h

## Purpose
Private user database interface for base policy users, extra prefix records, and joined public user records.

## APIs and integration
Declares record tables, file/policydb/join database init/release functions, base and extra record accessors, key unpacking, and join/split routines. It coordinates public users across `users_base_file`, `users_extra_file`, `users_base_policydb`, `users_join`, and local/policy CRUD files.

## State and risks
Defines the split-persistence model: policy user fields live in policydb/base files, while prefixes live in extra files. Callers must keep base and extra names synchronized through the join API.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/user_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/user_record.c -->
# sources/security-integrity/selinux/libsemanage/src/user_record.c

## Purpose
Implements public `semanage_user_t` as a joined record composed of base policy data and extra prefix data.

## APIs and control flow
Key functions wrap sepol user keys. Getters/setters delegate name, prefix, MLS, and roles to base/extra records. `semanage_user_create()` allocates base and extra parts and defaults prefix to `user`. `semanage_user_clone()` deep-copies both parts and synchronizes the shared name. `semanage_user_join()` merges optional base/extra halves, creating defaults for missing halves; `semanage_user_split()` clones both halves for persistence.

## State and dependencies
The joined record owns a cached `name` plus owned base and extra records. Database behavior is exposed through `SEMANAGE_USER_RTABLE`.

## Risks and test signals
`semanage_user_join()` error logging dereferences `record1` for a name even when `record1` may be NULL. Name synchronization is multi-step; partial setter failures leave underlying base/extra mutations possible before the cached name is updated.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/user_record.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/users_base_file.c -->
# sources/security-integrity/selinux/libsemanage/src/users_base_file.c

## Purpose
Parses and prints file-backed base SELinux user records.

## APIs and persistence
`user_base_print()` emits `user NAME roles { ... } [level L range R];`. `user_base_parse()` reads the same grammar, supports braced or unbraced role lists, optional MLS level/range, and semicolon termination. `user_base_file_dbase_init()` binds file storage to the base record table.

## Dependencies and risks
Uses `parse_utils`, ctype scanning, and base record setters. Roles and MLS strings cannot contain unescaped delimiter whitespace/semicolons. Parser mutates the input buffer while tokenizing, so ownership remains with parse infrastructure.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/users_base_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/users_base_policydb.c -->
# sources/security-integrity/selinux/libsemanage/src/users_base_policydb.c

## Purpose
Initializes a policydb-backed database for base SELinux user records.

## APIs and integration
Defines `SEMANAGE_USER_BASE_POLICYDB_RTABLE` with sepol modify/query/count/exists/iterate hooks. `user_base_policydb_dbase_init()` points the policydb layer at active and tmp kernel policy paths. Release delegates to `dbase_policydb_release()`.

## State and risks
Mutations target the tmp kernel policy during transactions and active policy for reads. Add/set are NULL, so behavior is constrained to supported modify/query operations.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/users_base_policydb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/users_extra_file.c -->
# sources/security-integrity/selinux/libsemanage/src/users_extra_file.c

## Purpose
File-backed parser/printer for user extra prefix records.

## APIs and persistence
`user_extra_print()` writes `user NAME prefix PREFIX;`. `user_extra_parse()` validates that grammar and stores parsed name/prefix. Init/release bind the extra record table to `SEMANAGE_FILE_DTABLE`.

## Dependencies and risks
Uses `parse_utils` and `database_file`. Prefix values cannot include semicolons without parser support. Like other file adapters, malformed lines are disposed and returned as parse errors.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/users_extra_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/users_join.c -->
# sources/security-integrity/selinux/libsemanage/src/users_join.c

## Purpose
Configures a joined database that presents base and extra user records as one `semanage_user_t`.

## APIs and integration
`SEMANAGE_USER_JOIN_RTABLE` points at `semanage_user_join()` and `semanage_user_split()`. `user_join_dbase_init()` combines two existing dbase configs with `dbase_join_init()`, while release delegates to `dbase_join_release()`.

## Risks and state
Correctness depends on both child databases sharing comparable keys and on join/split preserving name consistency. This file holds no state itself.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/users_join.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/users_local.c -->
# sources/security-integrity/selinux/libsemanage/src/users_local.c

## Purpose
Implements local SELinux user CRUD against the joined local database.

## APIs and control flow
Modify/query/exists/count/iterate/list are dbase wrappers. Delete first calls `lookup_seuser()` to reject removal of a SELinux user still referenced by local login records, then calls `dbase_del()`.

## Dependencies and risks
Depends on joined user local database and local seuser list. `lookup_seuser()` ignores the return from `semanage_seuser_list_local()`, so failures there may leave `records/count` undefined. Deletion safety is important for integrity of login mappings.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/users_local.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/users_policy.c -->
# sources/security-integrity/selinux/libsemanage/src/users_policy.c

## Purpose
Provides read-only policy-view operations for joined SELinux user records.

## APIs and integration
`semanage_user_query`, `exists`, `count`, `iterate`, and `list` delegate to the policy user database selected by the handle.

## State and risks
No persistence is changed here. Behavior is only as strong as policy database initialization, record join integrity, and generic dbase validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/users_policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/utilities.c -->
# sources/security-integrity/selinux/libsemanage/src/utilities.c

## Purpose
General helper library for string parsing, simple linked lists, file slurping, robust writes, and basename.

## APIs and control flow
`semanage_findval()` scans a file for a variable prefix and returns text after a delimiter. Split/prefix/rtrim/count helpers support configuration parsing. List helpers push unique strings, pop, destroy, find, and qsort nodes. `semanage_str_replace()` allocates a replacement string with optional occurrence limit. `semanage_slurp_file_filter()` stores accepted lines without duplicating after getline ownership transfer. `write_full()` retries short/EINTR writes.

## Dependencies and risks
Uses libc I/O, asserts, and errno. `semanage_list_sort()` dereferences `(*l)->next` when `*l` is NULL, so callers must pass a non-empty list. `semanage_str_replace()` assumes non-NULL inputs and can underflow size arithmetic if replacement is shorter without careful unsigned reasoning.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/utilities.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/utilities.h -->
# sources/security-integrity/selinux/libsemanage/src/utilities.h

## Purpose
Declares libsemanage utility helpers and the `semanage_list_t` string-list type.

## APIs and integration
Exposes parsing helpers, list operations, string counting/trimming/replacement, whitespace truncation, filtered slurp, `write_full()`, and portable `semanage_basename()`. `WARN_UNUSED` annotates functions where ignoring failures is risky.

## State and risks
The list type owns `data` strings for normal push/pop/destroy flows, but `semanage_slurp_file_filter()` deliberately transfers getline buffers into list nodes. Callers must free returned strings/lists according to the producing API.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/src/utilities.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/Makefile -->
# sources/security-integrity/selinux/libsemanage/tests/Makefile

## Purpose
Builds and runs the libsemanage CUnit test binary and compiles test CIL policies.

## Targets and dependencies
`SOURCES` and `CILS` are wildcard-driven. `all` builds `libsemanage-tests` and `.policy` outputs from `.cil` inputs via `../../secilc/secilc`. The test executable links every object with `../src/libsemanage.a` and `-lcunit -lbz2 -laudit -lselinux -lsepol`. `test` runs the binary.

## Risks and test signals
Wildcard ordering is sorted for determinism. Tests depend on local secilc, static libsemanage, and system SELinux/audit/sepol libraries. No parallel-test isolation is defined in this Makefile.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/libsemanage-tests.c -->
# sources/security-integrity/selinux/libsemanage/tests/libsemanage-tests.c

## Purpose
Main CUnit runner for libsemanage unit tests.

## Control flow
`DECLARE_SUITE` registers each suite with init/cleanup and add-tests functions. `do_tests()` initializes CUnit, registers store, utilities, handle, boolean, fcontext, iface, ibendport, node, port, user, and other suites, selects basic verbose/normal or console mode, runs tests, and returns success only when CUnit has no error and zero failed tests. `main()` parses `-v/--verbose` and `-i/--interactive`.

## Dependencies and risks
Depends on every suite header and CUnit Basic/Console APIs. Verbose defaults to enabled. A suite registration failure cleans up and propagates CUnit errors.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/libsemanage-tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_bool.c -->
# sources/security-integrity/selinux/libsemanage/tests/test_bool.c

## Purpose
CUnit coverage for boolean record, policy, and local transaction APIs.

## Control flow and fixtures
Suite setup creates a test store and writes `test_bool.policy`; cleanup destroys it. Helpers fetch policy booleans, keys, and create/delete local overrides. Tests cover key creation/extraction, compare/compare2, name/value setters, create/clone, policy query/exists/count/iterate/list, and local modify/delete/query/exists/count/iterate/list.

## State and persistence
Policy booleans are read from the test policy. Local boolean changes are only expected to succeed in transaction mode; transactional tests commit and reopen transactions to verify file persistence.

## Risks and signals
Tests intentionally exercise invalid handle state and NULL output arguments for some APIs. `helper_bool_key_extract()` defines unused invalid modes but only runs the valid indexed case, leaving NULL behavior less covered.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_bool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_bool.h -->
# sources/security-integrity/selinux/libsemanage/tests/test_bool.h

## Purpose
Declares the boolean CUnit suite interface.

## APIs and integration
Exports `boolean_test_init()`, `boolean_test_cleanup()`, and `boolean_add_tests(CU_pSuite)`. Includes CUnit Basic and public semanage header so the runner can register the suite.

## Risks
No state here; suite naming must match `DECLARE_SUITE(boolean)` in the test runner.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_bool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_fcontext.c -->
# sources/security-integrity/selinux/libsemanage/tests/test_fcontext.c

## Purpose
CUnit coverage for file-context record, policy, and local APIs.

## Control flow and fixtures
Setup creates the test store, writes `test_fcontext.policy`, and manually writes three file_contexts lines into `test-policy/store/active/file_contexts`. Tests cover compare ordering, keys, expression/type/context setters, type-string names, create/clone, policy query/exists/count/iterate/list, and local modify/delete/query/exists/count/iterate/list.

## State and persistence
Local fcontext changes are rejected in connected mode and accepted in transactions. Transaction tests commit and reopen before checking local query persistence.

## Risks and signals
The fixture directly writes the active file_contexts file, so failures can indicate store layout drift. Tests cover nonexistent expression/type combinations and invalid handle/list arguments, but not parser malformed-line behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_fcontext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_fcontext.h -->
# sources/security-integrity/selinux/libsemanage/tests/test_fcontext.h

## Purpose
Declares the file-context CUnit suite interface.

## APIs and integration
Exports init, cleanup, and add-tests functions consumed by `libsemanage-tests.c`.

## Risks
No runtime state. Function names must remain synchronized with the runner macro invocation `DECLARE_SUITE(fcontext)`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_fcontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_handle.c -->
# sources/security-integrity/selinux/libsemanage/tests/test_handle.c

## Purpose
CUnit coverage for semanage handle lifecycle and configuration-facing operations.

## Control flow and fixtures
Setup creates a test store and writes `test_handle.policy`. Tests cover handle create/destroy, connect/disconnect, transaction begin/commit, connection-state checks, access checks, managed-store detection, MLS enabled queries, message callback installation/removal, root setters, and store selection for valid/invalid connection types.

## State and persistence
Uses shared test helpers to create handles at null, raw handle, connected, and transaction levels. Store selection tests connect to direct stores and reject policy server modes.

## Risks and signals
Callback test verifies exactly one emitted error message from an invalid commit. Root changes are global process state, so ordering with other suites matters if tests are parallelized.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_handle.h -->
# sources/security-integrity/selinux/libsemanage/tests/test_handle.h

## Purpose
Declares the handle CUnit suite interface.

## APIs and integration
Exports `handle_test_init()`, `handle_test_cleanup()`, and `handle_add_tests(CU_pSuite)`.

## Risks
No persistent state, but the declarations must remain aligned with `DECLARE_SUITE(handle)`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_handle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_ibendport.c -->
# sources/security-integrity/selinux/libsemanage/tests/test_ibendport.c

## Purpose
CUnit coverage for InfiniBand endport policy and local APIs.

## Control flow and fixtures
Setup creates a test store and writes `test_ibendport.policy`. Helpers retrieve policy records/keys and add/delete local overrides. Tests cover policy query/exists/count/iterate/list and local modify/delete/query/exists/count/iterate/list.

## State and persistence
Policy fixtures define three endports with device names, ports, and contexts. Local tests run in transaction mode, commit/reopen for one query path, and verify local counts as records are added/deleted.

## Risks and signals
Iteration tests verify normal traversal, handler error propagation, and handler-requested break. Tests compare device names, ports, and contexts, but record creation/setter unit coverage is likely in separate files outside this subset.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_ibendport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_ibendport.h -->
# sources/security-integrity/selinux/libsemanage/tests/test_ibendport.h

## Purpose
Declares the InfiniBand endport CUnit suite interface.

## APIs and integration
Exports `ibendport_test_init()`, `ibendport_test_cleanup()`, and `ibendport_add_tests(CU_pSuite)`.

## Risks
No runtime state. Names must remain synchronized with `DECLARE_SUITE(ibendport)` in the runner.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/tests/test_ibendport.h -->
