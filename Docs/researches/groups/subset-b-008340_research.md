# Research Group subset-b-008340

This grouped report covers keyutils keyctl revoke/search/session/show/supports/timeout/unlink/update/watch tests, the shared keyutils test harness, keyutils watch queue ABI definitions, and libcap Go/contrib capability tooling. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/revoke/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/revoke/noargs/runtest.sh

## Purpose
Negative argument-count test for `keyctl revoke`. It validates command-line usage handling rather than kernel revocation semantics.

## Important APIs, Types, And Functions
Uses `expect_args_error keyctl revoke` for no arguments and for two arguments. `marker` records each phase and `toolbox_report_result` reports the shared `result` state.

## Control Flow
Initializes `result=PASS`, truncates `$OUTPUTFILE`, executes two invalid invocations, and finishes by appending the final status banner.

## State And Persistence Behavior
No keys are created. Persistent effects are limited to the per-test output log and optional RHTS result reporting.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
It only checks exit status 2 through `expect_args_error`; it does not assert exact usage text. A CLI that changes bad-argument exit codes would fail even if the kernel path is unchanged.

## Test Signals
Useful signals are no-argument and too-many-argument failures for the `revoke` subcommand.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/revoke/noargs/runtest.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/revoke/valid/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/revoke/valid/runtest.sh

## Purpose
Functional revoke test for a user key and a keyring. It confirms that revoked objects remain referenced but reject describe, read, list, and further validation operations with `EKEYREVOKED`.

## Important APIs, Types, And Functions
Uses `create_keyring`, `create_key`, `list_keyring`, `describe_key`, `print_key`, `revoke_key`, and `unlink_key`, plus `expect_keyring_rlist`, `expect_key_rdesc`, `expect_payload`, and `expect_error`.

## Control Flow
Creates a session-attached keyring, adds a `user` key, verifies listing, description, and payload, revokes the key, checks revoked-key failures, unlinks it, then revokes and validates failures on the keyring itself.

## State And Persistence Behavior
Mutates the kernel session keyring by adding one keyring and one key, then revoking and unlinking them. The revoked state is durable within key lifetime; log state is persisted in `$OUTPUTFILE`.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
The test assumes revocation returns `EKEYREVOKED` consistently for reads/describes/lists. Cleanup depends on unlinking revoked objects still being allowed.

## Test Signals
Signals include successful pre-revoke visibility, `EKEYREVOKED` after key revoke, and `EKEYREVOKED` after keyring revoke.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/revoke/valid/runtest.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/search/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/search/bad-args/runtest.sh

## Purpose
Bad-argument and invalid-search test for `keyctl search`. It covers malformed types/descriptions, invalid destination key IDs, and attempting to search a non-keyring key.

## Important APIs, Types, And Functions
Uses `search_for_key --fail`, `expect_error`, `create_key`, `unlink_key`, and version helpers such as `kernel_at_or_later_than` for MIPS/kernel-specific overlong description behavior.

## Control Flow
Runs invalid key type cases, max/overlong type and description cases, a bad destination ID case, creates a plain user key, confirms searching it as a keyring returns `ENOTDIR`, then unlinks it.

## State And Persistence Behavior
Creates one temporary user key in the session keyring. Otherwise state is transient command failure output plus `$OUTPUTFILE` diagnostics.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
Some overlong description assertions are gated for older MIPS kernels due to known kernel bugs. The distinction between `ENOKEY`, `EINVAL`, `EPERM`, and `ENOTDIR` is version and kernel-policy sensitive.

## Test Signals
Signals are exact errno mapping for invalid type, invalid length, invalid key ID, and non-keyring search roots.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/search/bad-args/runtest.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/search/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/search/noargs/runtest.sh

## Purpose
Negative argument-count test for `keyctl search`.

## Important APIs, Types, And Functions
Uses `expect_args_error keyctl search` for zero, one, two, and five arguments, with markers for each arity.

## Control Flow
Initializes the harness result, executes each invalid arity, and reports the final result.

## State And Persistence Behavior
No key objects are created. State is only test log output.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
Only CLI arity/exit-status behavior is covered; semantic search errors are covered in sibling tests.

## Test Signals
Signals are exit-status 2 for too-few and too-many `search` command arguments.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/search/noargs/runtest.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/search/valid/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/search/valid/runtest.sh

## Purpose
Comprehensive valid-search behavior test for keyrings, duplicate descriptions, nested keyrings, permissions, linking, revocation, and attach-on-search.

## Important APIs, Types, And Functions
Uses `create_keyring`, `create_key`, `search_for_key --expect/--fail`, `link_key`, `unlink_key`, `set_key_perm`, `revoke_key`, `print_key`, and `expect_error`.

## Control Flow
Builds two keyrings, creates overlapping `user:lizard` keys, searches from session and direct keyrings, attaches search results to another keyring, links/unlinks keyrings to change traversal, manipulates search permissions, and finally revokes a key to check search failure semantics.

## State And Persistence Behavior
Exercises persistent kernel keyring topology: links between keyrings, duplicate keys by type/description, permission masks, and revoked key state. The script cleans up by unlinking the main keyring from `@s`.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
Search behavior around revoked keys differs on old kernels and RHEL7 backports, so expected errno is gated. Permission masks are hard-coded and can be sensitive to key permission ABI changes.

## Test Signals
Signals include selected key ID precedence, attach-to-destination notification, keyring traversal visibility, permission-driven `EACCES`/`ENOKEY`, and post-revoke `EKEYREVOKED` or legacy `ENOKEY`.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/search/valid/runtest.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/session/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/session/bad-args/runtest.sh

## Purpose
Bad-argument test for creating a new session keyring with invalid names.

## Important APIs, Types, And Functions
Uses `new_session --fail`, `expect_error`, `maxdesc`, and kernel/architecture version helpers.

## Control Flow
Checks empty keyring names with `EINVAL`; conditionally checks an overlong name on kernels/architectures where the bug is not expected.

## State And Persistence Behavior
No lasting key state is intentionally retained; child session creation attempts fail and output is logged.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
The overlong-name case is skipped on pre-3.19 MIPS/MIPS64 because kernel behavior is known to be buggy.

## Test Signals
Signals are `EINVAL` for empty and supported overlong keyring names.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/session/bad-args/runtest.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/session/valid/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/session/valid/runtest.sh

## Purpose
Valid `keyctl session` test for anonymous and named session keyrings.

## Important APIs, Types, And Functions
Uses `new_session`, `keyctl rdescribe @s`, `expect_key_rdesc`, distro/version helpers, and output parsing with `tail`, `head`, and `expr`.

## Control Flow
On old RHEL it checks anonymous session creation. It always creates a named session `qwerty`, validates the raw session keyring description, and verifies that `Joined session keyring: <id>` was printed.

## State And Persistence Behavior
Creates child session keyrings for the subprocess command. The parent test process state is not replaced because `keyctl session` runs the supplied command in the new session.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
Anonymous-session coverage is distro-gated. The test depends on stable human-readable `keyctl session` output format and raw-description naming.

## Test Signals
Signals are the expected session keyring description pattern and visible joined keyring ID.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/session/valid/runtest.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/session/valid2/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/session/valid2/runtest.sh

## Purpose
Valid `keyctl new_session` test that replaces the running script's session keyring and confirms IDs change.

## Important APIs, Types, And Functions
Uses `id_key --to`, `new_session_to_parent`, `describe_key`, and `expect_key_rdesc`.

## Control Flow
Captures the original session keyring ID, creates an anonymous replacement and checks the ID differs, then creates a named replacement `lizard` and checks it differs from both earlier IDs.

## State And Persistence Behavior
Mutates the current process/session keyring association rather than just a child process. The session keyring persists for the remainder of the test process.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
The script assumes the session keyring ID changes on every successful replacement and that names `_ses` and `lizard` appear in raw descriptions.

## Test Signals
Signals are changed keyring IDs and matching anonymous/named keyring descriptions.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/session/valid2/runtest.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/show/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/show/noargs/runtest.sh

## Purpose
Default `keyctl show` test. It verifies that running without arguments shows the current session keyring in the expected textual layout.

## Important APIs, Types, And Functions
Invokes `keyctl show` directly, uses `wc`, `sed`, `grep`, `cut`, `awk`, `expr`, and shared `failed` handling.

## Control Flow
Runs `keyctl show`, requires enough output lines, checks the third line is `Session Keyring`, and verifies the first keyring listed is the RHTS/keyctl session keyring.

## State And Persistence Behavior
Does not create keys itself; it observes the session keyring created by `prepare.inc.sh`. State is output-format validation.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
Highly sensitive to `keyctl show` output layout, line numbers, field positions, and session naming convention.

## Test Signals
Signals are nonzero line count, the `Session Keyring` header, and an expected keyring name prefix.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/show/noargs/runtest.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/show/valid/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/show/valid/runtest.sh

## Purpose
Valid `keyctl show` test for nested keyrings and optional explicit-root display.

## Important APIs, Types, And Functions
Uses `create_keyring`, direct `keyctl show`, version helpers, `wc`, `tail`, `cut`, and shell loops.

## Control Flow
Creates seven nested keyrings under `@s`, shows the whole session tree, optionally checks line count and key ID order, and for keyutils >=1.5.4 checks `keyctl show <keyring>` for each nested root.

## State And Persistence Behavior
Mutates session keyring topology with a chain of keyrings. It does not explicitly unlink them, relying on session cleanup after the test.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
Output formatting checks are gated by RHEL/keyutils version. Key ID list comparison assumes traversal order matches creation chain.

## Test Signals
Signals are successful show, expected number of lines, matching key ID order, and decreasing subtree sizes for explicit roots.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/show/valid/runtest.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/supports/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/supports/bad-args/runtest.sh

## Purpose
Negative arity test for `keyctl supports`.

## Important APIs, Types, And Functions
Uses `expect_args_error keyctl support` for two and three arguments. The path name says `supports`, but the CLI subcommand used here is `support`.

## Control Flow
Runs invalid two-argument and three-argument invocations and reports the shared result.

## State And Persistence Behavior
No kernel key state is changed.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
This is only CLI usage validation. It does not check the newer capability-query semantics.

## Test Signals
Signals are bad-arity exit status 2 for `keyctl support`.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/supports/bad-args/runtest.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/supports/valid/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/supports/valid/runtest.sh

## Purpose
Valid feature-query test for `keyctl supports`.

## Important APIs, Types, And Functions
Uses the toolbox `supports` wrapper, including the `--unrecognised` mode that expects exit status 3.

## Control Flow
First lists supported capabilities, then queries an unrecognized capability name to confirm the wrapper accepts the expected nonzero status.

## State And Persistence Behavior
No key objects are created; it reads keyutils/kernel feature support and writes log output.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
Coverage is shallow: it does not assert specific capability variables, only command success and the unrecognized-query exit code.

## Test Signals
Signals are successful list operation and expected exit status for an unknown capability query.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/supports/valid/runtest.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/timeout/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/timeout/bad-args/runtest.sh

## Purpose
Bad-key-ID and missing-key test for `keyctl timeout`.

## Important APIs, Types, And Functions
Uses `timeout_key --fail`, `create_key`, `unlink_key --wait`, and `expect_error`.

## Control Flow
Checks key ID zero returns `EINVAL`, creates a user key, unlinks and waits for it to be unreachable, then checks setting timeout on the stale ID returns `ENOKEY`.

## State And Persistence Behavior
Creates and destroys one temporary user key. Lazy key destruction is handled through the toolbox wait path.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
The stale ID test depends on key garbage collection and the helper's wait loop making the ID unusable before timeout is attempted.

## Test Signals
Signals are `EINVAL` for key ID zero and `ENOKEY` for a destroyed key ID.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/timeout/bad-args/runtest.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/timeout/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/timeout/noargs/runtest.sh

## Purpose
Negative argument-count test for `keyctl timeout`.

## Important APIs, Types, And Functions
Uses `expect_args_error keyctl timeout` for zero, one, and three arguments.

## Control Flow
Runs invalid arities and records final result.

## State And Persistence Behavior
No key state is created.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
Only CLI arity behavior is covered; semantic timeout behavior is in sibling tests.

## Test Signals
Signals are exit-status 2 for invalid timeout argument counts.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/timeout/noargs/runtest.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/timeout/valid/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/timeout/valid/runtest.sh

## Purpose
Valid timeout semantics test for keys and keyrings, including expiration, revoked-key behavior, and expired-key operation failures.

## Important APIs, Types, And Functions
Uses `create_keyring`, `create_key`, `timeout_key`, `sleep_at_least`, `print_key`, `revoke_key`, `invalidate_key`, `list_keyring`, `describe_key`, `unlink_key`, and version-gated `expect_error`.

## Control Flow
Creates a key, proves a long timeout does not break reads, sets a short timeout and waits, verifies expired read/revoke/timeout failures, repeats with a revoked key, then expires the keyring and checks list/describe/timeout/invalidate/revoke failures.

## State And Persistence Behavior
Persists expiry timers in kernel key objects. The test intentionally waits for wall-clock expiry and relies on the session keyring to hold references until cleanup.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
Timing is inherently race-prone, mitigated by `sleep_at_least`. Expected expired-key errno differs on older kernels and RHEL7 backports.

## Test Signals
Signals include successful pre-expiry reads, `EKEYEXPIRED` or legacy `ENOKEY` after expiry, `EKEYREVOKED` after revocation, and expired-keyring failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/timeout/valid/runtest.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/unlink/all/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/unlink/all/runtest.sh

## Purpose
Tree-wide unlink test for keyutils versions supporting one-argument unlink-all behavior.

## Important APIs, Types, And Functions
Uses `keyutils_at_or_later_than`, `create_keyring`, `create_key`, `link_key`, `unlink_key`, `expect_unlink_count`, `list_keyring`, and `expect_keyring_rlist`.

## Control Flow
Creates one keyring and key, verifies normal unlink, then creates twenty subkeyrings all linking the same key. A one-argument `unlink_key $keyid` removes all links across the tree and reports the count.

## State And Persistence Behavior
Builds and then tears down a larger kernel keyring graph. The key's link count is the core state under test.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
Skipped for keyutils older than 1.5. Link-count expectations are exact and would break if search scope or output wording changes.

## Test Signals
Signals are zero links removed when already detached, twenty-one links removed for the tree case, and absence from all keyrings afterward.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/unlink/all/runtest.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/unlink/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/unlink/bad-args/runtest.sh

## Purpose
Bad-argument and invalid-object test for `keyctl unlink`.

## Important APIs, Types, And Functions
Uses `unlink_key --fail`, `create_key`, `unlink_key --wait`, and `expect_error`.

## Control Flow
Checks invalid source and keyring IDs, creates a non-keyring user key and uses it as a keyring argument to get `ENOTDIR`, then destroys the key and checks both source and destination stale-ID failures.

## State And Persistence Behavior
Creates one temporary user key and removes it. It depends on kernel key lifetime and unlink wait behavior.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
The non-keyring and stale-ID cases depend on exact errno mapping. Lazy destruction could otherwise make stale ID checks flaky.

## Test Signals
Signals are `EINVAL`, `ENOTDIR`, and `ENOKEY` from invalid unlink targets.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/unlink/bad-args/runtest.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/unlink/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/unlink/noargs/runtest.sh

## Purpose
Negative argument-count test for `keyctl unlink`.

## Important APIs, Types, And Functions
Uses `expect_args_error keyctl unlink`; the one-argument invalid case is only expected for keyutils older than 1.5 because newer versions support unlink-all.

## Control Flow
Checks no arguments, conditionally one argument, and three arguments.

## State And Persistence Behavior
No key state is created.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
Version-gated behavior is central because one argument changed from invalid syntax to a valid operation.

## Test Signals
Signals are bad-arity exit status for unsupported arities.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/unlink/noargs/runtest.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/unlink/valid/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/unlink/valid/runtest.sh

## Purpose
Valid unlink behavior test for removing keys and keyrings from a keyring.

## Important APIs, Types, And Functions
Uses `create_keyring`, `create_key`, `list_keyring`, `unlink_key --wait`, `expect_keyring_rlist`, `expect_error`, and direct `keyctl show`.

## Control Flow
Creates a keyring and key, unlinks the key and verifies repeat unlink fails, then creates twenty keys and twenty keyrings, validates membership, unlinks each entry, and confirms the keyring is empty.

## State And Persistence Behavior
Exercises kernel keyring link membership and lazy destruction. Final cleanup unlinks the top keyring from the session keyring.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
Exact membership checks assume `rlist` output is stable. The test creates many objects and can be affected by key quota limits.

## Test Signals
Signals are membership before unlink, `ENOKEY` on repeated unlink, and empty `rlist` after deleting all contents.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/unlink/valid/runtest.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/update/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/update/bad-args/runtest.sh

## Purpose
Bad-object test for `keyctl update`.

## Important APIs, Types, And Functions
Uses `update_key --fail`, `create_key`, `unlink_key --wait`, and `expect_error`.

## Control Flow
Confirms updating the session keyring returns `EOPNOTSUPP`, invalid key ID zero returns `EINVAL`, and updating a destroyed user key returns `ENOKEY`.

## State And Persistence Behavior
Creates and destroys one temporary user key. No lasting key payload is retained.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
The test assumes keyrings do not support update and that stale ID cleanup completes before the final update attempt.

## Test Signals
Signals are `EOPNOTSUPP`, `EINVAL`, and `ENOKEY` for unsupported, invalid, and stale update targets.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/update/bad-args/runtest.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/update/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/update/noargs/runtest.sh

## Purpose
Negative argument-count test for `keyctl update`.

## Important APIs, Types, And Functions
Uses `expect_args_error keyctl update` for zero, one, and three arguments.

## Control Flow
Runs invalid arities and reports the final result.

## State And Persistence Behavior
No key state is created.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
This only verifies CLI usage status, not payload parsing or kernel update behavior.

## Test Signals
Signals are exit-status 2 for bad update argument counts.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/update/noargs/runtest.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/update/userupdate/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/update/userupdate/runtest.sh

## Purpose
Valid user-key update test, including ordinary string payloads and hex-encoded input.

## Important APIs, Types, And Functions
Uses `create_key`, `print_key`, `update_key`, `update_key -x`, `expect_payload`, and `unlink_key`.

## Control Flow
Creates a `user` key with payload `stuff`, reads it back, updates to `lizard`, reads again, updates with spaced hex data, reads `lizardx`, then unlinks the key.

## State And Persistence Behavior
Mutates a single user key payload in the session keyring. Payload state persists until the key is unlinked.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
Only user keys are covered. It does not test binary NUL payloads, large payloads, pupdate, permissions, or quota errors.

## Test Signals
Signals are exact payload transitions from `stuff` to `lizard` to `lizardx`.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/update/userupdate/runtest.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/watch/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/watch/bad-args/runtest.sh

## Purpose
Bad-object and bad-filter test for `keyctl watch` when notification support is available.

## Important APIs, Types, And Functions
Uses `have_notify` gating, `watch_key --fail/--fail2`, `create_key`, `unlink_key --wait`, and `expect_error`.

## Control Flow
Skips if notifications are unavailable. Otherwise it checks invalid key ID zero, stale key ID after unlink, and malformed filter options.

## State And Persistence Behavior
Creates and destroys one user key. Watch command failures should not add lasting watches; output may touch `notify.log` through the toolbox wrapper.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
The test is skipped without notification support. Filter parsing expects specific exit status 2 through `--fail2` but does not assert text.

## Test Signals
Signals are `EINVAL`, `ENOKEY`, and bad-filter exit status for watch setup failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/watch/bad-args/runtest.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/watch/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/watch/noargs/runtest.sh

## Purpose
Negative argument-count and malformed-filter test for `keyctl watch`.

## Important APIs, Types, And Functions
Uses `expect_args_error keyctl watch` and `expect_args_error keyctl watch_key -f 0`.

## Control Flow
Checks no arguments, too many object arguments, and a bad filter option.

## State And Persistence Behavior
No key state is created; only CLI parsing output is logged.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
The last command names `watch_key`, which may be a compatibility alias or typo-sensitive path depending on keyutils CLI behavior.

## Test Signals
Signals are bad-arity and bad-filter usage failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/watch/noargs/runtest.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/prepare.inc.sh -->
# sources/security-integrity/keyutils/tests/prepare.inc.sh

## Purpose
Shared preparation script for the keyutils test tree. It ensures each test runs inside a private session keyring, optionally under a watched session, initializes environment/version variables, and derives feature flags.

## Important APIs, Types, And Functions
Defines `has_kernel_config`, session bootstrap logic around `keyctl watch_session` and `keyctl session`, RHTS integration, `OSDIST`, `OSRELEASE`, `KEYUTILSVER`, `KERNELVER`, `TEST`, and feature booleans such as `have_key_invalidate`, `have_big_key_type`, `have_dh_compute`, `have_restrict_keyring`, and `have_notify`.

## Control Flow
When not called with `--inside-test-session`, it re-execs the current test under a named session keyring. If notification support is present, it also creates watch and GC logs and exposes a watch fd to the child. Inside the session it initializes RHTS or local `$OUTPUTFILE`, detects distro and keyutils version, sources `version.inc.sh`, derives the test name from the working directory, probes feature support, and reads skip flags from the environment.

## State And Persistence Behavior
The script replaces the process with a child running in a new session keyring. It writes `watch.out`, `gc.out`, and `test.out`/RHTS output. Feature flags are shell variables consumed by runtest scripts and `toolbox.inc.sh`.

## Dependencies And Integration Points
Requires `keyctl`, `lsb_release`, optionally `rpm`, RHTS environment scripts, and kernel config files. It integrates with `version.inc.sh`, `toolbox.inc.sh`, and all keyctl test scripts via sourced shell state.

## Risks And Edge Cases
Re-exec argument handling is delicate because `$0` and `$@` are reused. Distro/version detection assumes `lsb_release` and keyutils version output formats. Notification setup changes fd state and creates side logs.

## Test Signals
Signals are successful re-exec into a private session, correct feature variables, and consistent `$TEST` naming for report output.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/prepare.inc.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/runtest.sh -->
# sources/security-integrity/keyutils/tests/runtest.sh

## Purpose
Top-level runner for keyutils tests. It iterates over test directories passed on the command line and invokes each `runtest.sh`.

## Important APIs, Types, And Functions
Uses `AUTOMATED`, `TESTS`, `TEST`, shell `pushd`/`popd`, and direct `bash ./runtest.sh`. It warns when not running as root because some tests need privileged behavior.

## Control Flow
For each requested test path it exports `TEST`, enters the directory, prints a running banner, and executes the local test. In non-automated mode the first failing test stops the suite; in automated mode it continues.

## State And Persistence Behavior
No kernel state is directly changed by this file; child tests do that. It mutates only the `TEST` environment variable and current working directory while dispatching.

## Dependencies And Integration Points
It is the suite dispatcher for the per-directory keyctl tests and relies on each child script sourcing the preparation/toolbox files.

## Risks And Edge Cases
Whitespace in test paths is not handled. Non-automated mode returns on first failure, which is useful for debugging but can hide later failures.

## Test Signals
Signals are child exit status in interactive mode and the presence of per-test banners for automation logs.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/runtest.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/toolbox.inc.sh -->
# sources/security-integrity/keyutils/tests/toolbox.inc.sh

## Purpose
Large shared shell toolbox for keyutils tests. It wraps `keyctl` subcommands, logs commands/output, captures IDs and payloads, checks errno text, validates notifications, and maintains the shared `result` state.

## Important APIs, Types, And Functions
Core helpers include `marker`, `failed`, `expect_args_error`, `toolbox_report_result`, `toolbox_skip_test`, `expect_error`, `create_key`, `create_keyring`, `list_keyring`, `describe_key`, `print_key`, `revoke_key`, `unlink_key`, `update_key`, `search_for_key`, `set_key_perm`, `new_session`, `timeout_key`, `invalidate_key`, `supports`, `watch_key`, and `expect_notification`.

## Control Flow
At source time it detects endianness, computes maximum test strings and page-sized payloads, records quota/GC delay defaults, and defines wrappers. Each wrapper logs the command, executes it with expected exit status, extracts final output lines when needed, stores shell variables via `eval`, calls notification checks on successful mutating operations, and invokes `failed` on mismatches.

## State And Persistence Behavior
The toolbox is the main persistence and observation layer for tests: it appends to `$OUTPUTFILE`, may append to `$watch_log` and `$PWD/notify.log`, adds watches for new keys, and mutates kernel keyrings through wrapped `keyctl` operations. `failed` records diagnostics and sets global `result=FAIL`.

## Dependencies And Integration Points
Depends on `keyctl`, `/proc/key-users`, `/proc/keys`, `file`, `getconf`, `grep`, `awk`, `md5sum`, `date`, and version helpers sourced before it. It integrates with notification support prepared by `prepare.inc.sh`.

## Risks And Edge Cases
Many helpers parse the last line of `$OUTPUTFILE`, so extra command output can break expectations. Error matching depends on English errno strings and alternate legacy messages. Several loops wait for lazy kernel key cleanup and can hang if `/proc/keys` behavior changes. `eval` variable assignment requires trusted variable names from tests.

## Test Signals
Signals are command exit status, exact errno classification, key ID extraction, raw keyring lists, raw descriptions, payload strings, unlink counts, and watch notification records.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/toolbox.inc.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/vercmp.sh -->
# sources/security-integrity/keyutils/tests/vercmp.sh

## Purpose
Command-line tester for the shell version-comparison functions.

## Important APIs, Types, And Functions
Sources `version.inc.sh` and calls `version_less_than` with two user-supplied version strings.

## Control Flow
Validates that two parameters were supplied, compares them, and prints either `<` or `>=`.

## State And Persistence Behavior
No persistent state is changed. It only reads the sourced functions and writes stdout/stderr.

## Dependencies And Integration Points
Used as a small manual/debug harness for `version.inc.sh`, not by normal runtest scripts.

## Risks And Edge Cases
It inherits all parser limitations from `version_less_than` and only reports a boolean less-than relationship.

## Test Signals
Signals are exit code 2 for missing parameters and human-readable comparison output.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/vercmp.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/version.inc.sh -->
# sources/security-integrity/keyutils/tests/version.inc.sh

## Purpose
Shell version-comparison library used by the keyutils tests to gate kernel, RHEL, and keyutils behavior.

## Important APIs, Types, And Functions
Defines `version_less_than`, internal `__version_less_than_dot`, `keyutils_older_than`, `keyutils_at_or_later_than`, `keyutils_newer_than`, `keyutils_at_or_older_than`, `kernel_older_than`, `kernel_at_or_later_than`, `rhel6_kernel_at_or_later_than`, and `rhel7_kernel_at_or_later_than`.

## Control Flow
`version_less_than` splits versions into base and release portions, gives `rc` releases pre-release ordering, and delegates dot-separated numeric/string component comparison to `__version_less_than_dot`. Public wrappers compare against `KEYUTILSVER`, `KERNELVER`, `OSDIST`, and `OSRELEASE`.

## State And Persistence Behavior
No state is persisted; it depends on global variables prepared by `prepare.inc.sh`.

## Dependencies And Integration Points
Used by many tests to handle historical kernel/keyutils differences in errno behavior, argument support, feature availability, and distro backports.

## Risks And Edge Cases
The comparison is shell/string based and can misorder unusual version components. It assumes release separators and `rcN` naming conventions.

## Test Signals
Signals are correct gating of version-sensitive tests such as timeout errno, search overlong descriptions, unlink-all support, and notification capability fallbacks.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/version.inc.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/watch_queue.h -->
# sources/security-integrity/keyutils/watch_queue.h

## Purpose
Local copy of Linux watch queue UAPI definitions used by keyutils notification support.

## Important APIs, Types, And Functions
Defines `O_NOTIFICATION_PIPE`, watch queue ioctl numbers, `watch_notification_type`, metadata subtypes, `struct watch_notification`, filter structs, `struct watch_notification_removal`, key notification subtypes, and `struct key_notification`.

## Control Flow
This is a header-only ABI description. Runtime code includes it to format notification pipes, filters, and key notification records.

## State And Persistence Behavior
No state is held in the header. Its structures describe records delivered by kernel notification pipes.

## Dependencies And Integration Points
Includes `<linux/types.h>` and `<sys/ioctl.h>`. Integrates with keyutils watch/watch_session implementation and the test toolbox notification expectations.

## Risks And Edge Cases
Because this mirrors kernel UAPI, divergence from the running kernel can cause decode/filter mismatches. Bitfield layout and alignment are ABI-sensitive.

## Test Signals
Signals are successful compilation and correct interpretation of key notification types such as instantiated, updated, linked, unlinked, revoked, invalidated, and setattr.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/watch_queue.h -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/Makefile -->
# sources/security-integrity/libcap/Makefile

## Purpose
Top-level libcap makefile. It coordinates building, testing, cleaning, distribution checks, Go module version updates, and release tagging across libcap subprojects.

## Important APIs, Types, And Functions
Targets include `all`, `test`, `sudotest`, `install`, `clean`, `gomods-update`, `distclean`, `release`, `ktest`, `distcheck`, `morgangodoc`, and `morganrelease`. It includes `Make.Rules` and dispatches into `libcap`, `pam_cap`, `go`, `tests`, `progs`, `doc`, and `kdebug`.

## Control Flow
Pattern targets run local no-op `%-here` hooks, then recurse into subdirectories with feature gates for PAM and Go. `distclean` validates Go module versions, exported header versions, and a clean git tree. Release targets create tarballs and signed tags.

## State And Persistence Behavior
Build targets create binaries, libraries, docs, Go sums, tags, and tarballs depending on target. Clean/distclean remove generated artifacts and require repository cleanliness.

## Dependencies And Integration Points
Depends on make, git, gpg, Go, C toolchains, optional PAM, musl, clang, and recursive makefiles throughout libcap.

## Risks And Edge Cases
Release targets are destructive in the sense of creating signed tags and tarballs. `distclean` fails on any ignored or untracked state. Recursive subproject behavior depends on `Make.Rules` feature variables.

## Test Signals
Signals include successful recursive builds/tests, version consistency checks, and `distcheck` matrix coverage across dynamic/static, compiler, PAM, and musl configurations.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/Makefile -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/cap.go -->
# sources/security-integrity/libcap/cap/cap.go

## Purpose
Core Go package implementation for Linux process capabilities. It defines capability sets, runtime ABI discovery, process set/get operations, bounding and ambient vector helpers, and syscall abstraction.

## Important APIs, Types, And Functions
Defines `Value`, `Flag`, `Effective`, `Permitted`, `Inheritable`, `Diff`, `Set`, `header`, `syscaller`, `MaxBits`, `NewSet`, `GetPID`, `GetProc`, `(*Set).SetProc`, `GetBound`, `DropBound`, `GetAmbient`, `SetAmbient`, and `ResetAmbient`.

## Control Flow
Lazy initialization probes `capget` with the newest magic, chooses word count, and discovers runtime maximum capability bits by scanning the bounding set. Getters use read syscalls; writers use the POSIX-semantics syscall path selected by `scwStateSC`. `SetProc`, `DropBound`, ambient changes, and reset operations serialize through launch-aware write-state handling.

## State And Persistence Behavior
`Set` stores compressed bitmaps protected by an RW mutex and optional namespace root UID. Process writes mutate kernel credential state for all OS threads through psx-backed syscalls except during launcher callbacks. Package globals cache ABI magic, word count, and max capability values.

## Dependencies And Integration Points
Uses `syscall`, `unsafe`, `sync`, `sort`, and the package syscall adapters from `syscalls.go`. Other files extend `Set` with flag operations, text, file xattrs, IAB, and launch behavior.

## Risks And Edge Cases
Capability writes are security-sensitive and partial failures can leave bounding/ambient operations only partly applied. Runtime max-bit discovery depends on kernel `prctl` behavior. Thread-state consistency relies on psx/all-thread syscall support and correct launch serialization.

## Test Signals
Signals come from package tests and examples: process set round trips, import/export comparisons, text parsing, IAB operations, and launcher state isolation.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/cap.go -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/cap_examples_test.go -->
# sources/security-integrity/libcap/cap/cap_examples_test.go

## Purpose
Testable examples for the public Go `cap` API. They serve both as documentation and as `go test` output checks for stable text/export behavior.

## Important APIs, Types, And Functions
Examples cover `Set.Fill`, `GetProc`, `NewSet`, `MaxBits`, `IABGetProc`, `NewIAB`, `Set.Export`, `Import`, `SetUID`, `FromText`, and `FromName`.

## Control Flow
Each example constructs or reads capability state, performs a small operation, and prints canonical output where deterministic. Privilege-dependent examples print informative runtime-dependent messages without fixed output.

## State And Persistence Behavior
Most examples are read-only or local `Set` transformations. `ExampleSetUID` can change the process UID if the process has permitted `SETUID`, so it is intentionally guarded by a capability check.

## Dependencies And Integration Points
Imports the public package path `kernel.org/pub/linux/libs/security/libcap/cap` and demonstrates consumer-facing use rather than internal package access.

## Risks And Edge Cases
Runtime-dependent examples do not assert output. `SetUID` is security-sensitive and intentionally exits early without permission.

## Test Signals
Signals are exact output for deterministic examples: empty sets, export bytes, import text, text equivalence, and name lookup.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/cap_examples_test.go -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/cap_file_test.go -->
# sources/security-integrity/libcap/cap/cap_file_test.go

## Purpose
Linux/go1.16 file-capability integration test for reading, writing, and removing `security.capability` xattrs.

## Important APIs, Types, And Functions
Uses `GetProc`, `GetFlag`, `Dup`, `SetFlag`, `SetProc`, `SetFile`, `GetFile`, `Cf`, `os.WriteFile`, `os.Symlink`, and `os.Chmod`.

## Control Flow
Skips if permitted `SETFCAP` is absent. Raises effective `SETFCAP`, creates a temp executable and symlink, asserts symlink writes fail, writes file capabilities to the real file, reads and compares them, removes them with nil `*Set`, then repeats on an unreadable file through the O_PATH fallback.

## State And Persistence Behavior
Temporarily raises process effective `SETFCAP` and restores the old capability set via defer. Persists xattrs on temp files and removes them before exit.

## Dependencies And Integration Points
Requires Linux, Go 1.16, xattr-capable filesystem, and permission to set file capabilities. Exercises `file.go` paths including symlink refusal and O_PATH fallback.

## Risks And Edge Cases
The test is skipped without privilege. It depends on filesystem xattr support and kernel file capability support. Incorrect cleanup could leave file caps in a temp dir until test cleanup.

## Test Signals
Signals are symlink write rejection, successful write/read comparison, successful nil removal, and successful set/read/remove on a chmod-0 file.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/cap_file_test.go -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/cap_test.go -->
# sources/security-integrity/libcap/cap/cap_test.go

## Purpose
Unit tests for core Go capability set logic, text conversion, import/export encoding, IAB behavior, and function-launch state isolation.

## Important APIs, Types, And Functions
Tests `bitOf`, `allMask`, `Value.String`, `FromText`, `Set.String`, `Export`, `Import`, `IABFromText`, `IAB.String`, `IAB.Fill`, `IAB.SetVector`, `FuncLauncher`, `Prctl`, and `Prctlw`.

## Control Flow
The tests force max-bit/word values for mask checks, parse and stringify known text cases, repeatedly mutate sets and validate export/import/text round trips, parse and mutate IAB tuples, read PID 1 capabilities, and run a launcher callback that flips `PR_KEEP_CAPS` without leaking it back.

## State And Persistence Behavior
Most state is in-memory package data. `TestFuncLaunch` mutates process secure state through `Prctlw` but verifies launcher isolation restores the outer process state and then intentionally flips it for the next iteration.

## Dependencies And Integration Points
Exercises internals because tests are in package `cap`. Relies on `/proc` and prctl support for some cases and on the launcher support for the active Go toolchain.

## Risks And Edge Cases
The test modifies package globals and process securebits; defers restore for globals but process prctl state depends on test ordering. Environment without PID 1 status visibility can fail IAB tests.

## Test Signals
Signals are exact canonical text, stable binary export sizes, lossless import/export, IAB round trips, and no privileged-state leak from `FuncLauncher`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/cap_test.go -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/convenience.go -->
# sources/security-integrity/libcap/cap/convenience.go

## Purpose
Convenience APIs for securebits, libcap security modes, UID/GID changes, and prctl wrappers with process-wide POSIX semantics.

## Important APIs, Types, And Functions
Defines `Secbits`, securebit constants, `GetSecbits`, `(Secbits).Set`, `Mode`, mode constants, `GetMode`, `(Mode).Set`, `SetUID`, `SetGroups`, `Prctlw`, and `Prctl`.

## Control Flow
Mode detection reads securebits, ambient bits, process sets, and bounding bits. Mode setting temporarily raises `SETPCAP`, sets securebits, optionally clears ambient/bounding/permitted state, and lowers effective caps on return. UID/GID helpers temporarily raise `SETUID` or `SETGID`, perform syscalls, and lower effective caps afterward.

## State And Persistence Behavior
These functions mutate process credential and securebit state across all OS threads via `scwStateSC`. Some operations, especially `ModeNoPriv` and bounding drops, are irreversible for the process.

## Dependencies And Integration Points
Uses constants from Linux prctl/securebits APIs, `sysSetGroupsVariant` from build-tag files, core `Set` operations, and the syscall synchronization layer.

## Risks And Edge Cases
Security mode changes can fail due to locked securebits or missing capabilities and may partially alter state. Dropping bounding bits cannot be undone. `SetUID`/`SetGroups` assume capability availability rather than root semantics.

## Test Signals
Signals include mode string output, successful prctl wrapper behavior, and tests/examples that verify capability lowering and launcher isolation.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/convenience.go -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/fd.go -->
# sources/security-integrity/libcap/cap/fd.go

## Purpose
Go 1.12+ helper for extracting an `os.File` descriptor without incurring Go runtime thread-pinning side effects from direct `File.Fd()` use.

## Important APIs, Types, And Functions
Defines `fd(file *os.File) uintptr` using `file.SyscallConn()` and `RawConn.Control`.

## Control Flow
Gets a syscall connection, returns all-bits-one on error, otherwise captures the descriptor passed to the control callback.

## State And Persistence Behavior
Does not mutate file or process state. It only observes the descriptor while under runtime-managed control.

## Dependencies And Integration Points
Used by `GetFd` and `SetFd` in `file.go` for fgetxattr/fsetxattr operations.

## Risks And Edge Cases
If `SyscallConn` fails, callers receive an invalid descriptor value and the subsequent syscall should fail. The helper assumes the descriptor remains valid for the immediate syscall use.

## Test Signals
Signals are file capability tests passing without runtime thread-lock leakage.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/fd.go -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/fdlegacy.go -->
# sources/security-integrity/libcap/cap/fdlegacy.go

## Purpose
Legacy pre-Go-1.12 fallback for extracting an `os.File` descriptor.

## Important APIs, Types, And Functions
Defines `fd(file *os.File) uintptr` as `uintptr(file.Fd())` under build tag `!go1.12`.

## Control Flow
Returns the descriptor directly from the standard library.

## State And Persistence Behavior
No explicit state is changed, but direct `Fd()` can cause Go runtime polling/thread behavior changes on old toolchains.

## Dependencies And Integration Points
Used by `file.go` when building with old Go versions.

## Risks And Edge Cases
The file comment notes this path is suboptimal because it can lock a thread to syscalls.

## Test Signals
Signals are successful file capability operations on legacy Go toolchains.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/fdlegacy.go -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/file.go -->
# sources/security-integrity/libcap/cap/file.go

## Purpose
File capability support for the Go package: read, write, remove, import, and export Linux `security.capability` data.

## Important APIs, Types, And Functions
Defines VFS capability wire structs, errors `ErrBadSize`, `ErrBadMagic`, `ErrBadPath`, `ErrOutOfRange`, `GetFd`, `GetFile`, `GetNSOwner`, `SetNSOwner`, `SetFd`, `SetFile`, `Import`, `Export`, `ExtMagic`, and `MinExtFlagSize`.

## Control Flow
`digestFileCap` parses little-endian v1/v2/v3 xattrs into `Set`. `packFileCap` converts `Set` into VFS xattr bytes, collapsing effective bits to the Linux legacy file-effective flag. Setters reject non-regular files, remove xattrs for nil sets, and use an O_PATH `/proc/self/fd` fallback when a file cannot be opened read-only.

## State And Persistence Behavior
Mutates file xattrs and optional namespace owner UID in `Set`. Import/export are in-memory and lossless except namespace owner is not exported. File xattr changes persist on disk.

## Dependencies And Integration Points
Uses Linux `getxattr`, `fgetxattr`, `setxattr`, `fsetxattr`, remove xattr syscalls, `/proc/self/fd`, and `fd.go` descriptor handling. Tested by `cap_file_test.go` and import/export tests.

## Risks And Edge Cases
Effective file capability storage is lossy by design. Symlink and special-file handling is security-sensitive. O_PATH fallback depends on procfs mount path. `MinExtFlagSize` is a mutable package global.

## Test Signals
Signals are xattr round trips, symlink rejection, nil removal, unreadable-file fallback, import/export size checks, and bad magic/size errors.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/file.go -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/flags.go -->
# sources/security-integrity/libcap/cap/flags.go

## Purpose
In-memory manipulation and comparison of capability `Set` flag bits.

## Important APIs, Types, And Functions
Defines `GetFlag`, `SetFlag`, `Clear`, `FillFlag`, `Fill`, `ErrBadValue`, `bitOf`, `allMask`, `ClearFlag`, `Cf`, deprecated `Compare`/`Differs`, and `(Diff).Has`.

## Control Flow
Operations validate set and value ranges, lock sets, then manipulate compressed 32-bit words. `SetFlag` snapshots old values and rolls back if any requested value is invalid. `FillFlag` duplicates the reference set to avoid deadlocks. `Cf` duplicates the alternate set before comparing flag bitmaps.

## State And Persistence Behavior
Mutates only the in-memory `Set`; no kernel state changes until callers apply it with `SetProc` or file setters.

## Dependencies And Integration Points
Used throughout the package by text parsing, IAB fill, convenience mode setters, launch setup, and tests.

## Risks And Edge Cases
`bitOf` permits values up to `words*32`, while runtime named values may be fewer; kernel validation happens later. Concurrency safety depends on respecting `Set` locks and duplicate-before-compare patterns.

## Test Signals
Signals are all-mask unit tests, text parse/string round trips, import/export mutation loops, and diff detection.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/flags.go -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/iab.go -->
# sources/security-integrity/libcap/cap/iab.go

## Purpose
IAB abstraction for Linux inheritable, ambient, and bounding capability vectors.

## Important APIs, Types, And Functions
Defines `IAB`, `Vector`, `Inh`, `Amb`, `Bound`, `IABDiff`, `NewIAB`, `IABGetProc`, `IABFromText`, `String`, `SetProc`, `GetVector`, `SetVector`, `Fill`, `Cf`, `ProcRoot`, and `IABGetPID`.

## Control Flow
Text parsing interprets prefixes `!`, `^`, and `%` into bound/ambient/inheritable vectors. `SetProc` builds a temporary process capability set, raises `SETPCAP` if needed, resets ambient bits, raises requested ambient bits, and drops bounding bits. `/proc/<pid>/status` parsing derives IAB for other processes.

## State And Persistence Behavior
`IAB` stores three locked bitmap slices. Applying it mutates process inheritable, ambient, and bounding state, with bounding drops irreversible. `ProcRoot` changes a package-global procfs root.

## Dependencies And Integration Points
Uses core `Set` operations, `GetAmbient`, `GetBound`, `DropBound`, `SetAmbient`, `/proc` parsing, and text/name mappings.

## Risks And Edge Cases
Ambient bits require matching inheritable bits; setters enforce this coupling. Bounding vector is represented inverted as `nb`, which is easy to misuse. `/proc` hex parsing depends on field width matching `words`.

## Test Signals
Signals are IAB text round trips, vector coupling checks, fill behavior, PID 1 parsing, and process apply behavior in integration use.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/iab.go -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/launch.go -->
# sources/security-integrity/libcap/cap/launch.go

## Purpose
Launch support for running a callback and/or child process on a disposable locked OS thread with altered capability/security state.

## Important APIs, Types, And Functions
Defines `Launcher`, `NewLauncher`, `FuncLauncher`, `Callback`, `SetUID`, `SetGroups`, `SetMode`, `SetIAB`, `SetChroot`, `Launch`, and errors `ErrLaunchFailed`, `ErrNoLaunch`, `ErrAmbiguousChroot`, `ErrAmbiguousIDs`, and `ErrAmbiguousAmbient`.

## Control Flow
`Launch` copies launcher state under lock, starts `launch` in a goroutine, locks an OS thread distinct from the PID thread, marks launch-active state, optionally runs a callback, validates `ProcAttr`, applies UID/GID/mode/IAB/chroot changes on the single launch thread, calls `ForkExec`, then waits for the launch thread to die before re-enabling normal write syscalls.

## State And Persistence Behavior
Temporarily diverges one OS thread's credential/security state from the rest of the process. Child process inherits requested state. Package launch state maps active TIDs and blocks unrelated capability writes until cleanup.

## Dependencies And Integration Points
Works with `syscalls.go` launch-state synchronization, `oslocks.go`/`oslockluster.go` build tags, core Set/IAB/convenience APIs, and `syscall.ForkExec`.

## Risks And Edge Cases
This intentionally violates normal POSIX process-wide semantics for a narrow launch window. Incorrect callback syscalls can corrupt process state. Launch support depends on Go runtime behavior for terminating excess locked OS threads.

## Test Signals
Signals include `TestFuncLaunch`, callback error propagation, no securebit leakage to the parent, and explicit errors for ambiguous ProcAttr settings.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/launch.go -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/legacy.go -->
# sources/security-integrity/libcap/cap/legacy.go

## Purpose
Build-tag-specific syscall selection for older Linux architectures/toolchains using the 32-bit `setgroups32` syscall.

## Important APIs, Types, And Functions
Defines package variable `sysSetGroupsVariant = uintptr(syscall.SYS_SETGROUPS32)` under build tag `linux,386 arm mips mipsle`.

## Control Flow
No runtime control flow; it supplies the syscall number used by `SetGroups`.

## State And Persistence Behavior
No state beyond the package variable.

## Dependencies And Integration Points
Consumed by `convenience.go` `setGroups`.

## Risks And Edge Cases
Incorrect build tags or syscall number would break group changes on affected 32-bit platforms.

## Test Signals
Signals are successful `SetGroups` operation on legacy architectures.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/legacy.go -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/modern.go -->
# sources/security-integrity/libcap/cap/modern.go

## Purpose
Default syscall selection for modern platforms using `SYS_SETGROUPS`.

## Important APIs, Types, And Functions
Defines package variable `sysSetGroupsVariant = uintptr(syscall.SYS_SETGROUPS)` for Linux builds excluding legacy 32-bit variants.

## Control Flow
No runtime control flow; build tags select this file.

## State And Persistence Behavior
No mutable behavior beyond package initialization.

## Dependencies And Integration Points
Used by `convenience.go` when applying supplementary groups.

## Risks And Edge Cases
Wrong build-tag coverage would select an unsupported syscall on a platform.

## Test Signals
Signals are successful group-setting calls on modern platforms.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/modern.go -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/names.go -->
# sources/security-integrity/libcap/cap/names.go

## Purpose
Generated Linux capability name table for the Go package.

## Important APIs, Types, And Functions
Defines `NamedCount`, constants from `CHOWN` through `CHECKPOINT_RESTORE`, and maps `names map[Value]string` and `bits map[string]Value`.

## Control Flow
No runtime control flow beyond map lookups by `Value.String` and `FromName`.

## State And Persistence Behavior
Static generated data only. Runtime `MaxBits` may exceed `NamedCount`, in which case numeric names are used for newer kernel capabilities.

## Dependencies And Integration Points
Generated from Linux UAPI capability definitions by libcap's Go builder. Used by text conversion, IAB parsing, examples, and documentation.

## Risks And Edge Cases
The table can lag newer kernels. Typos in generated descriptions or names would affect text parse/string compatibility with libcap.

## Test Signals
Signals are `FromName` examples, `Value.String` tests, and text parser round trips.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/names.go -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/oslockluster.go -->
# sources/security-integrity/libcap/cap/oslockluster.go

## Purpose
Pre-Go-1.10 launch support stub. It disables `Launcher` functionality when the Go runtime cannot safely terminate locked OS threads on return.

## Important APIs, Types, And Functions
Defines `LaunchSupported = false` and `validatePA` returning `ErrNoLaunch`.

## Control Flow
Build-tag selection causes `Launch` to fail early on unsupported toolchains.

## State And Persistence Behavior
No state is changed because launch is rejected.

## Dependencies And Integration Points
Selected by build tag `!go1.10`; used by `launch.go`.

## Risks And Edge Cases
Applications using launch must handle `ErrNoLaunch` or require newer Go.

## Test Signals
Signals are `LaunchSupported` false and expected `ErrNoLaunch`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/oslockluster.go -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/oslocks.go -->
# sources/security-integrity/libcap/cap/oslocks.go

## Purpose
Go-1.10+ launch support validation for child process attributes.

## Important APIs, Types, And Functions
Defines `LaunchSupported = true` and `validatePA(pa *syscall.ProcAttr, chroot string)`.

## Control Flow
If no `SysProcAttr` exists and chroot is requested, it creates one. It rejects callback-supplied chroot, credentials, or ambient caps that conflict with `Launcher` configuration.

## State And Persistence Behavior
May mutate the pending `ProcAttr` by assigning `SysProcAttr.Chroot`; it does not mutate process state.

## Dependencies And Integration Points
Used by `launch.go` before applying launch credentials and calling `ForkExec`.

## Risks And Edge Cases
Validation prevents ambiguous authority, but callbacks can still make other unsafe process-state changes.

## Test Signals
Signals are successful launch on supported Go and explicit ambiguous-configuration errors.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/oslocks.go -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/syscalls.go -->
# sources/security-integrity/libcap/cap/syscalls.go

## Purpose
Syscall dispatch and synchronization layer that preserves process-wide POSIX semantics while allowing temporary launcher-thread divergence.

## Important APIs, Types, And Functions
Defines `multisc`, `singlesc`, `launchState`, `launchIdle`, `launchActive`, `launchBlocked`, `scwMu`, `scwTIDs`, `scwState`, `scwCond`, `scwSetState`, and `scwStateSC`.

## Control Flow
Normal write syscalls use psx-backed all-thread calls. During launch, the launch TID can use single-thread syscalls while other writers block. `scwSetState` records launch TIDs and broadcasts state changes; `scwStateSC` waits for a safe writer state and returns the correct syscall adapter.

## State And Persistence Behavior
Maintains package-global synchronization state and active launch TID map. It controls when kernel credential/prctl writes are allowed.

## Dependencies And Integration Points
Depends on `kernel.org/pub/linux/libs/security/libcap/psx`, `runtime`, `sync`, and `syscall`. Used by all security-state writers.

## Risks And Edge Cases
Deadlocks or stale launch TIDs would block security writes. Inconsistent syscall selection during launch could panic pure-Go all-thread syscall implementations or leak thread-local privilege.

## Test Signals
Signals are launcher tests that mutate prctl state without leaking and normal capability APIs working during idle state.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/syscalls.go -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/text.go -->
# sources/security-integrity/libcap/cap/text.go

## Purpose
Text conversion for capability values and sets, compatible with libcap text syntax.

## Important APIs, Types, And Functions
Defines `Value.String`, `FromName`, `Set.String`, `FromText`, `ErrBadText`, `combos`, and helper `histo`.

## Control Flow
String generation builds a histogram of flag combinations to choose a compact background state, emits differences for named bits, then appends numeric unnamed bits. Parsing tokenizes space-separated chunks, supports `all`, named/numeric values, `=`, `+`, `-`, and flag letters `eip`, applying each operation to a new `Set`.

## State And Persistence Behavior
Only in-memory `Set` state is read or mutated. Parsing returns a new set; stringification locks an existing set for reading.

## Dependencies And Integration Points
Uses generated name maps from `names.go` and flag operations from `flags.go`. Used by examples, tests, import/export diagnostics, and user APIs.

## Risks And Edge Cases
The parser is intentionally strict and returns `ErrBadText` for malformed tokens. Canonical output may change compactness over releases but must remain parse-compatible.

## Test Signals
Signals are exact text tests, examples, and import/export/text round trips.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/text.go -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/Makefile -->
# sources/security-integrity/libcap/contrib/Makefile

## Purpose
Contrib makefile that dispatches build and clean targets into bug demonstration subdirectories.

## Important APIs, Types, And Functions
Defines phony `all` and `clean` targets that loop over `bug*` directories.

## Control Flow
For each matching directory, invokes `$(MAKE) -C $$x $@` and exits on the first failure.

## State And Persistence Behavior
Delegates all artifact creation/removal to child makefiles.

## Dependencies And Integration Points
Integrates the contrib bug reproducer directories into a simple aggregate target.

## Risks And Edge Cases
Only directories matching `bug*` are included; other contrib tools such as `capso` or scripts are not dispatched.

## Test Signals
Signals are successful recursive make completion for all bug directories.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/Makefile -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/Dockerfile -->
# sources/security-integrity/libcap/contrib/bug216610/Dockerfile

## Purpose
Docker build environment for bug216610 cross-compilation experiments.

## Important APIs, Types, And Functions
Uses Debian latest, installs ARM and AArch64 cross GCC/binutils packages, creates `/shared`, and adds a `builder` user.

## Control Flow
Docker build runs package update/install steps and creates user/home metadata.

## State And Persistence Behavior
Persists compiler packages and user entries inside the image. Host source is mounted at runtime by the makefile.

## Dependencies And Integration Points
Used by `bug216610/Makefile` `arms` target with `docker run -v $PWD/c:/shared`.

## Risks And Edge Cases
`debian:latest` is not pinned, so package versions can drift. The checked-in Dockerfile has fixed UID/GID 1000 while `mkdocker.sh` can generate host-specific IDs.

## Test Signals
Signals are successful image build and cross-compiled `.syso` files.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/Dockerfile -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/Makefile -->
# sources/security-integrity/libcap/contrib/bug216610/Makefile

## Purpose
Build orchestration for bug216610, a Go internal-linker/.syso experiment combining Go, assembly trampolines, and C object code.

## Important APIs, Types, And Functions
Targets include `go/fib`, generated `go/fibber/fib_$(GOTARGET).syso`, `go/fibber/linkage.go`, `Dockerfile`, `arms`, and `clean`. Uses `GOTARGET` from `go env`.

## Control Flow
Native build compiles `c/fib.c` through `c/gcc.sh` into a `.syso`, generates Go linkname wrappers with `package_fns.sh`, then builds the Go program with `CGO_ENABLED=0`. `arms` builds cross `.syso` files inside Docker.

## State And Persistence Behavior
Creates `.syso`, generated `linkage.go`, the `go/fib` binary, Dockerfile, and optional arm artifacts; clean removes them.

## Dependencies And Integration Points
Depends on Go, GCC, objdump, assembly files named by host target, Docker for cross builds, and the libcap `psx` module imported by the Go program.

## Risks And Edge Cases
The build relies on target-specific assembly trampolines and generated linknames. Missing `fibs_$(GOTARGET).s` or cross compiler support breaks the build.

## Test Signals
Signals are successful `go build`, generated linkage for exported C functions, and working Fibonacci output.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/Makefile -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/c/build.sh -->
# sources/security-integrity/libcap/contrib/bug216610/c/build.sh

## Purpose
Cross-build helper for bug216610 ARM and ARM64 `.syso` artifacts.

## Important APIs, Types, And Functions
Invokes `gcc.sh` twice with `GCC=arm-linux-gnueabi-gcc` and `GCC=aarch64-linux-gnu-gcc`.

## Control Flow
Changes to the script directory and compiles `fib.c` into `fib_linux_arm.syso` and `fib_linux_arm64.syso`.

## State And Persistence Behavior
Writes `.syso` files next to the script.

## Dependencies And Integration Points
Run inside the Docker image created for the makefile `arms` target.

## Risks And Edge Cases
Assumes cross compilers are installed and `gcc.sh` can fix generated assembly for both targets.

## Test Signals
Signals are the two expected `.syso` files.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/c/build.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/c/fib.c -->
# sources/security-integrity/libcap/contrib/bug216610/c/fib.c

## Purpose
C Fibonacci kernel used by bug216610 to demonstrate calling C object code from a pure-Go binary via `.syso` and assembly trampolines.

## Important APIs, Types, And Functions
Defines `struct state { uint32_t b, a; }`, `fib_init(struct state *)`, and `fib_next(struct state *)`.

## Control Flow
`fib_init` sets `a=0` and `b=1`. `fib_next` computes `next=a+b`, shifts `a=b`, and stores `b=next`.

## State And Persistence Behavior
Mutates only the caller-provided state struct.

## Dependencies And Integration Points
Compiled into target `.syso` files and called from Go `fibber.State` through generated linkname wrappers.

## Risks And Edge Cases
The C struct layout must match the Go `State` layout and assembly calling convention exactly. `uint32_t` Fibonacci values overflow naturally.

## Test Signals
Signals are expected first Fibonacci sequence values printed by `go/main.go`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/c/fib.c -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/c/gcc.sh -->
# sources/security-integrity/libcap/contrib/bug216610/c/gcc.sh

## Purpose
GCC wrapper that works around Go internal linker issues with RIP-relative `.rodata.*` references in `.syso` object files.

## Important APIs, Types, And Functions
Uses environment variable `GCC`, arrays `args`, `final`, and `ses`, GCC `-S`, `sed -i`, and final GCC invocation.

## Control Flow
Collects compiler flags until the first `.c` input, compiles each C file to assembly, rewrites `.rodata.*` section directives to `.text`, replaces C inputs with assembly paths, invokes GCC on the adjusted command line, and deletes intermediate `.s` files on success.

## State And Persistence Behavior
Creates temporary `.s` files and output objects requested by the original arguments. Removes intermediate assembly after successful compilation.

## Dependencies And Integration Points
Used by bug216610 make targets for native and cross `.syso` builds.

## Risks And Edge Cases
Argument parsing is fragile: flags after the first `.c` are not part of the C-to-assembly pass. Rewriting all matching `.rodata.*` lines to `.text` is broad and architecture/toolchain-sensitive.

## Test Signals
Signals are successful `.syso` generation and Go linker correctness when calling C functions.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/c/gcc.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/go/fibber/fib.go -->
# sources/security-integrity/libcap/contrib/bug216610/go/fibber/fib.go

## Purpose
Go wrapper package for the bug216610 Fibonacci C kernel.

## Important APIs, Types, And Functions
Defines `State { B, A uint32 }`, method `cPtr`, constructor `NewState`, and method `Next`.

## Control Flow
`NewState` allocates `State` and calls generated `syso__fib_init.call`. `Next` calls generated `syso__fib_next.call` to advance the state.

## State And Persistence Behavior
State lives in the Go heap but is mutated by C object code through unsafe pointers.

## Dependencies And Integration Points
Depends on generated `linkage.go`, target assembly `syso` trampoline, and `.syso` symbols from `fib.c`.

## Risks And Edge Cases
Unsafe pointer conversion assumes `State` layout matches C `struct state`. Generated symbol wrappers must exist before build.

## Test Signals
Signals are correct Fibonacci sequence values from the main program.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/go/fibber/fib.go -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/go/fibber/fibs_linux_amd64.s -->
# sources/security-integrity/libcap/contrib/bug216610/go/fibber/fibs_linux_amd64.s

## Purpose
amd64 Go assembly trampoline for calling C functions embedded in `.syso` objects from Go.

## Important APIs, Types, And Functions
Defines `TEXT ·spacer(SB)` and `TEXT ·syso(SB),$0-16`; passes function pointer in `SI` and state pointer in `DI` before `CALL *SI`.

## Control Flow
The wrapper receives a C function pointer and state pointer from Go, moves them into x86-64 ABI argument registers, calls the C function, and returns.

## State And Persistence Behavior
No persistent state; it mutates registers and whatever memory the C function modifies.

## Dependencies And Integration Points
Used by `fibber` generated wrappers on linux/amd64. Must match Go assembler syntax and System V x86-64 ABI.

## Risks And Edge Cases
The comments acknowledge this is a fragile Go-to-C transition without cgo. Stack maps, preemption, and ABI drift are risks.

## Test Signals
Signals are successful Go build and correct calls to `fib_init`/`fib_next`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/go/fibber/fibs_linux_amd64.s -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/go/fibber/fibs_linux_arm.s -->
# sources/security-integrity/libcap/contrib/bug216610/go/fibber/fibs_linux_arm.s

## Purpose
ARM Go assembly trampoline for calling C functions embedded in `.syso` objects from Go.

## Important APIs, Types, And Functions
Defines `TEXT ·spacer(SB)` and `TEXT ·syso(SB),$0-8`; loads the function into `R14`, state into `R0`, and branches with link.

## Control Flow
Receives a function pointer and state pointer, maps them to ARM calling convention registers, calls the C function, and returns.

## State And Persistence Behavior
No persistent state beyond C mutation of the provided state pointer.

## Dependencies And Integration Points
Used by bug216610 linux/arm builds with cross-generated `.syso` files.

## Risks And Edge Cases
Manual calling-convention bridging is fragile and architecture-specific. It assumes 32-bit pointer layout and Go assembler frame offsets.

## Test Signals
Signals are successful arm build/link and correct Fibonacci output on target.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/go/fibber/fibs_linux_arm.s -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/go/main.go -->
# sources/security-integrity/libcap/contrib/bug216610/go/main.go

## Purpose
Demo program for bug216610. It proves psx syscall use and the `.syso` Fibonacci bridge work in a pure-Go binary.

## Important APIs, Types, And Functions
Uses `psx.Syscall3(syscall.SYS_GETPID)`, `fibber.NewState`, and `State.Next`.

## Control Flow
Gets PID through psx, prints it, initializes Fibonacci state, prints the first two values, advances eight times, and prints the sequence prefix.

## State And Persistence Behavior
No persistent state; process output is the observable result.

## Dependencies And Integration Points
Imports local module `fib/fibber` and libcap `psx` package. Built by the bug216610 makefile.

## Risks And Edge Cases
Fails if psx syscall wrapper or generated syso bridge is unavailable. Fibonacci values are fixed-width uint32.

## Test Signals
Signals are printed PID and Fibonacci sequence `0, 1, 1, 2, 3, 5, ...`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/go/main.go -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/mkdocker.sh -->
# sources/security-integrity/libcap/contrib/bug216610/mkdocker.sh

## Purpose
Generates a Dockerfile for bug216610 cross-compilation with host-specific builder UID/GID.

## Important APIs, Types, And Functions
Shell here-document emits Debian base image, cross-compiler installs, `/shared` directory, and passwd/shadow entries using `id -u` and `id -g`.

## Control Flow
Runs once and writes Dockerfile text to stdout.

## State And Persistence Behavior
Does not mutate files by itself; callers redirect output to `Dockerfile`.

## Dependencies And Integration Points
Used by the bug216610 makefile `Dockerfile` target.

## Risks And Edge Cases
Generated image is based on floating `debian:latest`. `chown builder.bin` assumes a `bin` group exists in the base image.

## Test Signals
Signals are a usable Dockerfile and matching host UID/GID for mounted build outputs.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/mkdocker.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/package_fns.sh -->
# sources/security-integrity/libcap/contrib/bug216610/package_fns.sh

## Purpose
Generates Go linkname wrapper code for exported functions found in a `.syso` object.

## Important APIs, Types, And Functions
Validates arguments, emits `package`, imports `unsafe`, declares `func syso`, `sysoCaller`, and for each `objdump` function symbol emits `//go:linkname`, a byte symbol, and a `syso__<sym>` caller.

## Control Flow
Checks the second argument is a `.syso`, prints common wrapper boilerplate, scans `objdump -x` for global function symbols, and prints one wrapper variable per symbol.

## State And Persistence Behavior
Writes generated Go source to stdout. Does not modify the `.syso`.

## Dependencies And Integration Points
Used by bug216610 makefile to create `go/fibber/linkage.go`.

## Risks And Edge Cases
Parsing `objdump` output by columns is toolchain-sensitive. `go:linkname` requires unsafe import behavior and symbol names must match exactly.

## Test Signals
Signals are generated `syso__fib_init` and `syso__fib_next` wrappers that compile and work.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/package_fns.sh -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug218607/Makefile -->
# sources/security-integrity/libcap/contrib/bug218607/Makefile

## Purpose
Build and test makefile for bug218607, a C++/pthread repro verifying libpsx process-wide syscall behavior.

## Important APIs, Types, And Functions
Targets `all`, `test`, `threadcpp`, `../../libcap/libpsx.so`, and `clean`. Links with `-lpsx`, `-lpthread`, and an rpath to the in-tree libcap directory.

## Control Flow
Builds `libpsx.so` if needed, compiles `thread.cpp`, and `test` runs the resulting binary.

## State And Persistence Behavior
Creates `threadcpp`; clean removes it.

## Dependencies And Integration Points
Depends on g++, pthreads, in-tree libpsx, and `Make.Rules`.

## Risks And Edge Cases
The binary only runs from this directory because of the relative rpath.

## Test Signals
Signals are `threadcpp` printing PASSED and returning 0.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug218607/Makefile -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug218607/thread.cpp -->
# sources/security-integrity/libcap/contrib/bug218607/thread.cpp

## Purpose
C++ threaded repro for bug218607. It checks that `psx_syscall6` mirrors `PR_SET_NO_NEW_PRIVS` across threads.

## Important APIs, Types, And Functions
Uses `std::thread`, `std::mutex`, `std::condition_variable`, raw `syscall(__NR_prctl, PR_GET_NO_NEW_PRIVS)`, and `psx_syscall6(__NR_prctl, PR_SET_NO_NEW_PRIVS, 1, ...)`.

## Control Flow
Worker thread records initial no-new-privs state, signals readiness, waits. Main records its initial state, calls psx to set no-new-privs, releases worker, then both record final state and print before/after values.

## State And Persistence Behavior
Mutates process/thread no-new-privs state, which is sticky for the process. Synchronization state is in globals protected by mutex/condition variable.

## Dependencies And Integration Points
Includes `<sys/psx_syscall.h>` and links against libpsx. Built by the local makefile.

## Risks And Edge Cases
No-new-privs cannot be unset, so repeated execution in the same process model is not possible. The pass condition assumes both threads transitioned from 0 to 1.

## Test Signals
Signals are printed before/after values and `PASSED` when both threads observe the psx-applied state.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug218607/thread.cpp -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug400591/Makefile -->
# sources/security-integrity/libcap/contrib/bug400591/Makefile

## Purpose
Build recipe for bug400591 regression test around libcap external/internal capability copy APIs.

## Important APIs, Types, And Functions
Target `bug` builds `bug.c` statically against in-tree libcap and runs it. `clean` removes objects and binary.

## Control Flow
Builds `../../libcap`, compiles with include/library paths, then executes `./bug` as part of the build target.

## State And Persistence Behavior
Creates a static test binary; clean removes it.

## Dependencies And Integration Points
Depends on C compiler and in-tree libcap static library/header.

## Risks And Edge Cases
Static linking can fail if required static dependencies are unavailable. Running during build means compilation success is not enough.

## Test Signals
Signals are no assertion failures from `bug`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug400591/Makefile -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug400591/bug.c -->
# sources/security-integrity/libcap/contrib/bug400591/bug.c

## Purpose
Regression test for Debian bug 400591 covering libcap copy, text, and compare APIs.

## Important APIs, Types, And Functions
Uses `cap_get_pid`, `cap_to_text`, `cap_size`, `cap_copy_ext`, `cap_copy_int`, `cap_compare`, `malloc`, and `assert`.

## Control Flow
Reads PID 1 capabilities, converts to text, exports to an external buffer, imports back to a new cap object, converts again, and asserts text and `cap_compare` equality.

## State And Persistence Behavior
No system state is changed. Allocated memory/cap objects are not explicitly freed because process exit follows.

## Dependencies And Integration Points
Links against libcap and reads process capabilities from the kernel.

## Risks And Edge Cases
Assertion-based failure gives limited diagnostics. It assumes PID 1 capabilities are readable and external size is under 1024 bytes.

## Test Signals
Signals are matching text representation and zero comparison after copy ext/int round trip.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug400591/bug.c -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/capso/Makefile -->
# sources/security-integrity/libcap/contrib/capso/Makefile

## Purpose
Build recipe for `capso`, a shared-object file-capability demonstration that can bind to TCP port 80.

## Important APIs, Types, And Functions
Targets `bind`, `capso.o`, `capso.so`, `../../libcap/loader.txt`, and `clean`. Adds `-fPIC`, embeds `LIBCAP_VERSION` and `SHARED_LOADER`, links with libcap and libdl, and runs `sudo setcap cap_net_bind_service=p capso.so`.

## Control Flow
Builds the shared object with custom entry point `__so_start`, sets file capability on it, then builds the unprivileged `bind` program against `capso.so`.

## State And Persistence Behavior
Creates `capso.o`, `capso.so`, `bind`, and persists a file capability xattr on `capso.so`.

## Dependencies And Integration Points
Depends on in-tree libcap, loader metadata, sudo/setcap, C compiler/linker, and `execable.h` support.

## Risks And Edge Cases
The makefile invokes sudo during build. File capability setting depends on filesystem xattr support and privileges.

## Test Signals
Signals are successful build, setcap, and a `bind` binary that can obtain a port-80 socket through the shared object.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/capso/Makefile -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/capso/bind.c -->
# sources/security-integrity/libcap/contrib/capso/bind.c

## Purpose
Unprivileged demo executable that calls `capso` to bind port 80 and then listens.

## Important APIs, Types, And Functions
Uses `bind80` from `capso.h`, `listen`, `sleep`, `close`, `perror`, and stdout status messages.

## Control Flow
Calls `bind80("127.0.0.1")`, exits on failure, calls `listen`, prints the file descriptor, sleeps for 60 seconds for inspection, then closes the socket.

## State And Persistence Behavior
Creates a listening socket on TCP port 80 for up to 60 seconds. Does not persist files.

## Dependencies And Integration Points
Links against `capso.so`, which may launch itself with file capabilities to obtain the privileged socket.

## Risks And Edge Cases
Requires port 80 to be free. Sleeping server behavior is demo-only and can temporarily expose a listening socket.

## Test Signals
Signals are successful bind/listen and visible port 80 listener during the sleep window.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/capso/bind.c -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/capso/capso.c -->
# sources/security-integrity/libcap/contrib/capso/capso.c

## Purpose
Shared-object capability demonstration. It exposes `bind80()` and can execute itself as a helper with file capabilities to bind privileged port 80 and pass the socket back.

## Important APIs, Types, And Functions
Key functions include `fake_exploit`, `where_am_i`, `try_bind80`, `set_fd3`, `bind80`, and `SO_MAIN`. Uses libcap `cap_get_proc`, `cap_set_flag`, `cap_set_proc`, launcher APIs, sockets, `SCM_RIGHTS`, and dynamic loader introspection.

## Control Flow
`bind80` first tries to bind directly. On failure it locates its own shared object, creates a Unix datagram socketpair, launches itself as an executable helper with fd 3 mapped to the socket, and receives the bound fd by `recvmsg`. The shared-object main raises effective `CAP_NET_BIND_SERVICE`, binds, sends the fd over fd 3, and optionally executes exploit-demo code when compiled/enabled.

## State And Persistence Behavior
Creates sockets, launches a child process, and transfers file descriptors. The build installs a persistent file capability on the `.so`; runtime capability changes are process-local.

## Dependencies And Integration Points
Depends on libcap launcher and capability APIs, `execable.h`, dynamic loader support, Unix sockets, and the makefile-set file capability.

## Risks And Edge Cases
This is security-sensitive demo code. Helper launch, fd passing, environment handling, and optional exploit simulation must not be treated as production-hardening. Port availability and filecap setup affect behavior.

## Test Signals
Signals are direct or helper bind success, receipt of a valid fd via `SCM_RIGHTS`, and usable listener from `bind.c`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/capso/capso.c -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/capso/capso.h -->
# sources/security-integrity/libcap/contrib/capso/capso.h

## Purpose
Public header for the `capso` demo shared object.

## Important APIs, Types, And Functions
Declares `int bind80(const char *hostname);` with include guards.

## Control Flow
Header-only declaration; runtime behavior is in `capso.c`.

## State And Persistence Behavior
No state.

## Dependencies And Integration Points
Included by `bind.c` and `capso.c` consumers.

## Risks And Edge Cases
The API returns a raw file descriptor or negative error; callers must close successful descriptors.

## Test Signals
Signals are successful compilation and linkage against `capso.so`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/capso/capso.h -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/pcaps4convenience -->
# sources/security-integrity/libcap/contrib/pcaps4convenience

## Purpose
Legacy helper script for assigning inheritable/effective file capabilities to convenience binaries such as `eject`, `killall`, `modprobe`, `ntpdate`, `qemu`, and `route`.

## Important APIs, Types, And Functions
Defines capability variables, `APPSARRAY`, `SET=ie`, `p4c_test`, `p4c_app_convert`, `p4c_app_revert`, `p4c_convert`, `p4c_revert`, and `p4c_usage`.

## Control Flow
Validates root and `setcap`, resolves each application with `which -a`, skips symlinks, applies `setcap <caps>=ie` on convert, or removes capabilities on revert. CLI supports `con|convert`, `rev|revert`, and `help`.

## State And Persistence Behavior
Mutates file capability xattrs on system binaries. Does not change setuid bits.

## Dependencies And Integration Points
Requires root, `which`, `setcap`, and filesystem/kernel file capability support. Intended to pair with PAM-managed inheritable capabilities.

## Risks And Edge Cases
Hard-coded capability sets may be obsolete or unsafe. The loop condition stops before the final array element. Shell tests use unquoted paths and fragile `==` expressions.

## Test Signals
Signals are `setcap` success/removal for each found non-symlink binary and usage output for invalid commands.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/pcaps4convenience -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/pcaps4server -->
# sources/security-integrity/libcap/contrib/pcaps4server

## Purpose
Legacy server-conversion script that changes selected daemons from root-owned operation to unprivileged users plus file capabilities.

## Important APIs, Types, And Functions
Defines message helpers, `checkReturnCode`, `p4r_test`, per-service convert/revert functions for apache2, samba, bind, dhcpd, and cupsd, plus usage dispatch.

## Control Flow
Requires root, then either converts all services or one selected service. Convert paths create service users/groups, edit config user/group entries, chown service directories and binaries, set setuid bits for service users, and apply `setcap`. Revert paths restore root ownership, remove setuid/filecaps, revert config snippets, and delete users/groups.

## State And Persistence Behavior
Highly persistent system mutation: user/group database, daemon config files, ownership of `/etc`, `/var`, and `/usr/sbin` paths, mode bits, and file capability xattrs.

## Dependencies And Integration Points
Assumes Slackware-like hard-coded paths, root privileges, `groupadd`, `useradd`, `chown`, `chmod`, `setcap`, `sed`, and installed daemons.

## Risks And Edge Cases
Dangerous on modern systems: hard-coded paths/users, typo `rev|renvert` in global revert dispatch, no backup of configs, and broad recursive chown. Should be treated as historical example code.

## Test Signals
Signals are command return codes checked after key mutations and visible capability/ownership changes on target daemons.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/pcaps4server -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/pcaps4suid0 -->
# sources/security-integrity/libcap/contrib/pcaps4suid0

## Purpose
Legacy helper script for converting setuid-root binaries to file capabilities, with either inheritable/effective or permitted/effective semantics.

## Important APIs, Types, And Functions
Defines capability variables for `ping`, `traceroute`, `chsh`, `chfn`, `Xorg`, `chage`, `passwd`, `unix_chkpwd`, `mount`, and `umount`, `APPSARRAY`, `SET`, `p4s_test`, `p4s_app_convert`, `p4s_app_revert`, `p4s_convert`, `p4s_revert`, and `p4s_usage`.

## Control Flow
Checks root and required tools, resolves binaries with `which -a`, ignores symlinks, removes setuid and applies `setcap` on convert, or restores setuid and removes filecap on revert. CLI supports convert/revert/help.

## State And Persistence Behavior
Mutates system binary mode bits and file capability xattrs. These changes persist and alter privilege behavior for users.

## Dependencies And Integration Points
Requires root, `which`, `chmod`, `setcap`, file xattrs, and kernel file capability support.

## Risks And Edge Cases
Hard-coded numeric capability IDs are less readable and may age poorly. The array loop misses the last element because it stops at `COUNTER == UPPER`. The conversion can weaken or break system authentication/mount behavior.

## Test Signals
Signals are visible setuid-bit changes and `getcap`/`setcap -r` effects, though the script itself does not verify with `getcap`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/pcaps4suid0 -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/seccomp/Makefile -->
# sources/security-integrity/libcap/contrib/seccomp/Makefile

## Purpose
Makefile for the seccomp exploration program demonstrating interactions between no-new-privs, seccomp TSYNC, Go threads, and psx.

## Important APIs, Types, And Functions
Targets `all`, `go.sum`, `explore`, `test`, `sudotest`, and `clean`.

## Control Flow
Builds `explore.go`, tidies modules when `go.sum` is missing, and `sudotest` runs expected-success and expected-failure command variants with and without `--psx`.

## State And Persistence Behavior
Creates `explore` and `go.sum`; clean removes them.

## Dependencies And Integration Points
Depends on Go and sudo. Integrates with libcap `psx` module.

## Risks And Edge Cases
`sudotest` intentionally runs privileged seccomp experiments and expects some invocations to fail. The syscall number is x86_64-specific in the Go code.

## Test Signals
Signals are successful no-kill errno=0 runs and expected errors for default errno-blocking runs.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/seccomp/Makefile -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/seccomp/explore.go -->
# sources/security-integrity/libcap/contrib/seccomp/explore.go

## Purpose
Go seccomp experiment showing that seccomp filter application with TSYNC mirrors restrictions across threads and comparing raw prctl with psx-mediated prctl.

## Important APIs, Types, And Functions
Defines flags `--psx`, `--delays`, `--kill`, `--errno`, BPF structs `SockFilter` and `SockFProg`, filter constructors, `prctl`, `SeccompSetModeFilter`, `lockProcessThread`, `applyPolicy`, and `main`.

## Control Flow
Builds a BPF program that validates architecture, loads syscall number, traps or errno-blocks `setuid`, and allows everything else. It sets no-new-privs, applies seccomp TSYNC, locks to the PID thread, attempts `setuid(1)`, and reports whether the syscall was blocked or faked.

## State And Persistence Behavior
Mutates no-new-privs and seccomp filter state for the process; these are irreversible for the process lifetime. With `--delays`, sleeps expose inspection windows.

## Dependencies And Integration Points
Uses raw Linux syscalls, hard-coded x86_64 seccomp syscall number and audit arch, Go runtime thread locking, and optional libcap `psx` syscall wrapper.

## Risks And Edge Cases
Architecture constants are hard-coded and comments mark some offsets as not fully understood. Running with default kill/trap behavior can terminate the process. Seccomp/no-new-privs cannot be undone.

## Test Signals
Signals are expected fatal blocked `setuid`, errno-return behavior, fake-success with unchanged UID, and differences between raw and psx prctl setup paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/seccomp/explore.go -->


<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/sucap/Makefile -->
# sources/security-integrity/libcap/contrib/sucap/Makefile

## Purpose
Makefile for `sucap`, a PAM/libcap demonstration of an su-like program using capabilities.

## Important APIs, Types, And Functions
Defines `LINKEXTRA`, `DEPS`, target `su`, and `clean`. Builds `su.c` with `PAM_APP_NAME="sucap"`, links PAM, pam_misc, and libcap, then applies file capabilities with `sudo setcap`.

## Control Flow
Builds in-tree `libcap.so` dependency, compiles the program with an rpath to the in-tree library, and assigns permitted capabilities needed for chown, gid/uid changes, DAC read/search, and setpcap.

## State And Persistence Behavior
Creates `su` and persists file capability xattrs on it. Clean removes build outputs but not necessarily external PAM configuration.

## Dependencies And Integration Points
Depends on PAM development libraries, in-tree libcap, sudo, setcap, and `su.c` outside this work item.

## Risks And Edge Cases
The build invokes sudo and grants powerful file capabilities to a local executable. Runtime behavior also depends on PAM service configuration.

## Test Signals
Signals are successful link and `setcap` application to `./su`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/sucap/Makefile -->
