# Research Group subset-b-008344

This grouped report covers the SELinux checkpolicy round-trip fixtures, the `dispol` binary-policy inspection helper, the `org.selinux` D-Bus service packaging, and several `system-config-selinux` GUI pages. Each section is bounded for reconciliation into a source-tree-aligned per-file document.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/test/dispol.c -->
# sources/security-integrity/selinux/checkpolicy/test/dispol.c

## Purpose

`dispol.c` is an interactive and scriptable diagnostic utility for reading a binary SELinux policy file and rendering selected policydb contents in text form. It is explicitly test-oriented: the header describes it as a binary policy display program that focuses on AVTAB and conditional AVTAB rules, but the current implementation also displays booleans, conditional expressions, policy capabilities, classes, users, roles, types, attributes, permissive types, role transitions, filename transition rules, and unknown-class handling.

## Important APIs, Types, And Functions

The file is tightly coupled to libsepol internals through `policydb_t`, `policy_file`, `avtab_t`, `avtab_key_t`, `avtab_datum_t`, `cond_node_t`, `cond_expr_t`, `role_trans_t`, `filename_trans_key`, `filename_trans_datum`, `ebitmap_node_t`, and symbol tables such as `p_type_val_to_name`, `p_class_val_to_name`, and `sym_val_to_name`.

`commands[]` defines the UI and noninteractive action set. Its `CMD`, `HEADER`, and `NOOPT` metadata drive `usage()` and `menu()` display, while `main()` directly switches on the action character.

Rendering helpers include `render_access_mask()`, `render_type()`, `render_key()`, and `render_av_rule()`. `render_av_rule()` is the central formatter: it filters conditional rules by `RENDER_UNCONDITIONAL`, `RENDER_ENABLED`, `RENDER_DISABLED`, and `RENDER_CONDITIONAL`, then prints allow/auditallow/dontaudit, type transition/member/change, and extended-permission forms using `sepol_av_to_string()` and `sepol_extended_perms_to_string()`.

Display commands are implemented by `display_avtab()`, `display_expr()`, `display_cond_expressions()`, `display_handle_unknown()`, `display_booleans()`, `display_policycaps()`, `display_classes()`, `display_users()`, `display_roles()`, `display_types()`, `display_attributes()`, `display_permissive()`, `display_role_trans()`, and `display_filename_trans()`. `change_bool()` mutates an in-memory boolean and calls `evaluate_conds()` so later conditional displays reflect the new state.

## Control Flow

`main()` accepts `binary_pol_file` or `-a/--actions ACTIONS binary_pol_file`. It opens the policy, stats it, maps it privately with read/write permissions, initializes a memory-backed `policy_file`, initializes `policydb`, and calls `policydb_read()`. In interactive mode it prints progress and the menu; in action mode it consumes one character per action and defaults to `q` when the action string is exhausted.

The command loop dispatches numbered AVTAB and conditional commands, metadata commands such as classes/types/users/roles, output redirection via `f`, filename transition display via `F`, and shutdown via `q`. Interactive boolean changes prompt for a name and state; noninteractive actions cannot supply the boolean name/state because command `7` is marked `NOOPT` only in the menu metadata and still prompts through stdin.

## State And Persistence

The binary policy is loaded into memory and represented in `policydb`. `change_bool()` is the only policy state mutation and is deliberately in-memory only; the original policy file is not rewritten. Output state is held in `out_fp`, which can be switched to a newly opened file by the `f` command. The program destroys `policydb` only on the explicit `q` path, not on all error exits.

## Dependencies And Integration Points

The utility depends on libsepol policydb headers and functions, POSIX file APIs, and `mmap()`. It integrates with checkpolicy/libsepol tests by providing a way to inspect binary policy internals after compilation. Its output uses libsepol string formatting for access vectors and extended permissions, so changes in libsepol canonical output can affect tests or users of this diagnostic.

## Risks And Edge Cases

Several functions index libsepol value-to-name arrays with `value - 1`; malformed or unexpected policydb values could cause invalid reads. `render_key()` checks source and target type names but not `tclass` before printing. `display_id()` assumes the symbol name exists. The mapping requests `PROT_READ | PROT_WRITE` even though the file is opened read-only and mapped `MAP_PRIVATE`, which may be less portable than a read-only mapping. Error paths after `open()`, `fstat()`, `mmap()`, `policydb_init()`, or `policydb_read()` exit without centralized cleanup. `ans[strlen(ans) - 1] = 0` assumes non-empty input lines. Output file handles are overwritten without closing a previous non-stdout file.

## Test Signals

Useful tests compile a small binary policy, run `dispol -a` across actions `1` through `6` and metadata commands, and compare stable substrings for AV rules, booleans, policycaps, classes, roles, types, permissives, and unknown handling. Conditional tests should flip booleans interactively or through a scripted stdin path and verify `evaluate_conds()` changes enabled/disabled rendering. Fuzz or negative tests should cover unreadable files, invalid policy blobs, and policies with sparse symbol names.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/test/dispol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/tests/policy_allonce.conf -->
# sources/security-integrity/selinux/checkpolicy/tests/policy_allonce.conf

## Purpose

`policy_allonce.conf` is a compact non-MLS SELinux policy source fixture that deliberately exercises many checkpolicy language constructs in one file. It is used by `test_roundtrip.sh` as the input for normal round-trip testing and optimized round-trip testing.

## Policy Surface

The fixture declares handle-unknown behavior, object classes, inherited common permissions, initial SIDs, default user/role/type rules, `policycap open_perms`, attributes, expandattribute directives, types with aliases, `typealias`, `typeattribute`, `typebounds`, booleans, tunables, TE rules, filename transitions, extended permissions, permissive and neveraudit declarations, roles, role attributes, role transitions, conditional blocks, optional/require syntax, users, constraints, validatetrans, SID contexts, filesystem labeling, genfs contexts, port/netif/node contexts, InfiniBand pkey contexts, and InfiniBand endport contexts.

## Control Flow And Integration

The file has no runtime control flow, but its declaration order and syntax variants feed the checkpolicy parser. In the test script it is compiled with default options and decompiled with `-b -F` into `policy_allonce.expected.conf`; it is also compiled/decompiled with `-S -O` and compared against `policy_allonce.expected_opt.conf`.

## State And Persistence

This is a declarative policy artifact. Persistent state exists only as the semantic policy compiled into `testpol.bin` during testing. The source intentionally uses aliases, wildcard permissions, CIDR node syntax, wildcard network interfaces, hex InfiniBand values, and unquoted root genfs paths to verify canonical persistence through the binary policy format.

## Dependencies And Integration Points

It depends on the checkpolicy grammar and libsepol decompiler behavior. It integrates directly with `policy_allonce.expected.conf`, `policy_allonce.expected_opt.conf`, and `test_roundtrip.sh`.

## Risks

Because this fixture covers many unrelated grammar features, a failure can be broad and requires diff inspection to isolate whether the parser, optimizer, serializer, or decompiler changed. The test is order-sensitive for canonical output. The file also contains old-style comments documenting expected normalization, such as `sameuser` expansion, quoted paths, CIDR normalization, and hex-to-decimal conversion.

## Test Signals

The key signal is a clean `diff -u` against both expected files after the compile/decompile cycle. Important semantic signals include expansion of set-based rules, preservation of aliases as `typealias` output, decomposition of extended ioctl ranges, conditional rendering for booleans/tunables, canonical network context ordering, and conversion of InfiniBand hex ranges to decimal in the expected output.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/tests/policy_allonce.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/tests/policy_allonce.expected.conf -->
# sources/security-integrity/selinux/checkpolicy/tests/policy_allonce.expected.conf

## Purpose

This file is the canonical decompiled output expected when `policy_allonce.conf` is compiled and then converted back to source without `-S -O` optimization. It captures checkpolicy's normalized representation of the broad non-MLS fixture.

## Important Semantics

The file removes source-only constructs such as `expandattribute` and tunable declarations that do not survive in the same textual form, emits expanded type aliases as separate `typealias` statements, expands type sets into individual `auditallow`, `dontaudit`, and filename transition rules, emits optional `allow TYPE1 self:CLASS2` as a concrete rule, and rewrites `sameuser` to `(u1 == u2)`.

Extended permission ranges are canonicalized into segments, for example the ioctl range from `0x456-0x5678` is split along internal boundaries. Conditional blocks are printed in normalized `if (BOOL)` form, with the `! BOOL1` source becoming an empty true branch and populated `else` branch. Paths and network contexts are normalized: root genfs becomes `"/"`, CIDR node contexts become address/mask pairs, and netif contexts are sorted canonically. InfiniBand pkey hex values are rendered as decimal.

## Control Flow And Integration

`test_roundtrip.sh` first compares this file against decompiled output from `policy_allonce.conf`, then compiles this expected file and decompiles it again to ensure the canonical form is idempotent.

## State And Persistence

This artifact represents persisted binary policy semantics rather than authoring syntax. It intentionally excludes constructs optimized away only by `-S -O`; for example some conditional permissions remain broader here than in the optimized expected file.

## Dependencies And Risks

The file is sensitive to libsepol output ordering, xperm range formatting, condition simplification, and canonical address formatting. Legitimate compiler changes require synchronized updates to this expected file and `policy_allonce.expected_opt.conf`; otherwise the round-trip test will fail even if policy semantics remain equivalent.

## Test Signals

A passing diff confirms broad non-MLS parser/decompiler stability, including type/role/user sections, AV rules, xperms, conditional rules, constraints, SID contexts, filesystem contexts, network contexts, and InfiniBand contexts.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/tests/policy_allonce.expected.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/tests/policy_allonce.expected_opt.conf -->
# sources/security-integrity/selinux/checkpolicy/tests/policy_allonce.expected_opt.conf

## Purpose

This file is the expected canonical output for `policy_allonce.conf` when the policy is compiled and decompiled with `-S -O`. It validates the optimizer's effect on the same broad non-MLS grammar fixture.

## Important Semantics

Most content mirrors `policy_allonce.expected.conf`, but the optimized conditional bodies are pruned. In the `BOOL1` false branch, the unconditional `allow TYPE1 self:CLASS1 { PERM1 }` already grants `PERM1`, so the optimized branch keeps only `ioctl`. In the `BOOL2` branch, the unconditional xperm already includes `0x1`, so the branch keeps only `0x2`.

## Control Flow And Integration

`test_roundtrip.sh` uses this file for the `check_policy policy_allonce.conf policy_allonce.expected_opt.conf '-S -O'` lane, then verifies the expected file itself is stable under the same options.

## State And Persistence

The file represents the optimized persisted semantics of the compiled policy, not the original source form. Its main state signal is removal of redundant conditional permissions while preserving nonredundant rules, declarations, contexts, and constraints.

## Dependencies And Risks

The artifact is tightly coupled to optimizer logic. Changes in redundancy detection for normal permissions or extended permissions will surface as small but meaningful diffs. A risk is treating an optimizer diff as formatting-only; in this file the reduced permissions are the main test oracle.

## Test Signals

The strongest signal is the small diff from the non-optimized expected file: only redundant conditional permissions should disappear. Broader changes suggest unintended parser/decompiler or optimizer behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/tests/policy_allonce.expected_opt.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/tests/policy_allonce_mls.conf -->
# sources/security-integrity/selinux/checkpolicy/tests/policy_allonce_mls.conf

## Purpose

`policy_allonce_mls.conf` is the MLS counterpart to the broad all-in-one checkpolicy fixture. It exercises MLS declarations and range handling while still covering many of the same type, role, conditional, context, and xperm constructs as the non-MLS fixture.

## Policy Surface

The MLS-specific surface includes sensitivities, a sensitivity alias, dominance, categories with aliases, levels, `mlsconstrain`, `mlsvalidatetrans`, users with level/range, SID contexts with ranges, MLS ranges on `fs_use_*`, genfs, port, netif, node, InfiniBand pkey, and InfiniBand endport contexts, and a `range_transition`.

The non-MLS-style surface includes classes, common permissions, default rules, `policycap open_perms`, attributes, type aliases, typebounds, booleans and tunables, AV/TE rules, xperms, permissive and neveraudit declarations, roles, role transitions, optional rules, constraints, and validatetrans.

## Control Flow And Integration

The fixture is compiled by `test_roundtrip.sh` with `-M` for the standard MLS expected output and with `-M -S -O` for the optimized expected output. Its declaration choices are designed to expose MLS canonicalization rather than runtime flow.

## State And Persistence

The compiled binary policy must persist MLS lattice declarations, aliases, category ranges, and security contexts. The expected output verifies that shorthand ranges are expanded to canonical low-high forms such as `s0 - s0`, aliases like `CATALIAS` resolve to canonical categories, and `range_transition` prints as a low-high MLS range.

## Dependencies And Risks

This file is sensitive to the checkpolicy MLS parser and decompiler. Because it combines MLS and non-MLS constructs, failures can come from general TE formatting or MLS-specific formatting. Alias handling and range formatting are particularly fragile compatibility points.

## Test Signals

Passing tests confirm MLS declaration parsing, constraint formatting, alias resolution in dominance and categories, MLS context normalization for SIDs and labeling statements, xperm formatting, conditional rule handling, and optimized removal of redundant permissions in the `_expected_opt` lane.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/tests/policy_allonce_mls.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/tests/policy_allonce_mls.expected.conf -->
# sources/security-integrity/selinux/checkpolicy/tests/policy_allonce_mls.expected.conf

## Purpose

This file is the canonical decompiled output for `policy_allonce_mls.conf` with MLS enabled and without optimization. It is the oracle for MLS round-trip stability.

## Important Semantics

The expected output resolves `SENSALIAS` in dominance to `s2`, keeps the sensitivity alias declaration, preserves category alias `CATALIAS` while rendering ranges as `c0,c1`, formats `mlsvalidatetrans` with parentheses, expands type aliases and set-based rules, and prints `range_transition TYPE1 TYPE2:CLASS1 s1:c0,c1 - s1:c0,c1`.

MLS contexts are normalized consistently: user ranges become `level s0 range s0 - s1:c0,c1`, SID and fs contexts print canonical ranges, and single-level genfs/port/netif/node/InfiniBand contexts gain `s0 - s0`.

## Control Flow And Integration

`test_roundtrip.sh` compares this file to decompiled output from the source fixture under `-M`, then compiles and decompiles this expected file again to verify idempotence.

## State And Persistence

The file is a persisted semantic snapshot of MLS policy state after binary serialization. It intentionally reflects canonical values rather than original aliases or shorthand syntax where the compiler normalizes those forms.

## Dependencies And Risks

The artifact depends on stable MLS range rendering and rule ordering. Updates to MLS alias resolution, range compression/expansion, or conditional formatting must be reflected here. Small textual diffs can indicate meaningful changes to MLS policy semantics.

## Test Signals

The expected diff validates MLS lattice declarations, MLS constraints, range transitions, canonical MLS contexts, general TE and role/user declarations, and non-optimized conditional branches.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/tests/policy_allonce_mls.expected.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/tests/policy_allonce_mls.expected_opt.conf -->
# sources/security-integrity/selinux/checkpolicy/tests/policy_allonce_mls.expected_opt.conf

## Purpose

This file is the optimized MLS expected output for `policy_allonce_mls.conf` under `-M -S -O`. It verifies that optimizer behavior remains correct when MLS declarations and ranges are present.

## Important Semantics

It is nearly identical to `policy_allonce_mls.expected.conf`; the intentional optimization difference is in the `BOOL1` false branch, where the redundant `PERM1` permission is removed and only `ioctl` remains because `PERM1` is already granted unconditionally.

## Control Flow And Integration

`test_roundtrip.sh` uses this file in the MLS optimized lane and then verifies it is itself stable under repeated compile/decompile with the same options.

## State And Persistence

The file persists canonical MLS policy state plus optimizer-pruned conditional permission state. It should not alter MLS lattice declarations, ranges, SIDs, or context forms relative to the non-optimized expected file except where optimization changes effective rule output.

## Dependencies And Risks

The main risk is over-pruning conditional permissions in an MLS policy or accidentally changing MLS formatting while touching optimizer code. Because only one line differs from the non-optimized MLS expected file, unexpected wider diffs are high-value regression signals.

## Test Signals

Passing tests confirm that `-S -O` removes redundant conditional permissions without disturbing MLS declarations, range transitions, or context canonicalization.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/tests/policy_allonce_mls.expected_opt.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/tests/policy_allonce_xen.conf -->
# sources/security-integrity/selinux/checkpolicy/tests/policy_allonce_xen.conf

## Purpose

`policy_allonce_xen.conf` is a Xen-target all-in-one policy fixture. It exercises checkpolicy target-specific handling with Xen SIDs and hardware/device context statements while retaining a representative subset of TE, role, user, conditional, and constraint constructs.

## Policy Surface

The file declares classes, SIDs `kernel`, `dom0`, and `domio`, common permissions, default rules, attributes, types and aliases, booleans/tunables, type transition/member/change rules, allow/audit/dontaudit/neverallow, permissive type, roles and role transitions, conditionals, optional rules, `policycap open_perms`, users, constraints, validatetrans, SID contexts, and Xen-specific `pirqcon`, `iomemcon`, `ioportcon`, `pcidevicecon`, and `devicetreecon` statements.

## Control Flow And Integration

The test script compiles it with `--target xen -c 30 -E` and compares the decompiled result to `policy_allonce_xen.expected.conf`; the optimized lane adds `-S -O` and compares with `policy_allonce_xen.expected_opt.conf`.

## State And Persistence

The persisted policy state must translate the source's `sid kernel` into target-specific canonical output `sid xen` in expected files. Numeric hardware ranges are also canonicalized as hexadecimal for iomem, ioport, and pcidevice contexts.

## Dependencies And Risks

This fixture depends on Xen target support in checkpolicy and policy version 30 compatibility. Regressions may appear as SID target name changes, hardware context formatting differences, or optimizer behavior changes in conditional rules.

## Test Signals

Passing tests confirm Xen target parsing, SID canonicalization, hardware context handling, target-compatible TE rule output, conditional output in the non-optimized lane, and complete removal of the redundant `BOOL1` conditional block in the optimized lane.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/tests/policy_allonce_xen.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/tests/policy_allonce_xen.expected.conf -->
# sources/security-integrity/selinux/checkpolicy/tests/policy_allonce_xen.expected.conf

## Purpose

This file is the non-optimized expected canonical output for the Xen target fixture. It captures how checkpolicy decompiles the Xen-specific source policy after binary serialization.

## Important Semantics

The expected output emits `sid xen` instead of the source's `sid kernel`, preserves `dom0` and `domio`, expands type aliases and set-based rules, emits optional rules concretely, rewrites `sameuser` in `validatetrans`, normalizes role transition without an explicit class to `process`, and prints Xen hardware contexts with hexadecimal values for iomem/ioport/pcidevice ranges.

The non-optimized output retains the `BOOL1` conditional as an empty true branch and a false branch granting `PERM1`.

## Control Flow And Integration

`test_roundtrip.sh` uses this artifact for the `--target xen -c 30 -E` lane and verifies both source-to-expected and expected-to-expected round trips.

## State And Persistence

The file is a canonical snapshot of Xen-target policy state and target-specific context records. It represents the binary policy's output form rather than the exact authoring syntax.

## Dependencies And Risks

It is sensitive to target-specific SID mapping and numeric formatting. Any update to Xen policy support can require expected-file updates; unrelated diffs in general TE sections may indicate shared checkpolicy regressions.

## Test Signals

Passing diffs validate Xen SIDs, device contexts, class and type declarations, AV and TE rules, conditional rendering, role/user sections, constraints, and validatetrans canonicalization.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/tests/policy_allonce_xen.expected.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/tests/policy_allonce_xen.expected_opt.conf -->
# sources/security-integrity/selinux/checkpolicy/tests/policy_allonce_xen.expected_opt.conf

## Purpose

This file is the optimized expected output for the Xen target fixture under `--target xen -c 30 -E -S -O`.

## Important Semantics

The optimized file matches the non-optimized Xen expected output except that the redundant `BOOL1` conditional block is removed entirely. The unconditional `allow TYPE1 self:CLASS1 { PERM1 }` makes the false-branch conditional permission redundant, so no conditional remains.

## Control Flow And Integration

It is the oracle for the optimized Xen lane in `test_roundtrip.sh`, and the script verifies it is stable through repeated optimized compile/decompile.

## State And Persistence

The artifact persists Xen target state with optimizer-pruned conditionals. Xen-specific SIDs and hardware contexts must remain identical to the non-optimized expected file.

## Dependencies And Risks

The file is sensitive to optimizer block elimination and Xen target formatting. A regression can either keep redundant conditional output or accidentally remove nonredundant Xen target records.

## Test Signals

A passing diff confirms `-S -O` can eliminate a fully redundant conditional block while preserving Xen SID and device context output.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/tests/policy_allonce_xen.expected_opt.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/tests/policy_minimal.conf -->
# sources/security-integrity/selinux/checkpolicy/tests/policy_minimal.conf

## Purpose

`policy_minimal.conf` is the smallest non-MLS policy fixture in this test subset. It verifies that checkpolicy can round-trip a minimal policy with one class, one SID, one type, one allow rule, one role, one role-type assignment, one user, and one SID context.

## Control Flow And Integration

`test_roundtrip.sh` compiles and decompiles this file with `-E` and with `-E -S -O`, using the same file as both source and expected output. That means no canonical text changes are expected for this minimal policy.

## State And Persistence

The compiled policy persists a single `kernel` SID context `USER1:ROLE1:TYPE1`, a single object class permission, and the minimum type/role/user relationships required for the allow rule and context to be valid.

## Dependencies And Risks

The fixture depends on base checkpolicy grammar and the `-E` option used by the test harness. Because it is intentionally tiny, it is a good smoke test but provides little coverage for ordering, optimizer, aliases, constraints, conditionals, or context normalization.

## Test Signals

The expected signal is exact self-round-trip identity. A diff here indicates a basic parser/decompiler or canonical output regression that should be investigated before interpreting broader fixture failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/tests/policy_minimal.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/tests/policy_minimal_mls.conf -->
# sources/security-integrity/selinux/checkpolicy/tests/policy_minimal_mls.conf

## Purpose

`policy_minimal_mls.conf` is the smallest MLS policy fixture in this subset. It extends the minimal non-MLS policy with one sensitivity, dominance declaration, category, level, MLS constraint, user MLS range, and SID MLS range.

## Control Flow And Integration

The round-trip script compiles/decompiles it with `-M -E` and with `-M -E -S -O`, using the file itself as the expected output. No optimizer or canonical text changes are expected.

## State And Persistence

The persisted policy includes a minimal MLS lattice (`s0`, `c0`, `s0:c0`), an MLS constraint on `CLASS1 PERM1`, and contexts normalized in the source as `s0 - s0` ranges. The type/role/user state mirrors the non-MLS minimal fixture.

## Dependencies And Risks

This is a smoke test for MLS parser enablement and minimum valid MLS policy structure. It does not cover MLS aliases, range transitions, category sets beyond one category, or complex constraints.

## Test Signals

Exact identity after both MLS round-trip lanes confirms that basic MLS declarations, constraints, and contexts survive binary serialization without unexpected formatting changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/tests/policy_minimal_mls.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/tests/test_roundtrip.sh -->
# sources/security-integrity/selinux/checkpolicy/tests/test_roundtrip.sh

## Purpose

`test_roundtrip.sh` is the shell test harness for checkpolicy source-to-binary-to-source round trips. It validates that selected policy fixtures compile, decompile into canonical source, and remain idempotent when the canonical output is compiled and decompiled again.

## Important Functions And Flow

The script uses `set -eu`, computes `BASEDIR=$(dirname "$0")`, and sets `CHECKPOLICY="${BASEDIR}/../checkpolicy"`. The `check_policy()` function takes `POLICY`, `EXPECTED`, and `OPTS`. It compiles `${POLICY}` into `testpol.bin`, decompiles that binary with `-b -F` into `testpol.conf`, diffs against `${EXPECTED}`, then repeats the compile/decompile cycle using `${EXPECTED}` as input to ensure expected files are stable canonical forms.

The harness runs minimal non-MLS, minimal MLS, allonce non-MLS, allonce MLS, and allonce Xen lanes with option combinations covering `-E`, `-M`, `-S -O`, `--target xen`, and `-c 30`.

## State And Persistence

The script writes transient `testpol.bin` and `testpol.conf` into the tests directory and overwrites them on each lane. It does not clean them at the end. Exit state is controlled by shell `set -e` and `diff` return codes.

## Dependencies And Integration Points

It depends on the sibling `checkpolicy` binary, POSIX shell, `diff`, and the fixture/expected files in the same directory. It is an integration point for parser, optimizer, binary serializer, and source decompiler behavior.

## Risks

Because transient files are written in the source tests directory, concurrent test runs can race or produce confusing diffs. `BASEDIR=$(dirname "$0")` is robust for relative invocation but does not canonicalize symlinks. The script assumes `checkpolicy` is built at the expected path.

## Test Signals

A successful run means every fixture compiles, decompiles, matches expected canonical text, and the expected canonical text is idempotent. The lane names printed before each test make it straightforward to isolate which fixture or option set failed.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/checkpolicy/tests/test_roundtrip.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/dbus/Makefile -->
# sources/security-integrity/selinux/dbus/Makefile

## Purpose

This Makefile installs the SELinux D-Bus service files, PolicyKit action metadata, and the Python service implementation.

## Targets And Flow

`all` and `clean` are no-ops. `install` creates D-Bus system configuration, system service, polkit action, and `system-config-selinux` share directories under `DESTDIR` and `PREFIX`, then installs `org.selinux.conf`, `org.selinux.service`, `org.selinux.policy`, and executable `selinux_server.py`. `relabel` and `test` are empty placeholders.

## State And Persistence

The target persists system configuration under `/etc/dbus-1/system.d`, service activation metadata under `$(PREFIX)/share/dbus-1/system-services`, polkit actions under `$(PREFIX)/share/polkit-1/actions`, and the server script under `$(PREFIX)/share/system-config-selinux`.

## Dependencies And Integration Points

It depends on `mkdir`, `install`, `DESTDIR`, and `PREFIX`. Installed files integrate the root-owned `org.selinux` D-Bus name with PolicyKit authorization and D-Bus activation.

## Risks

The install command uses leading `-` for `mkdir` commands, allowing directory creation failures to be ignored. There is no uninstall target or validation that the service script path matches the service file. The server is installed mode `755`, appropriate for execution but important because D-Bus starts it as root.

## Test Signals

Packaging tests should verify the four installed paths, file modes, D-Bus activation of `org.selinux`, and that the PolicyKit actions referenced by `selinux_server.py` are present.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/dbus/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/dbus/org.selinux.conf -->
# sources/security-integrity/selinux/dbus/org.selinux.conf

## Purpose

This D-Bus system bus configuration controls ownership and message routing for the `org.selinux` service.

## Policy Behavior

Only `root` may own the `org.selinux` bus name. The default context allows clients to send messages to `org.selinux`; method-level authorization is delegated to PolicyKit checks in `selinux_server.py`.

## State And Persistence

Installed under `/etc/dbus-1/system.d/`, this file persists bus policy for the system D-Bus daemon. It does not define methods or authorization semantics itself.

## Dependencies And Integration Points

It depends on D-Bus busconfig DTD semantics. It integrates with `org.selinux.service`, which starts the root service, and `org.selinux.policy`, which defines the PolicyKit action defaults.

## Risks

The broad default `allow send_destination="org.selinux"` is intentional but places all authorization responsibility on the service implementation. Any unauthenticated method in `selinux_server.py` would be reachable by any bus client.

## Test Signals

Bus policy tests should confirm non-root users cannot own `org.selinux`, ordinary clients can call into the service, and unauthorized method calls are denied by PolicyKit rather than by bus routing.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/dbus/org.selinux.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/dbus/org.selinux.policy -->
# sources/security-integrity/selinux/dbus/org.selinux.policy

## Purpose

This PolicyKit policy file defines authorization actions for the privileged `org.selinux` D-Bus API.

## Actions

It defines actions for `org.selinux.restorecon`, `org.selinux.setenforce`, `org.selinux.semanage`, `org.selinux.customized`, `org.selinux.semodule_list`, `org.selinux.relabel_on_boot`, `org.selinux.change_default_policy`, and `org.selinux.change_default_mode`. Defaults deny inactive and arbitrary users, while active sessions require `auth_admin_keep`.

## State And Persistence

Installed under `share/polkit-1/actions`, this file persists authorization defaults for PolicyKit. It does not perform actions itself; `selinux_server.py` asks PolicyKit to evaluate these action IDs.

## Dependencies And Integration Points

It depends on PolicyKit policyconfig syntax and action ID consistency with `selinux_server.py`. It integrates with D-Bus service methods and desktop authentication agents.

## Risks

All actions use broad descriptions such as "SELinux write access" or "SELinux Read access", which may not give users precise prompts. Read actions also require admin authentication, which is conservative but may reduce usability. A typo in an action ID would cause authorization failure or mismatched privilege behavior.

## Test Signals

Tests should verify every action ID used by the server exists here, default authorization results match expectations for active/inactive sessions, and prompted admin authentication allows the corresponding method.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/dbus/org.selinux.policy -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/dbus/org.selinux.service -->
# sources/security-integrity/selinux/dbus/org.selinux.service

## Purpose

This D-Bus service activation file registers the `org.selinux` service.

## Behavior

It names `org.selinux`, executes `/usr/share/system-config-selinux/selinux_server.py`, and requests `User=root`, so D-Bus activation starts the Python server with root privileges.

## State And Persistence

Installed under `share/dbus-1/system-services`, it persists system service activation metadata.

## Dependencies And Integration Points

It must match the installed path from the D-Bus Makefile and the bus name owned by `selinux_server.py`. It also depends on the script having an executable shebang and mode.

## Risks

Because the service runs as root, method authorization and input validation in `selinux_server.py` are critical. A packaging path mismatch would break D-Bus activation.

## Test Signals

Activation tests should call a harmless method such as `semodule_list` or observe D-Bus service startup and confirm the process runs as root and owns `org.selinux`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/dbus/org.selinux.service -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/dbus/selinux_client.py -->
# sources/security-integrity/selinux/dbus/selinux_client.py

## Purpose

`selinux_client.py` is a small client/demo utility for the `org.selinux` D-Bus service. It calls `SELinuxDBus().customized()` and converts `semanage export` text into a Python dictionary.

## Important APIs And Functions

The script imports `dbus`, `dbus.service`, and `SELinuxDBus` from `sepolicy.sedbus`. `convert_customization(buf)` parses newline-separated semanage export records into dictionaries keyed by customization kind. It initializes a dedicated `fcontext-equiv` dictionary and then recognizes `boolean`, `login`, `interface`, `user`, `port`, `node`, `fcontext`, and `module` records.

When run as `__main__`, it creates a D-Bus proxy, calls `customized()`, prints the converted result, and prints any `dbus.DBusException`.

## Control Flow

Parsing is line oriented. Empty lines are skipped. Records with `rec[1] == "-D"` are ignored. For each record, the first token selects the output dictionary and fixed positional fields are used to extract values such as boolean active state, login SELinux user/range, user level/range/role, port protocol, node mask/protocol/type, fcontext type or equivalence, and module enabled state.

## State And Persistence

The script has no persistent state. It builds an in-memory dictionary from server output.

## Dependencies And Integration Points

It depends on `sepolicy.sedbus.SELinuxDBus` and the exact output format of `/usr/sbin/semanage export` as returned by `selinux_server.py`. It integrates with the D-Bus server's `customized` method and can feed higher-level migration or display tools.

## Risks

The parser assumes minimum token counts before indexing `rec[1]`, `rec[2]`, and later positions; malformed or changed semanage output can raise `IndexError`. The `interface` branch writes into `cust_dict["login"]`, which appears suspicious because an `interface` dictionary is initialized by the generic branch but not used there. It uses tuple keys for ports and fcontexts, which may complicate serialization.

## Test Signals

Unit tests should feed representative semanage export lines for each record type, including empty lines and `-D` deletes, and assert the dictionary shape. Negative tests should cover malformed records and the `interface` behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/dbus/selinux_client.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/dbus/selinux_server.py -->
# sources/security-integrity/selinux/dbus/selinux_server.py

## Purpose

`selinux_server.py` implements the privileged root-side `org.selinux` D-Bus service used by SELinux configuration tools. It exposes methods for exporting/importing semanage customizations, listing modules, restoring labels, changing enforcement, scheduling relabel, and editing default SELinux config values.

## Important APIs, Types, And Methods

The `selinux_server` class subclasses `dbus.service.Object`. `default_polkit_auth_required` is set to `org.selinux.semanage`, though each method performs explicit authorization through `is_authorized(sender, action_id)`. `is_authorized()` calls `org.freedesktop.PolicyKit1.Authority.CheckAuthorization` for the sender's system bus name.

D-Bus methods include `semanage(buf)`, `customized()`, `semodule_list()`, `restorecon(path)`, `setenforce(value)`, `relabel_on_boot(value)`, `change_default_mode(value)`, and `change_default_policy(value)`. Helper `write_selinux_config(enforcing=None, policy=None)` rewrites `selinux.selinux_path() + "config"` via a `.bck` file and `os.rename()`.

## Control Flow

At startup the script sets `DBusGMainLoop`, creates a GLib main loop, acquires `org.selinux` on the system bus, exports `/org/selinux/object`, and runs forever.

Each method first checks PolicyKit authorization for its specific action ID. Command-backed methods use `Popen`: `semanage()` runs `/usr/sbin/semanage import` with caller-provided input, `customized()` runs `/usr/sbin/semanage export`, and `semodule_list()` runs `/usr/sbin/semodule --list=full`. Direct libselinux-backed methods call `selinux.restorecon()` and `selinux.security_setenforce()`. Config methods validate input and rewrite config.

## State And Persistence

Persistent effects include semanage local policy store changes, module listing reads, filesystem relabeling, runtime enforcing mode changes, creation/removal of `/.autorelabel`, and edits to SELinux config. `write_selinux_config()` preserves unrelated config lines and atomically replaces the original path after writing a backup path.

## Dependencies And Integration Points

The server depends on Python D-Bus bindings, GLib main loop integration, PolicyKit, libselinux Python bindings, `/usr/sbin/semanage`, `/usr/sbin/semodule`, and the D-Bus/PolicyKit/service metadata in the same directory. GUI and client tools can use its D-Bus API instead of invoking privileged commands directly.

## Risks

The service runs as root, so authorization coverage and input validation are critical. `semanage()` passes arbitrary import text to semanage after authorization; this is expected but powerful. `restorecon()` accepts any path and runs recursively. `setenforce()` does not restrict integer values before passing to libselinux. `write_selinux_config()` does not preserve file mode/ownership explicitly and has no fsync/error recovery. PolicyKit errors are not handled separately from denial. `change_default_policy()` restricts names with a regex and requires a directory, which is a useful boundary.

## Test Signals

Tests should mock PolicyKit and command execution to verify authorization gates, command arguments, error propagation, and config rewrite behavior. Integration tests should verify installed action IDs, D-Bus method signatures, denial for unauthorized callers, and successful changes for authenticated admin callers in a controlled SELinux test environment.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/dbus/selinux_server.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/gui/Makefile -->
# sources/security-integrity/selinux/gui/Makefile

## Purpose

This Makefile builds and installs the `system-config-selinux` GUI, its policy generation GUI, Python page modules, UI files, icons, desktop files, man pages, translations, and PolicyKit launcher metadata.

## Targets And Flow

Variables define install roots such as `PREFIX`, `BINDIR`, `SHAREDIR`, `DATADIR`, `MANDIR`, and `DESKTOPDIR`. `TARGETS` lists Python pages, UI files, images, and supporting modules. `all` depends on targets plus entry scripts and delegates to `po`. `install` creates directories, installs executable scripts and wrappers, copies target resources, installs man pages including localized man pages when language directories exist, installs pixmaps and hicolor icons, installs desktop entries, installs `org.selinux.config.policy`, and delegates translation install to `po`.

`clean` delegates to `po`; `relabel` and `test` are placeholders.

## State And Persistence

Installed state spans executable commands under `bin`, shared Python/UI resources under `share/system-config-selinux`, icons and pixmaps under `share`, desktop entries, man pages, translations, and PolicyKit pkexec metadata.

## Dependencies And Integration Points

It depends on make, install utilities, the files listed in `TARGETS`, language directories, and the `po` submake. It integrates with the GUI Python modules in this subset and with PolicyKit through `org.selinux.config.policy`.

## Risks

The target list must stay synchronized with actual GUI modules and UI files. Leading `-` on `mkdir` commands can hide directory creation failures. Globbing `*.desktop` can fail or install unintended files depending on the directory contents. There is no validation of Python dependencies or UI object IDs at install time.

## Test Signals

Packaging tests should verify all target files install to expected locations, entry scripts are executable, icons and desktop files are present, translations install under `LC_MESSAGES`, and the pkexec policy path matches the installed GUI script.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/gui/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/gui/booleansPage.py -->
# sources/security-integrity/selinux/gui/booleansPage.py

## Purpose

`booleansPage.py` implements the GTK page for viewing, filtering, toggling, deleting, and reverting SELinux booleans in `system-config-selinux`.

## Important APIs, Types, And Methods

`Modifier` and `Boolean` are tiny state wrappers, but the page primarily uses GTK `ListStore`, `TreeView`, `CellRendererToggle`, and `CellRendererText`. Columns are `ACTIVE`, `MODULE`, `DESC`, and `BOOLEAN`. The page uses `seobject.booleanRecords()` for reads and command-line tools for writes.

Key methods are `load(filter)`, `match(key, filter)`, `boolean_toggled(widget, row)`, `deleteDialog()`, `on_revert_clicked()`, `on_local_clicked()`, `filter_changed()`, `wait()`, `ready()`, and `error()`.

## Control Flow

Initialization obtains widgets from the UI object, wires filter events, sets up columns and sorting, configures the toggle renderer, and calls `load()`. `load()` rebuilds the store from `booleanRecords().get_all(self.local)`, filtering by boolean name, category, or description. Toggling a row immediately updates the model, runs `/usr/sbin/setsebool -P name value`, reloads the store, and restores the cursor. Delete and revert use `semanage boolean -d` and `semanage boolean --deleteall`.

## State And Persistence

UI state includes the current filter, local/customized mode, cursor state, and the list store. Persistent SELinux state changes are made by `setsebool -P` and `semanage boolean` commands, modifying the local policy store.

## Dependencies And Integration Points

The page depends on PyGObject GTK/GDK, `seobject`, `semanagePage.idle_func`, gettext, `/usr/sbin/setsebool`, and `semanage`. It integrates with a Glade/GTK UI that must provide object IDs such as `mainWindow`, `booleansFilter`, `booleansView`, and `booleanRevertButton`.

## Risks

Command strings interpolate boolean names without shell quoting, relying on trusted boolean names from SELinux policy. Broad `except` blocks in gettext and `match()` can hide errors. The UI updates the checkbox before command success and then reloads, which is acceptable but can briefly show failed state. `deleteDialog()` and revert operations require privileges and surface failures through dialogs.

## Test Signals

Unit tests can mock `seobject.booleanRecords` and `getstatusoutput` to verify filtering, local-mode toggling, command generation, and reload behavior. GUI integration tests should verify columns, sorting, search, and error dialogs for failed commands.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/gui/booleansPage.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/gui/domainsPage.py -->
# sources/security-integrity/selinux/gui/domainsPage.py

## Purpose

`domainsPage.py` implements the GUI page for listing SELinux entrypoint domains and toggling per-domain permissive mode.

## Important APIs And Methods

The `domainsPage` class extends `semanagePage`. It uses `sepolicy.get_all_entrypoint_domains()` to seed domain names, `semodule -l` to infer installed permissive modules, and `semanage permissive -a/-d` to add or remove permissive domain modules.

Key methods are `get_modules()`, `load(filter)`, `itemSelected(selection)`, `add()`, `delete()`, and dialog pass-throughs `addDialog()`/`deleteDialog()`.

## Control Flow

Initialization builds a two-column GTK model for domain name and mode, wires filter events and selection changes, stores permissive/enforcing buttons, loads all entrypoint domains, and populates the view. `load()` compares each domain to installed modules named `permissive_<domain>_t` and displays "Permissive" when present. Selection changes enable either the permissive or enforcing button. `add()` runs `semanage permissive -a <domain>_t`; `delete()` runs `semanage permissive -d <domain>_t`.

## State And Persistence

The store reflects current domain permissive status. Persistent state changes are semanage permissive module additions/removals in the SELinux policy store.

## Dependencies And Integration Points

It depends on GTK, `sepolicy`, `semanagePage`, `semodule`, and `semanage`. UI IDs include `domainsFilterEntry`, `permissiveButton`, and `enforcingButton`.

## Risks

`get_modules()` uses `os.popen("semodule -l")` and the add/delete methods build shell command strings. Domain names originate from policy data and are expected to be safe, but shell invocation remains a boundary. Broad `except: pass` in `load()` can hide command or parsing failures. `sort_int` is not relevant here but inherited page behavior may affect selection.

## Test Signals

Tests should mock domain lists and module output to verify permissive detection. Command tests should assert correct semanage calls and button sensitivity transitions for permissive and enforcing states.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/gui/domainsPage.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/gui/fcontextPage.py -->
# sources/security-integrity/selinux/gui/fcontextPage.py

## Purpose

`fcontextPage.py` implements the GTK page for viewing and editing SELinux file context mappings.

## Important APIs, Types, And Methods

The local `context` class splits a displayed context string into type and MLS components. `fcontextPage` extends `semanagePage` and uses `seobject.fcontextRecords()` for reads plus `semanage fcontext` commands for writes. Columns are file specification, SELinux file type/range, and file type option.

Key methods are `load(filter)`, `match(fcon_dict, k, filter)`, `dialogInit()`, `dialogClear()`, `add()`, `modify()`, and `delete()`.

## Control Flow

Initialization creates a three-column view, loads fcontext records, populates the file type combo from `seobject.file_type_str_to_option`, and stores dialog entries. `load()` reads all records, optionally sorting keys, filters by tuple and context values, formats type/range with `seobject.translate()`, and selects the first row. Dialog initialization locks the file spec and file type for existing entries and splits the selected context into type/range fields. Add/modify/delete construct `semanage fcontext` commands with `-a`, `-m`, or `-d`.

## State And Persistence

The UI store mirrors fcontext records. Persistent changes are made to local semanage fcontext configuration. MLS/range input defaults to `s0` for new entries.

## Dependencies And Integration Points

It depends on GTK, `seobject`, `semanagePage`, `semanage`, and UI IDs for `fcontextView`, filter entry, text entries, and combo box. It integrates with restorecon workflows indirectly because changed mappings need relabeling to affect files.

## Risks

The `match()` method reuses variable `k` inside loops and then indexes `fcon_dict[k]` after `k` may have become a string element rather than the original tuple, so filtering can silently fail under the broad `except`. Command strings quote file specs but not type or MLS values. Incorrect user input can be passed to semanage and reported through dialogs.

## Test Signals

Tests should cover loading and filtering of tuple keys, dialog setup for contexts with and without MLS parts, combo population, and exact semanage command construction for add/modify/delete. A focused test for `match()` would expose the variable shadowing behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/gui/fcontextPage.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/gui/loginsPage.py -->
# sources/security-integrity/selinux/gui/loginsPage.py

## Purpose

`loginsPage.py` implements the GUI page for mapping Linux login names to SELinux users and MLS/MCS ranges.

## Important APIs And Methods

`loginsPage` extends `semanagePage`, uses `seobject.loginRecords()` to read login mappings and `seobject.seluserRecords()` to populate possible SELinux users. It writes changes through `semanage login`.

Important methods are `load(filter)`, `__dialogSetup()`, `dialogInit()`, `dialogClear()`, `add()`, `modify()`, and `delete()`.

## Control Flow

Initialization creates a three-column store for login name, SELinux user, and range, loads records, and stores dialog widgets. `load()` reads mappings, translates ranges, filters against login/user/range values, and selects the first row. `__dialogSetup()` lazily builds the SELinux user combo, omitting `system_u` and defaulting to `user_u`. Dialog initialization fills fields from the selected row and disables editing of existing login names. Add/modify/delete call `semanage login` with the selected user and range.

## State And Persistence

The page keeps UI store state and a `firstTime` flag for combo setup. Persistent changes are semanage login mappings. The code protects required `root` and `__default__` mappings from deletion.

## Dependencies And Integration Points

It depends on GTK, `seobject`, `semanagePage`, gettext, and `semanage`. UI IDs include `loginsNameEntry`, `loginsSelinuxUserCombo`, and `loginsMLSEntry`.

## Risks

Command strings interpolate login names, SELinux users, and ranges without shell quoting. `__dialogSetup()` assumes `user_u` exists and that the combo has at least one row. Broad gettext fallback hides localization issues. Deleting or modifying mappings requires privileges and may fail for policy-specific reasons surfaced only as command output.

## Test Signals

Tests should mock login and seluser records to verify filtering, default combo selection, delete protection for required mappings, range defaulting to `s0`, and semanage command strings for add/modify/delete.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/gui/loginsPage.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/gui/modulesPage.py -->
# sources/security-integrity/selinux/gui/modulesPage.py

## Purpose

`modulesPage.py` implements the GUI page for listing, installing, removing, and audit-toggling SELinux policy modules.

## Important APIs And Methods

`modulesPage` extends `semanagePage`. It uses `Popen("semodule -lfull", shell=True)` to list modules, `semodule -X <priority> -r <module>` to remove modules, `semodule -i <file>` to install modules, `semodule -DB` to disable dontaudit rules, `semodule -B` to rebuild and restore audit behavior, and `selinux.selinux_getpolicytype()` to read policy type.

Key methods are `load(filter)`, `sort_int()`, `new_module()`, `delete()`, `enable_audit()`, `disable_audit()`, `addDialog()`, and `add(file)`.

## Control Flow

Initialization builds a three-column model for module name, priority, and kind; wires filter, audit, and new-module buttons; sets a custom sort function for priority; reads policy type; and loads module data. `load()` parses each `semodule -lfull` line into priority/module/kind, filters, and inserts rows. `addDialog()` opens a file chooser limited to `*.pp`, and `add()` installs the selected module. `new_module()` launches `selinux-polgengui`.

## State And Persistence

UI state includes the module list and `audit_enabled` flag. Persistent state changes include module installation/removal and semodule rebuilds. Audit toggling changes whether dontaudit rules are active in the loaded policy until rebuilt.

## Dependencies And Integration Points

The page depends on GTK, `selinux`, `semanagePage`, `semodule`, and `selinux-polgengui`. It integrates with the policy generation UI and with package-installed module files.

## Risks

`sort_int()` appears to read both `p1` and `p2` from `iter1`, so numeric priority sorting will always compare equal. `load()` uses shell execution and broad `except: pass`, hiding parse or command failures. Removal builds a shell string from module and priority values parsed from command output. Installing modules executes a user-selected file path through argument-list `Popen`, which is safer. Audit button label changes before checking command success, so failure can leave misleading UI state.

## Test Signals

Tests should verify parsing of `semodule -lfull`, filtering, add/remove command calls, audit toggle behavior on success and failure, file chooser filtering, and a regression test for the `sort_int()` iterator bug.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/gui/modulesPage.py -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/gui/org.selinux.config.policy -->
# sources/security-integrity/selinux/gui/org.selinux.config.policy

## Purpose

This PolicyKit policy file authorizes launching the full `system-config-selinux` GUI through pkexec.

## Behavior

It defines action `org.selinux.config.pkexec.run`, describes the need to run system-config-selinux, denies arbitrary and inactive users, requires active users to authenticate as admin, and annotates the executable path as `/usr/share/system-config-selinux/system-config-selinux.py` with GUI allowance enabled.

## State And Persistence

Installed under `share/polkit-1/actions`, it persists pkexec authorization metadata for the GUI launcher.

## Dependencies And Integration Points

It depends on PolicyKit, pkexec annotations, and the install path used by `gui/Makefile`. It integrates with desktop launchers or wrapper scripts that invoke this action.

## Risks

The DTD URL uses `PolicyKit/1/policyconfig.dtd`, while the D-Bus policy file uses `PolicyKit/Policy Configuration 1.0`; packaging should ensure the form is accepted by target PolicyKit versions. The annotated path must match installation. Allowing GUI pkexec is intentional but increases the importance of GUI input validation because the application can run privileged.

## Test Signals

Tests should verify pkexec can locate the action, prompts for admin authentication, launches the installed script, and fails cleanly if the path is absent.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/gui/org.selinux.config.policy -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/gui/po/Makefile -->
# sources/security-integrity/selinux/gui/po/Makefile

## Purpose

This Makefile builds, refreshes, installs, and reports on gettext translation catalogs for the GUI package.

## Targets And Flow

Variables define `NLSPACKAGE=gui`, `POTFILE=gui.pot`, install helpers, locale destination, and gettext tools. `PO_LINGUAS` is discovered from `*.po`; `LINGUAS` can limit the build; otherwise all discovered languages are built. `all` builds `.mo` files. `$(POTFILE)` runs `xgettext` over files listed in `POTFILES`. `refresh-po` merges each `.po` with the pot file. `clean` removes `.mo`, backups, `.depend`, and `tmp`. `install` places compiled catalogs as `selinux-gui.mo` under each language's `LC_MESSAGES`. `report` runs `msgfmt --statistics`.

## State And Persistence

Build outputs are `.mo` files in the source directory. Installed state is locale catalog files under `$(PREFIX)/share/locale/<lang>/LC_MESSAGES/selinux-gui.mo`.

## Dependencies And Integration Points

It depends on gettext tools `xgettext`, `msgmerge`, and `msgfmt`, a `POTFILES` manifest, and the parent GUI Makefile. Runtime Python modules use gettext domain `selinux-gui`, matching the installed catalog name.

## Risks

If `POTFILES` is stale, strings will be missed. The package variable is `gui` while the installed message catalog is `selinux-gui.mo`; this is intentional through the install rule but can confuse maintainers. `LINGUAS` filtering is make-pattern based and should be tested for partial language names.

## Test Signals

Useful checks include successful `make all`, `make report`, installing catalogs for selected `LINGUAS`, and runtime gettext lookup of translated GUI strings.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/gui/po/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/gui/polgen.ui -->
# sources/security-integrity/selinux/gui/polgen.ui

## Purpose

`polgen.ui` is a GtkBuilder UI definition for the SELinux Policy Generation Tool. It defines the wizard-like interface used by `selinux-polgengui` to gather application/user type, executable/name, transition roles, network permissions, common capabilities, managed files/directories, booleans, and output directory.

## Important Objects And Signals

Top-level objects include `about_dialog`, `boolean_dialog`, `filechooserdialog`, and `main_window`. The main window contains a left-positioned `GtkNotebook` with tabs hidden, making it behave as a wizard controlled by `back_button`, `forward_button`, and `cancel_button`.

Important input widgets include policy type radio buttons (`init_radiobutton`, `dbus_radiobutton`, `inetd_radiobutton`, `cgi_radiobutton`, `user_radiobutton`, `sandbox_radiobutton`, user role radio buttons, and `root_user_radiobutton`), entries such as `exec_entry`, `name_entry`, `init_script_entry`, network port entries, `output_entry`, tree views for existing users/transitions/admins/roles/write paths/booleans, and checkboxes for TCP/UDP permissions and common access such as syslog, tmp, pam, uid, dbus, audit, terminal, and mail.

Signals bind several buttons to controller methods expected in the Python code: `on_exec_select_clicked`, `on_init_script_select_clicked`, `on_add_clicked`, `on_add_dir_clicked`, `on_delete_clicked`, `on_add_boolean_clicked`, and `on_delete_boolean_clicked`.

## Control Flow

The UI itself is declarative. Runtime flow is driven by the controller loading this file, advancing the hidden-tab notebook, reading widget state, and handling button signals. The layout starts with policy type selection, moves through name/executable selection and role/domain choices, then collects inbound/outbound network rules, common permissions, managed file paths, booleans, and output directory.

## State And Persistence

Widget state is transient until the controller generates policy files. The file chooser allows multiple hidden file selections. Text labels are marked translatable where user-facing. No persistent policy state is stored in this XML.

## Dependencies And Integration Points

The file depends on GTK/GtkBuilder object classes from the older GTK stack (`GtkVBox`, `GtkHBox`, `GtkTable`, stock buttons/images). It integrates with `polgengui.py` or equivalent controller code through exact object IDs and signal handler names, and with gettext through translatable properties.

## Risks

The UI is large and ID-sensitive; renaming widgets breaks controller lookups. It uses deprecated GTK classes and stock items, which can complicate GTK version migration. Hidden notebook tabs make controller navigation correctness important. Several labels contain `%s` placeholders, so controller code must set them safely and translators must preserve placeholders.

## Test Signals

UI tests should load the file with GtkBuilder, assert all controller-required object IDs and signal handlers exist, navigate every notebook page, and verify that tree views/buttons/entries needed by policy generation can be accessed. Translation checks should validate placeholder preservation in marked strings.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/gui/polgen.ui -->
