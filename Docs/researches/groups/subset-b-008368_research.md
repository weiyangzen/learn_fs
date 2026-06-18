# Research Group subset-b-008368

This grouped report covers SELinux libsepol unit-test policy fixtures and C test harnesses under `sources/security-integrity/selinux/libsepol/tests`. Each section is delimited for reconciliation into a source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-cond/refpolicy-base.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-cond/refpolicy-base.conf

## Purpose
This is the full reference-policy-like base fixture consumed by `test-cond.c`. It gives the conditional-expression tests a realistic base module containing kernel and userspace object classes, initial SIDs, a large MLS lattice, constraints, booleans, users, roles, types, and many conditional rules.

## Important APIs, Types, And Functions
The file is policy language, not C, but its important symbols are object classes such as `file`, `process`, sockets, X classes, and `dbus`; SIDs such as `kernel`, `security`, and `devnull`; categories `c0` through `c255`; booleans such as `allow_ypbind`, `secure_mode`, and `allow_execstack`; and policy constructs such as `mlsconstrain`, `if (...) { allow ... }`, `gen_user`, `gen_context`, `fs_use_xattr`, and `genfscon`.

## Control Flow
`cond_test_init()` loads this base with MLS enabled, links it as a base module, expands it, then walks `base_expanded.cond_list`. The control-flow signal in this fixture is its conditional policy tree: each `if` expression becomes a `cond_node_t`, and the test compares each node to every other node with `cond_expr_equal()`.

## State And Persistence Behavior
The fixture is parsed into a `policydb_t`, linked in place, then expanded into a second `policydb_t`. No runtime state is persisted by the policy file itself, but its symbols populate global symbol tables, scope tables, conditional nodes, MLS tables, context tables, and access-vector rules.

## Dependencies And Integration Points
It depends on the m4-style policy parser support used by `test_load_policy()`, including `ifdef(enable_mls, ...)`, `gen_user`, and `gen_context`. Its integration points are `link_modules()`, `expand_module()`, and the conditional-expression equality implementation.

## Risks And Edge Cases
Because the fixture is large, removing apparently unused classes, categories, or booleans can change condition node ordering or expression identity. The test only asserts equality against self and inequality against distinct nodes; it does not assert semantic equivalence for differently shaped expressions that evaluate the same way.

## Test Signals
Successful load, link, expand, and a populated `cond_list` are the main signals. A regression in conditional parsing, expression allocation, or expansion should surface as `cond_expr_equal()` returning true for distinct nodes or false for the same node.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-cond/refpolicy-base.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/base-metreq.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/base-metreq.conf

## Purpose
This base policy fixture is the positive dependency baseline for `test-deps.c`. It declares the normal class, MLS, role, user, type, boolean, and context scaffolding plus the exact symbols that module require tests expect to be present.

## Important APIs, Types, And Functions
Key dependency symbols are `type_req_t`, `attr_req`, `bool_req`, and `role_req_r`. It also includes object classes including `sem` and `msg` with the permissions tested by module fixtures, ordinary types such as `system_t`, `sysadm_t`, `file_t`, and `fs_t`, attributes such as `domain` and `files`, and booleans such as `secure_mode`.

## Control Flow
`deps_test_init()` loads this file into each `bases_met[]` slot. Global-require tests link one module into a copy and expect `link_modules()` to return success. Optional-require tests use it to enable optional module declarations when the required symbol exists.

## State And Persistence Behavior
The fixture builds a reusable base `policydb_t` per dependency case. Linking mutates each base by merging module declarations and enabling optional blocks whose requirements are satisfied. The file also seeds SID, fs_use, genfscon, and user context state needed for a complete policydb.

## Dependencies And Integration Points
It integrates with every `modreq-*-global.conf` and `modreq-*-opt.conf` fixture. `test_find_decl_by_sym()` later locates module marker types such as `mod_global_t` or `mod_opt_t` in the linked base to verify declaration enablement.

## Risks And Edge Cases
If this fixture accidentally diverges from `base-notmetreq.conf` in unrelated class or MLS scaffolding, dependency failures may be misattributed. The positive symbols must remain minimal and intentional, especially `sem`, `msg`, and the required role/type/attribute/boolean names.

## Test Signals
Expected signals are zero return from `link_modules()` for positive cases and enabled declarations for marker symbols. A missing required symbol should flip a positive case into the same `-3` failure path used by the negative base.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/base-metreq.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/base-notmetreq.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/base-notmetreq.conf

## Purpose
This is the negative counterpart to `base-metreq.conf`. It provides a valid base policy that intentionally omits the module-required symbols for dependency failure and disabled-optional tests.

## Important APIs, Types, And Functions
The file retains the broad class, common permission, MLS, type, role, user, boolean, SID, `fs_use_xattr`, and `genfscon` scaffolding needed to parse and link modules. It intentionally lacks `type_req_t`, `attr_req`, `bool_req`, and `role_req_r`; it also omits or changes dependency-relevant object class availability compared with the positive base.

## Control Flow
`deps_test_init()` loads this file into each `bases_notmet[]` slot. Global-require module tests link against it and expect `link_modules()` to fail with `-3`. Optional-require module tests often still expect link success, but the optional declaration containing `mod_opt_t` should be disabled or absent.

## State And Persistence Behavior
The file initializes complete base policy state, but linking should not merge declarations that rely on unmet optional requires. For global unmet requires, linking stops with a dependency error and the module is destroyed without any further assertions on enabled declarations.

## Dependencies And Integration Points
It is paired with all `modreq-*` fixtures and consumed by `do_deps_modreq_global()` and `do_deps_modreq_opt()`. The fixture is also a guard against dependency resolution incorrectly consulting optional base declarations that should not satisfy a module global requirement.

## Risks And Edge Cases
The negative signal depends on absence, so adding a convenient test symbol can silently invalidate an entire dependency lane. Optional permission tests are stricter than most optional tests because missing permissions can still produce `-3` instead of a disabled declaration.

## Test Signals
Global require tests should return `-3`. Optional tests should either link with disabled marker declarations or, for the permission optional case, return the expected failure. Any unexpected `0` for a global missing requirement is a dependency-check regression.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/base-notmetreq.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-attr-global.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-attr-global.conf

## Purpose
This module fixture tests a global-scope `require` for an attribute. It should link only when the base provides `attr_req`.

## Important APIs, Types, And Functions
The module declares `module modreq_attr_global 1.0`, requires `attribute attr_req`, creates marker type `mod_global_t`, and declares `new_t` as a member of `attr_req`.

## Control Flow
`do_deps_modreq_global()` loads the module, links it into either the positive or negative base, and then searches the linked base for `mod_global_t`. If requirements are met, the declaration containing this marker must be enabled.

## State And Persistence Behavior
When linked successfully, the base policydb gains a module declaration and attribute membership for `new_t`. When the requirement is absent, linking fails before the marker declaration is asserted.

## Dependencies And Integration Points
The module depends directly on `base-metreq.conf` declaring `attr_req`. It integrates with libsepol scope checking for global module requires and type-to-attribute mapping.

## Risks And Edge Cases
The fixture only verifies a single required attribute and one type membership. It does not test inherited attributes, aliases, or multiple required attributes.

## Test Signals
Success with `base-metreq.conf`, `-3` with `base-notmetreq.conf`, and `decl->enabled == 1` for `mod_global_t` are the expected signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-attr-global.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-attr-opt.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-attr-opt.conf

## Purpose
This module tests attribute requirements inside an optional block. The outer module should link even when `attr_req` is missing, while the optional declaration should be disabled.

## Important APIs, Types, And Functions
The global `require` only asks for `class file { read write }`; the global marker is `mod_global_t`. The optional block requires `attribute attr_req`, declares marker `mod_opt_t`, and assigns `new_t` to `attr_req`.

## Control Flow
`do_deps_modreq_opt()` loads the module and expects link success for both positive and negative bases. It locates `mod_opt_t` and checks `decl->enabled`: `1` when `attr_req` exists and `0` when it does not.

## State And Persistence Behavior
The global declaration always exists. The optional declaration is conditionally merged into active policy state based on requirement satisfaction, preserving disabled declaration metadata for inspection.

## Dependencies And Integration Points
This file exercises the linker’s optional-block dependency resolver and its ability to keep global module scope independent from optional scope.

## Risks And Edge Cases
If disabled declarations are dropped instead of retained, the test lookup by `mod_opt_t` can fail differently from an enabled-state mismatch. The file has no allow rule using the attribute, so it mainly tests symbol presence and membership parsing.

## Test Signals
Expected signals are link return `0` in both cases and enabled-state matching the base’s attribute availability.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-attr-opt.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-bool-global.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-bool-global.conf

## Purpose
This module fixture tests a global required boolean used in a conditional rule.

## Important APIs, Types, And Functions
It requires `bool bool_req` and `class file { read write }`, declares marker `mod_global_t`, creates `a_t` and `b_t`, and gates an `allow a_t b_t:file { read write }` rule behind `if (bool_req)`.

## Control Flow
The dependency test links this module against both base variants. A positive link validates that required booleans can be referenced in module conditional expressions; a negative link should fail before conditional rules are active.

## State And Persistence Behavior
On success, the linked base gains a conditional node referencing a base boolean and a module allow rule. On failure, no lasting state should be assumed after the module is destroyed.

## Dependencies And Integration Points
The module integrates global dependency checking with conditional expression parsing and the conditional rule list generated from the `if` block.

## Risks And Edge Cases
The boolean is only tested as a simple positive identifier. There is no nested expression, negation, or optional boolean reference in this fixture.

## Test Signals
Expected signals are link success only with `bool_req` present and an enabled declaration for `mod_global_t` in the positive case.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-bool-global.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-bool-opt.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-bool-opt.conf

## Purpose
This optional dependency fixture tests a boolean required only inside an optional block.

## Important APIs, Types, And Functions
The global module requires only `class file { read write }` and declares `mod_global_t`. The optional block requires `bool_req`, declares `a_t`, `b_t`, and marker `mod_opt_t`, then uses `if (bool_req)` around an allow rule.

## Control Flow
The linker should always accept the module. When the base provides `bool_req`, the optional block is enabled and its conditional rule is available. When absent, the optional declaration is disabled.

## State And Persistence Behavior
The test validates conditional policy state inside an optional declaration. Disabled optional state should not activate types or conditional rules, but it must remain findable enough for `test_find_decl_by_sym()` to inspect `mod_opt_t`.

## Dependencies And Integration Points
It integrates boolean dependency resolution, optional declaration enablement, and conditional rule parsing in the module linker.

## Risks And Edge Cases
Because the allow rule is only parsed when the optional block exists, errors can manifest as either dependency handling failures or conditional parse/link failures.

## Test Signals
The return value should be `0` for both bases, with `decl->enabled` toggling according to `bool_req` availability.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-bool-opt.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-obj-global.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-obj-global.conf

## Purpose
This module validates global object-class dependency checking.

## Important APIs, Types, And Functions
It requires `class sem { create destroy }`, declares marker `mod_global_t`, creates `mod_foo_t` and `mod_bar_t`, and grants `sem` permissions between them.

## Control Flow
`do_deps_modreq_global()` links this module into the positive and negative bases. The positive path must merge the module and enable the marker declaration; the negative path must fail due to missing class or permission requirements.

## State And Persistence Behavior
Successful linking adds module-local types and an access-vector rule for the `sem` object class. Failed linking should not partially enable module declarations.

## Dependencies And Integration Points
The fixture targets the class/permission half of require resolution, not type or role resolution. It is sensitive to base object-class definitions.

## Risks And Edge Cases
Only one class and two permissions are tested. A base that declares `sem` but not both permissions should still be treated as unmet, so preserving exact class permission sets matters.

## Test Signals
Expected signals are success with the met base and `-3` with the unmet base, plus an enabled `mod_global_t` declaration on success.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-obj-global.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-obj-opt.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-obj-opt.conf

## Purpose
This fixture tests optional object-class requirements and optional allow-rule activation.

## Important APIs, Types, And Functions
The global scope requires `class file { read }`, declares `mod_global_t`, `mod_foo_t`, and `mod_bar_t`. The optional block requires `class sem { create destroy }`, declares marker `mod_opt_t`, and grants `sem` permissions.

## Control Flow
The module links against both bases. If `sem` and its permissions exist, the optional block is enabled; otherwise the optional block is disabled without making the whole link fail.

## State And Persistence Behavior
The policydb should retain global module types regardless of optional state. The optional declaration’s allow rule is active only when enabled.

## Dependencies And Integration Points
It integrates class/permission require checking with optional declaration state and access-vector rule linking.

## Risks And Edge Cases
The module name is `modreq_obj_global` despite being the optional-object fixture, which can confuse report readers or test failure triage. The dependency signal still comes from `mod_opt_t`.

## Test Signals
Both links should return `0`, and `mod_opt_t` should be enabled only against the positive base.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-obj-opt.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-perm-global.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-perm-global.conf

## Purpose
This module tests global permission requirements for an existing object class.

## Important APIs, Types, And Functions
It requires `class msg { send receive }`, declares marker `mod_global_t`, creates `a_t` and `b_t`, and grants `msg` `send` and `receive`.

## Control Flow
The dependency suite links this fixture against base policies where the `msg` class and permissions are either present or not sufficient. Positive linking enables the marker declaration; negative linking should return `-3`.

## State And Persistence Behavior
On success, the base gains module types and an access-vector rule tied to the `msg` class. The fixture does not persist external state beyond the mutated in-memory policydb.

## Dependencies And Integration Points
It specifically exercises permission-level require checking rather than only object-class presence.

## Risks And Edge Cases
A test base with `msg` but a partial permission set could expose more subtle failures than the current positive/negative split. This fixture assumes exact permission availability.

## Test Signals
Expected signals are positive link success, negative link failure, and enabled `mod_global_t` in the positive base.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-perm-global.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-perm-opt.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-perm-opt.conf

## Purpose
This module tests permissions required inside an optional declaration.

## Important APIs, Types, And Functions
The module globally requires `class file { read write }` and declares `mod_global_t`. The optional block requires `class msg { send receive }`, declares marker `mod_opt_t`, creates `a_mod_t` and `b_mod_t`, and grants `msg` permissions.

## Control Flow
`deps_modreq_opt()` expects the positive base to link and enable the optional block. The negative permission case expects `link_modules()` to return `-3`, making it stricter than most optional fixtures.

## State And Persistence Behavior
When positive, the optional declaration contributes active types and an access-vector rule. When negative, the module is rejected by the linker rather than merely leaving `mod_opt_t` disabled.

## Dependencies And Integration Points
This fixture probes a nuanced linker path where optional permission requirements interact with class resolution and access-vector rule validation.

## Risks And Edge Cases
The asymmetric expectation, success for most missing optional symbols but failure for missing optional permissions, is a regression-prone contract. Changes to optional handling should revisit this fixture explicitly.

## Test Signals
Positive link return `0` with enabled `mod_opt_t`; negative link return `-3`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-perm-opt.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-role-global.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-role-global.conf

## Purpose
This module validates global role requirements and role allow linking.

## Important APIs, Types, And Functions
It requires `role role_req_r, user_r`, declares marker `mod_global_t`, creates `a_t`, and emits `allow role_req_r user_r`. A role-type assignment for `role_req_r` is intentionally commented out.

## Control Flow
The dependency suite links this fixture into positive and negative bases. The required roles must be found before the role allow rule can be accepted.

## State And Persistence Behavior
Successful linking adds module declaration state and a role allow relationship to the base policydb. Failed linking should produce no enabled marker declaration.

## Dependencies And Integration Points
It integrates role symbol scope, role allow rule parsing, and module global require resolution.

## Risks And Edge Cases
The fixture does not test role type-set mutation for the required role because that line is commented. It therefore isolates role require plus role allow, not role membership.

## Test Signals
Expected signals are success only when both roles exist and enabled `mod_global_t` in the positive case.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-role-global.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-role-opt.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-role-opt.conf

## Purpose
This optional dependency module tests role requirements inside an optional declaration.

## Important APIs, Types, And Functions
Global scope requires only `class file { read write }` and declares `mod_global_t`. The optional block requires `role_req_r` and `user_r`, declares `mod_opt_t`, and creates `allow role_req_r user_r`.

## Control Flow
The linker should accept the module against both bases. The optional declaration should be enabled only when the base provides the required roles.

## State And Persistence Behavior
The policydb retains global module state in both paths. Role allow state from the optional block is active only when the declaration is enabled.

## Dependencies And Integration Points
This file exercises optional role scope resolution and role allow rule merging.

## Risks And Edge Cases
Only role existence is tested; role attributes or role type-set expansion are not covered here.

## Test Signals
Both links return `0`; `mod_opt_t` declaration enablement tracks whether `role_req_r` is present.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-role-opt.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-type-global.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-type-global.conf

## Purpose
This module tests a global required type used as the target of an allow rule.

## Important APIs, Types, And Functions
It requires `type type_req_t` and `class file { read write }`, declares marker `mod_global_t`, creates `test_t`, and grants `test_t type_req_t:file { read write }`.

## Control Flow
The positive dependency base satisfies the type and class requirements, allowing link success. The negative base omits `type_req_t`, so global linking should fail with `-3`.

## State And Persistence Behavior
Successful linking adds `test_t`, marker declaration state, and the file allow rule to the base policydb.

## Dependencies And Integration Points
It is the simplest type dependency case for `do_deps_modreq_global()` and validates global symbol scope checks for `SYM_TYPES`.

## Risks And Edge Cases
The fixture does not test type aliases or attributes; the required symbol must be a concrete base type.

## Test Signals
Link success and enabled `mod_global_t` on the met base; `-3` on the unmet base.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-type-global.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-type-opt.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-type-opt.conf

## Purpose
This module tests a type required only inside an optional block.

## Important APIs, Types, And Functions
Global scope requires `type file_t` and `class file { read write }`, then declares `mod_global_t`. The optional block requires `type_req_t`, declares `mod_opt_t`, and grants `type_req_t file_t:file { read write }`.

## Control Flow
Both positive and negative bases should link because the missing type is optional. The optional block is enabled only when `type_req_t` is present.

## State And Persistence Behavior
The global declaration persists in both cases; optional allow-rule state is active only for the positive base. Disabled optional state remains inspectable through `mod_opt_t`.

## Dependencies And Integration Points
This fixture targets optional `SYM_TYPES` require handling and its interaction with allow-rule validation.

## Risks And Edge Cases
The allow rule uses a base type as source and another base type as target, so module-local type mapping is not stressed.

## Test Signals
Link return `0` for both bases, with `decl->enabled == 1` only when `type_req_t` exists.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/modreq-type-opt.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/module.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/module.conf

## Purpose
This general module fixture combines ordinary module requires, a new domain type, role type assignment, unconditional allow rules, and a conditional allow rule.

## Important APIs, Types, And Functions
It requires `secure_mode`, `system_t`, `sysadm_t`, `file_t`, attribute `domain`, role `system_r`, and `class file { read write }`. It declares `new_t, domain`, assigns `system_r types new_t`, grants `system_t file_t:file`, and conditionally grants `sysadm_t file_t:file` under `secure_mode`.

## Control Flow
The module is parsed as a standalone policy module and can be linked with the dependency base. The unconditional allow should always be present after link; the conditional allow becomes a conditional node tied to a base boolean.

## State And Persistence Behavior
Linking adds a new type, attribute membership, role type-set membership, access-vector rules, and a conditional expression to the target base policydb.

## Dependencies And Integration Points
This file integrates type, attribute, role, class, permission, and boolean require resolution in one compact module.

## Risks And Edge Cases
It is broader but less isolated than the `modreq-*` fixtures, so a failure can come from several symbol families. It assumes `secure_mode` exists in the base even though its default value is false.

## Test Signals
Useful signals are successful parsing/linking, active `new_t` role membership, and creation of the conditional rule for `secure_mode`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/module.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/small-base.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-deps/small-base.conf

## Purpose
This is a compact dependency base that preserves the core SELinux class, MLS, type, role, boolean, user, SID, and filesystem context scaffolding used by dependency tests.

## Important APIs, Types, And Functions
It declares the common object classes and permissions, `s0:c0.c23` MLS data, attributes such as `domain`, `system`, `foo`, and `files`, ordinary types such as `system_t`, `sysadm_t`, `file_t`, and `fs_t`, roles `system_r`, `user_r`, and `sysadm_r`, optional `base_optional_*` types, and booleans used by modules.

## Control Flow
The file is loaded by helper routines as a base policy. Its optional block requiring `base_optional_1` and `base_optional_2` should enable because both types are declared before the block.

## State And Persistence Behavior
The parsed policydb includes symbol tables, scope information, a small MLS lattice, users, initial SID context, xattr filesystem use declarations, and a proc genfscon.

## Dependencies And Integration Points
It integrates with general module fixtures that need a valid base without the specialized positive/negative required-symbol split.

## Risks And Edge Cases
Despite the `small` name, it still encodes many baseline object classes. Removing rarely used classes can break module parsing if a fixture requires them indirectly.

## Test Signals
The main signal is that a minimal base can load, link modules, and support optional block enablement without the large reference policy.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-deps/small-base.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-expander/alias-base.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-expander/alias-base.conf

## Purpose
This expander fixture tests how type aliases declared in a base policy and optional base blocks survive module expansion.

## Important APIs, Types, And Functions
Important symbols are `enable_optional`, `alias_check_1_t`, `alias_check_2_t`, `alias_check_3_t`, aliases `alias_check_1_a` and `alias_check_2_a`, and an optional block requiring `alias_check_3_a`. It also defines normal roles, users, booleans, SID, fs_use, and genfscon scaffolding.

## Control Flow
The base declares a direct alias, an alias inside an enabled optional block, and an optional block whose requirement is satisfied by a module-provided alias from `alias-module.conf`.

## State And Persistence Behavior
After link and expansion, alias datums should map to the correct primary type and flavor. Optional alias declarations should contribute only when their requirements are satisfied.

## Dependencies And Integration Points
The fixture pairs with `alias-module.conf` and `test_alias_datum()` from `test-common.c`, which checks `TYPE_ALIAS` or primary-type layout.

## Risks And Edge Cases
Alias values and primary references are subtle in expanded policydbs. Reordering or changing optional alias requirements can alter whether aliases are retained as aliases or collapsed into primary type datums.

## Test Signals
Expansion should preserve expected alias-to-primary relationships and enable the module-dependent optional block when `alias_check_3_a` exists.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-expander/alias-base.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-expander/alias-module.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-expander/alias-module.conf

## Purpose
This small module supplies a type alias needed by the alias expansion tests.

## Important APIs, Types, And Functions
It requires `type alias_check_3_t` and declares `typealias alias_check_3_t alias alias_check_3_a`.

## Control Flow
When linked with `alias-base.conf`, this module makes `alias_check_3_a` available. That in turn satisfies the base optional block requiring the alias and permits a rule involving the alias.

## State And Persistence Behavior
The linked policydb gains a module alias datum whose primary is the base type. Expansion must retain enough alias state for alias datum assertions to distinguish alias versus primary flavor.

## Dependencies And Integration Points
It directly integrates with `test_alias_datum()` and the base optional block in `alias-base.conf`.

## Risks And Edge Cases
If alias requirements are resolved before module aliases are visible to base optionals, the dependent optional block can be incorrectly disabled.

## Test Signals
Expected signals are successful module link and an alias datum for `alias_check_3_a` pointing at `alias_check_3_t`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-expander/alias-module.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-expander/base-base-only.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-expander/base-base-only.conf

## Purpose
This is a minimal base-only expander fixture used to validate expansion without any module overlay.

## Important APIs, Types, And Functions
It declares `security` and `file` classes, `sid kernel`, common file permissions, optional MLS data under `enable_mls`, attribute `myattr`, type `mytype_t`, role `myrole_r`, boolean `mybool`, user `myuser_u`, and a kernel SID context.

## Control Flow
The file is loaded as a base policy and expanded directly. There are no module dependency or optional interactions beyond the MLS macro guard.

## State And Persistence Behavior
The fixture seeds the smallest useful policydb state: classes, one SID, MLS state when enabled, a type/role/user relationship, and an initial SID context.

## Dependencies And Integration Points
It integrates with the expander’s base-only path and parser macros `gen_user` and `gen_context`.

## Risks And Edge Cases
Because it is intentionally tiny, adding module-like constructs would weaken its value as a base-only control. With MLS disabled, `gen_user` ranges must still parse consistently.

## Test Signals
Successful load and expansion verify that base policy expansion does not require modules or the larger reference scaffolding.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-expander/base-base-only.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-expander/module.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-expander/module.conf

## Purpose
This is the main expander module fixture. It stress-tests conditional mapping, optional block enablement, and type-to-attribute expansion across base and module declarations.

## Important APIs, Types, And Functions
The module requires base booleans `allow_ypbind`, `secure_mode`, and `allow_execstack`, base types `system_t` and `sysadm_t`, `class file`, and several base attributes. It declares `module_1_bool`, optional `module_1_bool_2`, `module_t`, `attr_check_mod_1` through `attr_check_mod_11`, multiple optional module attributes, and many `typeattribute` relationships.

## Control Flow
The global conditional rule depends on a conjunction of module and base booleans. Optional blocks are deliberately split between satisfied requirements (`base_t`, existing attributes) and unsatisfied requirements (`does_not_exist_t`) to test enabled and disabled declaration expansion.

## State And Persistence Behavior
Successful link/expand should merge type-attribute memberships from global, base optional, module optional, disabled base optional, and disabled module optional contexts into the expected expanded ebitmaps. Disabled optional blocks should not contribute active membership.

## Dependencies And Integration Points
This module pairs with `test-expander/small-base.conf` and common helpers such as `test_attr_types()` to inspect attribute membership after expansion.

## Risks And Edge Cases
The file encodes a dense matrix by naming convention. Renaming an attribute or moving a declaration between global and optional scope can invalidate multiple expected mappings.

## Test Signals
Strong signals are correct enabled/disabled optional declarations, correct expanded attribute member sets, and preserved conditional expression mapping for the complex boolean expression.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-expander/module.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-expander/role-base.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-expander/role-base.conf

## Purpose
This base fixture tests role type-set expansion from a base role declaration.

## Important APIs, Types, And Functions
The focused symbols are `role_check_1`, base type `role_check_1_1_t`, and ordinary roles/users/types used for complete policy context. The file assigns `role_check_1 types role_check_1_1_t`.

## Control Flow
When linked with `role-module.conf`, the same role receives an additional module type. Expansion should combine role type memberships across base and module declarations.

## State And Persistence Behavior
The policydb initially contains a role type ebitmap with one base type. Linking and expansion should mutate that role’s type set to include module-provided additions.

## Dependencies And Integration Points
It integrates with `test_role_type_set()` and `role-module.conf`.

## Risks And Edge Cases
Role membership is represented as ebitmaps indexed through `sym_val_to_name`; symbol value changes can make failures appear as wrong type sets.

## Test Signals
Expected signals are presence of `role_check_1` and a final type set containing both base and module type members after expansion.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-expander/role-base.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-expander/role-module.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-expander/role-module.conf

## Purpose
This module adds a type to a role declared in `role-base.conf`.

## Important APIs, Types, And Functions
It requires `class file { read write }` and `role role_check_1`, declares `role_check_1_2_t`, and assigns `role role_check_1 types role_check_1_2_t`.

## Control Flow
The linker resolves the required base role, merges the module type, and expansion should combine it with the base type membership.

## State And Persistence Behavior
The module contributes one new type and one role type-set addition to the linked policydb.

## Dependencies And Integration Points
It is inspected through `test_role_type_set()` after expansion with `role-base.conf`.

## Risks And Edge Cases
If role declarations from modules are treated as separate role datums instead of merged, this fixture will expose missing or duplicate type-set state.

## Test Signals
Expected signal is `role_check_1` containing `role_check_1_2_t` in addition to the base type after expansion.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-expander/role-module.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-expander/small-base.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-expander/small-base.conf

## Purpose
This base fixture backs the main expander module matrix. It defines attributes and optional blocks arranged to test type-attribute expansion across global, enabled optional, and disabled optional scopes.

## Important APIs, Types, And Functions
Important symbols include `attr_check_base_1` through `attr_check_base_11`, optional attributes `attr_check_base_optional_*`, disabled optional attributes, `base_t`, many `attr_check_base_*_t` types, and optional blocks requiring either real attributes/module types or `does_not_exist_t`.

## Control Flow
The base declares some attributes and type memberships globally, some in optional blocks that should be enabled by the module, and some in optional blocks that should remain disabled. It also provides booleans used by module conditional expressions.

## State And Persistence Behavior
Expansion should produce accurate attribute member ebitmaps for attributes sourced from the base, module, and optional declarations. Disabled optionals should not leak memberships into active expanded state.

## Dependencies And Integration Points
It pairs with `test-expander/module.conf` and common helpers that inspect attribute membership, policydb indexes, and conditional maps.

## Risks And Edge Cases
The naming scheme is the contract. Small edits to numbers or optional requirements can break several expected mapping categories at once.

## Test Signals
Expected signals are enabled optional blocks when their requirements are satisfied by the module, disabled blocks when `does_not_exist_t` is required, and exact type sets for each test attribute.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-expander/small-base.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-expander/user-base.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-expander/user-base.conf

## Purpose
This base fixture tests user mapping and expansion, especially MLS-gated user requirements.

## Important APIs, Types, And Functions
Focused symbols are `user_check_1`, roles `user_check_1_1_r` and `user_check_1_2_r`, types `user_check_1_1_t` and `user_check_1_2_t`, and the `gen_user(user_check_1, ...)` declaration. It also contains standard class, MLS, role, type, boolean, SID, and filesystem context scaffolding.

## Control Flow
When MLS is enabled, `user-module.conf` requires `user_check_1`. The base provides that user and its roles, allowing module link and expansion to exercise user symbol visibility.

## State And Persistence Behavior
The parsed policydb contains user datum state, role sets, MLS range, and contexts. Expansion must preserve the user mapping and role associations.

## Dependencies And Integration Points
It integrates with `user-module.conf`, the parser’s `gen_user` macro handling, and user symbol indexing in `policydb_t`.

## Risks And Edge Cases
The module’s user requirement is under `enable_mls`, so MLS/non-MLS runs can cover different dependency paths. User-role range semantics are not deeply asserted by the tiny module.

## Test Signals
Expected signals are successful user symbol resolution in MLS mode and stable user-to-role mapping after expansion.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-expander/user-base.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-expander/user-module.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-expander/user-module.conf

## Purpose
This module is a minimal user-require fixture for expander tests.

## Important APIs, Types, And Functions
It requires `class file { read write }` and, under `enable_mls`, `user user_check_1`.

## Control Flow
In MLS-enabled parsing, the module depends on the user declared by `user-base.conf`. In non-MLS parsing, the user require is omitted by the macro guard.

## State And Persistence Behavior
The module does not add active rules or symbols beyond requirements; its value is in whether user scope checking succeeds during link.

## Dependencies And Integration Points
It integrates with user symbol tables, m4 MLS guards, and the expander’s module link path.

## Risks And Edge Cases
Because the module has no marker type or rule body, failures are mostly load/link failures. It is easy to underestimate because its behavior changes with MLS configuration.

## Test Signals
Expected signals are successful parsing and link when `user_check_1` is available in MLS mode.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-expander/user-module.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-hooks/cmp_policy.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-hooks/cmp_policy.conf

## Purpose
This comparison policy is the expected baseline for hook tests that add symbols or role rules programmatically.

## Important APIs, Types, And Functions
It declares a small base with `g_b_type_1`, roles `g_b_role_1`, `g_b_role_2`, `g_b_role_3`, type `g_b_type_2`, and an optional block requiring `invalid_type` that would add role allow and role transition rules if enabled.

## Control Flow
Hook tests can load or synthesize a policy, apply modifications, and compare against this known policy shape. The optional block is deliberately disabled because `invalid_type` is absent.

## State And Persistence Behavior
The policydb holds base symbols, user/context state, and disabled optional declaration state. It should not include active rules from the invalid optional.

## Dependencies And Integration Points
It integrates with test hooks that compare policydb contents after adding symbols or role allow/transition rules.

## Risks And Edge Cases
If a hook accidentally enables disabled optional declarations or copies disabled rules into active state, this comparison policy should reveal the mismatch.

## Test Signals
Matching policydb state against this fixture validates that hook-added state has the expected symbols and no unintended optional activation.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-hooks/cmp_policy.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-hooks/module_add_role_allow_trans.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-hooks/module_add_role_allow_trans.conf

## Purpose
This module fixture supplies role allow and role transition declarations for hook tests.

## Important APIs, Types, And Functions
It requires `class file { read }`, declares roles `role_a_1`, `role_a_2`, `role_t_1`, `role_t_2`, type `type_rt_1`, an `allow role_a_1 role_a_2`, and a `role_transition role_t_1 type_rt_1 role_t_2`.

## Control Flow
The module is loaded and linked or used by hooks to add role relationship state into a policydb, then compared with expected policy state.

## State And Persistence Behavior
Successful processing adds role symbols, a type symbol, a role allow rule, and a role transition rule.

## Dependencies And Integration Points
It targets libsepol hook paths for role allow and role transition insertion.

## Risks And Edge Cases
The fixture has no optional blocks and no role type-set assignments, so it isolates rule insertion but not role membership validation.

## Test Signals
Expected signals are presence of both role relationship rules and successful comparison against the hook-generated policy.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-hooks/module_add_role_allow_trans.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-hooks/module_add_symbols.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-hooks/module_add_symbols.conf

## Purpose
This module fixture supplies one symbol of each major family for hook tests that add policy symbols.

## Important APIs, Types, And Functions
It requires `class file { read write }`, declares `type_add_1`, `attribute attrib_add_1`, `role role_add_1`, `bool bool_add_1 false`, and in non-MLS mode declares `user user_add_1 roles { role_add_1 }`.

## Control Flow
The fixture is processed by hooks or linker tests to add symbols and then compare the resulting policydb against an expected policy.

## State And Persistence Behavior
Successful processing mutates symbol tables for types, attributes, roles, booleans, and sometimes users. MLS configuration controls whether user state is added.

## Dependencies And Integration Points
It integrates with policy symbol creation hooks and policydb index validation for added symbols.

## Risks And Edge Cases
The user declaration is under an inverse MLS guard, so test expectations must branch by MLS mode. It does not assign the new type to the new attribute.

## Test Signals
Expected signals are successful addition and correct indexing of the declared symbols, with user addition only in non-MLS mode.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-hooks/module_add_symbols.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-hooks/small-base.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-hooks/small-base.conf

## Purpose
This is the small base policy used by hook tests before programmatic symbol or rule additions.

## Important APIs, Types, And Functions
It declares the ordinary class and MLS scaffolding plus `g_b_type_1`, roles `g_b_role_1`, `g_b_role_2`, `g_b_role_3`, `g_b_type_2`, and a disabled optional block requiring `invalid_type` that would add role allow and transition rules.

## Control Flow
Hook tests start from this base, apply additions from hook modules or direct APIs, and compare the resulting state to `cmp_policy.conf`.

## State And Persistence Behavior
The base policydb holds active core symbols and disabled optional state. It also includes user and context state for `g_b_user_1` and filesystem context declarations.

## Dependencies And Integration Points
It is the input side of hook comparison tests and integrates with policydb mutation APIs.

## Risks And Edge Cases
The file is nearly identical to `cmp_policy.conf`; any intentional difference must align with the hook operation under test. Disabled optional leakage is a key risk.

## Test Signals
Expected signals are successful base loading and deterministic policydb comparison after hooks run.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-hooks/small-base.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-linker/module1.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-linker/module1.conf

## Purpose
This is the first large linker module fixture. It tests cross-module and base/module merging for attributes, roles, aliases, booleans, conditionals, and optional declarations.

## Important APIs, Types, And Functions
It requires base roles, classes, attributes, and type `g_b_type_3`. It declares marker `tag_g_m1`, attributes `g_m1_attr_*`, types `g_m1_type_*`, roles `g_m1_role_1`, base role additions, alias `g_m_alias_1`, boolean `g_m1_bool_1`, and optional blocks tagged `tag_o1_m1` through `tag_o4_m1`.

## Control Flow
Global declarations should always merge. Optional blocks depend on `optional_type`, base attributes, `enable_optional`, or attributes from other modules. Some optionals intentionally reference absent requirements to remain disabled.

## State And Persistence Behavior
Linking mutates the base with new module symbols, type-attribute memberships, role type-set additions, aliases, conditional rules, and enabled optional declarations. It also exposes symbols that can enable base optional blocks and `module2.conf` optionals.

## Dependencies And Integration Points
This fixture pairs with `test-linker/small-base.conf` and `module2.conf`. It is used to verify that the linker resolves dependencies across base, module, and optional declaration boundaries.

## Risks And Edge Cases
The fixture deliberately relies on declaration ordering and cross-module requirements. A change to optional activation timing can affect base optional blocks and second-module optional blocks simultaneously.

## Test Signals
Expected signals include enabled marker tags for satisfied optionals, disabled tags for unsatisfied ones, correct merged attribute memberships, role type additions, alias resolution, and conditional mapping.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-linker/module1.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-linker/module2.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-linker/module2.conf

## Purpose
This second linker module completes the cross-module merge matrix by consuming symbols declared by `module1.conf` and contributing more role, attribute, type, boolean, and optional state.

## Important APIs, Types, And Functions
It requires `g_b_attr_5`, `g_b_attr_6`, `g_m1_attr_3`, and `o3_m1_attr_2`, declares marker `tag_g_m2`, types `g_m2_type_*`, role `g_m2_role_1`, additions to base roles, booleans `g_m2_bool_1` and `g_m2_bool_2`, and optional tags `tag_o1_m2` and `tag_o2_m2`.

## Control Flow
The global block links after `module1.conf` provides its required module attribute. Optional block `o1` depends on `optional_type`; optional block `o2` depends on `g_m1_attr_4` and `o4_m1_attr_1`.

## State And Persistence Behavior
Successful linking adds cross-module attribute memberships, role type-set additions, and a conditional rule controlled by two module booleans. It also validates that module2 can add types to attributes originating in base optionals and module1 optionals.

## Dependencies And Integration Points
It integrates tightly with `module1.conf` and `small-base.conf`, stressing multi-module link ordering and optional dependency resolution.

## Risks And Edge Cases
If modules are linked in isolation or in the wrong dependency visibility phase, required module attributes can appear missing. Conditional mapping also depends on both module booleans being represented consistently.

## Test Signals
Expected signals are successful link with module1, correct activation of satisfied optionals, and final type/role/attribute sets that include contributions from both modules.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-linker/module2.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-linker/small-base.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-linker/small-base.conf

## Purpose
This base fixture drives the linker’s main multi-module tests. It defines global base symbols and optional base blocks that modules can enable.

## Important APIs, Types, And Functions
Important symbols include `enable_optional`, marker `tag_g_b`, attributes `g_b_attr_1` through `g_b_attr_6`, types `g_b_type_1` through `g_b_type_3`, roles `g_b_role_1` through `g_b_role_4`, booleans `g_b_bool_1` and `g_b_bool_2`, alias `g_b_alias_1`, and optional blocks tagged `tag_o1_b` through `tag_o7_b`.

## Control Flow
Global base rules are active immediately. Optional base blocks are enabled only after requirements are satisfied, often by module declarations from `module1.conf` or `module2.conf`; one block requiring `invalid_type` is intended to remain disabled.

## State And Persistence Behavior
The policydb contains base symbol tables, base allow rules including wildcard and complement permission sets, alias state, conditional rules, users, contexts, and optional declaration metadata. Linking modules can retroactively enable some optional declarations.

## Dependencies And Integration Points
It integrates with both linker modules and common test helpers for role type sets, attribute types, alias datums, and policydb index validation.

## Risks And Edge Cases
This fixture is sensitive to optional dependency iteration and cross-declaration visibility. Alias-driven optional `tag_o7_b` depends on module alias visibility, which is easy to mishandle.

## Test Signals
Expected signals are correct enabled tags, disabled invalid optional tags, merged type-attribute maps, role type-set additions, aliases `g_b_alias_1` and optionally `g_b_alias_2`, and valid indexes after linking.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-linker/small-base.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-neverallow/policy.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-neverallow/policy.conf

## Purpose
This policy fixture tests libsepol neverallow and neverallowxperm assertion checking across ordinary allows, attributes, complements, wildcards, self, audit/dontaudit, transitions, and extended permissions.

## Important APIs, Types, And Functions
It declares minimal classes `process` and `file` plus permissions including `ioctl`, many test types and attributes (`test1_t` through `test26_*`), `allow`, `auditallow`, `dontaudit`, `type_transition`, `neverallow`, `allowxperm`, and `neverallowxperm` rules. Comments marked `nofail` identify rules expected not to violate assertions.

## Control Flow
The policy is loaded by neverallow tests, then libsepol assertion evaluation compares each allow or extended-permission allow against neverallow constraints. The numbered blocks isolate one semantic case at a time.

## State And Persistence Behavior
The policydb records assertion rules and allowed access-vector/extended-permission rules. It also carries the minimal users, SIDs, MLS data, and fs_use declarations required for a valid binary policy.

## Dependencies And Integration Points
It integrates with assertion checking logic for type sets, attributes, complements, wildcard permissions, `self`, non-allow rules, and ioctl extended permission ranges.

## Risks And Edge Cases
Many blocks are intentionally violating. A test harness must know expected failure counts or failure locations; otherwise a successful compile can still mean assertions were not checked.

## Test Signals
Signals include detection of expected neverallow violations, non-detection for `nofail` blocks, and correct handling of xperm singleton and range intersections.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-neverallow/policy.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-neverallow/policy_cond.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-neverallow/policy_cond.conf

## Purpose
This fixture tests neverallow and neverallowxperm interactions with conditional policy rules.

## Important APIs, Types, And Functions
It declares booleans `boolean1` and `boolean2`, minimal classes and MLS state, test types `test1_t` through `test15_t`, conditional `allow` and `allowxperm` rules, and corresponding `neverallow`/`neverallowxperm` assertions. It ends with SID contexts and fs_use declarations.

## Control Flow
Each numbered test places allows behind boolean expressions and checks whether assertion logic considers possible conditional states. Some cases are marked `nofail` where the conditional expression or xperm set should not intersect the assertion.

## State And Persistence Behavior
The policydb stores conditional nodes with true/false rule lists plus assertion rules. Boolean default values seed initial state but assertion checking must reason about conditional policy, not just defaults.

## Dependencies And Integration Points
It integrates with conditional expression parsing, conditional AV rule storage, and neverallowxperm set-intersection logic.

## Risks And Edge Cases
Conditional neverallow behavior is easy to under-check if only the default boolean branch is examined. Xperm conditions add another dimension of range/singleton intersection risk.

## Test Signals
Expected signals are assertion failures for conditionally reachable conflicts and no failures for explicitly non-overlapping or `nofail` conditional cases.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-neverallow/policy_cond.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-neverallow/policy_minus_self.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-neverallow/policy_minus_self.conf

## Purpose
This fixture focuses on neverallow target sets expressed as `{ set -self }`.

## Important APIs, Types, And Functions
It declares file and custom classes, many numbered test types and attributes, ordinary `allow`, `allowxperm`, `neverallow`, and `neverallowxperm` rules. The central syntax is target sets such as `{ test3_2_t -self }` and attribute sets such as `{ test13_2_a -self }`.

## Control Flow
Numbered tests compare concrete and attribute-sourced allow pairs with neverallow target sets that remove self-pairs. Later tests extend the same pattern to ioctl xperm ranges.

## State And Persistence Behavior
The policydb stores expanded type sets and assertion rules where `self` exclusion must be resolved per source type. Correct behavior depends on evaluating `self` after source/target expansion, not as a static type.

## Dependencies And Integration Points
It integrates with type-set complement/subtraction code, attribute expansion, self semantics, and extended-permission assertion checking.

## Risks And Edge Cases
The semantics of `{ attribute -self }` can differ from `~self`; this fixture protects against collapsing both forms too early. Some duplicated or similarly named attributes make test maintenance error-prone.

## Test Signals
Expected signals are violations only when the non-self target set intersects an allow, and no failures for comments marked `nofail`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-neverallow/policy_minus_self.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-neverallow/policy_not_self.conf -->
# sources/security-integrity/selinux/libsepol/tests/policies/test-neverallow/policy_not_self.conf

## Purpose
This companion fixture tests neverallow target expressions using `~self`.

## Important APIs, Types, And Functions
It mirrors many cases from `policy_minus_self.conf`, but uses targets such as `~self` or `~{ self test6_1_t }`. It includes custom classes, attributes, ordinary allows, xperm allows, and neverallowxperm ranges through test 31.

## Control Flow
Each block checks whether a non-self complement target intersects the corresponding allow relation. Extended-permission blocks test the same target semantics with ioctl singleton and range permissions.

## State And Persistence Behavior
The policydb must represent `~self` as a relation-dependent complement rather than a single static type set. Attribute expansion and xperm range storage are both involved.

## Dependencies And Integration Points
It integrates with neverallow type-set complement logic, self relation evaluation, attribute expansion, and xperm assertion checking.

## Risks And Edge Cases
`~self` and `{ set -self }` look similar but differ in universe and exclusion behavior. Reusing code paths without preserving those semantics can produce false positives or false negatives.

## Test Signals
Signals are correct assertion outcomes for non-self conflicts and non-conflicts, especially in the later attribute/xperm violation cases.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/policies/test-neverallow/policy_not_self.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-common.c -->
# sources/security-integrity/selinux/libsepol/tests/test-common.c

## Purpose
This C file provides shared CUnit assertion helpers for libsepol policydb tests. It centralizes checks for symbol scope, reverse indexes, type aliases, role type sets, and attribute type sets.

## Important APIs, Types, And Functions
Public helpers are `test_sym_presence()`, `test_policydb_indexes()`, `test_alias_datum()`, `test_role_type_set()`, and `test_attr_types()`. Internal map callbacks validate `common_datum_t`, `class_datum_t`, `role_datum_t`, `type_datum_t`, `user_datum_t`, `cond_bool_datum_t`, `level_datum_t`, and `cat_datum_t` indexes.

## Control Flow
Index tests iterate each `p->symtab[i].table` with `hashtab_map()` and assert reverse mappings such as `sym_val_to_name`, `class_val_to_struct`, and `role_val_to_struct`. Role and attribute helpers iterate positive bits in ebitmaps and compare names against expected arrays.

## State And Persistence Behavior
The file does not own persistent state. It inspects mutable `policydb_t` structures after load/link/expand operations and uses CUnit assertions to fail fast on missing required data.

## Dependencies And Integration Points
It depends on libsepol policydb internals, `hashtab_search()`, `ebitmap_for_each_positive_bit`, CUnit, and helper routines declared elsewhere. Many expander/linker tests rely on these helpers to validate in-memory structures rather than serialized policies.

## Risks And Edge Cases
Helpers compare by symbol names through value-index arrays, so corrupted reverse indexes can cascade into confusing failures. `test_sym_presence()` checks declared IDs without requiring order, but role/attribute helpers require exact set membership counts.

## Test Signals
Any CUnit failure indicates symbol scope, index, alias, role set, or attribute set inconsistency after policy processing.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-common.h -->
# sources/security-integrity/selinux/libsepol/tests/test-common.h

## Purpose
This header publishes the common policydb assertion helpers used by multiple libsepol test suites.

## Important APIs, Types, And Functions
It includes `<sepol/policydb/policydb.h>` and declares `test_sym_presence()`, `test_policydb_indexes()`, `test_alias_datum()`, `test_role_type_set()`, and `test_attr_types()`.

## Control Flow
There is no runtime control flow in the header. Its comments document expected inputs for each helper and how tests should pass policydbs, symbol names, declarations, expected type arrays, and flags.

## State And Persistence Behavior
The header carries no state. It exposes helpers that inspect `policydb_t`, `avrule_decl_t`, `role_datum_t`, and symbol table state owned elsewhere.

## Dependencies And Integration Points
It is included by expander, linker, and other test files that need consistent policydb structural assertions.

## Risks And Edge Cases
The API exposes internal libsepol data types, so changes to policydb internals can require broad test updates. The comments are part of the contract for correct helper usage.

## Test Signals
Successful compilation of users confirms the expected helper signatures remain stable; runtime signals come from the implementations in `test-common.c`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-cond.c -->
# sources/security-integrity/selinux/libsepol/tests/test-cond.c

## Purpose
This CUnit suite tests conditional expression equality in expanded policydbs.

## Important APIs, Types, And Functions
Important functions are `cond_test_init()`, `cond_test_cleanup()`, `test_cond_expr_equal()`, and `cond_add_tests()`. It uses `policydb_t basemod`, `policydb_t base_expanded`, `test_load_policy()`, `link_modules()`, `expand_module()`, and `cond_expr_equal()`.

## Control Flow
Initialization creates the expanded policydb, loads `test-cond/refpolicy-base.conf`, links the base, expands it, and leaves `base_expanded.cond_list` ready. The test nests two loops over every conditional node: a node must equal itself and not equal any distinct node.

## State And Persistence Behavior
The suite owns two static policydbs for the lifetime of the CUnit suite and destroys them in cleanup. It does not write external files.

## Dependencies And Integration Points
It depends on parser helpers, linker, expander, and the conditional module. The policy fixture provides enough conditionals to make equality checks meaningful.

## Risks And Edge Cases
The test assumes distinct conditional nodes are not structurally equal. If two policy expressions are intentionally identical but allocated as separate nodes, this test would treat equality as a bug.

## Test Signals
The registered CUnit test `cond_expr_equal` fails on load/link/expand errors or incorrect equality behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-cond.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-cond.h -->
# sources/security-integrity/selinux/libsepol/tests/test-cond.h

## Purpose
This header exposes the conditional-expression test suite hooks to the libsepol CUnit runner.

## Important APIs, Types, And Functions
It includes `<CUnit/Basic.h>` and declares `cond_test_init()`, `cond_test_cleanup()`, and `cond_add_tests(CU_pSuite suite)`.

## Control Flow
The runner calls the init hook before suite execution, `cond_add_tests()` to register `cond_expr_equal`, and cleanup after execution.

## State And Persistence Behavior
The header owns no state; the static policydbs live in `test-cond.c`.

## Dependencies And Integration Points
It integrates the conditional suite with the common CUnit suite registration pattern used by libsepol tests.

## Risks And Edge Cases
Signature drift here breaks test runner integration even if the implementation still compiles standalone.

## Test Signals
Compilation and successful suite registration are the header-level signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-cond.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-deps.c -->
# sources/security-integrity/selinux/libsepol/tests/test-deps.c

## Purpose
This CUnit suite verifies libsepol module dependency checking for global and optional `require` blocks across types, attributes, object classes, booleans, roles, and permissions.

## Important APIs, Types, And Functions
Key functions are `deps_test_init()`, `deps_test_cleanup()`, `do_deps_modreq_global()`, `deps_modreq_global()`, `do_deps_modreq_opt()`, `deps_modreq_opt()`, and `deps_add_tests()`. Static arrays `bases_met[NUM_BASES]` and `bases_notmet[NUM_BASES]` hold separate loaded base policydbs.

## Control Flow
Initialization loads many copies of the positive and negative base fixtures. Each test loads a module, suppresses expected error logging through `sepol_handle_t`, calls `link_modules()`, checks the return value, destroys the module, and if appropriate inspects the linked declaration containing a marker type.

## State And Persistence Behavior
Each base policydb is mutated by a single link scenario and kept separate to avoid cross-test contamination. Cleanup destroys all base policydbs.

## Dependencies And Integration Points
The suite depends on `test_load_policy()`, `test_find_decl_by_sym()`, `link_modules()`, sepol handles/message callbacks, and all `test-deps` policy fixtures.

## Risks And Edge Cases
The test uses numeric base indexes that must align with the module matrix. Optional permission behavior intentionally expects a link failure in the negative case, unlike most optional symbol families.

## Test Signals
CUnit tests `deps_modreq_global` and `deps_modreq_opt` validate return values (`0` or `-3`) and declaration enablement for marker types.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-deps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-deps.h -->
# sources/security-integrity/selinux/libsepol/tests/test-deps.h

## Purpose
This header exposes dependency-test suite hooks to the libsepol CUnit runner.

## Important APIs, Types, And Functions
It includes `<CUnit/Basic.h>` and declares `deps_test_init()`, `deps_test_cleanup()`, and `deps_add_tests(CU_pSuite suite)`.

## Control Flow
The runner uses these functions to load base fixtures, register dependency test cases, and release policydb state.

## State And Persistence Behavior
No state is declared here; static policydb arrays live in `test-deps.c`.

## Dependencies And Integration Points
It follows the common suite interface used by other test headers in this directory.

## Risks And Edge Cases
Changing names or signatures would disconnect the dependency suite from the runner.

## Test Signals
Compilation and successful CUnit test registration are the direct signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-deps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-downgrade.c -->
# sources/security-integrity/selinux/libsepol/tests/test-downgrade.c

## Purpose
This CUnit suite tests backward compatibility of binary policy writing by repeatedly downgrading a high-version policy and reading it back.

## Important APIs, Types, And Functions
Key functions are `downgrade_test_init()`, `downgrade_test_cleanup()`, `downgrade_add_tests()`, `test_downgrade()`, `do_downgrade_test(int mls)`, `read_binary_policy()`, and `write_binary_policy()`. Constants are `POLICY_BIN_HI` and `POLICY_BIN_LO`.

## Control Flow
`test_downgrade()` runs non-MLS and MLS downgrade loops. `do_downgrade_test()` reads `policy.hi`, toggles `policydb.mls`, then for each high version writes lower versions down to `POLICYDB_VERSION_MIN` and reads each generated `policy.lo` back into a temporary policydb.

## State And Persistence Behavior
The suite owns a static `policydb`. It writes `policies/test-downgrade/policy.lo` repeatedly as a test artifact and reads it back. It suppresses libsepol warning output while writing through a temporary `sepol_handle_t`.

## Dependencies And Integration Points
It depends on `policydb_read()`, `policydb_write()`, `struct policy_file`, policy version constants, standard file I/O, and CUnit.

## Risks And Edge Cases
The test mutates and reuses a global policydb. Early returns after initializing `policydb_tmp` can leak temporary state. MLS downgrades before `POLICYDB_VERSION_MLS` are expected write failures and must remain special-cased.

## Test Signals
Signals are successful write/read round trips for each supported lower version and expected skips for unsupported MLS-to-pre-MLS downgrades.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-downgrade.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-downgrade.h -->
# sources/security-integrity/selinux/libsepol/tests/test-downgrade.h

## Purpose
This header exposes the binary policy downgrade test suite and its file I/O helpers.

## Important APIs, Types, And Functions
It includes CUnit and `policydb.h`, then declares suite hooks `downgrade_test_init()`, `downgrade_test_cleanup()`, `downgrade_add_tests()`, test entry `test_downgrade()`, worker `do_downgrade_test(int mls)`, and helpers `read_binary_policy()` and `write_binary_policy()`.

## Control Flow
The runner registers the downgrade test through `downgrade_add_tests()`. Other code may call the read/write helpers directly with a path and policydb pointer.

## State And Persistence Behavior
No state is declared in the header, but the APIs expose functions that read and write binary policy files.

## Dependencies And Integration Points
It integrates binary policy version tests with the common CUnit runner and policydb serialization APIs.

## Risks And Edge Cases
The helper declarations make file-writing utilities visible beyond the suite; callers must pass initialized policydbs and valid paths.

## Test Signals
Header-level signals are compile-time compatibility and suite registration.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-downgrade.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-ebitmap.c -->
# sources/security-integrity/selinux/libsepol/tests/test-ebitmap.c

## Purpose
This CUnit suite tests libsepol extended bitmap behavior across initialization, comparison, set/get, ranges, boolean operations, complement operations, and randomized algebraic checks.

## Important APIs, Types, And Functions
Important functions are `ebitmap_init_random()`, `test_ebitmap_init_destroy()`, `test_ebitmap_cmp()`, `test_ebitmap_set_and_get()`, `test_ebitmap_init_range()`, `test_ebitmap_or()`, `test_ebitmap_and()`, `test_ebitmap_xor()`, `test_ebitmap_not()`, `test_ebitmap_andnot()`, `test_ebitmap__random_impl()`, `test_ebitmap__random()`, `ebitmap_test_init()`, and `ebitmap_add_tests()`.

## Control Flow
The suite creates small deterministic bitmaps around node boundaries such as 63/64, 191/192, 319/320, 1023/1024, and larger random bitmaps. Each operation writes a destination bitmap, compares against expected bitmaps, then destroys all temporary bitmaps.

## State And Persistence Behavior
There is no persistent external state. Runtime state is heap-backed `ebitmap_t` nodes. `ebitmap_test_init()` seeds `random()` with `time(NULL)` and disables sepol debug output.

## Dependencies And Integration Points
It depends on `<sepol/policydb/ebitmap.h>`, errno-style return codes, random number generation, and CUnit. These tests are direct low-level coverage for data structures used throughout policydb type sets.

## Risks And Edge Cases
Randomized tests are nondeterministic because the seed is current time, making rare failures harder to reproduce. The suite stresses boundary allocation but does not inject allocation failures.

## Test Signals
Signals include correct return codes (`-EINVAL`, `-EOVERFLOW`), correct cardinality/highest-bit values, exact operation results, and randomized per-bit equivalence for OR, AND, XOR, NOT, ANDNOT, and copy.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-ebitmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-ebitmap.h -->
# sources/security-integrity/selinux/libsepol/tests/test-ebitmap.h

## Purpose
This header exposes the ebitmap CUnit suite hooks.

## Important APIs, Types, And Functions
It includes `<CUnit/Basic.h>` and declares `ebitmap_test_init()`, `ebitmap_test_cleanup()`, and `ebitmap_add_tests(CU_pSuite suite)`.

## Control Flow
The test runner initializes random/debug state, registers the bitmap test cases, and calls cleanup through these functions.

## State And Persistence Behavior
The header contains no state. The implementation allocates and destroys bitmap state per test.

## Dependencies And Integration Points
It integrates low-level ebitmap tests with the libsepol CUnit runner.

## Risks And Edge Cases
Only suite-level hooks are exposed; individual test functions are static in the implementation, which is good for encapsulation but limits selective external invocation.

## Test Signals
Compilation and successful registration of all ebitmap tests are the header-level signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-ebitmap.h -->
