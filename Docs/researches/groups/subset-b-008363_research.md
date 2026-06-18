# Research Report: subset-b-008363

This grouped report covers SELinux libsepol CIL unit tests, fuzzing harnesses, installed public headers, policydb internal headers, makefiles, and selected core implementation files. Each source file has a source-tree-aligned section delimited for reconciliation into its mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_resolve_ast.h -->
# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_resolve_ast.h

Purpose: Declares the CuTest test surface for CIL AST/name resolution. It is not implementation code; it is the registration contract for a very broad set of resolver unit tests.

Important APIs and functions: The header exports prototypes for `test_cil_resolve_name`, `test_cil_resolve_ast_curr_null_neg`, resolver cases for role/type/user/MLS/category/class/permission constructs, `call`, `boolif`, `tunif`, context/net/file object contexts, expression-stack evaluation, optional disabling, and many `__cil_resolve_ast_node_helper` paths. Each test takes `CuTest *`.

Control flow: No executable flow exists here. The unit-test runner includes this header, binds the declared functions into suites, and the implementations construct CIL AST fixtures and assert resolver return codes.

State and persistence: The header owns no state. Test implementations exercise transient CIL databases, AST nodes, symbol tables, macro/call stacks, optional stacks, and resolved datum pointers.

Dependencies and integration points: Includes `CuTest.h`; pairs with CIL unit-test implementation files and internal resolver code under `cil/src`.

Risks: Because this header is a large manual declaration list, duplicate or missing prototypes can silently hide unregistered coverage. It has a duplicated `test_cil_resolve_call1_level` and repeated userlevel helper prototypes, signaling historical drift.

Test signals: Successful CIL unit-test build, suite registration for every prototype, and negative tests returning expected resolver errors are the validation signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_resolve_ast.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_symtab.c -->
# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_symtab.c

Purpose: Implements a focused CuTest for inserting a block datum into a CIL symbol table.

Important APIs and functions: `test_cil_symtab_insert()` calls `cil_tree_node_init`, `cil_db_init`, `cil_symtab_array_init`, `cil_get_symtab`, and `cil_symtab_insert`. It asserts `SEPOL_OK`.

Control flow: The test allocates a `cil_block`, creates a test AST node and database, attaches the node under the database root, initializes the block symbol table array, fetches the root block symbol table, and inserts the block under key `"test"`.

State and persistence: State is in heap-allocated CIL objects and the db root symbol table. The test does not persist policy data and does not explicitly free all allocations, which is acceptable only for short-lived test processes.

Dependencies and integration points: Includes public `sepol/policydb/policydb.h`, CuTest, and internal `cil_tree.h`, `cil_symtab.h`, and `cil_internal.h`.

Risks: The test validates only the success path, not duplicate insertion, invalid keys, cleanup, or null inputs. Manual heap allocation without full cleanup can obscure leak checks.

Test signals: Passing assertion on `SEPOL_OK` and no crash during CIL db/tree setup indicate the symtab insertion path remains usable.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_symtab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_symtab.h -->
# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_symtab.h

Purpose: Declares the CuTest entry point for CIL symbol-table insertion coverage.

Important APIs and types: Exposes `void test_cil_symtab_insert(CuTest *)` and includes `CuTest.h`.

Control flow: No runtime logic exists. The test runner uses this prototype to register the implementation from `test_cil_symtab.c`.

State and persistence: No state is declared. All tested state is transient CIL database and symbol-table memory created by the implementation.

Dependencies and integration points: It is consumed by the CIL unit-test suite and must remain synchronized with `test_cil_symtab.c`.

Risks: Any rename mismatch breaks compilation or silently drops coverage if suite registration is manually maintained elsewhere.

Test signals: Build success and execution of `test_cil_symtab_insert` confirm this header contract.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_symtab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_tree.c -->
# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_tree.c

Purpose: Implements CuTest coverage for basic CIL tree allocation and initialization.

Important APIs and functions: `test_cil_tree_node_init()` validates `cil_tree_node_init`; `test_cil_tree_init()` validates `cil_tree_init`. Both assert null child/parent/data/next fields and zeroed flavor/line state.

Control flow: Each test creates a tree node or tree, inspects initialized fields, asserts expected defaults, then frees the top-level allocation.

State and persistence: State is heap-only and short lived. `test_cil_tree_init` checks the root node attached to the allocated `struct cil_tree`, but only frees `test_tree`; deeper cleanup depends on allocation layout and the broader test process.

Dependencies and integration points: Includes public `policydb.h`, CuTest, the local header, and internal `cil_tree.h`.

Risks: Tests cover only pristine initialization, not child insertion, destruction, traversal, parse data attachment, or allocation failure.

Test signals: Passing null/zero default assertions catch regressions in constructor initialization that would destabilize parser and resolver code.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_tree.h -->
# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_tree.h

Purpose: Declares CuTest entry points for CIL tree initialization tests.

Important APIs and types: Exposes `test_cil_tree_node_init(CuTest *)` and `test_cil_tree_init(CuTest *)`.

Control flow: No executable logic exists. It lets the suite driver compile against the implementations in `test_cil_tree.c`.

State and persistence: No state is owned. The implementations allocate transient tree structures.

Dependencies and integration points: Depends only on `CuTest.h` and is part of the CIL unit-test build.

Risks: Header/implementation drift would break the unit-test target or omit a test during suite registration.

Test signals: Compilation and invocation of both tests validate the header surface.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_integration.c -->
# sources/security-integrity/selinux/libsepol/cil/test/unit/test_integration.c

Purpose: Provides integration tests comparing secilc-generated policy output with checkpolicy output and compiling a minimal CIL policy.

Important APIs and functions: `test_integration()` invokes `system()` for `./secilc -M -c 24 test/integration.cil`, `checkpolicy -M -c 24 -o policy.conf.24 test/policy.conf`, and `sediff -q policy.24 ; policy.conf.24`; `test_min_policy()` invokes secilc on `test/policy.cil`.

Control flow: Each command is run through the shell with output redirected to `/dev/null`; signal exits for SIGINT/SIGQUIT print diagnostics; CuTest asserts normal exit and status zero.

State and persistence: Commands create or consume policy artifacts in the working directory, especially `policy.24` and `policy.conf.24`. No cleanup is performed here.

Dependencies and integration points: Requires built `secilc`, external `checkpolicy` and `sediff`, and test policy files.

Risks: Shell redirection is non-portable to non-sh shells, and command availability/path assumptions make this more environment-sensitive than pure unit tests.

Test signals: Zero exit from secilc, checkpolicy, and sediff indicates CIL compilation matches reference policy semantics for the fixture.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_integration.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_integration.h -->
# sources/security-integrity/selinux/libsepol/cil/test/unit/test_integration.h

Purpose: Declares the CIL integration test entry points.

Important APIs and types: Exposes `test_min_policy(CuTest *)` and `test_integration(CuTest *)`.

Control flow: No logic exists in the header; it is a suite registration contract for `test_integration.c`.

State and persistence: No state is declared. The implementations create policy files by running external compilers.

Dependencies and integration points: Depends on `CuTest.h` and the CIL test runner.

Risks: Prototype drift breaks builds or loses integration coverage.

Test signals: The suite compiles and both commands are run by the test binary.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/cil/test/unit/test_integration.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/fuzz/binpolicy-fuzzer.c -->
# sources/security-integrity/selinux/libsepol/fuzz/binpolicy-fuzzer.c

Purpose: Defines a libFuzzer harness for binary SELinux policy images and module/base policy processing.

Important APIs and functions: `LLVMFuzzerTestOneInput()` drives `policydb_init`, `policydb_read`, `policydb_load_isids`, `policydb_optimize`, external `policydb_validate`, `check_assertions`, `hierarchy_check_constraints`, `policydb_write`, kernel-to-conf/CIL conversion, `link_modules`, and `expand_module`. `write_binary_policy()` wraps `policydb_write` to a `FILE`.

Control flow: The input is exposed as a memory `policy_file`; parse failures exit quietly. Valid kernel policies are optimized/validated/written/converted. Base policies are linked, expanded into `out`, checked, written, and converted.

State and persistence: State is local `policydb_t`, output policydb, SID table, and `/dev/null` stream. Cleanup destroys policydbs and SID table on all exits.

Dependencies and integration points: Exercises libsepol binary reader, module linker/expander, assertion and hierarchy checks, and CIL/conf emitters.

Risks: Calls `abort()` on internal invariant failures, intentionally turning unexpected successful parse plus failed write/convert/validate into fuzzer findings. Null handle paths must tolerate diagnostics.

Test signals: Fuzzer crashes, sanitizer reports, timeouts, and corpus coverage over kernel/base/module policy branches are key signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/fuzz/binpolicy-fuzzer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/fuzz/secilc-fuzzer.c -->
# sources/security-integrity/selinux/libsepol/fuzz/secilc-fuzzer.c

Purpose: Defines a libFuzzer harness for secilc/CIL source parsing, compilation, policydb generation, optimization, and binary writing.

Important APIs and functions: `LLVMFuzzerTestOneInput()` configures a `cil_db`, calls `cil_add_file`, `cil_compile`, `cil_build_policydb`, `sepol_policydb_optimize`, `sepol_policy_file_create`, `sepol_policy_file_set_fp`, and `sepol_policydb_write`. `log_handler()` suppresses CIL log output.

Control flow: Fuzzer bytes are treated as an in-memory file named `"fuzz"`. Any parser/compiler/optimizer/write failure exits normally; only memory-safety bugs or unexpected crashes are findings.

State and persistence: Transient CIL db and `sepol_policydb_t` are freed at exit. Binary output goes to `/dev/null`; no corpus-derived files persist.

Dependencies and integration points: Integrates CIL public API, policydb public API, and the writer path.

Risks: It uses maximum policy version and default SELinux target, so alternative targets/options need separate fuzzing if desired. Silent normal exits require coverage tooling to prove deep paths are reached.

Test signals: libFuzzer coverage, sanitizer findings, and stable cleanup under malformed CIL are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/fuzz/secilc-fuzzer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/Makefile -->
# sources/security-integrity/selinux/libsepol/include/Makefile

Purpose: Installs libsepol public headers into a destination include tree.

Important APIs and targets: The `install` target creates `$(INCDIR)`, `$(INCDIR)/policydb`, and `$(INCDIR)/cil`, then installs `sepol/*.h`, `sepol/policydb/*.h`, and CIL public headers from `$(CILDIR)/include/cil/*.h`.

Control flow: `all` is empty; `install` performs directory checks and `install -m 644` copies. Variables include `PREFIX`, `INCDIR`, and `CILDIR`.

State and persistence: The makefile writes only installation artifacts under `$(DESTDIR)$(PREFIX)/include/sepol`.

Dependencies and integration points: Used by distro/package builds and top-level libsepol install flows. It bridges libsepol and CIL public header installation.

Risks: `wildcard` expansion can silently omit headers if paths are wrong. Install mode and destination layout are ABI/API visible to downstream builds.

Test signals: `make install DESTDIR=...` followed by compile tests using installed headers validates the contract.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/boolean_record.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/boolean_record.h

Purpose: Declares the opaque public record API for SELinux booleans.

Important APIs and types: Defines opaque `sepol_bool_t` and `sepol_bool_key_t`. Exports key create/unpack/extract/free, compare/compare2, name and value getters/setters, create/clone/free.

Control flow: The API is object-style: create a record or key, mutate fields, pass it to collection APIs in `booleans.h`, then free it.

State and persistence: Records hold name and integer value in implementation-owned heap memory. Persistence occurs only when a record is applied to a `sepol_policydb_t`.

Dependencies and integration points: Depends on `sepol_handle_t` for diagnostics/allocation errors and is consumed by `booleans.c` and external policy manipulation tools.

Risks: Value validity is not enforced by the setter; collection update validates 0/1 later. Callers must manage ownership and free cloned keys/records.

Test signals: Round-trip create/set/clone/free plus policydb query/set tests validate this header.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/boolean_record.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/booleans.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/booleans.h

Purpose: Declares public policydb collection operations for SELinux booleans.

Important APIs and functions: `sepol_bool_set`, `sepol_bool_count`, `sepol_bool_exists`, `sepol_bool_query`, and `sepol_bool_iterate`. Iterator callbacks return negative for error, positive to stop, or zero to continue.

Control flow: Callers build a key/record with `boolean_record.h`, query or update a `sepol_policydb_t`, and iteration materializes one temporary record per boolean.

State and persistence: `sepol_bool_set` mutates boolean state inside the policydb and triggers conditional rule re-evaluation in the implementation.

Dependencies and integration points: Depends on public policydb, boolean record, and handle APIs; implemented by `src/booleans.c`.

Risks: Boolean changes affect conditional AV rules, so failures during reevaluation can leave callers with an error path to handle. Iterator callbacks must not retain freed temporary records without cloning.

Test signals: Count/existence/query/set plus conditional rule state changes after set are important tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/booleans.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/context.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/context.h

Purpose: Declares public validation helpers for SELinux contexts and MLS strings.

Important APIs and functions: Deprecated `sepol_check_context`, plus `sepol_context_check`, `sepol_mls_contains`, and `sepol_mls_check`.

Control flow: Callers create or parse `sepol_context_t` records, then validate them against a loaded `sepol_policydb_t`; MLS helpers compare/check string forms against policy MLS definitions.

State and persistence: Functions do not persist state except for deprecated compatibility paths that operate through service-layer global policy/SID state.

Dependencies and integration points: Depends on `context_record.h`, `policydb.h`, and `handle.h`; implementation bridges public records to internal `context_struct_t`.

Risks: Deprecated `sepol_check_context` depends on global service state and is harder to reason about. MLS presence must match whether the policydb is MLS-enabled.

Test signals: Valid/invalid user:role:type[:mls] records, MLS disabled/enabled cases, and deprecated compatibility calls provide coverage.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/context_record.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/context_record.h

Purpose: Declares the opaque public record API for SELinux security contexts.

Important APIs and types: Defines `sepol_context_t` and exports user/role/type/MLS getters and setters, create/clone/free, `sepol_context_from_string`, and `sepol_context_to_string`.

Control flow: Callers build contexts field-by-field or parse colon-separated strings; policy-aware validation is delegated to `context.h`.

State and persistence: The implementation stores heap-duplicated strings for user, role, type, and optional MLS. Records by themselves are not persisted in policydb collections.

Dependencies and integration points: Depends on `sepol_handle_t`; used by node/port/interface/user APIs and internal context conversion.

Risks: Setters expect non-null strings. String parsing accepts three or four components but does not validate policy existence; callers need `sepol_context_check`.

Test signals: Parse/to-string round trips, clone/free, optional MLS handling, and malformed strings validate this surface.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/context_record.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/debug.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/debug.h

Purpose: Declares public libsepol messaging and legacy debug controls.

Important APIs and symbols: Defines message levels `SEPOL_MSG_ERR`, `SEPOL_MSG_WARN`, `SEPOL_MSG_INFO`; exports deprecated `sepol_debug`, getters for message level/channel/file name, and `sepol_msg_set_callback` with printf-style callback annotation.

Control flow: Callers install or suppress a callback on a `sepol_handle_t`; internal `ERR/WARN/INFO` macros route diagnostics through that handle.

State and persistence: Callback pointer and argument live in the handle. Deprecated debug state is process-global compatibility behavior.

Dependencies and integration points: Central to diagnostics across policydb parsing, linking, context conversion, and record APIs.

Risks: Passing NULL suppresses messages, which can hide parse causes. Callback format handling must remain ABI-compatible and variadic-safe.

Test signals: Error-path tests with custom callbacks should observe expected level/channel/file metadata and formatted messages.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/errcodes.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/errcodes.h

Purpose: Defines shared libsepol status and error-code constants.

Important APIs and symbols: `SEPOL_OK`, legacy `SEPOL_ERR`, `SEPOL_ENOTSUP`, `SEPOL_EREQ`, and errno-mapped `SEPOL_ENOMEM`, `SEPOL_EEXIST`, `SEPOL_ENOENT`.

Control flow: No logic exists. Functions throughout libsepol return these values for success, allocation failure, duplicate entries, missing entries, and unsupported requests.

State and persistence: No state.

Dependencies and integration points: Includes `<errno.h>` and is used by policydb, hashtab, avtab, CIL tests, and public APIs.

Risks: Negative errno mapping is part of API behavior. Mixing these constants with internal `STATUS_ERR` conventions requires careful translation at public boundaries.

Test signals: Unit tests should assert exact return values for duplicate/missing/allocation-style paths where API documentation promises them.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/errcodes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/handle.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/handle.h

Purpose: Declares the opaque libsepol handle API used for diagnostics and option flags.

Important APIs and functions: `sepol_handle_create/destroy`, dontaudit getters/setters, `sepol_set_expand_consume_base`, and preserve-tunables getters/setters.

Control flow: Callers create a handle, configure policy transformation options, pass it into operations, and destroy it after use.

State and persistence: The handle stores per-operation options and message callback metadata. It does not persist policy data by itself.

Dependencies and integration points: Used by nearly every public API that can report errors or honor policy expansion flags.

Risks: Null handles are accepted in many internal paths but lose user diagnostics. Option semantics affect module expansion output and must be set before operations that consume them.

Test signals: Handle lifecycle, callback behavior, dontaudit/preserve-tunable option effects, and consume-base expansion behavior validate this API.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/handle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/ibendport_record.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/ibendport_record.h

Purpose: Declares the public record/key API for InfiniBand end port security contexts.

Important APIs and types: Opaque `sepol_ibendport_t` and key type; compare/key create/unpack/extract/free; device-name allocation/get/set, port get/set, context get/set, create/clone/free.

Control flow: Keys are formed from IB device name plus port. Records carry the same identity and a `sepol_context_t`.

State and persistence: Record state is heap-owned until applied to a policydb through `ibendports.h`.

Dependencies and integration points: Depends on context records and handles; maps to `OCON_IBENDPORT` internals in policydb.

Risks: Device names have policydb maximum-length constraints enforced lower down. Context ownership must be clear when setting/cloning records.

Test signals: Key round trips, modify/query through policydb, clone/free, and invalid device/port cases are useful tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/ibendport_record.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/ibendports.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/ibendports.h

Purpose: Declares collection operations for InfiniBand end port entries in a policydb.

Important APIs and functions: `sepol_ibendport_count`, `exists`, `query`, `modify`, and `iterate`.

Control flow: Callers create keys/records with `ibendport_record.h`, then query or upsert entries in the policydb object-context list.

State and persistence: `modify` mutates policydb ocontext state; query/iterate materialize public record copies.

Dependencies and integration points: Integrates public policydb, handle, and IB end port record APIs. Internally corresponds to SELinux `ibendportcon`.

Risks: Range and identity uniqueness must match kernel policy semantics. Iterator callback ownership mirrors other record APIs: temporary records should be cloned if retained.

Test signals: Count/query/modify/iterate against policies with `ibendportcon` entries validate behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/ibendports.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/ibpkey_record.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/ibpkey_record.h

Purpose: Declares the public record/key API for InfiniBand partition key ranges.

Important APIs and types: Opaque `sepol_ibpkey_t` and key type; key creation from subnet prefix plus low/high pkey, compare helpers, range setters/getters, subnet prefix string/byte accessors, context accessors, create/clone/free.

Control flow: Callers build a range identity, attach a context, and pass it to collection operations in `ibpkeys.h`.

State and persistence: Records store a subnet prefix, pkey range, and context. Persistence happens only when modifying a policydb.

Dependencies and integration points: Uses `stdint.h`, context records, and handles; maps to `OCON_IBPKEY` policydb entries.

Risks: String subnet prefix parsing and byte-order representation must be consistent with binary policy and kernel expectations. Range bounds need validation.

Test signals: String/byte prefix round trips, low/high range handling, and query/modify in policydb are key tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/ibpkey_record.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/ibpkeys.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/ibpkeys.h

Purpose: Declares policydb collection operations for InfiniBand pkey contexts.

Important APIs and functions: `sepol_ibpkey_count`, `exists`, `query`, `modify`, and `iterate`.

Control flow: Keys identify subnet-prefix/pkey ranges; collection functions search or mutate the policydb object-context structures and return public records.

State and persistence: `modify` persists changes in the in-memory policydb until the caller writes it. Other operations are read-only.

Dependencies and integration points: Depends on `policydb.h`, `handle.h`, and `ibpkey_record.h`; integrates with SELinux `ibpkeycon` policy handling.

Risks: Overlapping pkey ranges and prefix normalization are subtle policy correctness cases. Callback-return conventions must be honored.

Test signals: Policies with multiple pkey ranges, overlapping/missing queries, and iteration early exit/error paths provide coverage.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/ibpkeys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/iface_record.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/iface_record.h

Purpose: Declares the public record/key API for network interface contexts.

Important APIs and types: Opaque `sepol_iface_t` and key type; key create/unpack/extract/free; compare helpers; name get/set; interface and message context get/set; create/clone/free.

Control flow: Interface records represent `netifcon` entries with two contexts: one for the interface and one for received packets/messages.

State and persistence: Records own name/context fields until applied to policydb collection APIs.

Dependencies and integration points: Depends on context records and handles; collection APIs live in `interfaces.h`.

Risks: Two-context ownership can be confused by callers. Name identity must match policydb string keys exactly.

Test signals: Round-trip name/key behavior, both context fields, clone/free, and policydb query/modify validate the contract.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/iface_record.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/interfaces.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/interfaces.h

Purpose: Declares public collection operations for network interface policy entries.

Important APIs and functions: `sepol_iface_count`, `exists`, `query`, `modify`, and `iterate`.

Control flow: Functions search or mutate the policydb `OCON_NETIF` list using keys from `iface_record.h`.

State and persistence: `modify` updates in-memory policydb state; write APIs are needed for persistence to binary policy.

Dependencies and integration points: Depends on public policydb, interface record, and handle APIs; connects external tools to SELinux `netifcon` data.

Risks: Interface names are environment-specific but policydb entries are static. Iterator callback ownership and error propagation mirror the other collection APIs.

Test signals: Query/modify of policies with interface and packet contexts, iteration early stop, and missing-key behavior are important.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/interfaces.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/kernel_to_cil.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/kernel_to_cil.h

Purpose: Declares conversion APIs from an in-memory kernel policydb to CIL text.

Important APIs and functions: `sepol_kernel_policydb_to_cil(FILE *out, struct policydb *pdb)` and `sepol_kernel_policydb_decls_to_cil(FILE *out, struct policydb *pdb)`.

Control flow: Callers provide a populated kernel `policydb` and output stream; implementation walks policy symbols/rules and emits CIL.

State and persistence: No state is declared. Output is persisted only through the supplied `FILE`.

Dependencies and integration points: Includes `policydb/policydb.h`; used by tools and the binary policy fuzzer to exercise text emission.

Risks: Header lacks include guards and uses `FILE` while including `<stdlib.h>` rather than `<stdio.h>`, relying on prior includes in many build contexts.

Test signals: Conversion of valid kernel policies, round-trip comparison with expected CIL, and fuzzer execution validate this contract.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/kernel_to_cil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/kernel_to_conf.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/kernel_to_conf.h

Purpose: Declares conversion from an in-memory kernel policydb to policy.conf text.

Important APIs and functions: `sepol_kernel_policydb_to_conf(FILE *fp, struct policydb *pdb)`.

Control flow: Caller supplies an output stream and kernel policydb; implementation emits checkpolicy-style configuration text.

State and persistence: No state is owned. Generated text persists in the caller-provided stream.

Dependencies and integration points: Includes internal policydb definitions and is used by tools/fuzzers to check decompilation paths.

Risks: Like `kernel_to_cil.h`, it lacks an include guard and relies on `FILE` availability from included headers or transitive includes.

Test signals: Conversion success for representative kernel policies and comparison against parseable/conf-equivalent output are primary tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/kernel_to_conf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/module.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/module.h

Purpose: Declares public APIs for SELinux module packages and module link/expand operations.

Important APIs and types: Opaque `sepol_module_package_t`; create/free; getters/setters for file contexts, seusers, user_extra, netfilter contexts; policy getter; package read/write/info; `sepol_link_packages`, `sepol_link_modules`, and `sepol_expand_module`.

Control flow: Callers read packages, optionally link multiple modules into a base, expand to a kernel policydb, and write packages or policydb output.

State and persistence: Module packages own policydb plus ancillary text buffers. Writes persist to `sepol_policy_file_t`.

Dependencies and integration points: Ties public handle/policydb APIs to internal module representation and linker/expander.

Risks: Setters taking `char *data` raise ownership questions that callers must follow from implementation docs. Link/expand options can consume base policy depending on handle settings.

Test signals: Package read/write round trips, module info extraction, link failures, and expansion with assertions validate this API.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/module_to_cil.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/module_to_cil.h

Purpose: Declares conversion APIs from module policydb/package formats to CIL.

Important APIs and functions: `sepol_module_policydb_to_cil(FILE *fp, struct policydb *pdb, int linked)`, `sepol_module_package_to_cil`, and `sepol_ppfile_to_module_package`.

Control flow: Conversion accepts either a module policydb or package and writes CIL to a stream; pp-file parsing creates a module package before conversion.

State and persistence: No global state; package parsing allocates a `sepol_module_package` returned to the caller.

Dependencies and integration points: Includes `sepol/module.h` and internal `policydb.h`; used by semodule/decompiler-style tooling.

Risks: Header has no include guard and relies on `FILE` via transitive includes. The `linked` flag changes emitted semantics and must match caller state.

Test signals: Module package to CIL round trips and linked/unlinked output comparisons validate behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/module_to_cil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/node_record.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/node_record.h

Purpose: Declares the public record/key API for IPv4/IPv6 node contexts.

Important APIs and types: Opaque `sepol_node_t` and key type; protocol constants `SEPOL_PROTO_IP4/IP6`; key create/unpack/extract/free; address/mask string and byte getters/setters; protocol get/set/string; context accessors; create/clone/free.

Control flow: Keys identify address, mask, and protocol; records carry the same plus a context. Collection APIs in `nodes.h` search or modify policydb node ocontexts.

State and persistence: Records own address/mask/context data; persistence requires policydb modification and write.

Dependencies and integration points: Depends on context records and handles; maps to `OCON_NODE` and `OCON_NODE6`.

Risks: Address byte order, family mismatch, and mask length validation are high-risk. String conversion must handle IPv4 and IPv6 consistently.

Test signals: IPv4/IPv6 string/byte round trips, protocol string mapping, invalid family/mask cases, and policydb query/modify are key tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/node_record.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/nodes.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/nodes.h

Purpose: Declares collection APIs for network node contexts in a policydb.

Important APIs and functions: `sepol_node_count`, `exists`, `query`, `modify`, and `iterate`.

Control flow: Callers create node keys/records, then functions search or update the policydb object-context lists for IPv4/IPv6 nodes.

State and persistence: `modify` changes in-memory policydb state; write APIs persist it.

Dependencies and integration points: Depends on policydb, handle, and node record APIs. Integrates external tools with `nodecon` entries.

Risks: Overlapping CIDR-like ranges and family-specific ordering can affect lookup semantics. Iterator callbacks must respect temporary record ownership.

Test signals: Multiple node entries, family mismatch, missing keys, and iteration behavior validate the collection layer.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/nodes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/policydb.h

Purpose: Declares the opaque public policydb and policy-file API.

Important APIs and types: Opaque `sepol_policy_file_t` and `sepol_policydb_t`; policy file create/free, memory/FILE setters, length getter, handle setter; policydb create/free, type/version/unknown/target setters, optimize, read/write, image conversion, MLS and compat-net queries.

Control flow: Callers allocate a policy file wrapper around memory or `FILE`, allocate a policydb, read or configure it, mutate/query it through other APIs, then write or convert it.

State and persistence: `sepol_policydb_t` owns an internal `policydb`. `sepol_policy_file_t` references caller memory/streams or computes output length.

Dependencies and integration points: Foundation for all public libsepol record, module, context, and service APIs.

Risks: Type/version compatibility is strict. Memory-backed policy files need correct length and lifetime. Unknown-class behavior and target platform affect kernel semantics.

Test signals: Read/write round trips for kernel/base/module policies, image conversion, version bounds, and invalid policy images are core tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/avrule_block.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/policydb/avrule_block.h

Purpose: Declares internal helpers for module AV rule blocks and declarations.

Important APIs and functions: `avrule_block_create/destroy/list_destroy`, `avrule_decl_create/destroy`, `get_avrule_decl`, `get_decl_cond_list`, `is_id_enabled`, and `is_perm_existent`.

Control flow: Parser/linker code creates blocks and declarations, attaches conditions/rules/symbol scopes, and later checks enabled declarations and permission existence.

State and persistence: Blocks own declaration lists, symbol tables, required/declared scope bitmaps, and module-name metadata. They are serialized indirectly as module policydb structures.

Dependencies and integration points: Includes internal `policydb.h`; implemented by `src/avrule_block.c`.

Risks: Scope bookkeeping controls whether optional/module declarations activate. Incorrect destruction leaks nested rule lists and bitmaps.

Test signals: Module parsing/linking with optional blocks, conditional declarations, and inherited common permissions validates these helpers.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/avrule_block.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/avtab.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/policydb/avtab.h

Purpose: Defines the internal access-vector table used for TE allow/audit/type-transition and extended-permission rules.

Important APIs and types: `avtab_key_t`, `avtab_datum_t`, `avtab_extended_perms_t`, `avtab_node`, `avtab_t`; operations `avtab_init/alloc/insert/search/search_node/search_node_next/insert_nonunique/insert_with_parse_context/map/read/read_item/destroy/hash_eval`.

Control flow: Policy read/expand code allocates buckets, inserts sorted nodes keyed by source type, target type, class, and specified rule flavor, then decision code searches matching entries.

State and persistence: AVTAB nodes own optional xperm allocations and parse context pointers. Binary policy read/write serializes semantic entries but not parse context or merge flags.

Dependencies and integration points: Used by policydb, conditional rules, assertion checking, services, and expansion.

Risks: Uniqueness rules differ for normal and conditional tables. Extended permission masks and enabled bits require careful filtering.

Test signals: Duplicate detection, xperm read/write, conditional nonunique insertion, and access-decision searches validate this table.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/avtab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/conditional.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/policydb/conditional.h

Purpose: Defines internal conditional-policy expression and rule-list structures.

Important APIs and types: `cond_expr_t`, `cond_av_list_t`, `cond_node_t`; constants for RPN boolean operations, max expression depth, and precomputed bool count. Functions include expression evaluation/copy/equality/normalization, node search/create/destroy, bool indexing/read, list read/destroy, condition evaluation, AV lookup, and optimization.

Control flow: Conditional expressions are evaluated from reverse Polish notation against indexed booleans. True/false AV lists point into conditional avtab nodes whose `AVTAB_ENABLED` bit is toggled.

State and persistence: Policydb stores boolean indexes, `te_cond_avtab`, and `cond_list`. Precomputed truth tables optimize expressions with up to five unique booleans.

Dependencies and integration points: Used by boolean updates, binary policy read, expansion, and access decisions.

Risks: Stack-depth failures disable rules. Conflicting conditional type rules are rejected. Precompute assumptions depend on `COND_MAX_BOOLS`.

Test signals: Boolean changes re-enabling rules, RPN operator cases, long expressions, and binary conditional reads are critical tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/conditional.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/constraint.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/policydb/constraint.h

Purpose: Defines internal policy constraint expression structures.

Important APIs and types: `constraint_expr_t` models logical and attribute/name/type-set comparisons; `constraint_node_t` binds permissions to an expression. Exports `constraint_expr_init` and `constraint_expr_destroy`.

Control flow: Constraint evaluators walk linked expressions for permission checks and validatetrans checks. This header only declares data shape and lifecycle helpers.

State and persistence: Expressions own `ebitmap_t names` and optional `type_set` names. Nodes chain per class/permission set and are serialized in policydb.

Dependencies and integration points: Depends on ebitmap and Flask types; used by policydb class data, services, and hierarchy/constraint checks.

Risks: Expression depth and operator/attribute combinations are security-sensitive because they gate permissions beyond TE rules. Destruction must release nested type sets.

Test signals: Constraint parse/read, validatetrans denial reasons, MLS constraint checks, and destroy/leak tests validate this layer.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/constraint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/context.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/policydb/context.h

Purpose: Defines the internal numeric security-context representation and inline lifecycle/comparison helpers.

Important APIs and types: `context_struct_t` holds user, role, type, and `mls_range_t`. Inline helpers initialize, copy, copy low/high MLS level, compute GLB/LUB, compare, and destroy MLS or full contexts.

Control flow: Public string/record conversion resolves names into numeric values; services and SID tables operate on this compact structure.

State and persistence: The structure stores numeric IDs into policydb value arrays and owns MLS category bitmaps. It is serialized inside ocontexts and SID tables.

Dependencies and integration points: Depends on ebitmap and MLS types; used by context conversion, sidtab, services, and policydb object contexts.

Risks: Copy helpers allocate/copy ebitmaps; partial failure cleanup must be correct. Numeric IDs are one-based and invalid zero values must be rejected by validators.

Test signals: Context copy/destroy, MLS low/high copy, equality, and validation against policydb indexes are key tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/ebitmap.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/policydb/ebitmap.h

Purpose: Defines extensible bitmaps used for sets of types, roles, categories, classes, permissions, and scopes.

Important APIs and types: `ebitmap_node_t`, `ebitmap_t`, iterator macros, bit tests, and operations for compare, union, and/or/xor/not/andnot, cardinality, distance, copy, contains, match_any, get/set bit, range initialization, highest-set-bit, destroy, and binary read.

Control flow: Bitmaps are sparse linked lists of 64-bit map nodes with explicit start bits. Iterator macros walk all or positive bits.

State and persistence: Nodes are heap allocated and owned by the containing ebitmap. Many policydb structures serialize these sets.

Dependencies and integration points: Used across MLS, type/role sets, scope indexes, constraints, policy capabilities, and context validation caches.

Risks: Highbit/startbit invariants and sparse-node allocation are critical. Maxbit parameters for complement operations prevent accidental infinite universes.

Test signals: Sparse high-bit sets, range operations, contains/match_any, copy/destroy, and binary read of malformed bitmaps validate behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/ebitmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/expand.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/policydb/expand.h

Purpose: Declares internal module expansion helpers that convert modular policy structures into expanded kernel-ready policydb data.

Important APIs and functions: `expand_module_avrules`, `expand_module`, type/role/MLS semantic conversion helpers, `expand_rule`, `expand_avtab`, and `expand_cond_av_list`.

Control flow: Expansion maps module-local types/bools/roles/users through provided maps, expands type/role sets into concrete ebitmaps, copies or expands neverallow rules, and optionally runs assertion/hierarchy checks.

State and persistence: Mutates or fills destination policydb avtabs, role/user/type structures, conditions, and MLS ranges. May expand base into itself only for AV rules under documented map constraints.

Dependencies and integration points: Depends on handles and conditionals; called by public `sepol_expand_module` and fuzzers.

Risks: Incorrect maps corrupt policy semantics. Expanding neverallow rules in-place can duplicate entries if the documented constraints are violated.

Test signals: Module expansion with attributes, conditionals, MLS users/ranges, neverallow checks, and base==out AV expansion validate it.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/expand.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/flask_types.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/policydb/flask_types.h

Purpose: Defines core Flask/SELinux scalar types and constants.

Important APIs and types: `sepol_security_context_t`, `sepol_access_vector_t`, `sepol_security_class_t`, `sepol_security_id_t`, null constants, SELinux magic values, and `struct sepol_av_decision`.

Control flow: No logic exists; these types are used by services, policydb, avtab, sidtab, and public APIs.

State and persistence: Access vectors, class IDs, SIDs, and decisions are serialized or returned by policy decision APIs. `sepol_av_decision` carries allowed/decided/audit masks and sequence number.

Dependencies and integration points: Base dependency for most `policydb` headers and service APIs.

Risks: Widths are ABI-sensitive. Changing type sizes would break binary policy parsing and public API compatibility.

Test signals: ABI checks, binary policy read/write, and service decision tests validate these definitions indirectly.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/flask_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/hashtab.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/policydb/hashtab.h

Purpose: Declares the generic chained hash table used by policydb symbol tables and other mappings.

Important APIs and types: `hashtab_key_t`, `hashtab_datum_t`, `hashtab_node_t`, `hashtab_t`; create, insert, remove, search, destroy, map, and hash-evaluation functions.

Control flow: Callers provide hash and key comparison callbacks at create time, then insert/search/remove arbitrary key/datum pairs. `hashtab_map` stops and propagates nonzero callback results.

State and persistence: Tables own nodes but ownership of keys/data is controlled by caller destroy callbacks or surrounding symtab policy.

Dependencies and integration points: Included by `symtab.h` and many policydb internals.

Risks: Ownership is manual; mismatched key/data destroy behavior leaks or double-frees. Iteration order is bucket-dependent and not stable API.

Test signals: Duplicate insert, missing remove, map early error, destroy callbacks, and collision-heavy buckets validate behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/hashtab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/hierarchy.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/policydb/hierarchy.h

Purpose: Declares internal hierarchy/bounds validation helpers for users, roles, and types.

Important APIs and functions: `hierarchy_add_bounds`, `bounds_destroy_bad`, `bounds_check_type`, `bounds_check_users`, `bounds_check_roles`, `bounds_check_types`, and `hierarchy_check_constraints`.

Control flow: Expansion/validation code adds or checks bounds relationships and scans avtab entries for child permissions exceeding parent permissions.

State and persistence: Bounds fields live in user/role/type datums; bad avtab lists are temporary diagnostic state.

Dependencies and integration points: Depends on avtab and policydb internals; used by module expansion, validation, and fuzz harnesses.

Risks: Bounds enforcement is security-sensitive because it restricts child domains/users/roles. Diagnostics must free bad-entry lists.

Test signals: Policies with valid and violating typebounds/rolebounds/userbounds and hierarchy constraint checks validate the API.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/hierarchy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/link.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/policydb/link.h

Purpose: Declares the internal module linker entry point.

Important APIs and functions: `link_modules(sepol_handle_t *handle, policydb_t *b, policydb_t **mods, int len, int verbose)`.

Control flow: Linker combines a base policydb with module policydbs, resolving scopes, required symbols, declarations, and rules before expansion.

State and persistence: Mutates the base policydb to include linked module declarations and rule structures.

Dependencies and integration points: Wrapped by public `sepol_link_modules` and used in fuzzing. Depends on handles, errcodes, and internal policydb.

Risks: Link order, duplicate declarations, optional blocks, and unresolved requirements are high-risk correctness points.

Test signals: Multiple-module link scenarios, missing requirements, duplicate symbols, optional blocks, and verbose diagnostics validate this boundary.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/link.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/mls_types.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/policydb/mls_types.h

Purpose: Defines internal MLS levels, ranges, semantic category ranges, and inline MLS operations.

Important APIs and types: `mls_level_t`, `mls_range_t`, semantic cat/level/range structs; inline dominance/equality/between/contains/copy/destroy/GLB-LUB helpers; exported semantic init/destroy/copy functions.

Control flow: MLS checks compare sensitivities and category ebitmaps. Semantic structures from policy source are expanded into numeric `mls_level_t`/`mls_range_t`.

State and persistence: MLS levels own category ebitmaps. Ranges are stored in contexts, users, constraints, and range transitions.

Dependencies and integration points: Depends on ebitmap, Flask types, and system min/max helpers; used by context validation and expansion.

Risks: Dominance and GLB/LUB logic is security-critical. Copy failures must destroy partially copied category bitmaps.

Test signals: Range containment, incomparable levels, overlapping/non-overlapping GLB/LUB, semantic copy/destroy, and context MLS validation are essential.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/mls_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/module.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/policydb/module.h

Purpose: Defines the internal layout of `sepol_module_package`.

Important APIs and types: `SEPOL_MODULE_PACKAGE_MAGIC`, `struct sepol_module_package` with policy pointer, package version, file_contexts, seusers, user_extra, and netfilter_contexts buffers plus lengths. Exports `sepol_module_package_init`.

Control flow: Package read/write code fills this structure; public getters/setters expose buffers through `sepol/module.h`.

State and persistence: The package owns a policydb and ancillary text buffers that are serialized into module package files.

Dependencies and integration points: Bridges public module API to internal policydb and conditional structures.

Risks: Buffer ownership and length fields must stay synchronized. Package magic/version compatibility gates read/write behavior.

Test signals: Package init/free, read/write of all ancillary sections, and version/magic validation test this structure.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/polcaps.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/policydb/polcaps.h

Purpose: Defines known SELinux policy capability IDs and lookup helpers.

Important APIs and symbols: Capability enum entries from `POLICYDB_CAP_NETPEER` through `POLICYDB_CAP_BPF_TOKEN_PERMS`, `POLICYDB_CAP_MAX`, `sepol_polcap_getnum`, and `sepol_polcap_getname`.

Control flow: Parser/converter code maps textual policycap names to numbers and back for ebitmap storage/emission.

State and persistence: Capability bits are stored in `policydb_t.policycaps`.

Dependencies and integration points: Used by policydb parsing/writing, kernel-to-text conversion, and service behavior checks.

Risks: Enum ordering is persistent policy ABI. Adding capabilities requires updates to name maps and policy version support.

Test signals: Name/number round trips, unknown-name handling, and binary policies containing each cap validate behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/polcaps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/policydb.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/policydb/policydb.h

Purpose: Defines libsepol's internal policy database schema, binary policy versions, and lifecycle/manipulation entry points.

Important APIs and types: Major types include symbol datums, type/role sets, class/user/type/role datums, AV rules, role/range/filename transition rules, object contexts, genfs entries, scope indexes, AV rule blocks/declarations, and `policydb_t`. Exports init/destroy, image conversion, indexing, optimization, ISID loading, ocontext sorting, file transition insertion, assertion checks, symtab insertion, policy file I/O, and many datum lifecycle helpers.

Control flow: Policy readers populate symbol tables and object contexts, index value-to-name arrays, evaluate conditionals, expand/link modules, validate contexts, and write binary policy according to version/target flags.

State and persistence: `policydb_t` is the authoritative in-memory policy state: symbols, rules, conditionals, contexts, genfs, range/file transitions, caps, permissive/neveraudit maps, versions, and target platform.

Dependencies and integration points: Central dependency for all internal policydb modules and many public wrappers.

Risks: One-based symbol values, version-gated fields, target-specific ocontext meanings, and manual ownership make this high risk.

Test signals: Binary read/write across versions, module expansion, context validation, assertions, and fuzzing malformed policies validate it.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/policydb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/services.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/policydb/services.h

Purpose: Declares the internal/public security-server style service API over policydb and SID tables.

Important APIs and functions: Set/load policy state; compute AV decisions and denial reasons/buffers; validate transitions; class/permission name mapping; transition/member/change SID computation; SID/context conversion; user SID enumeration; fs/port/ibpkey/ibendport/netif/node/genfs labeling lookups.

Control flow: Callers load or set policydb/sidtab, then request decisions or labeling SIDs. Service code consults avtabs, constraints, RBAC, bounds, ocontexts, genfs, and sidtab mappings.

State and persistence: Can use explicit caller-provided policydb/sidtab or private global structures initialized by `sepol_load_policy`/`sepol_set_policydb_from_file`.

Dependencies and integration points: Used by checkpolicy-like tools, deprecated context checks, and consumers needing userspace SELinux decisions.

Risks: Global fallback state is hard to isolate. Returned buffers/SIDs require caller ownership discipline. Decision reasons are security-sensitive diagnostics.

Test signals: AV decisions, constraint reason buffers, transition SID creation, and all ocontext lookup types need coverage.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/services.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/sidtab.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/policydb/sidtab.h

Purpose: Defines the internal security identifier table mapping SIDs to context structures.

Important APIs and types: `sidtab_node_t`, `sidtab_t`, hash constants, and functions for init, insert, search, map, map-remove-on-error, context-to-SID allocation/lookup, hash eval, destroy, set, and shutdown.

Control flow: Service code loads initial SIDs, resolves contexts to existing or newly allocated SIDs, and searches by SID during access decisions and context conversion.

State and persistence: Sidtab owns hash buckets of SID/context copies, next SID counter, element count, and shutdown flag. It is runtime state, not the policydb itself.

Dependencies and integration points: Depends on internal context representation and Flask SID types; used by services and policy loading.

Risks: Context equality/copy and next_sid allocation must avoid duplicate or invalid SIDs. Shutdown behavior affects dynamic SID allocation.

Test signals: Insert/search, context-to-SID duplicate detection, map removal on callback failure, destroy, and shutdown tests validate it.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/sidtab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/symtab.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/policydb/symtab.h

Purpose: Defines policy symbol tables backed by generic hash tables.

Important APIs and types: `symtab_datum_t` with one-based `value`, `symtab_t` with `hashtab_t table` and `nprim`, plus `symtab_init` and `symtab_destroy`.

Control flow: Policy readers/parsers insert named symbols with datum structs whose first field is `symtab_datum_t`; indexers build value-to-name arrays from `value`.

State and persistence: Symbol tables own name/datum mappings and primary-name counts within policydb or AV rule declarations.

Dependencies and integration points: Depends on `hashtab.h`; used for classes, roles, types, users, bools, levels, categories, permissions, scopes.

Risks: The "common first field" casting convention is easy to break. Zero is invalid for values; off-by-one indexing is common risk.

Test signals: Symbol insertion/indexing, duplicate names, destroy behavior, and value-to-name array population validate it.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/symtab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/util.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/policydb/util.h

Purpose: Declares miscellaneous internal utility helpers for arrays, AV formatting, extended permissions formatting, and tokenization.

Important APIs and functions: `add_i_to_a`, `sepol_av_to_string`, `sepol_extended_perms_to_string`, and `tokenize`.

Control flow: Formatting helpers convert permission bitmasks to textual names for diagnostics/conversion; `tokenize` parses delimited strings as an `sscanf` replacement.

State and persistence: `add_i_to_a` grows caller-owned arrays. Formatting functions allocate strings that callers must free.

Dependencies and integration points: Used by assertion reporting, conversion code, and parsers.

Risks: Formatting failures affect diagnostics for security violations. Caller ownership of returned strings/arrays must be clear.

Test signals: AV/xperm formatting for known/unknown bits, allocation failure paths, and tokenization edge cases validate it.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/policydb/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/port_record.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/port_record.h

Purpose: Declares the public record/key API for TCP/UDP/DCCP/SCTP port contexts.

Important APIs and types: Opaque `sepol_port_t` and key type; protocol constants; key create/unpack/extract/free; compare helpers; protocol, low/high port, single-port/range, context accessors; create/clone/free.

Control flow: Keys identify low/high port plus protocol; records attach a context. Collection APIs in `ports.h` search or modify policydb port ocontexts.

State and persistence: Records own scalar range/protocol values and context pointer/copy semantics through implementation.

Dependencies and integration points: Depends on context records and handles; maps to `OCON_PORT`.

Risks: Range overlap, protocol constants, and low/high ordering must match kernel policy semantics.

Test signals: Protocol string mapping, range/single-port setters, invalid protocol/range cases, and policydb query/modify validate it.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/port_record.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/ports.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/ports.h

Purpose: Declares public collection operations for port contexts in a policydb.

Important APIs and functions: `sepol_port_count`, `exists`, `query`, `modify`, and `iterate`.

Control flow: Functions search/update `OCON_PORT` entries using keys from `port_record.h`, returning public record copies.

State and persistence: `modify` changes in-memory policydb state; persistence requires writing the policydb.

Dependencies and integration points: Depends on policydb, handle, and port record APIs; used by semanage-like tools.

Risks: Port-range overlaps and protocol-specific ordering can affect lookups. Iterator callback ownership follows the temporary-record pattern.

Test signals: Multiple protocols, overlapping/missing ranges, modification, count, and iterator stop/error paths provide coverage.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/ports.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/sepol.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/sepol.h

Purpose: Provides an umbrella public header for libsepol records, collections, handles, debugging, policydb, modules, and contexts.

Important APIs and symbols: Includes all major public record and collection headers plus `sepol_set_policydb_from_file(FILE *fp)`.

Control flow: External callers include this single header to access the public libsepol API. `sepol_set_policydb_from_file` initializes internal service state from a file.

State and persistence: The umbrella itself has no state. The service initializer affects process-global internal policydb state used by service calls.

Dependencies and integration points: Central downstream integration point for C and C++ callers, with `extern "C"` wrapping.

Risks: Pulling many headers increases compile coupling. Global service initialization should be avoided in code requiring isolation.

Test signals: Installed-header compilation from C and C++, and service initialization from a valid policy file, validate the umbrella.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/sepol.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/user_record.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/user_record.h

Purpose: Declares the public record/key API for SELinux users.

Important APIs and types: Opaque `sepol_user_t` and key type; key create/unpack/extract/free; compare helpers; name getters/setters; MLS level/range getters/setters; role add/delete/has/get/set; create/clone/free.

Control flow: Callers construct a user record with name, authorized roles, and MLS data, then apply/query it through `users.h`.

State and persistence: Records own strings and role arrays in implementation memory; policydb modification persists them in memory until write.

Dependencies and integration points: Depends on handle API; collection operations in `users.h` bridge to policydb user datums.

Risks: Role array ownership, duplicate roles, and MLS enabled/disabled policy constraints require care. Name keys must remain stable.

Test signals: Role add/delete/set/get, MLS fields, clone/free, and policydb query/modify validate it.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/user_record.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/users.h -->
# sources/security-integrity/selinux/libsepol/include/sepol/users.h

Purpose: Declares public collection operations for SELinux user entries in a policydb.

Important APIs and functions: `sepol_user_modify`, `count`, `exists`, `query`, and `iterate`.

Control flow: Users are keyed by name and represented by `sepol_user_t` records; collection functions search or mutate policydb user symbols and associated role/MLS data.

State and persistence: `modify` updates the in-memory policydb. Query/iterate return record copies.

Dependencies and integration points: Depends on public policydb, user record, handle, and standard size types.

Risks: Modifying users affects context validity, user SID generation, and MLS constraints. Iterator callbacks must not retain freed records.

Test signals: User modification followed by context validation, role/MLS round trips, missing users, and iterator behavior provide coverage.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/include/sepol/users.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/man/Makefile -->
# sources/security-integrity/selinux/libsepol/man/Makefile

Purpose: Installs libsepol manual pages.

Important APIs and targets: Empty `all`; `install` creates man3/man8 destination directories, installs `man3/*.3` and `man8/*.8`, and loops over `LINGUAS` to install translated manpages when language-specific directories exist.

Control flow: The target uses shell conditionals inside a `for lang in $(LINGUAS)` loop to copy translated sections selectively.

State and persistence: Writes installed manpage files under `$(DESTDIR)$(MANDIR)` and language subdirectories.

Dependencies and integration points: Used by package/install workflows; variables include `PREFIX`, `MANDIR`, `MAN3SUBDIR`, `MAN8SUBDIR`, and `LINGUAS`.

Risks: Globs fail if no manpages exist depending on shell/install behavior. Translated directories are optional and silently skipped.

Test signals: `make install DESTDIR=... LINGUAS=...` and verifying expected man3/man8 files validates it.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/man/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/Makefile -->
# sources/security-integrity/selinux/libsepol/src/Makefile

Purpose: Builds and installs static/shared libsepol libraries, pkg-config metadata, symbol map, and optional CIL objects.

Important APIs and targets: Builds `libsepol.a`, `libsepol.so`/Darwin dylib, `libsepol.pc`, and `libsepol.map`; supports `DISABLE_CIL`, `DISABLE_SHARED`, `relabel`, and `clean`.

Control flow: Object lists are generated from local `.c` files and optionally CIL sources plus generated lexer. It probes for `reallocarray`, generates lexer via `flex`, compiles `.o`/`.lo`, links shared library with version script/soname, installs static/shared/pkgconfig artifacts, and creates relative symlink.

State and persistence: Produces build artifacts in `src/` and installs under `$(DESTDIR)$(LIBDIR)`/`$(SHLIBDIR)`.

Dependencies and integration points: Consumed by top-level builds and downstream packaging; ties CIL sources into libsepol unless disabled.

Risks: Wildcard object inclusion can pull unintended files. Darwin branch changes linker flags and symlink tool. Version map filtering when CIL disabled affects ABI exports.

Test signals: Static/shared builds with and without CIL/shared, install DESTDIR, pkg-config content, and clean target validate it.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/assertion.c -->
# sources/security-integrity/selinux/libsepol/src/assertion.c

Purpose: Implements neverallow and neverallowxperm assertion checking against expanded policy AV tables.

Important APIs and functions: Public `check_assertion(policydb_t *p, const avrule_t *narule)` and `check_assertions(sepol_handle_t *handle, policydb_t *p, const avrule_t *avrules)`. Internals match class permissions, compare extended-permission forms, compute violated xperms, scan avtabs/conditional lists, and report failures with source line information.

Control flow: For each neverallow rule, type sets and class-permission nodes are expanded/matched against allowed rules in `te_avtab` and conditional rules. Violations are formatted with type/class/permission names and counted as errors.

State and persistence: No persistent state is created. It reads policydb indexes, type attribute maps, AV tables, conditional lists, and rule metadata.

Dependencies and integration points: Depends on avtab, policydb, expand, util, private/debug helpers. Called during module expansion/checking and fuzzing.

Risks: This is security-critical: missed matches allow invalid policy; false positives block valid policy. Extended permission and conditional conflict logic is complex.

Test signals: Positive/negative neverallow and neverallowxperm policies, conditionals, attributes, source-line diagnostics, and fuzz coverage validate it.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/assertion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/avrule_block.c -->
# sources/security-integrity/selinux/libsepol/src/avrule_block.c

Purpose: Implements lifecycle and lookup helpers for module AV rule blocks/declarations and scope checks.

Important APIs and functions: `avrule_block_create`, `avrule_decl_create`, `avrule_decl_destroy`, `avrule_block_destroy`, `avrule_block_list_destroy`, `get_decl_cond_list`, `is_id_enabled`, and `is_perm_existent`.

Control flow: Declaration creation allocates and initializes per-declaration symbol tables and scope bitmaps. Destroy paths recursively release conditionals, AV/range/role/filename rules, scopes, symtabs, and module name. Lookup helpers find equivalent conditional nodes, test enabled declarations through scope metadata, and search class/common permissions.

State and persistence: Manages heap-owned block/declaration structures embedded in `policydb_t.global` and module declaration indexes.

Dependencies and integration points: Uses policydb, conditional, avrule_block headers, ebitmap/symtab helpers, and linker/expander state.

Risks: Scope activation rules differ for roles/users versus other symbols. Destroy functions must match nested ownership exactly to avoid leaks or use-after-free.

Test signals: Optional/conditional module blocks, permission inheritance from commons, enabled declaration lookup, and leak checks validate behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/avrule_block.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/avtab.c -->
# sources/security-integrity/selinux/libsepol/src/avtab.c

Purpose: Implements the access-vector table hash structure and binary policy AVTAB reader.

Important APIs and functions: `avtab_init`, `avtab_alloc`, `avtab_insert`, `avtab_insert_nonunique`, `avtab_search`, `avtab_search_node`, `avtab_search_node_next`, `avtab_destroy`, `avtab_map`, `avtab_hash_eval`, `avtab_read_item`, and `avtab_read`.

Control flow: Keys hash via a MurmurHash3-derived mix of class/target/source. Buckets are sorted by source, target, class. Normal insert rejects duplicate non-xperm keys; nonunique insert supports conditionals. Read code handles old and new binary formats, validates specifier masks, version-gates xperms, decodes little-endian data, and inserts each item.

State and persistence: `avtab_t` owns bucket arrays and nodes. Nodes optionally own `avtab_extended_perms_t`. Binary read populates persistent policydb AV tables.

Dependencies and integration points: Used by policydb reading, expansion, conditionals, assertions, and services.

Risks: Duplicate/specifier handling and xperm allocation are correctness hot spots. Malformed binary input must not overread or allocate excessive buckets.

Test signals: Binary policies across AVTAB versions, duplicate entries, xperms, zero/saturated counts, and lookup ordering validate it.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/avtab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/boolean_internal.h -->
# sources/security-integrity/selinux/libsepol/src/boolean_internal.h

Purpose: Provides the internal include bridge for boolean record and collection APIs.

Important APIs and types: It does not declare new symbols; it includes `sepol/boolean_record.h` and `sepol/booleans.h`.

Control flow: No logic exists. Implementation files include this header to share public boolean type declarations internally.

State and persistence: No state.

Dependencies and integration points: Used by `boolean_record.c` and potentially boolean-related internals.

Risks: As a thin wrapper, risk is low. It can hide direct dependency needs if public headers change.

Test signals: Boolean implementation compilation validates it.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/boolean_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/boolean_record.c -->
# sources/security-integrity/selinux/libsepol/src/boolean_record.c

Purpose: Implements the opaque public boolean record and key API.

Important APIs and functions: Implements key create/unpack/extract/free, compare/compare2, name get/set, value get/set, record create/clone/free.

Control flow: Create functions allocate structures and duplicate names. Setters replace owned strings. Clone creates a new record and deep-copies name/value. Key extraction builds a key from a record name.

State and persistence: `struct sepol_bool` owns `char *name` and `int value`; `struct sepol_bool_key` owns `char *name`. No policydb state is changed here.

Dependencies and integration points: Uses `boolean_internal.h`, `debug.h`, libc allocation/string helpers, and handle-based diagnostics. Consumed by `booleans.c` and external callers.

Risks: `sepol_bool_set_value` accepts any int; policydb update rejects non-0/1 later. Null names passed to strdup would crash.

Test signals: Allocation failure handling, clone deep copy, compare ordering, key extraction, and invalid value rejection through `sepol_bool_set` are useful tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/boolean_record.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/booleans.c -->
# sources/security-integrity/selinux/libsepol/src/booleans.c

Purpose: Implements public policydb operations for booleans.

Important APIs and functions: `sepol_bool_set`, `sepol_bool_count`, `sepol_bool_exists`, `sepol_bool_query`, and `sepol_bool_iterate`; internal `bool_update` and `bool_to_record`.

Control flow: Updates duplicate the key name, find the `cond_bool_datum_t` in `p_bools`, validate value 0/1, mutate `state`, then `sepol_bool_set` calls `evaluate_conds` to toggle conditional rule enable bits. Query/iterate convert indexed bool datums to public records.

State and persistence: Mutates `policydb->p_bools` datum state and conditional AV rule state. Records returned to callers are heap-owned copies.

Dependencies and integration points: Uses internal policydb/hashtab/conditional structures, public boolean records, debug/handle helpers.

Risks: If conditional reevaluation fails after state mutation, caller receives error but state may already be changed. Iteration assumes indexed bool arrays are current.

Test signals: Set valid/invalid values, observe conditional AV changes, query missing booleans, and iterator callback stop/error coverage.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/booleans.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/conditional.c -->
# sources/security-integrity/selinux/libsepol/src/conditional.c

Purpose: Implements conditional policy expression evaluation, node/list lifecycle, bool indexing, and binary conditional rule reading.

Important APIs and functions: `cond_optimize_lists`, `cond_expr_equal`, `cond_node_create/find/search`, `cond_evaluate_expr`, `cond_copy_expr`, `cond_normalize_expr`, `evaluate_conds`, `cond_policydb_init/destroy`, destroy helpers, `cond_init_bool_indexes`, `cond_destroy_bool`, `cond_index_bool`, `cond_read_bool`, `cond_read_list`, and `cond_av_list_search`.

Control flow: RPN expressions are evaluated on a bounded stack. Normalization removes top-level NOT by swapping true/false lists and precomputes truth tables for expressions with up to five unique booleans. Boolean updates call `evaluate_conds`, which toggles `AVTAB_ENABLED` on true/false list nodes. Binary read builds condition nodes and inserts nonunique AVTAB nodes while checking type-rule conflicts.

State and persistence: Owns condition expression/list allocations, policydb bool index arrays, and conditional avtab entries.

Dependencies and integration points: Used by policydb read, bool APIs, expansion, services, and assertion checks.

Risks: Undefined expressions disable rules. Conditional type rule conflict handling is subtle. Precompute state depends on stable bool IDs.

Test signals: Operator truth tables, stack-depth failure, bool indexing, binary reads with true/false lists, and conditional type conflicts validate it.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/conditional.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/constraint.c -->
# sources/security-integrity/selinux/libsepol/src/constraint.c

Purpose: Implements lifecycle helpers for policy constraint expressions.

Important APIs and functions: `constraint_expr_init` zeroes a `constraint_expr_t`, initializes its names ebitmap, allocates `type_names`, and initializes the type set. `constraint_expr_destroy` walks a linked expression list and frees names, type sets, and nodes.

Control flow: Init prepares a single expression node for parser/read use. Destroy handles an entire linked expression chain.

State and persistence: Each expression owns an ebitmap and allocated `type_set_t`; constraints are attached to class datums and serialized in policydb.

Dependencies and integration points: Depends on policydb, constraint, expand/type-set helpers, and Flask types.

Risks: If `type_names` allocation fails after ebitmap init, caller must handle partially initialized state. Destroy assumes nodes are heap allocated.

Test signals: Init failure paths, destroy of multi-node expressions, constraints using name and type-set operands, and leak checks validate it.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/constraint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/context.c -->
# sources/security-integrity/selinux/libsepol/src/context.c

Purpose: Implements internal/public context validation and conversion between records, strings, and numeric `context_struct_t`.

Important APIs and functions: `policydb_context_isvalid`, deprecated `sepol_check_context`, `context_is_valid`, `context_to_string`, `context_from_record`, `context_to_record`, `context_from_string`, and `sepol_context_check`.

Control flow: Validation checks one-based user/role/type bounds, role-to-type cache, user-to-role cache, and MLS validity. Record-to-struct conversion resolves names through policydb symbol tables, rejects type attributes, enforces MLS presence/absence, parses MLS strings, and validates. Struct-to-record/string conversions use value-to-name indexes and MLS formatting helpers.

State and persistence: Allocates temporary contexts/strings/records; does not mutate policydb. Deprecated check uses service SID conversion.

Dependencies and integration points: Uses policydb services, public context records, internal MLS helpers, debug/handle/private utilities.

Risks: Symbol indexes must be populated. MLS mismatch is a hard error. Caller owns returned allocations.

Test signals: Valid/invalid contexts, object_r shortcut behavior, MLS enabled/disabled, type attribute rejection, string length overflow, and service compatibility tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/context.h -->
# sources/security-integrity/selinux/libsepol/src/context.h

Purpose: Declares internal context conversion and validation helpers implemented by `context.c`.

Important APIs and functions: `context_from_record`, `context_to_record`, `context_from_string`, `context_is_valid`, and `context_to_string`.

Control flow: Internal modules include this header when they need to bridge public `sepol_context_t` records or strings with numeric policydb `context_struct_t`.

State and persistence: No state is owned. Functions allocate returned contexts/records/strings and validate against policydb state.

Dependencies and integration points: Includes `context_internal.h`, internal policydb context and policydb headers, and public handle API. Used by record collection implementations and services.

Risks: API callers must destroy returned `context_struct_t` with `context_destroy` and free memory. Validation requires indexed policydb structures.

Test signals: Internal compile coverage plus public context/record collection tests validate the declarations.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/context_internal.h -->
# sources/security-integrity/selinux/libsepol/src/context_internal.h

Purpose: Provides the internal include bridge for context public APIs.

Important APIs and types: It declares no new symbols; it includes `sepol/context.h` and `sepol/context_record.h`.

Control flow: No logic exists. Implementation files include it to access public context declarations consistently.

State and persistence: No state.

Dependencies and integration points: Used by `context.c`, `context_record.c`, and internal headers.

Risks: Low; as a wrapper, it can mask direct dependency changes in public context headers.

Test signals: Context implementation compilation validates it.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/context_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/context_record.c -->
# sources/security-integrity/selinux/libsepol/src/context_record.c

Purpose: Implements the opaque public `sepol_context_t` record API and string parsing/formatting.

Important APIs and functions: User/role/type/MLS getters and setters, `sepol_context_create`, `sepol_context_clone`, `sepol_context_free`, `sepol_context_from_string`, and `sepol_context_to_string`.

Control flow: Setters duplicate incoming strings and replace owned fields. Clone deep-copies all required fields and optional MLS. `from_string` accepts `"<<none>>"` as a null context, otherwise splits `user:role:type[:mls]`. `to_string` computes size with overflow checks and formats with `snprintf`.

State and persistence: `struct sepol_context` owns four heap strings. No policydb validation or persistence occurs here.

Dependencies and integration points: Uses public context headers through `context_internal.h`, debug/private helpers, and libc. Higher-level `context.c` validates records against policydb.

Risks: Clone assumes user/role/type are non-null. Parsing treats everything after the third colon as MLS, so malformed extra-colon MLS validation is deferred.

Test signals: Round-trip strings with/without MLS, `"<<none>>"`, malformed strings, clone deep copy, overflow/error paths, and free-on-null validate behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/context_record.c -->
