# subset-b-008369 Research

Grouped source research for SELinux libsepol expander/linker/neverallow tests, libsepol diagnostic utilities, mcstrans daemon/configuration/utilities, and policycoreutils build/helper sources. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-expander-attr-map.c -->
# sources/security-integrity/selinux/libsepol/tests/test-expander-attr-map.c

## Purpose

Validates expanded type-attribute membership for base, module, optional, and disabled optional declarations after `test-expander.c` has produced `base_expanded2`. The source was read completely for this report (138 lines).

## Important APIs, Types, and Functions

Exports `test_expander_attr_mapping()`. It defines expected type-name arrays for many `attr_check_*` attributes and calls `test_attr_types()` against `base_expanded2`; disabled optional symbols are checked with `hashtab_search()` and CUnit negated assertions.

## Control Flow

The test is linear: build expected arrays, assert membership for present attributes, assert zero-member attributes where optionals should not contribute, then verify disabled optional attributes and member types are absent from `p_types.table`.

## State and Persistence Behavior

No owned persistent state. It reads the external `policydb_t base_expanded2` initialized by the expander harness and uses stack arrays for expectations.

## Dependencies and Integration Points

Depends on local helper assertions, `sepol/policydb/policydb.h`, CUnit, and the policy fixture naming scheme under `policies/test-expander`.

## Risks and Edge Cases

The suite is sensitive to fixture symbol names and optional-enable semantics. A linker or expander change that leaves disabled optional symbols in the global type table will be caught here.

## Test Signals

The signal is exact attribute membership and absence coverage across base, module, optional, and disabled optional combinations.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-expander-attr-map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-expander-attr-map.h -->
# sources/security-integrity/selinux/libsepol/tests/test-expander-attr-map.h

## Purpose

Header for the corresponding libsepol CUnit test module. It exposes the test entry point(s) `test_expander_attr_mapping` while hiding implementation details in the paired `.c` file. The source was read completely for this report (26 lines).

## Important APIs, Types, and Functions

Contains an include guard and prototypes for `test_expander_attr_mapping`. No types or macros beyond the guard are part of the API.

## Control Flow

There is no executable control flow; CUnit harness files include this header to register or invoke the test functions.

## State and Persistence Behavior

No state is declared or stored in this header.

## Dependencies and Integration Points

Integrated with the libsepol tests build and the paired implementation file in the same directory.

## Risks and Edge Cases

The main risk is prototype drift between the header, implementation, and suite registration code.

## Test Signals

Compile/link success of the CUnit test binary is the relevant signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-expander-attr-map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-expander-roles.c -->
# sources/security-integrity/selinux/libsepol/tests/test-expander-roles.c

## Purpose

Checks that role-to-type mappings survive module expansion for the role-specific expander fixture. The source was read completely for this report (38 lines).

## Important APIs, Types, and Functions

Exports `test_expander_role_mapping()`, which expects `role_check_1` to map to `role_check_1_1_t` and `role_check_1_2_t` via `test_role_type_set()`.

## Control Flow

The test reads the externally initialized `role_expanded` policydb and performs one focused role type-set assertion.

## State and Persistence Behavior

No storage is owned; it consumes the global `policydb_t role_expanded` built by `expander_test_init()`.

## Dependencies and Integration Points

Depends on `helpers.h`, `test-common.h`, CUnit, and libsepol policydb types.

## Risks and Edge Cases

Small fixture breadth means it is a regression tripwire for basic role expansion, not exhaustive RBAC behavior.

## Test Signals

Passing CUnit output confirms the expected role type bitmap was mapped in the expanded policy.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-expander-roles.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-expander-roles.h -->
# sources/security-integrity/selinux/libsepol/tests/test-expander-roles.h

## Purpose

Header for the corresponding libsepol CUnit test module. It exposes the test entry point(s) `test_expander_role_mapping` while hiding implementation details in the paired `.c` file. The source was read completely for this report (27 lines).

## Important APIs, Types, and Functions

Contains an include guard and prototypes for `test_expander_role_mapping`. No types or macros beyond the guard are part of the API.

## Control Flow

There is no executable control flow; CUnit harness files include this header to register or invoke the test functions.

## State and Persistence Behavior

No state is declared or stored in this header.

## Dependencies and Integration Points

Integrated with the libsepol tests build and the paired implementation file in the same directory.

## Risks and Edge Cases

The main risk is prototype drift between the header, implementation, and suite registration code.

## Test Signals

Compile/link success of the CUnit test binary is the relevant signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-expander-roles.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-expander-users.c -->
# sources/security-integrity/selinux/libsepol/tests/test-expander-users.c

## Purpose

Validates user-to-role mapping after expansion by walking the expanded user role bitmap and comparing it with expected role names. The source was read completely for this report (77 lines).

## Important APIs, Types, and Functions

`check_user_roles()` locates a `user_datum_t`, allocates a found-count array, iterates `user->roles.roles` with `ebitmap_for_each_positive_bit`, maps role values through `p_role_val_to_name`, and asserts exact role coverage. `test_expander_user_mapping()` applies it to `user_check_1`.

## Control Flow

The helper fails fast for missing users or allocation failure, counts every positive role bit, checks each expected role is found exactly once, and asserts there are no extra roles.

## State and Persistence Behavior

Uses only stack and temporary heap state; the external `policydb_t user_expanded` owns all policy structures.

## Dependencies and Integration Points

Depends on libsepol user/role policydb internals, ebitmap iteration, CUnit, and the expander fixture initialized elsewhere.

## Risks and Edge Cases

Risks include off-by-one role value/name mapping and fixture drift. The test intentionally catches both missing and extra roles, so unexpected role inheritance is visible.

## Test Signals

The main test signal is exact bitmap-to-name verification for the expanded user fixture.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-expander-users.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-expander-users.h -->
# sources/security-integrity/selinux/libsepol/tests/test-expander-users.h

## Purpose

Header for the corresponding libsepol CUnit test module. It exposes the test entry point(s) `test_expander_user_mapping` while hiding implementation details in the paired `.c` file. The source was read completely for this report (27 lines).

## Important APIs, Types, and Functions

Contains an include guard and prototypes for `test_expander_user_mapping`. No types or macros beyond the guard are part of the API.

## Control Flow

There is no executable control flow; CUnit harness files include this header to register or invoke the test functions.

## State and Persistence Behavior

No state is declared or stored in this header.

## Dependencies and Integration Points

Integrated with the libsepol tests build and the paired implementation file in the same directory.

## Risks and Edge Cases

The main risk is prototype drift between the header, implementation, and suite registration code.

## Test Signals

Compile/link success of the CUnit test binary is the relevant signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-expander-users.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-expander.c -->
# sources/security-integrity/selinux/libsepol/tests/test-expander.c

## Purpose

This CUnit harness loads modular SELinux policy fixtures from `policies/test-expander`, links modules with libsepol, expands them into concrete `policydb_t` instances, and registers tests for expander index integrity, attribute mapping, role/user mapping, and alias preservation. It owns the shared expanded policy objects consumed by the companion expander test files. The source was read completely for this report (254 lines).

## Important APIs, Types, and Functions

`expander_policy_init()` allocates fixture paths, calls `test_load_policy()`, `link_modules()`, `policydb_init()`, and `expand_module()`, and captures the typemap returned by linking. `expander_test_init()` builds base-only, base+module, role, user, and alias fixtures. `expander_test_cleanup()` destroys every `policydb_t` and frees `typemap`. `expander_add_tests()` registers `test_expander_indexes`, `test_expander_attr_mapping`, `test_expander_role_mapping`, `test_expander_user_mapping`, and `test_expander_alias`.

## Control Flow

Initialization is fixture-driven: load base and module policy text, link optional/global declarations, expand the linked module tree, then run CUnit assertions over the resulting expanded databases. The alias test checks alias datum mapping directly; the index test delegates to the common helper.

## State and Persistence Behavior

State is process-local test state held in global/static `policydb_t` variables and a `uint32_t *typemap`. No persistent storage is written, but cleanup must mirror initialization or later suites can observe leaked policydb state.

## Dependencies and Integration Points

Depends on libsepol `policydb`, `expand`, `link`, and conditional headers, plus local `parse_util`, `helpers`, and companion expander test headers. It integrates with the repository CUnit runner through `expander_test_init`, `expander_add_tests`, and `expander_test_cleanup`.

## Risks and Edge Cases

Important risks are fixture path allocation failures, early-return cleanup gaps during init, and regressions in optional block expansion that preserve symbols in the linked module but drop them during expansion. The variable-length filename array also relies on `num_modules` being small and controlled by tests.

## Test Signals

Strong test signals are the registered CUnit cases, successful load/link/expand of all fixture policy combinations, `test_policydb_indexes()`, and exact assertions in the companion role/user/attribute files.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-expander.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-expander.h -->
# sources/security-integrity/selinux/libsepol/tests/test-expander.h

## Purpose

Header for the corresponding libsepol CUnit test module. It exposes the test entry point(s) `expander_test_init, expander_test_cleanup, expander_add_tests` while hiding implementation details in the paired `.c` file. The source was read completely for this report (30 lines).

## Important APIs, Types, and Functions

Contains an include guard and prototypes for `expander_test_init, expander_test_cleanup, expander_add_tests`. No types or macros beyond the guard are part of the API.

## Control Flow

There is no executable control flow; CUnit harness files include this header to register or invoke the test functions.

## State and Persistence Behavior

No state is declared or stored in this header.

## Dependencies and Integration Points

Integrated with the libsepol tests build and the paired implementation file in the same directory.

## Risks and Edge Cases

The main risk is prototype drift between the header, implementation, and suite registration code.

## Test Signals

Compile/link success of the CUnit test binary is the relevant signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-expander.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-linker-cond-map.c -->
# sources/security-integrity/selinux/libsepol/tests/test-linker-cond-map.c

## Purpose

Tests that conditional boolean symbols, default states, and conditional expression nodes are preserved and remapped correctly by the module linker. The source was read completely for this report (163 lines).

## Important APIs, Types, and Functions

Defines `test_cond_expr_t`, `test_cond_expr_mapping()`, `test_bool_state()`, `base_cond_tests()`, and `module_cond_tests()`. The checks compare `cond_expr_t` node types and boolean name mapping through `sym_val_to_name[SYM_BOOLS]`.

## Control Flow

For each declaration tag, the test verifies boolean symbol scope, expected boolean state, and the exact postfix expression sequence used by the declaration conditional list.

## State and Persistence Behavior

The file owns no persistent data; it inspects linked policydb structures supplied by the harness.

## Dependencies and Integration Points

Depends on libsepol conditional policydb structures, CUnit, and local linker test helpers.

## Risks and Edge Cases

Risks under test include boolean value remapping errors, default state loss, malformed conditional expression lists, and optional declaration conditional leakage.

## Test Signals

Passing tests indicate boolean and conditional AST remapping survived linker symbol renumbering.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-linker-cond-map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-linker-cond-map.h -->
# sources/security-integrity/selinux/libsepol/tests/test-linker-cond-map.h

## Purpose

Header for the corresponding libsepol CUnit test module. It exposes the test entry point(s) `base_cond_tests, module_cond_tests` while hiding implementation details in the paired `.c` file. The source was read completely for this report (29 lines).

## Important APIs, Types, and Functions

Contains an include guard and prototypes for `base_cond_tests, module_cond_tests`. No types or macros beyond the guard are part of the API.

## Control Flow

There is no executable control flow; CUnit harness files include this header to register or invoke the test functions.

## State and Persistence Behavior

No state is declared or stored in this header.

## Dependencies and Integration Points

Integrated with the libsepol tests build and the paired implementation file in the same directory.

## Risks and Edge Cases

The main risk is prototype drift between the header, implementation, and suite registration code.

## Test Signals

Compile/link success of the CUnit test binary is the relevant signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-linker-cond-map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-linker-roles.c -->
# sources/security-integrity/selinux/libsepol/tests/test-linker-roles.c

## Purpose

Verifies RBAC role symbols and role type sets after base-only and base-plus-module linking, including optional declarations and additive role type-set contributions. The source was read completely for this report (232 lines).

## Important APIs, Types, and Functions

`only_dominates_self()` walks each role dominance bitmap. `base_role_tests()` validates base/global and base/optional roles. `module_role_tests()` validates module roles and additive type-set placement across global and optional declaration scopes.

## Control Flow

Each case finds declaration IDs by tag, asserts role symbol scope, validates role type sets through `test_role_type_set()`, and confirms dominance does not gain unexpected role relationships.

## State and Persistence Behavior

No state is stored by this file; it reads caller-owned policydbs.

## Dependencies and Integration Points

Depends on libsepol policydb/link headers, CUnit, and local helper functions for declaration lookup and role type-set checking.

## Risks and Edge Cases

Key risks are incorrect unioning of role type sets, misplaced optional declaration data, and accidental dominance expansion beyond self-dominance.

## Test Signals

Test signal comes from exact role symbol presence, type-set contents, and dominance bitmap checks for both base and linked module databases.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-linker-roles.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-linker-roles.h -->
# sources/security-integrity/selinux/libsepol/tests/test-linker-roles.h

## Purpose

Header for the corresponding libsepol CUnit test module. It exposes the test entry point(s) `base_role_tests, module_role_tests` while hiding implementation details in the paired `.c` file. The source was read completely for this report (29 lines).

## Important APIs, Types, and Functions

Contains an include guard and prototypes for `base_role_tests, module_role_tests`. No types or macros beyond the guard are part of the API.

## Control Flow

There is no executable control flow; CUnit harness files include this header to register or invoke the test functions.

## State and Persistence Behavior

No state is declared or stored in this header.

## Dependencies and Integration Points

Integrated with the libsepol tests build and the paired implementation file in the same directory.

## Risks and Edge Cases

The main risk is prototype drift between the header, implementation, and suite registration code.

## Test Signals

Compile/link success of the CUnit test binary is the relevant signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-linker-roles.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-linker-types.c -->
# sources/security-integrity/selinux/libsepol/tests/test-linker-types.c

## Purpose

Exercises libsepol linker handling of types, attributes, aliases, declaration scopes, optional blocks, and type-attribute bitmap placement across base and module policy declarations. The source was read completely for this report (337 lines).

## Important APIs, Types, and Functions

`test_type_datum()` verifies global and declaration-local `type_datum_t` flavor, primary bit, and value consistency. `base_type_tests()` checks base/global/optional symbols and aliases. `module_type_tests()` checks copied module types, merged attributes, optional declaration-local type sets, multi-module additions, and alias mapping.

## Control Flow

The tests locate declarations by tag symbols, assert symbol presence in expected declaration IDs, then validate either type datums, attribute member type sets, or alias datums through local helpers.

## State and Persistence Behavior

No persistent state is owned; all reads are against the `policydb_t *base` supplied by the linker harness.

## Dependencies and Integration Points

Depends on libsepol `policydb` and `link` internals, CUnit, and local helpers such as `test_find_decl_by_sym`, `test_sym_presence`, `test_attr_types`, and `test_alias_datum`.

## Risks and Edge Cases

The risks under test are scope smashing, incorrect optional/global merge behavior, alias primary-value drift, and attribute bitmap updates landing in the wrong declaration table.

## Test Signals

A passing suite is a high-value signal for module linker symbol table correctness for type-related policy constructs.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-linker-types.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-linker-types.h -->
# sources/security-integrity/selinux/libsepol/tests/test-linker-types.h

## Purpose

Header for the corresponding libsepol CUnit test module. It exposes the test entry point(s) `base_type_tests, module_type_tests` while hiding implementation details in the paired `.c` file. The source was read completely for this report (29 lines).

## Important APIs, Types, and Functions

Contains an include guard and prototypes for `base_type_tests, module_type_tests`. No types or macros beyond the guard are part of the API.

## Control Flow

There is no executable control flow; CUnit harness files include this header to register or invoke the test functions.

## State and Persistence Behavior

No state is declared or stored in this header.

## Dependencies and Integration Points

Integrated with the libsepol tests build and the paired implementation file in the same directory.

## Risks and Edge Cases

The main risk is prototype drift between the header, implementation, and suite registration code.

## Test Signals

Compile/link success of the CUnit test binary is the relevant signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-linker-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-linker.c -->
# sources/security-integrity/selinux/libsepol/tests/test-linker.c

## Purpose

Main CUnit harness for libsepol module linker behavior. It loads one base module and two policy modules, links them into `linkedbase`, also links a no-module base as `basenomods`, then delegates role, type, and conditional checks to companion files. The source was read completely for this report (155 lines).

## Important APIs, Types, and Functions

`linker_test_init()` uses `test_load_policy()` and `link_modules()` to prepare fixtures. `linker_test_cleanup()` destroys base and module policydbs. `linker_add_tests()` registers index, type, role, and conditional tests. Static wrappers call `base_*` and `module_*` helper suites.

## Control Flow

Control flow is init/load all policies, link with and without modules, then CUnit calls wrapper tests over both the unaugmented base and linked base. Cleanup destroys each policydb and frees module pointers.

## State and Persistence Behavior

Owns static `policydb_t basenomods`, `linkedbase`, and a two-element module pointer array for suite lifetime. No disk writes occur.

## Dependencies and Integration Points

Depends on libsepol `link`, `expand`, and conditional policydb APIs plus local helper/test headers and fixture policy files in `policies/test-linker`.

## Risks and Edge Cases

Risks are early init failures leaking already allocated module policydbs and test fragility to fixture symbol names. Functionally, it targets regressions in declaration copying, optional scope preservation, and symbol indexes.

## Test Signals

Test signals are successful link of module fixtures, `test_policydb_indexes()`, and companion assertions for roles, types, aliases, attributes, and conditional booleans.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-linker.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-linker.h -->
# sources/security-integrity/selinux/libsepol/tests/test-linker.h

## Purpose

Header for the corresponding libsepol CUnit test module. It exposes the test entry point(s) `linker_test_init, linker_test_cleanup, linker_add_tests` while hiding implementation details in the paired `.c` file. The source was read completely for this report (30 lines).

## Important APIs, Types, and Functions

Contains an include guard and prototypes for `linker_test_init, linker_test_cleanup, linker_add_tests`. No types or macros beyond the guard are part of the API.

## Control Flow

There is no executable control flow; CUnit harness files include this header to register or invoke the test functions.

## State and Persistence Behavior

No state is declared or stored in this header.

## Dependencies and Integration Points

Integrated with the libsepol tests build and the paired implementation file in the same directory.

## Risks and Edge Cases

The main risk is prototype drift between the header, implementation, and suite registration code.

## Test Signals

Compile/link success of the CUnit test binary is the relevant signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-linker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-neverallow.c -->
# sources/security-integrity/selinux/libsepol/tests/test-neverallow.c

## Purpose

CUnit suite for neverallow and neverallowxperm assertion diagnostics. It builds several policy fixtures, expands them, runs `check_assertions()`, captures libsepol messages through a custom callback, and compares exact expected failure output. The source was read completely for this report (393 lines).

## Important APIs, Types, and Functions

`msg_handler()` stores formatted sepol messages in a linked list. `messages_check()` compares count and message text. Test cases cover basic neverallow, minus self, not self, and conditional neverallow scenarios. `neverallow_add_tests()` skips the suite under MLS mode and registers the four cases otherwise.

## Control Flow

Each test initializes policydbs, loads a fixture, links and expands it, installs the message callback on a `sepol_handle_t`, expects `check_assertions()` to fail, checks all messages, then destroys handle, messages, and policydbs.

## State and Persistence Behavior

State consists of a temporary linked list of captured messages and per-test policydb/handle objects. No persistent files are changed.

## Dependencies and Integration Points

Depends on libsepol debug/link/expand assertion APIs, local policy fixtures in `policies/test-neverallow`, GNU `vasprintf`, and CUnit.

## Risks and Edge Cases

Exact string expectations are intentionally brittle: line-number or wording changes require fixture/test updates. The list insertion order also depends on libsepol callback ordering.

## Test Signals

Strong signal for assertion matching, xperm diagnostics, self-set handling, conditional assertion evaluation, and user-visible error text.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-neverallow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-neverallow.h -->
# sources/security-integrity/selinux/libsepol/tests/test-neverallow.h

## Purpose

Header for the corresponding libsepol CUnit test module. It exposes the test entry point(s) `neverallow_test_init, neverallow_test_cleanup, neverallow_add_tests` while hiding implementation details in the paired `.c` file. The source was read completely for this report (10 lines).

## Important APIs, Types, and Functions

Contains an include guard and prototypes for `neverallow_test_init, neverallow_test_cleanup, neverallow_add_tests`. No types or macros beyond the guard are part of the API.

## Control Flow

There is no executable control flow; CUnit harness files include this header to register or invoke the test functions.

## State and Persistence Behavior

No state is declared or stored in this header.

## Dependencies and Integration Points

Integrated with the libsepol tests build and the paired implementation file in the same directory.

## Risks and Edge Cases

The main risk is prototype drift between the header, implementation, and suite registration code.

## Test Signals

Compile/link success of the CUnit test binary is the relevant signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-neverallow.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/utils/Makefile -->
# sources/security-integrity/selinux/libsepol/utils/Makefile

## Purpose

Builds all C utility programs in the libsepol utils directory from local `*.c` files. The source was read completely for this report (21 lines).

## Important APIs, Types, and Functions

Uses `TARGETS=$(patsubst %.c,%,...)`, compiles with `-I../include`, links with `-L../src -lsepol`, installs into `$(BINDIR)`, and cleans binaries/objects.

## Control Flow

Make target flow is declarative: variables establish install paths and flags, `all` builds local or child targets, `install` creates directories and installs artifacts, `clean` removes generated outputs, and `relabel` restores SELinux labels where applicable.

## State and Persistence Behavior

State is build output on disk: binaries, object files, installed files under `DESTDIR`, and relabeled paths. The makefile itself owns no runtime state.

## Dependencies and Integration Points

Integrates with the surrounding SELinux userspace build by sharing `PREFIX`, `DESTDIR`, `LIBSELINUX_LDLIBS`, `LINGUAS`, and recursive make conventions.

## Risks and Edge Cases

Risks include environment-dependent feature detection, install path mismatches, missing localized files, and relabel commands that assume SELinux tools are present on the build host.

## Test Signals

Signals are `make`, `make install DESTDIR=...`, `make clean`, optional relabel smoke tests, and feature-matrix builds where present.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/utils/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/utils/chkcon.c -->
# sources/security-integrity/selinux/libsepol/utils/chkcon.c

## Purpose

Small command-line utility that loads a binary policy and checks whether one or more supplied SELinux contexts are valid under that policy. The source was read completely for this report (44 lines).

## Important APIs, Types, and Functions

`main()` expects a policy path followed by contexts, loads the policy with `sepol_set_policydb_from_file()`, then calls `sepol_check_context()` for each context and prints validity.

## Control Flow

Open policy, load libsepol global policydb, iterate contexts, report invalid entries, and return failure if any check fails.

## State and Persistence Behavior

State is limited to libsepol process-global loaded policydb state and the opened policy file; no output is persisted.

## Dependencies and Integration Points

Depends on `sepol/sepol.h` and `sepol/policydb/services.h`. It integrates as a developer diagnostic built by the libsepol utils Makefile.

## Risks and Edge Cases

Risks are global libsepol policy state reuse in long-running embedding and sparse CLI diagnostics for malformed policies.

## Test Signals

Manual smoke signal: valid contexts return success, invalid contexts print an error and produce non-zero exit status.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/utils/chkcon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/utils/sepol_check_access.c -->
# sources/security-integrity/selinux/libsepol/utils/sepol_check_access.c

## Purpose

Policy diagnostic utility that answers whether a source context has one or more permissions to a target context/class and reports denial reasons. The source was read completely for this report (139 lines).

## Important APIs, Types, and Functions

`main()` loads a policy, maps source/target contexts to SIDs, maps a class and comma-separated permission list to an access vector, then calls `sepol_compute_av_reason_buffer()` and prints allowed or denial reasons.

## Control Flow

After input validation, permission parsing loops over comma-delimited names, accumulates an access vector, computes an AV decision, and exits `0` for fully allowed or `7` for denied.

## State and Persistence Behavior

Uses libsepol global policydb state and a heap `reason_buf` returned by libsepol. No persistent state.

## Dependencies and Integration Points

Depends on libsepol services APIs for policy loading, context/SID conversion, permission mapping, AV computation, and reason formatting.

## Risks and Edge Cases

One subtle risk is access-vector accumulation: the local `av` variable must be initialized before OR-style permission construction by the libsepol API path. CLI parsing also mutates only temporary permission slices.

## Test Signals

Signals include allowed/denied exit codes, reason categories for TE/constraint/RBAC/bounds, and constraint reason text when available.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/utils/sepol_check_access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/utils/sepol_compute_av.c -->
# sources/security-integrity/selinux/libsepol/utils/sepol_compute_av.c

## Purpose

Diagnostic wrapper for `sepol_compute_av()` that prints allowed, decided, auditallow, and auditdeny permission sets for a source/target/class request. The source was read completely for this report (71 lines).

## Important APIs, Types, and Functions

`main()` loads policy, converts contexts and class, calls `sepol_compute_av()`, and formats each returned access-vector field with `sepol_av_perm_to_string()`.

## Control Flow

Straight-line CLI flow: validate arity, load policy, convert identifiers, compute, switch on return code, print human-readable output.

## State and Persistence Behavior

State is process-local plus libsepol loaded policydb globals. No persistence.

## Dependencies and Integration Points

Depends on libsepol services and sepol public APIs; built with other libsepol utilities.

## Risks and Edge Cases

Risks are mainly diagnostic accuracy for invalid classes/contexts and ensuring errno-style returns are interpreted correctly.

## Test Signals

Useful smoke tests run known allow and deny examples and compare printed AV fields.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/utils/sepol_compute_av.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/utils/sepol_compute_member.c -->
# sources/security-integrity/selinux/libsepol/utils/sepol_compute_member.c

## Purpose

Computes a member SID/context for a source context, target context, and target class using the loaded SELinux policy. The source was read completely for this report (67 lines).

## Important APIs, Types, and Functions

`main()` loads policy, converts inputs to SIDs/class, calls `sepol_member_sid()`, converts the output SID back to context with `sepol_sid_to_context()`, prints it, and frees the returned context.

## Control Flow

The control flow is linear validation and computation; any conversion or compute failure prints an error and returns non-zero.

## State and Persistence Behavior

Only transient SIDs and a heap context string are held. The loaded policydb is process global inside libsepol.

## Dependencies and Integration Points

Depends on libsepol services APIs for type/member transition diagnostics.

## Risks and Edge Cases

Risks are poor differentiation between invalid input and policy absence, and reliance on loaded policydb global state.

## Test Signals

Test signal is a known type/member transition producing the expected output context.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/utils/sepol_compute_member.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/utils/sepol_compute_relabel.c -->
# sources/security-integrity/selinux/libsepol/utils/sepol_compute_relabel.c

## Purpose

Computes the relabel/change SID for source and target contexts under a target class. The source was read completely for this report (67 lines).

## Important APIs, Types, and Functions

`main()` mirrors the member utility but calls `sepol_change_sid()` and prints the converted output context.

## Control Flow

Load policy, convert contexts/class, compute changed SID, convert to context, print, and clean up.

## State and Persistence Behavior

No persisted state; uses transient libsepol SID values and a heap context string.

## Dependencies and Integration Points

Depends on libsepol policy loading and service decision APIs.

## Risks and Edge Cases

Risks are equivalent to the member tool: sparse diagnostics and reliance on global policydb initialization.

## Test Signals

Known relabel transition fixtures provide the best smoke signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/utils/sepol_compute_relabel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/utils/sepol_validate_transition.c -->
# sources/security-integrity/selinux/libsepol/utils/sepol_validate_transition.c

## Purpose

Validates whether a transition from old context to new context by a task context is permitted for a class, including explanatory denial text. The source was read completely for this report (78 lines).

## Important APIs, Types, and Functions

`main()` loads policy, maps old/new/task contexts and class, calls `sepol_validate_transition_reason_buffer(..., SHOW_GRANTED)`, prints `allowed` or `denied`, and returns `7` for denied transitions.

## Control Flow

The utility follows a strict parse/load/convert/validate/print path and frees the reason string before exit.

## State and Persistence Behavior

Only transient SID values and the reason buffer are stored. No persistence.

## Dependencies and Integration Points

Depends on libsepol validation APIs and policydb services.

## Risks and Edge Cases

Risks include interpreting negative errno returns and emitting reason text that may change across libsepol versions.

## Test Signals

Test signal is policy fixture coverage for allowed, denied, invalid context, and invalid class cases.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/utils/sepol_validate_transition.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/Makefile -->
# sources/security-integrity/selinux/mcstrans/Makefile

## Purpose

Top-level mcstrans recursive makefile. The source was read completely for this report (24 lines).

## Important APIs, Types, and Functions

Forwards `all`, `install`, `relabel`, and `clean` into `src`, `utils`, and `man` subdirectories and leaves `test` empty.

## Control Flow

Make target flow is declarative: variables establish install paths and flags, `all` builds local or child targets, `install` creates directories and installs artifacts, `clean` removes generated outputs, and `relabel` restores SELinux labels where applicable.

## State and Persistence Behavior

State is build output on disk: binaries, object files, installed files under `DESTDIR`, and relabeled paths. The makefile itself owns no runtime state.

## Dependencies and Integration Points

Integrates with the surrounding SELinux userspace build by sharing `PREFIX`, `DESTDIR`, `LIBSELINUX_LDLIBS`, `LINGUAS`, and recursive make conventions.

## Risks and Edge Cases

Risks include environment-dependent feature detection, install path mismatches, missing localized files, and relabel commands that assume SELinux tools are present on the build host.

## Test Signals

Signals are `make`, `make install DESTDIR=...`, `make clean`, optional relabel smoke tests, and feature-matrix builds where present.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/man/Makefile -->
# sources/security-integrity/selinux/mcstrans/man/Makefile

## Purpose

Installs mcstrans manual pages. The source was read completely for this report (31 lines).

## Important APIs, Types, and Functions

Creates man8 directories, installs local manpages, handles localized `LINGUAS`, and provides no-op all/clean/relabel targets.

## Control Flow

Make target flow is declarative: variables establish install paths and flags, `all` builds local or child targets, `install` creates directories and installs artifacts, `clean` removes generated outputs, and `relabel` restores SELinux labels where applicable.

## State and Persistence Behavior

State is build output on disk: binaries, object files, installed files under `DESTDIR`, and relabeled paths. The makefile itself owns no runtime state.

## Dependencies and Integration Points

Integrates with the surrounding SELinux userspace build by sharing `PREFIX`, `DESTDIR`, `LIBSELINUX_LDLIBS`, `LINGUAS`, and recursive make conventions.

## Risks and Edge Cases

Risks include environment-dependent feature detection, install path mismatches, missing localized files, and relabel commands that assume SELinux tools are present on the build host.

## Test Signals

Signals are `make`, `make install DESTDIR=...`, `make clean`, optional relabel smoke tests, and feature-matrix builds where present.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/man/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/default/setrans.conf -->
# sources/security-integrity/selinux/mcstrans/share/examples/default/setrans.conf

## Purpose

This is an mcstrans example example setrans translation configuration. It demonstrates syntax consumed by `mcstrans.c` when parsing translation or color data. The source was read completely for this report (52 lines).

## Important APIs, Types, and Functions

Important directives/signals: 0 Include directive(s), 0 Domain directive(s), 0 Base section marker(s), 0 ModifierGroup directive(s), about 26 mapping lines, and 0 constraint-style lines. The file is declarative rather than compiled code.

## Control Flow

At runtime the mcstrans parser reads the file line by line, strips comments/whitespace, splits directives on `=`, `!`, or `>`, expands Include globs, and appends domains, base classifications, modifier groups, words, defaults, constraints, or direct cache mappings.

## State and Persistence Behavior

The file persists administrator/example policy mapping data. Loaded daemon state becomes in-memory domains, groups, constraints, colors, and caches until reload or shutdown.

## Dependencies and Integration Points

Depends on mcstrans parser syntax and is used by example/test utilities under `share/util`; installed systems normally provide their own `/etc/selinux/.../setrans.conf` and `secolor.conf`.

## Risks and Edge Cases

Risks include ambiguous wording order, invalid raw category ranges, include path mistakes, constraints that reject intended levels, and example data being copied into production without local policy review.

## Test Signals

Signals are parser acceptance, `mlstrans-test`/`mlscolor-test` output, round-trip raw/trans conversions, and daemon reload behavior with this file selected.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/default/setrans.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/include/setrans.conf -->
# sources/security-integrity/selinux/mcstrans/share/examples/include/setrans.conf

## Purpose

This is an mcstrans example example setrans translation configuration. It demonstrates syntax consumed by `mcstrans.c` when parsing translation or color data. The source was read completely for this report (15 lines).

## Important APIs, Types, and Functions

Important directives/signals: 1 Include directive(s), 0 Domain directive(s), 0 Base section marker(s), 0 ModifierGroup directive(s), about 1 mapping lines, and 0 constraint-style lines. The file is declarative rather than compiled code.

## Control Flow

At runtime the mcstrans parser reads the file line by line, strips comments/whitespace, splits directives on `=`, `!`, or `>`, expands Include globs, and appends domains, base classifications, modifier groups, words, defaults, constraints, or direct cache mappings.

## State and Persistence Behavior

The file persists administrator/example policy mapping data. Loaded daemon state becomes in-memory domains, groups, constraints, colors, and caches until reload or shutdown.

## Dependencies and Integration Points

Depends on mcstrans parser syntax and is used by example/test utilities under `share/util`; installed systems normally provide their own `/etc/selinux/.../setrans.conf` and `secolor.conf`.

## Risks and Edge Cases

Risks include ambiguous wording order, invalid raw category ranges, include path mistakes, constraints that reject intended levels, and example data being copied into production without local policy review.

## Test Signals

Signals are parser acceptance, `mlstrans-test`/`mlscolor-test` output, round-trip raw/trans conversions, and daemon reload behavior with this file selected.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/include/setrans.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/nato/setrans.conf -->
# sources/security-integrity/selinux/mcstrans/share/examples/nato/setrans.conf

## Purpose

This is an mcstrans example example setrans translation configuration. It demonstrates syntax consumed by `mcstrans.c` when parsing translation or color data. The source was read completely for this report (23 lines).

## Important APIs, Types, and Functions

Important directives/signals: 3 Include directive(s), 1 Domain directive(s), 1 Base section marker(s), 0 ModifierGroup directive(s), about 16 mapping lines, and 0 constraint-style lines. The file is declarative rather than compiled code.

## Control Flow

At runtime the mcstrans parser reads the file line by line, strips comments/whitespace, splits directives on `=`, `!`, or `>`, expands Include globs, and appends domains, base classifications, modifier groups, words, defaults, constraints, or direct cache mappings.

## State and Persistence Behavior

The file persists administrator/example policy mapping data. Loaded daemon state becomes in-memory domains, groups, constraints, colors, and caches until reload or shutdown.

## Dependencies and Integration Points

Depends on mcstrans parser syntax and is used by example/test utilities under `share/util`; installed systems normally provide their own `/etc/selinux/.../setrans.conf` and `secolor.conf`.

## Risks and Edge Cases

Risks include ambiguous wording order, invalid raw category ranges, include path mistakes, constraints that reject intended levels, and example data being copied into production without local policy review.

## Test Signals

Signals are parser acceptance, `mlstrans-test`/`mlscolor-test` output, round-trip raw/trans conversions, and daemon reload behavior with this file selected.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/nato/setrans.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/nato/setrans.d/constraints.conf -->
# sources/security-integrity/selinux/mcstrans/share/examples/nato/setrans.d/constraints.conf

## Purpose

This is an mcstrans example constraint include file limiting invalid sensitivity/category combinations. It demonstrates syntax consumed by `mcstrans.c` when parsing translation or color data. The source was read completely for this report (10 lines).

## Important APIs, Types, and Functions

Important directives/signals: 0 Include directive(s), 0 Domain directive(s), 0 Base section marker(s), 0 ModifierGroup directive(s), about 0 mapping lines, and 1 constraint-style lines. The file is declarative rather than compiled code.

## Control Flow

At runtime the mcstrans parser reads the file line by line, strips comments/whitespace, splits directives on `=`, `!`, or `>`, expands Include globs, and appends domains, base classifications, modifier groups, words, defaults, constraints, or direct cache mappings.

## State and Persistence Behavior

The file persists administrator/example policy mapping data. Loaded daemon state becomes in-memory domains, groups, constraints, colors, and caches until reload or shutdown.

## Dependencies and Integration Points

Depends on mcstrans parser syntax and is used by example/test utilities under `share/util`; installed systems normally provide their own `/etc/selinux/.../setrans.conf` and `secolor.conf`.

## Risks and Edge Cases

Risks include ambiguous wording order, invalid raw category ranges, include path mistakes, constraints that reject intended levels, and example data being copied into production without local policy review.

## Test Signals

Signals are parser acceptance, `mlstrans-test`/`mlscolor-test` output, round-trip raw/trans conversions, and daemon reload behavior with this file selected.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/nato/setrans.d/constraints.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/nato/setrans.d/eyes-only.conf -->
# sources/security-integrity/selinux/mcstrans/share/examples/nato/setrans.d/eyes-only.conf

## Purpose

This is an mcstrans example large NATO example mapping many category combinations to eyes-only caveat words. It demonstrates syntax consumed by `mcstrans.c` when parsing translation or color data. The source was read completely for this report (748 lines).

## Important APIs, Types, and Functions

Important directives/signals: 0 Include directive(s), 0 Domain directive(s), 0 Base section marker(s), 1 ModifierGroup directive(s), about 483 mapping lines, and 0 constraint-style lines. The file is declarative rather than compiled code.

## Control Flow

At runtime the mcstrans parser reads the file line by line, strips comments/whitespace, splits directives on `=`, `!`, or `>`, expands Include globs, and appends domains, base classifications, modifier groups, words, defaults, constraints, or direct cache mappings.

## State and Persistence Behavior

The file persists administrator/example policy mapping data. Loaded daemon state becomes in-memory domains, groups, constraints, colors, and caches until reload or shutdown.

## Dependencies and Integration Points

Depends on mcstrans parser syntax and is used by example/test utilities under `share/util`; installed systems normally provide their own `/etc/selinux/.../setrans.conf` and `secolor.conf`.

## Risks and Edge Cases

Risks include ambiguous wording order, invalid raw category ranges, include path mistakes, constraints that reject intended levels, and example data being copied into production without local policy review.

## Test Signals

Signals are parser acceptance, `mlstrans-test`/`mlscolor-test` output, round-trip raw/trans conversions, and daemon reload behavior with this file selected.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/nato/setrans.d/eyes-only.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/nato/setrans.d/rel.conf -->
# sources/security-integrity/selinux/mcstrans/share/examples/nato/setrans.d/rel.conf

## Purpose

This is an mcstrans example large NATO releasability mapping table translating category sets to release markings. It demonstrates syntax consumed by `mcstrans.c` when parsing translation or color data. The source was read completely for this report (751 lines).

## Important APIs, Types, and Functions

Important directives/signals: 0 Include directive(s), 0 Domain directive(s), 0 Base section marker(s), 1 ModifierGroup directive(s), about 485 mapping lines, and 0 constraint-style lines. The file is declarative rather than compiled code.

## Control Flow

At runtime the mcstrans parser reads the file line by line, strips comments/whitespace, splits directives on `=`, `!`, or `>`, expands Include globs, and appends domains, base classifications, modifier groups, words, defaults, constraints, or direct cache mappings.

## State and Persistence Behavior

The file persists administrator/example policy mapping data. Loaded daemon state becomes in-memory domains, groups, constraints, colors, and caches until reload or shutdown.

## Dependencies and Integration Points

Depends on mcstrans parser syntax and is used by example/test utilities under `share/util`; installed systems normally provide their own `/etc/selinux/.../setrans.conf` and `secolor.conf`.

## Risks and Edge Cases

Risks include ambiguous wording order, invalid raw category ranges, include path mistakes, constraints that reject intended levels, and example data being copied into production without local policy review.

## Test Signals

Signals are parser acceptance, `mlstrans-test`/`mlscolor-test` output, round-trip raw/trans conversions, and daemon reload behavior with this file selected.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/nato/setrans.d/rel.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/non-mls-color/secolor.conf -->
# sources/security-integrity/selinux/mcstrans/share/examples/non-mls-color/secolor.conf

## Purpose

This is an mcstrans example color mapping configuration for mcstrans raw-context-to-color lookup. It demonstrates syntax consumed by `mcstrans.c` when parsing translation or color data. The source was read completely for this report (13 lines).

## Important APIs, Types, and Functions

Important directives/signals: 0 Include directive(s), 0 Domain directive(s), 0 Base section marker(s), 0 ModifierGroup directive(s), about 11 mapping lines, and 0 constraint-style lines. The file is declarative rather than compiled code.

## Control Flow

At runtime the mcstrans parser reads the file line by line, strips comments/whitespace, splits directives on `=`, `!`, or `>`, expands Include globs, and appends domains, base classifications, modifier groups, words, defaults, constraints, or direct cache mappings.

## State and Persistence Behavior

The file persists administrator/example policy mapping data. Loaded daemon state becomes in-memory domains, groups, constraints, colors, and caches until reload or shutdown.

## Dependencies and Integration Points

Depends on mcstrans parser syntax and is used by example/test utilities under `share/util`; installed systems normally provide their own `/etc/selinux/.../setrans.conf` and `secolor.conf`.

## Risks and Edge Cases

Risks include ambiguous wording order, invalid raw category ranges, include path mistakes, constraints that reject intended levels, and example data being copied into production without local policy review.

## Test Signals

Signals are parser acceptance, `mlstrans-test`/`mlscolor-test` output, round-trip raw/trans conversions, and daemon reload behavior with this file selected.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/non-mls-color/secolor.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/pipes/setrans.conf -->
# sources/security-integrity/selinux/mcstrans/share/examples/pipes/setrans.conf

## Purpose

This is an mcstrans example example setrans translation configuration. It demonstrates syntax consumed by `mcstrans.c` when parsing translation or color data. The source was read completely for this report (20 lines).

## Important APIs, Types, and Functions

Important directives/signals: 1 Include directive(s), 1 Domain directive(s), 1 Base section marker(s), 0 ModifierGroup directive(s), about 16 mapping lines, and 0 constraint-style lines. The file is declarative rather than compiled code.

## Control Flow

At runtime the mcstrans parser reads the file line by line, strips comments/whitespace, splits directives on `=`, `!`, or `>`, expands Include globs, and appends domains, base classifications, modifier groups, words, defaults, constraints, or direct cache mappings.

## State and Persistence Behavior

The file persists administrator/example policy mapping data. Loaded daemon state becomes in-memory domains, groups, constraints, colors, and caches until reload or shutdown.

## Dependencies and Integration Points

Depends on mcstrans parser syntax and is used by example/test utilities under `share/util`; installed systems normally provide their own `/etc/selinux/.../setrans.conf` and `secolor.conf`.

## Risks and Edge Cases

Risks include ambiguous wording order, invalid raw category ranges, include path mistakes, constraints that reject intended levels, and example data being copied into production without local policy review.

## Test Signals

Signals are parser acceptance, `mlstrans-test`/`mlscolor-test` output, round-trip raw/trans conversions, and daemon reload behavior with this file selected.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/pipes/setrans.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/pipes/setrans.d/pipes.conf -->
# sources/security-integrity/selinux/mcstrans/share/examples/pipes/setrans.d/pipes.conf

## Purpose

This is an mcstrans example included pipe-specific modifier group example. It demonstrates syntax consumed by `mcstrans.c` when parsing translation or color data. The source was read completely for this report (11 lines).

## Important APIs, Types, and Functions

Important directives/signals: 0 Include directive(s), 0 Domain directive(s), 0 Base section marker(s), 1 ModifierGroup directive(s), about 10 mapping lines, and 0 constraint-style lines. The file is declarative rather than compiled code.

## Control Flow

At runtime the mcstrans parser reads the file line by line, strips comments/whitespace, splits directives on `=`, `!`, or `>`, expands Include globs, and appends domains, base classifications, modifier groups, words, defaults, constraints, or direct cache mappings.

## State and Persistence Behavior

The file persists administrator/example policy mapping data. Loaded daemon state becomes in-memory domains, groups, constraints, colors, and caches until reload or shutdown.

## Dependencies and Integration Points

Depends on mcstrans parser syntax and is used by example/test utilities under `share/util`; installed systems normally provide their own `/etc/selinux/.../setrans.conf` and `secolor.conf`.

## Risks and Edge Cases

Risks include ambiguous wording order, invalid raw category ranges, include path mistakes, constraints that reject intended levels, and example data being copied into production without local policy review.

## Test Signals

Signals are parser acceptance, `mlstrans-test`/`mlscolor-test` output, round-trip raw/trans conversions, and daemon reload behavior with this file selected.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/pipes/setrans.d/pipes.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/urcsts-via-include/secolor.conf -->
# sources/security-integrity/selinux/mcstrans/share/examples/urcsts-via-include/secolor.conf

## Purpose

This is an mcstrans example color mapping configuration for mcstrans raw-context-to-color lookup. It demonstrates syntax consumed by `mcstrans.c` when parsing translation or color data. The source was read completely for this report (21 lines).

## Important APIs, Types, and Functions

Important directives/signals: 0 Include directive(s), 0 Domain directive(s), 0 Base section marker(s), 0 ModifierGroup directive(s), about 18 mapping lines, and 0 constraint-style lines. The file is declarative rather than compiled code.

## Control Flow

At runtime the mcstrans parser reads the file line by line, strips comments/whitespace, splits directives on `=`, `!`, or `>`, expands Include globs, and appends domains, base classifications, modifier groups, words, defaults, constraints, or direct cache mappings.

## State and Persistence Behavior

The file persists administrator/example policy mapping data. Loaded daemon state becomes in-memory domains, groups, constraints, colors, and caches until reload or shutdown.

## Dependencies and Integration Points

Depends on mcstrans parser syntax and is used by example/test utilities under `share/util`; installed systems normally provide their own `/etc/selinux/.../setrans.conf` and `secolor.conf`.

## Risks and Edge Cases

Risks include ambiguous wording order, invalid raw category ranges, include path mistakes, constraints that reject intended levels, and example data being copied into production without local policy review.

## Test Signals

Signals are parser acceptance, `mlstrans-test`/`mlscolor-test` output, round-trip raw/trans conversions, and daemon reload behavior with this file selected.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/urcsts-via-include/secolor.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/urcsts-via-include/setrans.conf -->
# sources/security-integrity/selinux/mcstrans/share/examples/urcsts-via-include/setrans.conf

## Purpose

This is an mcstrans example example setrans translation configuration. It demonstrates syntax consumed by `mcstrans.c` when parsing translation or color data. The source was read completely for this report (15 lines).

## Important APIs, Types, and Functions

Important directives/signals: 1 Include directive(s), 0 Domain directive(s), 0 Base section marker(s), 0 ModifierGroup directive(s), about 1 mapping lines, and 0 constraint-style lines. The file is declarative rather than compiled code.

## Control Flow

At runtime the mcstrans parser reads the file line by line, strips comments/whitespace, splits directives on `=`, `!`, or `>`, expands Include globs, and appends domains, base classifications, modifier groups, words, defaults, constraints, or direct cache mappings.

## State and Persistence Behavior

The file persists administrator/example policy mapping data. Loaded daemon state becomes in-memory domains, groups, constraints, colors, and caches until reload or shutdown.

## Dependencies and Integration Points

Depends on mcstrans parser syntax and is used by example/test utilities under `share/util`; installed systems normally provide their own `/etc/selinux/.../setrans.conf` and `secolor.conf`.

## Risks and Edge Cases

Risks include ambiguous wording order, invalid raw category ranges, include path mistakes, constraints that reject intended levels, and example data being copied into production without local policy review.

## Test Signals

Signals are parser acceptance, `mlstrans-test`/`mlscolor-test` output, round-trip raw/trans conversions, and daemon reload behavior with this file selected.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/urcsts-via-include/setrans.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/urcsts-via-include/setrans.d/c.conf -->
# sources/security-integrity/selinux/mcstrans/share/examples/urcsts-via-include/setrans.d/c.conf

## Purpose

This is an mcstrans example small included setrans fragment contributing one modifier/base mapping family. It demonstrates syntax consumed by `mcstrans.c` when parsing translation or color data. The source was read completely for this report (7 lines).

## Important APIs, Types, and Functions

Important directives/signals: 0 Include directive(s), 0 Domain directive(s), 0 Base section marker(s), 0 ModifierGroup directive(s), about 3 mapping lines, and 0 constraint-style lines. The file is declarative rather than compiled code.

## Control Flow

At runtime the mcstrans parser reads the file line by line, strips comments/whitespace, splits directives on `=`, `!`, or `>`, expands Include globs, and appends domains, base classifications, modifier groups, words, defaults, constraints, or direct cache mappings.

## State and Persistence Behavior

The file persists administrator/example policy mapping data. Loaded daemon state becomes in-memory domains, groups, constraints, colors, and caches until reload or shutdown.

## Dependencies and Integration Points

Depends on mcstrans parser syntax and is used by example/test utilities under `share/util`; installed systems normally provide their own `/etc/selinux/.../setrans.conf` and `secolor.conf`.

## Risks and Edge Cases

Risks include ambiguous wording order, invalid raw category ranges, include path mistakes, constraints that reject intended levels, and example data being copied into production without local policy review.

## Test Signals

Signals are parser acceptance, `mlstrans-test`/`mlscolor-test` output, round-trip raw/trans conversions, and daemon reload behavior with this file selected.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/urcsts-via-include/setrans.d/c.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/urcsts-via-include/setrans.d/r.conf -->
# sources/security-integrity/selinux/mcstrans/share/examples/urcsts-via-include/setrans.d/r.conf

## Purpose

This is an mcstrans example small included setrans fragment contributing one modifier/base mapping family. It demonstrates syntax consumed by `mcstrans.c` when parsing translation or color data. The source was read completely for this report (7 lines).

## Important APIs, Types, and Functions

Important directives/signals: 0 Include directive(s), 0 Domain directive(s), 0 Base section marker(s), 0 ModifierGroup directive(s), about 3 mapping lines, and 0 constraint-style lines. The file is declarative rather than compiled code.

## Control Flow

At runtime the mcstrans parser reads the file line by line, strips comments/whitespace, splits directives on `=`, `!`, or `>`, expands Include globs, and appends domains, base classifications, modifier groups, words, defaults, constraints, or direct cache mappings.

## State and Persistence Behavior

The file persists administrator/example policy mapping data. Loaded daemon state becomes in-memory domains, groups, constraints, colors, and caches until reload or shutdown.

## Dependencies and Integration Points

Depends on mcstrans parser syntax and is used by example/test utilities under `share/util`; installed systems normally provide their own `/etc/selinux/.../setrans.conf` and `secolor.conf`.

## Risks and Edge Cases

Risks include ambiguous wording order, invalid raw category ranges, include path mistakes, constraints that reject intended levels, and example data being copied into production without local policy review.

## Test Signals

Signals are parser acceptance, `mlstrans-test`/`mlscolor-test` output, round-trip raw/trans conversions, and daemon reload behavior with this file selected.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/urcsts-via-include/setrans.d/r.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/urcsts-via-include/setrans.d/s.conf -->
# sources/security-integrity/selinux/mcstrans/share/examples/urcsts-via-include/setrans.d/s.conf

## Purpose

This is an mcstrans example small included setrans fragment contributing one modifier/base mapping family. It demonstrates syntax consumed by `mcstrans.c` when parsing translation or color data. The source was read completely for this report (7 lines).

## Important APIs, Types, and Functions

Important directives/signals: 0 Include directive(s), 0 Domain directive(s), 0 Base section marker(s), 0 ModifierGroup directive(s), about 3 mapping lines, and 0 constraint-style lines. The file is declarative rather than compiled code.

## Control Flow

At runtime the mcstrans parser reads the file line by line, strips comments/whitespace, splits directives on `=`, `!`, or `>`, expands Include globs, and appends domains, base classifications, modifier groups, words, defaults, constraints, or direct cache mappings.

## State and Persistence Behavior

The file persists administrator/example policy mapping data. Loaded daemon state becomes in-memory domains, groups, constraints, colors, and caches until reload or shutdown.

## Dependencies and Integration Points

Depends on mcstrans parser syntax and is used by example/test utilities under `share/util`; installed systems normally provide their own `/etc/selinux/.../setrans.conf` and `secolor.conf`.

## Risks and Edge Cases

Risks include ambiguous wording order, invalid raw category ranges, include path mistakes, constraints that reject intended levels, and example data being copied into production without local policy review.

## Test Signals

Signals are parser acceptance, `mlstrans-test`/`mlscolor-test` output, round-trip raw/trans conversions, and daemon reload behavior with this file selected.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/urcsts-via-include/setrans.d/s.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/urcsts-via-include/setrans.d/system.conf -->
# sources/security-integrity/selinux/mcstrans/share/examples/urcsts-via-include/setrans.d/system.conf

## Purpose

This is an mcstrans example small included setrans fragment contributing one modifier/base mapping family. It demonstrates syntax consumed by `mcstrans.c` when parsing translation or color data. The source was read completely for this report (6 lines).

## Important APIs, Types, and Functions

Important directives/signals: 0 Include directive(s), 0 Domain directive(s), 0 Base section marker(s), 0 ModifierGroup directive(s), about 2 mapping lines, and 0 constraint-style lines. The file is declarative rather than compiled code.

## Control Flow

At runtime the mcstrans parser reads the file line by line, strips comments/whitespace, splits directives on `=`, `!`, or `>`, expands Include globs, and appends domains, base classifications, modifier groups, words, defaults, constraints, or direct cache mappings.

## State and Persistence Behavior

The file persists administrator/example policy mapping data. Loaded daemon state becomes in-memory domains, groups, constraints, colors, and caches until reload or shutdown.

## Dependencies and Integration Points

Depends on mcstrans parser syntax and is used by example/test utilities under `share/util`; installed systems normally provide their own `/etc/selinux/.../setrans.conf` and `secolor.conf`.

## Risks and Edge Cases

Risks include ambiguous wording order, invalid raw category ranges, include path mistakes, constraints that reject intended levels, and example data being copied into production without local policy review.

## Test Signals

Signals are parser acceptance, `mlstrans-test`/`mlscolor-test` output, round-trip raw/trans conversions, and daemon reload behavior with this file selected.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/urcsts-via-include/setrans.d/system.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/urcsts-via-include/setrans.d/ts.conf -->
# sources/security-integrity/selinux/mcstrans/share/examples/urcsts-via-include/setrans.d/ts.conf

## Purpose

This is an mcstrans example small included setrans fragment contributing one modifier/base mapping family. It demonstrates syntax consumed by `mcstrans.c` when parsing translation or color data. The source was read completely for this report (8 lines).

## Important APIs, Types, and Functions

Important directives/signals: 0 Include directive(s), 0 Domain directive(s), 0 Base section marker(s), 0 ModifierGroup directive(s), about 4 mapping lines, and 0 constraint-style lines. The file is declarative rather than compiled code.

## Control Flow

At runtime the mcstrans parser reads the file line by line, strips comments/whitespace, splits directives on `=`, `!`, or `>`, expands Include globs, and appends domains, base classifications, modifier groups, words, defaults, constraints, or direct cache mappings.

## State and Persistence Behavior

The file persists administrator/example policy mapping data. Loaded daemon state becomes in-memory domains, groups, constraints, colors, and caches until reload or shutdown.

## Dependencies and Integration Points

Depends on mcstrans parser syntax and is used by example/test utilities under `share/util`; installed systems normally provide their own `/etc/selinux/.../setrans.conf` and `secolor.conf`.

## Risks and Edge Cases

Risks include ambiguous wording order, invalid raw category ranges, include path mistakes, constraints that reject intended levels, and example data being copied into production without local policy review.

## Test Signals

Signals are parser acceptance, `mlstrans-test`/`mlscolor-test` output, round-trip raw/trans conversions, and daemon reload behavior with this file selected.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/urcsts-via-include/setrans.d/ts.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/urcsts-via-include/setrans.d/u.conf -->
# sources/security-integrity/selinux/mcstrans/share/examples/urcsts-via-include/setrans.d/u.conf

## Purpose

This is an mcstrans example small included setrans fragment contributing one modifier/base mapping family. It demonstrates syntax consumed by `mcstrans.c` when parsing translation or color data. The source was read completely for this report (7 lines).

## Important APIs, Types, and Functions

Important directives/signals: 0 Include directive(s), 0 Domain directive(s), 0 Base section marker(s), 0 ModifierGroup directive(s), about 3 mapping lines, and 0 constraint-style lines. The file is declarative rather than compiled code.

## Control Flow

At runtime the mcstrans parser reads the file line by line, strips comments/whitespace, splits directives on `=`, `!`, or `>`, expands Include globs, and appends domains, base classifications, modifier groups, words, defaults, constraints, or direct cache mappings.

## State and Persistence Behavior

The file persists administrator/example policy mapping data. Loaded daemon state becomes in-memory domains, groups, constraints, colors, and caches until reload or shutdown.

## Dependencies and Integration Points

Depends on mcstrans parser syntax and is used by example/test utilities under `share/util`; installed systems normally provide their own `/etc/selinux/.../setrans.conf` and `secolor.conf`.

## Risks and Edge Cases

Risks include ambiguous wording order, invalid raw category ranges, include path mistakes, constraints that reject intended levels, and example data being copied into production without local policy review.

## Test Signals

Signals are parser acceptance, `mlstrans-test`/`mlscolor-test` output, round-trip raw/trans conversions, and daemon reload behavior with this file selected.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/urcsts-via-include/setrans.d/u.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/urcsts/secolor.conf -->
# sources/security-integrity/selinux/mcstrans/share/examples/urcsts/secolor.conf

## Purpose

This is an mcstrans example color mapping configuration for mcstrans raw-context-to-color lookup. It demonstrates syntax consumed by `mcstrans.c` when parsing translation or color data. The source was read completely for this report (21 lines).

## Important APIs, Types, and Functions

Important directives/signals: 0 Include directive(s), 0 Domain directive(s), 0 Base section marker(s), 0 ModifierGroup directive(s), about 18 mapping lines, and 0 constraint-style lines. The file is declarative rather than compiled code.

## Control Flow

At runtime the mcstrans parser reads the file line by line, strips comments/whitespace, splits directives on `=`, `!`, or `>`, expands Include globs, and appends domains, base classifications, modifier groups, words, defaults, constraints, or direct cache mappings.

## State and Persistence Behavior

The file persists administrator/example policy mapping data. Loaded daemon state becomes in-memory domains, groups, constraints, colors, and caches until reload or shutdown.

## Dependencies and Integration Points

Depends on mcstrans parser syntax and is used by example/test utilities under `share/util`; installed systems normally provide their own `/etc/selinux/.../setrans.conf` and `secolor.conf`.

## Risks and Edge Cases

Risks include ambiguous wording order, invalid raw category ranges, include path mistakes, constraints that reject intended levels, and example data being copied into production without local policy review.

## Test Signals

Signals are parser acceptance, `mlstrans-test`/`mlscolor-test` output, round-trip raw/trans conversions, and daemon reload behavior with this file selected.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/urcsts/secolor.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/urcsts/setrans.conf -->
# sources/security-integrity/selinux/mcstrans/share/examples/urcsts/setrans.conf

## Purpose

This is an mcstrans example example setrans translation configuration. It demonstrates syntax consumed by `mcstrans.c` when parsing translation or color data. The source was read completely for this report (27 lines).

## Important APIs, Types, and Functions

Important directives/signals: 0 Include directive(s), 0 Domain directive(s), 0 Base section marker(s), 0 ModifierGroup directive(s), about 18 mapping lines, and 0 constraint-style lines. The file is declarative rather than compiled code.

## Control Flow

At runtime the mcstrans parser reads the file line by line, strips comments/whitespace, splits directives on `=`, `!`, or `>`, expands Include globs, and appends domains, base classifications, modifier groups, words, defaults, constraints, or direct cache mappings.

## State and Persistence Behavior

The file persists administrator/example policy mapping data. Loaded daemon state becomes in-memory domains, groups, constraints, colors, and caches until reload or shutdown.

## Dependencies and Integration Points

Depends on mcstrans parser syntax and is used by example/test utilities under `share/util`; installed systems normally provide their own `/etc/selinux/.../setrans.conf` and `secolor.conf`.

## Risks and Edge Cases

Risks include ambiguous wording order, invalid raw category ranges, include path mistakes, constraints that reject intended levels, and example data being copied into production without local policy review.

## Test Signals

Signals are parser acceptance, `mlstrans-test`/`mlscolor-test` output, round-trip raw/trans conversions, and daemon reload behavior with this file selected.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/examples/urcsts/setrans.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/util/mlscolor-test -->
# sources/security-integrity/selinux/mcstrans/share/util/mlscolor-test

## Purpose

Shell test helper for exercising mcstrans example configurations and conversion/color utilities. The source was read completely for this report (44 lines).

## Important APIs, Types, and Functions

Uses shell commands from the mcstrans build/install environment; first line is `#!/usr/bin/python3 -E`. The script drives combinations of example config files, translation/color utilities, or daemon/client calls depending on its role.

## Control Flow

Control flow is shell sequencing: choose example data, invoke mcstrans utilities, compare or display conversion results, and propagate command failures through shell exit status where implemented.

## State and Persistence Behavior

State is temporary process environment, selected config paths, and command output. It may depend on installed or locally built utilities but does not define daemon state itself.

## Dependencies and Integration Points

Depends on POSIX shell, mcstrans utilities, example `setrans.conf`/`secolor.conf` trees, and an SELinux/MLS-capable environment.

## Risks and Edge Cases

Risks are hard-coded relative paths, environment sensitivity, and tests that are more demonstrative than assertive if output is not compared.

## Test Signals

Useful signals are successful execution over all bundled examples and visible expected translations/colors.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/util/mlscolor-test -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/util/mlstrans-test -->
# sources/security-integrity/selinux/mcstrans/share/util/mlstrans-test

## Purpose

Shell test helper for exercising mcstrans example configurations and conversion/color utilities. The source was read completely for this report (57 lines).

## Important APIs, Types, and Functions

Uses shell commands from the mcstrans build/install environment; first line is `#!/usr/bin/python3 -E`. The script drives combinations of example config files, translation/color utilities, or daemon/client calls depending on its role.

## Control Flow

Control flow is shell sequencing: choose example data, invoke mcstrans utilities, compare or display conversion results, and propagate command failures through shell exit status where implemented.

## State and Persistence Behavior

State is temporary process environment, selected config paths, and command output. It may depend on installed or locally built utilities but does not define daemon state itself.

## Dependencies and Integration Points

Depends on POSIX shell, mcstrans utilities, example `setrans.conf`/`secolor.conf` trees, and an SELinux/MLS-capable environment.

## Risks and Edge Cases

Risks are hard-coded relative paths, environment sensitivity, and tests that are more demonstrative than assertive if output is not compared.

## Test Signals

Useful signals are successful execution over all bundled examples and visible expected translations/colors.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/util/mlstrans-test -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/util/try-all -->
# sources/security-integrity/selinux/mcstrans/share/util/try-all

## Purpose

Shell test helper for exercising mcstrans example configurations and conversion/color utilities. The source was read completely for this report (64 lines).

## Important APIs, Types, and Functions

Uses shell commands from the mcstrans build/install environment; first line is `#!/bin/bash`. The script drives combinations of example config files, translation/color utilities, or daemon/client calls depending on its role.

## Control Flow

Control flow is shell sequencing: choose example data, invoke mcstrans utilities, compare or display conversion results, and propagate command failures through shell exit status where implemented.

## State and Persistence Behavior

State is temporary process environment, selected config paths, and command output. It may depend on installed or locally built utilities but does not define daemon state itself.

## Dependencies and Integration Points

Depends on POSIX shell, mcstrans utilities, example `setrans.conf`/`secolor.conf` trees, and an SELinux/MLS-capable environment.

## Risks and Edge Cases

Risks are hard-coded relative paths, environment sensitivity, and tests that are more demonstrative than assertive if output is not compared.

## Test Signals

Useful signals are successful execution over all bundled examples and visible expected translations/colors.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/share/util/try-all -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/Makefile -->
# sources/security-integrity/selinux/mcstrans/src/Makefile

## Purpose

Builds and installs the `mcstransd` daemon and systemd service. The source was read completely for this report (39 lines).

## Important APIs, Types, and Functions

Compiles sources with libselinux/libsepol/PCRE2/capability dependencies, installs daemon under sbin, service under systemd unit dir, and supports relabel/clean.

## Control Flow

Make target flow is declarative: variables establish install paths and flags, `all` builds local or child targets, `install` creates directories and installs artifacts, `clean` removes generated outputs, and `relabel` restores SELinux labels where applicable.

## State and Persistence Behavior

State is build output on disk: binaries, object files, installed files under `DESTDIR`, and relabeled paths. The makefile itself owns no runtime state.

## Dependencies and Integration Points

Integrates with the surrounding SELinux userspace build by sharing `PREFIX`, `DESTDIR`, `LIBSELINUX_LDLIBS`, `LINGUAS`, and recursive make conventions.

## Risks and Edge Cases

Risks include environment-dependent feature detection, install path mismatches, missing localized files, and relabel commands that assume SELinux tools are present on the build host.

## Test Signals

Signals are `make`, `make install DESTDIR=...`, `make clean`, optional relabel smoke tests, and feature-matrix builds where present.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mcscolor.c -->
# sources/security-integrity/selinux/mcstrans/src/mcscolor.c

## Purpose

Color translation engine for SELinux contexts. It parses `secolor.conf`, maps raw MLS/MCS patterns to foreground/background color strings, supports color mnemonics, and selects the best matching pattern for a raw context. The source was read completely for this report (362 lines).

## Important APIs, Types, and Functions

Exports `init_colors()`, `finish_context_colors()`, and `raw_color()`. Internal helpers include `check_dominance()` for pattern matching, `add_secolor()`, `find_mnemonic()`, `add_mnemonic()`, `process_color()`, and `parse_components()`.

## Control Flow

Initialization reads `selinux_colors_path()`, processes mnemonic and context color lines, and stores mappings in memory. `raw_color()` parses a context, compares raw range/category dominance against configured patterns, and returns a string color pair.

## State and Persistence Behavior

State is static color/mnemonic arrays or lists populated at init and freed by finish. No persistent writes occur.

## Dependencies and Integration Points

Depends on libselinux context/path APIs, local MLS parsing utilities, stdio parsing, and config files such as `secolor.conf` examples.

## Risks and Edge Cases

Risks include parser ambiguity, malformed hex colors, dominance matching errors for category ranges, and stale state if reload cleanup does not precede reinit.

## Test Signals

Test signals are `mlscolor-test`, example `secolor.conf` cases, daemon raw-color requests, and malformed color-line tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mcscolor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mcscolor.h -->
# sources/security-integrity/selinux/mcstrans/src/mcscolor.h

## Purpose

Public internal header for mcstrans color lookup operations. The source was read completely for this report (8 lines).

## Important APIs, Types, and Functions

Declares `finish_context_colors()`, `init_colors()`, and `raw_color()`.

## Control Flow

No control flow; daemon initializes colors, serves raw color lookups, and finishes on shutdown/reload.

## State and Persistence Behavior

No storage is declared here; color state is static in `mcscolor.c`.

## Dependencies and Integration Points

Included by `mcstransd.c` and tied to `secolor.conf` parsing.

## Risks and Edge Cases

Risk is lifecycle mismatch between daemon reloads and color state cleanup.

## Test Signals

`mlscolor-test` and daemon color requests are the main signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mcscolor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mcstrans.c -->
# sources/security-integrity/selinux/mcstrans/src/mcstrans.c

## Purpose

Core mcstrans translation engine. It parses `setrans.conf` and included `.d` files, builds domains, base classifications, modifier groups, constraints, regexes, and bounded raw/trans caches, then translates SELinux MLS/MCS ranges in both directions. The source was read completely for this report (2209 lines).

## Important APIs, Types, and Functions

Exports `init_translations()`, `finish_context_translations()`, `trans_context()`, and `untrans_context()`. Important internal types include `domain_t`, `base_classification_t`, `word_group_t`, `word_t`, `context_map_t`, and sensitivity/category constraint nodes. Key helpers parse raw MLS levels, category bitmaps, config lines, includes, constraints, cache entries, PCRE2 regexes, and computed raw/trans strings.

## Control Flow

Configuration flow: `init_translations()` requires MLS enabled, reads `selinux_translations_path()`, and `process_trans()` handles `Domain`, `Include`, `Base`, `ModifierGroup`, `Whitespace`, `Join`, `Prefix`, `Suffix`, `Default`, constraints, direct cache mappings, and group words. Translation flow extracts a context range, checks caches, computes full or split range translations, updates caches, and rewrites the context range using libselinux context APIs.

## State and Persistence Behavior

Persistent-on-daemon state is in static globals: linked-list domains, constraints, parser cursor fields, `maxbit`, per-domain hash tables, compiled PCRE2 expressions, and cache entry counts capped by `CACHE_MAX_ENTRIES`. `finish_context_translations()` tears down domains, constraints, bitmaps, regexes, and parser state.

## Dependencies and Integration Points

Depends on libselinux context/path APIs, libsepol MLS ebitmap helpers, PCRE2, glob includes, syslog, and local `mls_level` helpers. It is called by `mcstransd` and by command-line utilities through `mcstrans.h`.

## Risks and Edge Cases

High-risk areas include config parser permissiveness, glob include recursion, category bounds (`MAX_CATS`, `maxbit`), PCRE2 pattern construction from config text, cache consistency between raw/trans tables, split range mutation/restoration, and memory cleanup on allocation failures. Translation semantics are sensitive to group ordering and Hamming-distance word selection.

## Test Signals

Signals include `mlstrans-test`, `try-all`, example configuration round-trips, daemon SIGHUP reload checks, cache hit/miss smoke tests, malformed config tests, and ASan/Valgrind runs over init/translate/finish cycles.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mcstrans.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mcstrans.h -->
# sources/security-integrity/selinux/mcstrans/src/mcstrans.h

## Purpose

Public internal header for mcstrans translation operations used by the daemon and helper utilities. The source was read completely for this report (8 lines).

## Important APIs, Types, and Functions

Declares `init_translations()`, `finish_context_translations()`, `trans_context()`, and `untrans_context()`, and includes `selinux/selinux.h` for SELinux types/config context.

## Control Flow

No control flow; callers use init before translation, call one of the conversion functions, and call finish during shutdown/reload.

## State and Persistence Behavior

No state is declared here; state lives in `mcstrans.c`.

## Dependencies and Integration Points

Connects `mcstrans.c` to `mcstransd`, `transcon`, and `untranscon`.

## Risks and Edge Cases

Risk is lifecycle misuse by callers, especially translation calls before successful initialization or after finish.

## Test Signals

Compile coverage and utility/daemon smoke tests validate the contract.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mcstrans.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mcstrans.service -->
# sources/security-integrity/selinux/mcstrans/src/mcstrans.service

## Purpose

Systemd unit for running the mcstrans daemon. The source was read completely for this report (15 lines).

## Important APIs, Types, and Functions

Declares service metadata, starts `mcstransd`, supports reload through SIGHUP or service reload command, and participates in normal multi-user/system SELinux service ordering.

## Control Flow

Systemd controls lifecycle: start executes the daemon, reload asks it to reread translation/color state, stop terminates it and allows socket cleanup.

## State and Persistence Behavior

Persistent state is systemd unit installation plus runtime daemon/socket state outside the unit file.

## Dependencies and Integration Points

Integrates `mcstransd` with distributions that use systemd units from the mcstrans build.

## Risks and Edge Cases

Risks are stale executable paths, reload semantics drifting from daemon signal handling, and service ordering that starts before SELinux paths/config are ready.

## Test Signals

Signals are `systemctl start/reload/stop mcstrans`, daemon socket existence, and journal messages.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mcstrans.service -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mcstransd.c -->
# sources/security-integrity/selinux/mcstrans/src/mcstransd.c

## Purpose

Daemon process for mcstrans. It initializes translation and color state, listens on `/var/run/setrans/.setrans-unix`, accepts libselinux client requests, and serves raw-to-translated, translated-to-raw, and raw-to-color operations. The source was read completely for this report (598 lines).

## Important APIs, Types, and Functions

Important functions are `initialize()`, `process_connections()`, `process_events()`, `service_request()`, `process_request()`, `send_response()`, `cleanup_exit()`, `sighup_handler()`, and `dropprivs()`. Protocol constants identify init, raw-to-trans, trans-to-raw, and color requests; request/response payloads are length-prefixed strings over a Unix stream socket.

## Control Flow

Startup checks root outside DEBUG, opens syslog, loads translations/colors, installs signal handlers, binds/listens the Unix socket, chmods it world-accessible, raises fd limits, drops capabilities, optionally daemonizes, then polls listening and client fds. SIGHUP marks a reload flag that is serviced inside the poll loop.

## State and Persistence Behavior

State includes global `sockfd`, `restart_daemon`, dynamic pollfd arrays, loaded translation/color globals in other modules, and the filesystem socket path. Cleanup frees loaded state and unlinks the socket.

## Dependencies and Integration Points

Depends on libselinux, POSIX sockets/poll/signals/resource limits, libcap, syslog, and local `mcstrans.h`/`mcscolor.h`. It is installed and managed by the systemd service file.

## Risks and Edge Cases

Risks include unauthenticated local socket accessibility, request length validation, partial read/write handling, client fd exhaustion, reload atomicity while serving requests, and privilege/capability assumptions. The source also has dead duplicate `return -1` text in an allocation branch, which is harmless but noisy.

## Test Signals

Signals include foreground daemon smoke tests, libselinux client request tests, SIGHUP reload tests, invalid length/function tests, fd limit tests, and Valgrind/callgrind helper scripts.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mcstransd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mls_level.c -->
# sources/security-integrity/selinux/mcstrans/src/mls_level.c

## Purpose

Utility code for converting libsepol `mls_level_t` values to and from textual MLS/MCS level strings such as `s0:c1,c2.c4`. The source was read completely for this report (175 lines).

## Important APIs, Types, and Functions

Exports `mls_compute_string_len()`, `mls_level_from_string()`, and `mls_level_to_string()`. It uses ebitmap iteration and libsepol MLS helpers to parse sensitivities and category ranges and to emit compact category ranges.

## Control Flow

Parsing turns text into a heap `mls_level_t`; formatting computes buffer length, emits sensitivity and category runs, and returns a heap string.

## State and Persistence Behavior

The caller owns returned `mls_level_t` and strings. No static state is owned here.

## Dependencies and Integration Points

Depends on `sepol/policydb/mls_types.h` and libsepol ebitmap/MLS helpers. It is used by translation and color modules.

## Risks and Edge Cases

Risks are off-by-one category range formatting, allocation failure cleanup, and accepting/rejecting malformed MLS strings consistently with the main parser.

## Test Signals

Round-trip tests of single categories, ranges, empty categories, and high category numbers are key signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mls_level.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mls_level.h -->
# sources/security-integrity/selinux/mcstrans/src/mls_level.h

## Purpose

Header for MLS level parse/format helpers shared by mcstrans translation and color code. The source was read completely for this report (10 lines).

## Important APIs, Types, and Functions

Declares `mls_compute_string_len()`, `mls_level_from_string()`, and `mls_level_to_string()` over `mls_level_t` from libsepol.

## Control Flow

No executable flow; consumers allocate/format/destroy MLS level data through the implementation and libsepol helpers.

## State and Persistence Behavior

No state is declared in the header.

## Dependencies and Integration Points

Depends on `sepol/policydb/mls_types.h` and pairs with `mls_level.c`.

## Risks and Edge Cases

Risk is ownership ambiguity for heap-returned strings/levels if callers do not follow implementation expectations.

## Test Signals

Compile coverage plus round-trip parse/format tests are the signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mls_level.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/utils/Makefile -->
# sources/security-integrity/selinux/mcstrans/utils/Makefile

## Purpose

Builds and installs mcstrans helper utilities. The source was read completely for this report (38 lines).

## Important APIs, Types, and Functions

Targets are derived from local C files and linked against the mcstrans source objects/libraries; install places utilities in the configured bindir.

## Control Flow

Make target flow is declarative: variables establish install paths and flags, `all` builds local or child targets, `install` creates directories and installs artifacts, `clean` removes generated outputs, and `relabel` restores SELinux labels where applicable.

## State and Persistence Behavior

State is build output on disk: binaries, object files, installed files under `DESTDIR`, and relabeled paths. The makefile itself owns no runtime state.

## Dependencies and Integration Points

Integrates with the surrounding SELinux userspace build by sharing `PREFIX`, `DESTDIR`, `LIBSELINUX_LDLIBS`, `LINGUAS`, and recursive make conventions.

## Risks and Edge Cases

Risks include environment-dependent feature detection, install path mismatches, missing localized files, and relabel commands that assume SELinux tools are present on the build host.

## Test Signals

Signals are `make`, `make install DESTDIR=...`, `make clean`, optional relabel smoke tests, and feature-matrix builds where present.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/utils/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/utils/callgrind-mcstransd -->
# sources/security-integrity/selinux/mcstrans/utils/callgrind-mcstransd

## Purpose

Helper wrapper for running `mcstransd` under callgrind during profiling or memory diagnostics. The source was read completely for this report (5 lines).

## Important APIs, Types, and Functions

The script invokes the relevant callgrind command with mcstransd-oriented arguments.

## Control Flow

Control flow is a simple shell handoff to the diagnostic tool and daemon.

## State and Persistence Behavior

No persistent state except diagnostic output generated by the tool.

## Dependencies and Integration Points

Depends on the external diagnostic program and a built `mcstransd` binary.

## Risks and Edge Cases

Risks are hard-coded paths/options becoming stale and requiring root/SELinux environment privileges.

## Test Signals

Signal is successful daemon startup under callgrind and useful generated diagnostic output.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/utils/callgrind-mcstransd -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/utils/transcon.c -->
# sources/security-integrity/selinux/mcstrans/utils/transcon.c

## Purpose

Command-line mcstrans helper that converts a SELinux context in the raw context to translated context direction. The source was read completely for this report (30 lines).

## Important APIs, Types, and Functions

`main()` initializes translations, calls `trans_context()` for the supplied context argument, prints the returned context, frees it, and finishes translation state.

## Control Flow

The utility is linear: validate CLI, initialize translation config, convert one context, print result, cleanup.

## State and Persistence Behavior

Runtime state is the translation engine globals initialized in `mcstrans.c` plus the returned heap context string.

## Dependencies and Integration Points

Depends on `mcstrans.h`, mcstrans source objects, libselinux/libsepol, and installed translation config.

## Risks and Edge Cases

Risks are poor behavior when MLS is disabled, config parse failures, and missing cleanup on early errors.

## Test Signals

Signals are example config round-trips and failure tests for malformed contexts/configuration.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/utils/transcon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/utils/untranscon.c -->
# sources/security-integrity/selinux/mcstrans/utils/untranscon.c

## Purpose

Command-line mcstrans helper that converts a SELinux context in the translated context to raw context direction. The source was read completely for this report (28 lines).

## Important APIs, Types, and Functions

`main()` initializes translations, calls `untrans_context()` for the supplied context argument, prints the returned context, frees it, and finishes translation state.

## Control Flow

The utility is linear: validate CLI, initialize translation config, convert one context, print result, cleanup.

## State and Persistence Behavior

Runtime state is the translation engine globals initialized in `mcstrans.c` plus the returned heap context string.

## Dependencies and Integration Points

Depends on `mcstrans.h`, mcstrans source objects, libselinux/libsepol, and installed translation config.

## Risks and Edge Cases

Risks are poor behavior when MLS is disabled, config parse failures, and missing cleanup on early errors.

## Test Signals

Signals are example config round-trips and failure tests for malformed contexts/configuration.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/utils/untranscon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/utils/valgrind-mcstransd -->
# sources/security-integrity/selinux/mcstrans/utils/valgrind-mcstransd

## Purpose

Helper wrapper for running `mcstransd` under valgrind during profiling or memory diagnostics. The source was read completely for this report (5 lines).

## Important APIs, Types, and Functions

The script invokes the relevant valgrind command with mcstransd-oriented arguments.

## Control Flow

Control flow is a simple shell handoff to the diagnostic tool and daemon.

## State and Persistence Behavior

No persistent state except diagnostic output generated by the tool.

## Dependencies and Integration Points

Depends on the external diagnostic program and a built `mcstransd` binary.

## Risks and Edge Cases

Risks are hard-coded paths/options becoming stale and requiring root/SELinux environment privileges.

## Test Signals

Signal is successful daemon startup under valgrind and useful generated diagnostic output.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/utils/valgrind-mcstransd -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/.tx/config -->
# sources/security-integrity/selinux/policycoreutils/.tx/config

## Purpose

Transifex client configuration for policycoreutils translation resources. The source was read completely for this report (8 lines).

## Important APIs, Types, and Functions

Defines the Transifex project/resource mapping, source language, source file path, and translated file path pattern for localization workflows.

## Control Flow

No executable flow; external `tx` tooling reads the config to pull or push translation catalogs.

## State and Persistence Behavior

Persistent state is translation metadata in the repository plus downloaded/generated locale files when the external tool runs.

## Dependencies and Integration Points

Integrates policycoreutils with the Transifex translation service and the build system `LINGUAS` locale installation paths.

## Risks and Edge Cases

Risks include stale project/resource names, path changes that break translation sync, and accidental overwrites by external tooling.

## Test Signals

Signals are successful `tx status/pull` operations and localized man/message build output.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/.tx/config -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/Makefile -->
# sources/security-integrity/selinux/policycoreutils/Makefile

## Purpose

Top-level policycoreutils recursive makefile. The source was read completely for this report (14 lines).

## Important APIs, Types, and Functions

Iterates configured subdirectories for build/install/relabel/clean and provides an empty test target.

## Control Flow

Make target flow is declarative: variables establish install paths and flags, `all` builds local or child targets, `install` creates directories and installs artifacts, `clean` removes generated outputs, and `relabel` restores SELinux labels where applicable.

## State and Persistence Behavior

State is build output on disk: binaries, object files, installed files under `DESTDIR`, and relabeled paths. The makefile itself owns no runtime state.

## Dependencies and Integration Points

Integrates with the surrounding SELinux userspace build by sharing `PREFIX`, `DESTDIR`, `LIBSELINUX_LDLIBS`, `LINGUAS`, and recursive make conventions.

## Risks and Edge Cases

Risks include environment-dependent feature detection, install path mismatches, missing localized files, and relabel commands that assume SELinux tools are present on the build host.

## Test Signals

Signals are `make`, `make install DESTDIR=...`, `make clean`, optional relabel smoke tests, and feature-matrix builds where present.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/hll/Makefile -->
# sources/security-integrity/selinux/policycoreutils/hll/Makefile

## Purpose

Recursive makefile for high-level-language converters. The source was read completely for this report (8 lines).

## Important APIs, Types, and Functions

Delegates all/install/relabel/clean to `pp`; test is empty.

## Control Flow

Make target flow is declarative: variables establish install paths and flags, `all` builds local or child targets, `install` creates directories and installs artifacts, `clean` removes generated outputs, and `relabel` restores SELinux labels where applicable.

## State and Persistence Behavior

State is build output on disk: binaries, object files, installed files under `DESTDIR`, and relabeled paths. The makefile itself owns no runtime state.

## Dependencies and Integration Points

Integrates with the surrounding SELinux userspace build by sharing `PREFIX`, `DESTDIR`, `LIBSELINUX_LDLIBS`, `LINGUAS`, and recursive make conventions.

## Risks and Edge Cases

Risks include environment-dependent feature detection, install path mismatches, missing localized files, and relabel commands that assume SELinux tools are present on the build host.

## Test Signals

Signals are `make`, `make install DESTDIR=...`, `make clean`, optional relabel smoke tests, and feature-matrix builds where present.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/hll/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/hll/pp/Makefile -->
# sources/security-integrity/selinux/policycoreutils/hll/pp/Makefile

## Purpose

Builds the `pp` high-level-language converter. The source was read completely for this report (27 lines).

## Important APIs, Types, and Functions

Compiles all local C files with warning flags, links `-lsepol`, installs to `$(LIBEXECDIR)/selinux/hll`, and cleans binary/object files.

## Control Flow

Make target flow is declarative: variables establish install paths and flags, `all` builds local or child targets, `install` creates directories and installs artifacts, `clean` removes generated outputs, and `relabel` restores SELinux labels where applicable.

## State and Persistence Behavior

State is build output on disk: binaries, object files, installed files under `DESTDIR`, and relabeled paths. The makefile itself owns no runtime state.

## Dependencies and Integration Points

Integrates with the surrounding SELinux userspace build by sharing `PREFIX`, `DESTDIR`, `LIBSELINUX_LDLIBS`, `LINGUAS`, and recursive make conventions.

## Risks and Edge Cases

Risks include environment-dependent feature detection, install path mismatches, missing localized files, and relabel commands that assume SELinux tools are present on the build host.

## Test Signals

Signals are `make`, `make install DESTDIR=...`, `make clean`, optional relabel smoke tests, and feature-matrix builds where present.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/hll/pp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/hll/pp/pp.c -->
# sources/security-integrity/selinux/policycoreutils/hll/pp/pp.c

## Purpose

Command-line converter from SELinux binary policy package `.pp` input to CIL output for policycoreutils high-level-language support. The source was read completely for this report (168 lines).

## Important APIs, Types, and Functions

Defines `log_err()`, `usage()`, and `main()`. `main()` parses `-h`, supports stdin/stdout via missing or `-` paths, reads a module package with `sepol_ppfile_to_module_package()`, optionally warns when the output basename does not match the module name, and writes CIL with `sepol_module_package_to_cil()`.

## Control Flow

Control flow is CLI parse, open input/output streams, decode `.pp`, close input, inspect module/output names for warning, convert package to CIL, and clean up streams/package on exit.

## State and Persistence Behavior

State is transient: `struct sepol_module_package *`, FILE handles, duplicated output path for basename manipulation, and static `progname`.

## Dependencies and Integration Points

Depends on libsepol module/package and module-to-CIL APIs, libc getopt/basename/signal handling, and the hll/pp Makefile that links `-lsepol`.

## Risks and Edge Cases

Risks include stream ownership on stdin/stdout, SIGPIPE behavior when consumers close output, basename mutation of duplicated paths, and user confusion from module-name/output-name mismatch.

## Test Signals

Signals include converting known `.pp` packages, stdin/stdout mode, invalid package failures, broken pipe handling, and warning coverage for mismatched names.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/hll/pp/pp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/load_policy/Makefile -->
# sources/security-integrity/selinux/policycoreutils/load_policy/Makefile

## Purpose

Builds and installs `load_policy`. The source was read completely for this report (32 lines).

## Important APIs, Types, and Functions

Adds libselinux include/library paths, NLS defines, links libselinux and libsepol, installs binary and man8 pages, supports localized manpages and relabel.

## Control Flow

Make target flow is declarative: variables establish install paths and flags, `all` builds local or child targets, `install` creates directories and installs artifacts, `clean` removes generated outputs, and `relabel` restores SELinux labels where applicable.

## State and Persistence Behavior

State is build output on disk: binaries, object files, installed files under `DESTDIR`, and relabeled paths. The makefile itself owns no runtime state.

## Dependencies and Integration Points

Integrates with the surrounding SELinux userspace build by sharing `PREFIX`, `DESTDIR`, `LIBSELINUX_LDLIBS`, `LINGUAS`, and recursive make conventions.

## Risks and Edge Cases

Risks include environment-dependent feature detection, install path mismatches, missing localized files, and relabel commands that assume SELinux tools are present on the build host.

## Test Signals

Signals are `make`, `make install DESTDIR=...`, `make clean`, optional relabel smoke tests, and feature-matrix builds where present.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/load_policy/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/load_policy/load_policy.c -->
# sources/security-integrity/selinux/policycoreutils/load_policy/load_policy.c

## Purpose

Implements the `load_policy` utility that loads the installed SELinux policy, with compatibility warnings for obsolete positional policy/boolean arguments. The source was read completely for this report (89 lines).

## Important APIs, Types, and Functions

`usage()` prints syntax. `main()` handles `-b`, `-q`, and `-i`; quiet mode disables sepol debug; init mode calls `selinux_init_load_policy(&enforce)`, otherwise `selinux_mkload_policy(0)`.

## Control Flow

After optional NLS setup, the utility parses flags, warns about deprecated arguments unless quiet, chooses init-load or normal load, and exits with distinct codes for enforcing init-load failure or general load failure.

## State and Persistence Behavior

No persistent state beyond loading kernel SELinux policy through libselinux. Local state tracks quiet/init/enforce and getopt positions.

## Dependencies and Integration Points

Depends on libselinux policy loading, libsepol debug control, gettext when enabled, and the load_policy Makefile build flags.

## Risks and Edge Cases

Risks are behavior differences during early boot/init mode, maintaining legacy CLI compatibility, and correct exit status for init systems.

## Test Signals

Signals include quiet/deprecated argument behavior, init-load enforcing failure path, normal policy load, and NLS-enabled builds.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/load_policy/load_policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/man/Makefile -->
# sources/security-integrity/selinux/policycoreutils/man/Makefile

## Purpose

Installs shared policycoreutils man5 pages. The source was read completely for this report (21 lines).

## Important APIs, Types, and Functions

Creates target man directories, installs English and localized man5 files, with no-op all/clean/relabel.

## Control Flow

Make target flow is declarative: variables establish install paths and flags, `all` builds local or child targets, `install` creates directories and installs artifacts, `clean` removes generated outputs, and `relabel` restores SELinux labels where applicable.

## State and Persistence Behavior

State is build output on disk: binaries, object files, installed files under `DESTDIR`, and relabeled paths. The makefile itself owns no runtime state.

## Dependencies and Integration Points

Integrates with the surrounding SELinux userspace build by sharing `PREFIX`, `DESTDIR`, `LIBSELINUX_LDLIBS`, `LINGUAS`, and recursive make conventions.

## Risks and Edge Cases

Risks include environment-dependent feature detection, install path mismatches, missing localized files, and relabel commands that assume SELinux tools are present on the build host.

## Test Signals

Signals are `make`, `make install DESTDIR=...`, `make clean`, optional relabel smoke tests, and feature-matrix builds where present.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/man/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/newrole/Makefile -->
# sources/security-integrity/selinux/policycoreutils/newrole/Makefile

## Purpose

Builds `newrole` with optional PAM, audit, namespace, LSPP, capability, and setuid/capability modes. The source was read completely for this report (104 lines).

## Important APIs, Types, and Functions

Detects headers, selects PAM or crypt authentication dependencies, toggles audit/capability defines and mode, installs binary/PAM/man files, and includes a `test-build-options` matrix.

## Control Flow

Make target flow is declarative: variables establish install paths and flags, `all` builds local or child targets, `install` creates directories and installs artifacts, `clean` removes generated outputs, and `relabel` restores SELinux labels where applicable.

## State and Persistence Behavior

State is build output on disk: binaries, object files, installed files under `DESTDIR`, and relabeled paths. The makefile itself owns no runtime state.

## Dependencies and Integration Points

Integrates with the surrounding SELinux userspace build by sharing `PREFIX`, `DESTDIR`, `LIBSELINUX_LDLIBS`, `LINGUAS`, and recursive make conventions.

## Risks and Edge Cases

Risks include environment-dependent feature detection, install path mismatches, missing localized files, and relabel commands that assume SELinux tools are present on the build host.

## Test Signals

Signals are `make`, `make install DESTDIR=...`, `make clean`, optional relabel smoke tests, and feature-matrix builds where present.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/newrole/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/newrole/hashtab.c -->
# sources/security-integrity/selinux/policycoreutils/newrole/hashtab.c

## Purpose

Standalone generic hash table implementation used by policycoreutils newrole PAM builds. The source was read completely for this report (205 lines).

## Important APIs, Types, and Functions

Implements `hashtab_create`, `hashtab_insert`, `hashtab_remove`, `hashtab_search`, `hashtab_destroy`, `hashtab_map`, and `hashtab_hash_eval`. The table uses creator-provided hash and comparison callbacks and ordered singly linked chains per bucket.

## Control Flow

Creation allocates the table and bucket array. Insert locates sorted position and rejects duplicate keys. Remove unlinks matching nodes and calls a caller-supplied destructor. Search walks the ordered chain. Map visits entries until callback failure. Destroy frees nodes and buckets but not key/datum payloads unless removed with a destructor earlier.

## State and Persistence Behavior

State is heap-owned `hashtab_val_t` with bucket chains and element count. Payload ownership remains with callers except for node storage.

## Dependencies and Integration Points

Depends only on libc allocation/string and `hashtab.h`; integrated into newrole when PAM support is present.

## Risks and Edge Cases

Risks include caller ownership mistakes for key/datum lifetimes, hash callbacks returning out-of-range bucket indexes, sorted-chain assumptions tied to `keycmp`, and no internal locking.

## Test Signals

Signals include insert/search/remove duplicate/missing cases, destructor invocation, map early return, destroy under empty/non-empty tables, and hash distribution diagnostics.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/newrole/hashtab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/newrole/hashtab.h -->
# sources/security-integrity/selinux/policycoreutils/newrole/hashtab.h

## Purpose

Public contract for the newrole generic hash table implementation. The source was read completely for this report (115 lines).

## Important APIs, Types, and Functions

Defines generic key/datum typedefs, node/table structs, status macros (`HASHTAB_SUCCESS`, `HASHTAB_OVERFLOW`, `HASHTAB_PRESENT`, `HASHTAB_MISSING`), and prototypes for create/insert/remove/search/destroy/map/hash-eval.

## Control Flow

No executable flow; it describes callback-driven hashing/comparison and table operations implemented in `hashtab.c`.

## State and Persistence Behavior

The table struct exposes bucket array, size, element count, and callbacks, so callers can inspect but should avoid mutating internals outside the implementation contract.

## Dependencies and Integration Points

Depends on stdint/errno/stdio and pairs directly with `hashtab.c`.

## Risks and Edge Cases

Risks are ABI drift with `hashtab.c`, exposed internals enabling misuse, and generic `char *` key typing that may not fit all callers.

## Test Signals

Compile coverage and hashtab operation tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/newrole/hashtab.h -->
