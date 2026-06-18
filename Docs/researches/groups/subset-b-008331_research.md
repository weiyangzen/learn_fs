# subset-b-008331 Research

Grouped research for the fscrypt action, cgroup, CLI-test, command, and crypto files listed in work item `subset-b-008331`. Each section preserves its source path and is delimited for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/actions/config.go -->
# sources/security-integrity/fscrypt/actions/config.go

## Purpose
Implements global fscrypt configuration creation and loading. It writes `ConfigFileLocation` with defaults, calibrated passphrase hashing costs, and optional policy version override, then reloads configs with missing fields filled from `metadata.Default*`.

## APIs, Types, and Control Flow
Key exports are `ConfigFileLocation`, `CreateConfigFile`, and config-related error types. `CreateConfigFile` opens the config with `O_CREATE|O_WRONLY|O_EXCL` via `filesystem.OpenFileOverridingUmask`, builds `metadata.Config`, applies a policy-version override, calls `getHashingCosts`, and writes through `metadata.WriteConfig`. `getConfig` opens and parses the protobuf/json metadata config, applies defaults for source, padding, contents, filenames, and policy version, then validates.

Hash calibration starts with one Argon2 time pass, memory of `8 * parallelism` KiB, and effective CPU parallelism capped by `metadata.MaxParallelism`. It repeatedly doubles memory up to `memoryBytesLimit()/1024`, then doubles time, timing via process CPU time divided by parallelism, and linearly interpolates between the last two cost points.

## State, Dependencies, and Integration
Persistent state is `/etc/fscrypt.conf` by default, overridable in tests and CLI via `FSCRYPT_CONF`. It depends on `metadata` for config validation and serialization, `crypto.PassphraseHash`, `cgroup` for container-aware limits, `filesystem` for umask override, and `unix` syscalls for sysinfo and CPU time.

## Risks and Test Signals
Calibration is environment-sensitive and can be slow; cgroup failures intentionally fall back to host CPU/RAM. `timeHashingCosts` assumes `costs.Parallelism` is nonzero after metadata validity constraints. Tests check config file permissions and policy-version override, while `hashing_test.go` checks calibration roughness.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/actions/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/actions/config_test.go -->
# sources/security-integrity/fscrypt/actions/config_test.go

## Purpose
Tests global config creation behavior that matters for install safety and policy-version selection.

## APIs and Control Flow
`TestConfigFileIsCreatedWithCorrectMode` sets a restrictive umask, redirects `ConfigFileLocation` to a temp file, calls `CreateConfigFile`, and verifies final mode `0644`. `TestCreateConfigFileV2Policy` creates a config with policy version `2`, reloads it through `getConfig`, and checks that `Options.PolicyVersion` is preserved.

## State, Dependencies, and Integration
Tests mutate package global `ConfigFileLocation` and process umask. They use `metadata.Config` via `getConfig`, so they exercise the real serializer and defaulting path rather than inspecting file bytes directly.

## Risks and Test Signals
The umask test protects against accidentally creating a private or overly permissive config due to process umask. Tests do not restore `ConfigFileLocation`, so test ordering relies on later setup resetting it. Hashing is run with a millisecond target to keep tests bounded.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/actions/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/actions/context.go -->
# sources/security-integrity/fscrypt/actions/context.go

## Purpose
Defines the action-layer `Context`, the high-level state object tying together config, mount, target user, and metadata trust policy for protector and policy operations.

## APIs, Types, and Control Flow
`Context` contains `Config`, `Mount`, `TargetUser`, and optional `TrustedUser`. `NewContextFromPath` resolves the mount containing a path; `NewContextFromMountpoint` resolves a specific mountpoint. Both call `newContextFromUser`, which defaults to `util.EffectiveUser`, loads config, and sets `TrustedUser` to the effective user for non-root callers unless cross-user metadata is allowed.

`checkContext` validates config and filesystem setup. `getKeyringOptions` projects context into `keyring.Options`. `getProtectorOption` loads protector metadata, detecting linked protectors by comparing returned mount with the context mount. `ProtectorOptions` lists descriptors and converts them into options with per-option load errors.

## State, Dependencies, and Integration
Context is read-mostly state, but it controls all later persistence through `filesystem.Mount`, filtering by `TrustedUser`, and keyring behavior through `keyring.Options`. It integrates config loading, mount discovery, user identity, and metadata ownership constraints.

## Risks and Test Signals
The trusted-user rule is a security boundary for non-root metadata reads. Mount equality is pointer/value sensitive and affects linked protector reporting. `context_test.go` builds a real test context and validates that a config file is required before context creation.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/actions/context.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/actions/context_test.go -->
# sources/security-integrity/fscrypt/actions/context_test.go

## Purpose
Provides package-wide integration test setup for the `actions` package by creating a real test mount context, config file, and fscrypt metadata directory.

## APIs and Control Flow
`setupContext` obtains `util.TestRoot`, redirects `ConfigFileLocation`, verifies `NewContextFromMountpoint` fails without a config file, creates a config, creates a context, and sets up the mount with world-writable metadata. `TestMain` initializes `testContext`, skips cleanly on `util.ErrSkipIntegration`, runs package tests, and cleans up config and metadata.

## State, Dependencies, and Integration
This file is the shared fixture for protector, policy, recovery, and hashing-adjacent action tests. It mutates real filesystem metadata through `filesystem.Mount.Setup` and `RemoveAllMetadata`.

## Risks and Test Signals
Because it uses integration infrastructure, test results depend on available filesystem encryption support. Cleanup is centralized, but package globals and real mount metadata can leak if a process exits abruptly.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/actions/context_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/actions/hashing_test.go -->
# sources/security-integrity/fscrypt/actions/hashing_test.go

## Purpose
Tests and benchmarks passphrase hashing cost calibration from `config.go`.

## APIs and Control Flow
`TestCostsSearch` calls `getHashingCosts` for 100 ms, 200 ms, and 500 ms targets, retimes the selected costs with `timeHashingCosts`, and accepts results within a factor of three. Benchmarks run calibration for 10 ms, 100 ms, and 1 s targets with logging discarded.

## State, Dependencies, and Integration
The tests exercise actual Argon2 hashing and process CPU timing. They indirectly use cgroup-aware CPU and memory limits from `config.go`.

## Risks and Test Signals
The factor-of-three threshold acknowledges noisy machines and CPU scheduling. The test can be expensive or flaky on constrained hosts, but it is the primary regression signal for calibration returning wildly weak or slow parameters.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/actions/hashing_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/actions/policy.go -->
# sources/security-integrity/fscrypt/actions/policy.go

## Purpose
Implements fscrypt policy lifecycle: create, load, apply, unlock, provision, deprovision, add/remove protectors, and purge keys. A policy represents a directory encryption key plus metadata describing its wrapped copies and encryption options.

## APIs, Types, and Control Flow
Error types cover access denied on unsupported v2 kernels, already protected, filesystem mismatch, missing metadata, not protected, removing the only protector, and metadata mismatch. `PurgeAllPolicies` lists policies on a mount and removes their keys from keyrings while tolerating absent keys and logging partial-removal cases.

`Policy` stores context, metadata, in-memory key, creation flag, owner for metadata creation, and linked protectors created during cross-filesystem attachment. `CreatePolicy` generates a random policy key, computes a v1 or v2 descriptor, creates metadata from context options, determines metadata owner for login protectors, and calls `AddProtector`. `GetPolicy` loads mount metadata by descriptor. `GetPolicyFromPath` reads kernel policy from the path, maps encryption support errors, detects likely unsupported-v2 permission denial, loads stored metadata, and verifies descriptor/options match.

Unlocking occurs either through `Unlock`, which selects a protector option and unwraps via callback-derived protector key, or `UnlockWithProtector`, which uses an already-unlocked protector. `AddProtector` requires both keys unlocked, creates linked protector metadata when mounts differ, wraps the policy key with the protector key, appends metadata, and commits. `RemoveProtector` removes a wrapped key unless it is the last one. `Apply` enforces same filesystem before calling `metadata.SetPolicy`. Provisioning and deprovisioning proxy to `keyring`.

## State, Dependencies, and Integration
Persistent state lives in `.fscrypt/policies` and linked `.fscrypt/protectors` through `filesystem.Mount`. Kernel state lives in user or filesystem keyrings via `keyring`. Crypto wrapping uses `crypto.Wrap` and `Unwrap`; metadata comparison uses protobuf equality.

## Risks and Test Signals
Rollback is mostly in-memory: failed commits restore wrapped-key lists, and created policies can be reverted by callers. Cross-filesystem links are cleanup-sensitive via `newLinkedProtectors`. `RemoveProtector` intentionally does not preserve wrapped-key order. Tests cover creation, duplicate additions, removal failures, callback unlock, direct protector unlock, and locked-protector rejection. CLI tests add coverage for corrupt/missing metadata, v1 behavior, and lock/unlock integration.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/actions/policy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/actions/policy_test.go -->
# sources/security-integrity/fscrypt/actions/policy_test.go

## Purpose
Integration tests for policy creation, modification, and unlock paths.

## APIs and Control Flow
`makeBoth` creates a protector and a policy using the shared `testContext`. Cleanup helpers lock and destroy objects. Tests validate creating a policy/protector pair, adding a second protector, rejecting duplicate protector attachment, removing an added protector, rejecting removal of absent or only protectors, unlocking by option callback, unlocking with an already-unlocked protector, and rejecting unlock with a locked protector.

## State, Dependencies, and Integration
All tests write real fscrypt metadata under the test mount and use the real crypto wrapping path. They depend on callback helpers from `protector_test.go` and fixture setup from `context_test.go`.

## Risks and Test Signals
The tests focus on metadata-level behavior, not kernel keyring provisioning or policy application to directories. They provide good regression coverage for wrapped-key list invariants and `ErrLocked` behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/actions/policy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/actions/protector.go -->
# sources/security-integrity/fscrypt/actions/protector.go

## Purpose
Implements protector lifecycle. Protectors wrap policy keys and are themselves protected by login passphrases, custom passphrases, or raw keys.

## APIs, Types, and Control Flow
Exports include `LoginProtectorMountpoint`, protector naming errors, `Protector`, `CreateProtector`, `GetProtector`, `GetProtectorFromOption`, and methods for descriptor, destroy, revert, unlock, lock, and rewrap. `CreateProtector` validates naming rules, checks duplicate names or login protectors, populates source-specific metadata such as UID, salt, and hashing costs, generates a random internal key, computes a v1 descriptor, wraps it using `Rewrap`, and persists metadata.

`Unlock` calls `unwrapProtectorKey` only when the in-memory key is absent. `Lock` wipes the key and nils it. `Rewrap` requires an unlocked internal key, derives or reads the wrapping key via `getWrappingKey`, wraps the internal key, persists with `Mount.AddProtector`, and restores the old wrapped key if persistence fails.

## State, Dependencies, and Integration
Protector metadata is persisted in `.fscrypt/protectors` through `filesystem.Mount`. Passphrase protectors depend on config hashing costs and random salt. Login protectors embed target UID and are usually stored on `LoginProtectorMountpoint` by command-layer helpers. Crypto dependencies include random key generation, descriptors, wrapping, and key wiping.

## Risks and Test Signals
`Lock` assumes `protector.key.Wipe()` is safe when the key is nil. Naming and duplicate checks rely on readable existing metadata. Failed callback or wrapping paths must wipe generated keys and avoid partially persisted protectors. Tests cover creation and callback error propagation, while CLI tests cover names, login protectors, raw keys, and passphrase changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/actions/protector.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/actions/protector_test.go -->
# sources/security-integrity/fscrypt/actions/protector_test.go

## Purpose
Tests basic protector creation and callback error propagation.

## APIs and Control Flow
Defines shared constants, a callback error, `goodCallback` returning a fixed-length key from `timingPassphrase`, and `badCallback` returning `errCallback`. `TestCreateProtector` creates, locks, and destroys a protector. `TestBadCallback` verifies `CreateProtector` returns the original callback error and does not require cleanup if creation failed.

## State, Dependencies, and Integration
Uses the shared integration `testContext` and real metadata persistence. The `goodCallback` is also reused by policy and recovery tests.

## Risks and Test Signals
Coverage is narrow but protects the important guarantee that key callbacks are not swallowed or converted. More source-specific protector behavior is covered in CLI tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/actions/protector_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/actions/recovery.go -->
# sources/security-integrity/fscrypt/actions/recovery.go

## Purpose
Adds automatic recovery passphrase support for login-protected directories on non-root filesystems, allowing access if root-filesystem login protector metadata is lost.

## APIs, Types, and Control Flow
`modifiedContextWithSource` clones a context and config with a different protector source. `AddRecoveryPassphrase` generates a 20-character random passphrase, creates a custom-passphrase protector named `Recovery passphrase for <dirname>` with numeric suffixes on collisions, adds it to the policy, and returns both the passphrase key and protector. On add failure it reverts the created protector.

`WriteRecoveryInstructions` opens a new no-follow `0600` file, writes human-readable instructions including the recovery passphrase, protector identifier, and removal command, optionally chowns it to the metadata owner, and fsyncs it.

## State, Dependencies, and Integration
This code persists an additional protector and updates policy metadata. It uses `proto.Clone` to avoid mutating the original context config, `crypto.NewRandomPassphrase`, and `util.Chown`. The CLI `encryptPath` calls this when a login protector is on a different mount and `--no-recovery` is not set.

## Risks and Test Signals
The recovery file contains plaintext recovery secret by design and must be protected by directory encryption plus mode `0600`. Name collision handling can loop until an available name is found. Tests verify length, default and collision names, policy protector count, unlockability, and file contents.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/actions/recovery.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/actions/recovery_test.go -->
# sources/security-integrity/fscrypt/actions/recovery_test.go

## Purpose
Tests recovery passphrase creation, usability, instruction file generation, and naming collisions.

## APIs and Control Flow
`TestRecoveryPassphrase` creates a protector/policy pair, calls `AddRecoveryPassphrase`, checks passphrase length and protector name, confirms the policy now has two protectors, unlocks the recovery protector with the generated passphrase, writes instructions, verifies the file contains the passphrase, then calls `AddRecoveryPassphrase` again and expects the ` (2)` suffix.

## State, Dependencies, and Integration
Uses real policy/protector metadata and a temp recovery file. It depends on shared action test fixtures and `crypto.Key.Clone` to unlock with the generated passphrase.

## Risks and Test Signals
The test confirms core recovery correctness but does not verify file mode, `O_NOFOLLOW`, ownership changes, or fsync behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/actions/recovery_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/bin/files-changed -->
# sources/security-integrity/fscrypt/bin/files-changed

## Purpose
CI helper that fails if repository files changed after a generation or formatting step.

## APIs and Control Flow
The script checks `git status -s`. If dirty, it prints `git diff --minimal HEAD`, emits a banner tailored to `proto`, `format`, or generic mode, runs `git reset HEAD --hard`, and exits with status 1.

## State, Dependencies, and Integration
Depends on Git and assumes it runs in a repository where generated or formatted output should match committed files. It is likely called from Makefile or CI targets after `make gen` or `make format`.

## Risks and Test Signals
The script is destructive: it hard-resets all working tree changes. This is acceptable in CI but dangerous in an interactive developer tree. It has no local tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/bin/files-changed -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/bin/gen-cgroup-testdata -->
# sources/security-integrity/fscrypt/bin/gen-cgroup-testdata

## Purpose
Regenerates cgroup v2 test fixtures by running `snapshot-cgroup` inside Docker containers with known CPU and memory limits.

## APIs and Control Flow
The script changes to repo root, defines `testdata` and `snapshot_script`, and defines `generate(name, cpu_quota, memory_limit, docker args...)`. Each case removes/recreates its fixture directory, runs `docker run` with mounted snapshot script and output directory, then writes `expected.json`. It generates two limited containers and one no-limit fixture.

## State, Dependencies, and Integration
Writes under `cgroup/testdata`. Requires Docker and a host using cgroup v2. Integrates with `cgroup_test.go`, which reads the generated snapshots and expected JSON.

## Risks and Test Signals
Fixture generation is host/runtime dependent; Docker cgroup configuration must match expectations. The expected JSON is manually provided from function arguments, so a Docker behavior change could produce snapshot files inconsistent with expected limits.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/bin/gen-cgroup-testdata -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/bin/snapshot-cgroup -->
# sources/security-integrity/fscrypt/bin/snapshot-cgroup

## Purpose
Captures the minimal live cgroup v2 files needed by cgroup package tests into a mock root tree.

## APIs and Control Flow
The script requires exactly one output directory. It copies `/proc/self/cgroup`, extracts the v2 group path with `awk -F: '/^0::/'`, builds `/sys/fs/cgroup${group}`, and copies `cpu.max` and `memory.max` if present.

## State, Dependencies, and Integration
Writes a `proc/self/cgroup` and `sys/fs/cgroup/...` subtree under the output directory. It is invoked by `gen-cgroup-testdata` inside Docker containers.

## Risks and Test Signals
It assumes cgroup v2 entries are present and does not fail if limit files are absent. Missing files intentionally let the Go package report `ErrNoLimit`.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/bin/snapshot-cgroup -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cgroup/cgroup.go -->
# sources/security-integrity/fscrypt/cgroup/cgroup.go

## Purpose
Reads CPU and memory limits from Linux cgroup v2. The actions config calibrator uses this to avoid choosing Argon2 costs based on host resources when running inside containers.

## APIs, Types, and Control Flow
Exports `ErrNoLimit`, `ErrV1Detected`, `Cgroup`, `New`, `NewFromRoot`, `CPUQuota`, and `MemoryLimit`. `NewFromRoot` parses `proc/self/cgroup`, rejects any v1 controller entries, finds the v2 `0::` path, and builds a cgroup directory under `sys/fs/cgroup`. `CPUQuota` reads `cpu.max` and parses either `max` or quota/period into fractional CPUs. `MemoryLimit` reads `memory.max` and parses bytes or `max`.

## State, Dependencies, and Integration
The package is read-only and filesystem based. `NewFromRoot` enables deterministic tests with captured fixture trees. Integration with `actions/config.go` feeds `effectiveCPUCount` and `memoryBytesLimit`.

## Risks and Test Signals
The implementation intentionally supports only cgroup v2 and returns `ErrV1Detected` on any v1 controllers. `parseCPUMax` allows a single numeric field and defaults period to 100000, matching kernel defaults. Tests cover v1 rejection, real snapshots, and optional live integration.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cgroup/cgroup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cgroup/cgroup_test.go -->
# sources/security-integrity/fscrypt/cgroup/cgroup_test.go

## Purpose
Tests cgroup v2 resource limit parsing using synthetic v1 input, captured v2 fixtures, and optional live environment expectations.

## APIs and Control Flow
`writeFile` creates fixture files. `TestCgroupV1Unsupported` writes v1-style `/proc/self/cgroup` and expects `ErrV1Detected`. `TestWithRootFromTestdata` iterates fixture directories, unmarshals `expected.json`, constructs `NewFromRoot`, and checks `CPUQuota` and `MemoryLimit`, using `ErrNoLimit` when JSON values are null. `TestIntegrationCgroupLimits` reads expected values from environment and tests the live system.

## State, Dependencies, and Integration
Uses `cgroup/testdata` captured by shell scripts. Optional live tests are controlled by `CGROUP_EXPECTED_CPU_QUOTA` and `CGROUP_EXPECTED_MEMORY_LIMIT`.

## Risks and Test Signals
Snapshot tests are deterministic and cover no-limit and limited cases. They do not directly unit-test malformed `cpu.max` or `memory.max`, but error paths are simple parser returns.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cgroup/cgroup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cgroup/testdata/v2-no-limit/expected.json -->
# sources/security-integrity/fscrypt/cgroup/testdata/v2-no-limit/expected.json

## Purpose
Expected result fixture for a cgroup v2 snapshot with no CPU or memory limits.

## Data and Integration
Contains `{"cpu_quota": null, "memory_limit": null}`. `cgroup_test.go` interprets null pointers as expecting `ErrNoLimit` from `CPUQuota` and `MemoryLimit`.

## Risks and Test Signals
This fixture validates `max` handling and missing/no-limit semantics. It is regenerated by `bin/gen-cgroup-testdata`.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cgroup/testdata/v2-no-limit/expected.json -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cgroup/testdata/v2-quarter-core-64m/expected.json -->
# sources/security-integrity/fscrypt/cgroup/testdata/v2-quarter-core-64m/expected.json

## Purpose
Expected result fixture for a cgroup v2 snapshot constrained to one quarter CPU and 64 MiB memory.

## Data and Integration
Contains `{"cpu_quota": 0.25, "memory_limit": 67108864}`. The Go test compares CPU with tolerance 0.001 and memory exactly.

## Risks and Test Signals
This fixture validates fractional quota parsing and byte memory limit parsing for small containers.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cgroup/testdata/v2-quarter-core-64m/expected.json -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cgroup/testdata/v2-two-cores-256m/expected.json -->
# sources/security-integrity/fscrypt/cgroup/testdata/v2-two-cores-256m/expected.json

## Purpose
Expected result fixture for a cgroup v2 snapshot constrained to two CPUs and 256 MiB memory.

## Data and Integration
Contains `{"cpu_quota": 2.0, "memory_limit": 268435456}`. It checks whole-number quota parsing and larger memory limit propagation.

## Risks and Test Signals
This fixture ensures the parser returns floating quotas even for integer CPU limits and feeds confidence for container-aware Argon2 calibration.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cgroup/testdata/v2-two-cores-256m/expected.json -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/common.sh -->
# sources/security-integrity/fscrypt/cli-tests/common.sh

## Purpose
Shared shell helpers for fscrypt CLI integration tests. It enforces execution through `run.sh`, provides failure helpers, filesystem resets, descriptor lookup, test-user execution, keyring isolation, and expect wrapping.

## APIs and Control Flow
Important helpers include `_fail`, `_expect_failure`, `_print_header`, `_reset_filesystems`, `_get_enabled_fs_count`, `_get_setup_fs_count`, `_get_protector_descriptor`, `_get_login_descriptor`, `_rm_metadata`, `_run_noisy_command`, `_user_do`, `_user_do_and_expect_failure`, `_cleanup_user_keyrings`, `_setup_session_keyring`, and an `expect` wrapper that fixes terminal width.

## State, Dependencies, and Integration
Requires `MNT`, `MNT_ROOT`, `TEST_USER`, `TMPDIR`, and `PATH` from `run.sh`. Mutates mounted test filesystems, `.fscrypt` metadata, and Linux keyrings. Uses `su`, `keyctl`, and `fscrypt status` parsing.

## Risks and Test Signals
Strict mode catches shell errors. Descriptor lookup depends on stable CLI status formatting, intentionally tying tests to user-visible output. Keyring setup re-execs the test script to obtain a clean session.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/common.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/run.sh -->
# sources/security-integrity/fscrypt/cli-tests/run.sh

## Purpose
End-to-end runner for CLI tests. It creates throwaway ext4 filesystems, a test user, isolated config, normalized output, and compares each test against checked-in expected output.

## APIs and Control Flow
The script parses `--update-output`, requires root and prerequisite commands, creates `TMPDIR`, installs cleanup traps, creates the test user, sets locale/umask/PATH, and runs selected `t_*.sh` tests. `setup_for_test` formats loopback ext4 images with encryption, mounts them, sets `FSCRYPT_ROOT_MNT`, `FSCRYPT_CONSISTENT_OUTPUT`, and `FSCRYPT_CONF`, runs global setup with v2-policy check, and sets up the data mount. `run_test` executes a test, filters unstable values, compares output, and optionally updates expected output.

## State, Dependencies, and Integration
Depends on root, `mkfs.ext4`, `losetup`, `mount`, `expect`, `keyctl`, `useradd`, and `chpasswd`. It drives the built `../bin/fscrypt` binary copied into temp space.

## Risks and Test Signals
The runner is intentionally destructive within temp loop devices and test user accounts. Output filtering masks temp paths, devices, config path, descriptors, and protojson spacing, creating stable golden tests for real filesystem behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_change_passphrase.sh -->
# sources/security-integrity/fscrypt/cli-tests/t_change_passphrase.sh

## Purpose
End-to-end test for changing a custom passphrase protector.

## Control Flow and Integration
Creates an encrypted directory with passphrase `pass1`, verifies `pass2` cannot unlock, resolves the protector descriptor, changes passphrase non-interactively with old and new inputs, verifies old passphrase fails and new passphrase succeeds, tests interactive mismatch, then changes interactively to `pass3` and validates lock/unlock.

## State and Risks
Exercises `fscrypt metadata change-passphrase`, protector rewrapping, key wiping, and locked directory behavior. It relies on expect prompt strings and status of encrypted directories after lock.

## Test Signals
Covers both non-interactive and interactive passphrase change paths, including mismatch rejection.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_change_passphrase.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_encrypt.sh -->
# sources/security-integrity/fscrypt/cli-tests/t_encrypt.sh

## Purpose
General integration tests for `fscrypt encrypt` independent of protector-specific variants.

## Control Flow and Integration
Defines reset/status helpers, then verifies encryption fails for nonexistent and nonempty directories, including trailing slash. It tests successful encryption by non-root owner with named protector, status visibility for root and user, rejection of re-encrypting an encrypted directory, and rejection when a non-root user tries to encrypt another user's directory.

## State and Risks
Mutates directory ownership and metadata. It covers precondition checks in `checkEncryptable`, context trust rules, and permissions.

## Test Signals
Strong signal for user-facing encrypt validation and error formatting through status checks and expected failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_encrypt.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_encrypt_custom.sh -->
# sources/security-integrity/fscrypt/cli-tests/t_encrypt_custom.sh

## Purpose
Tests encryption using custom passphrase protectors.

## Control Flow and Integration
Runs non-interactive encryption with `--name=prot`, interactive encryption selecting custom passphrase source and name, and a negative case where quiet custom protector creation lacks a name.

## State and Risks
Exercises `promptForSource`, `promptForName`, `makeKeyFunc`, `CreateProtector`, `CreatePolicy`, and status output. Prompt text changes can break expected output.

## Test Signals
Validates both flag-driven and prompt-driven custom passphrase flows, plus required-name enforcement.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_encrypt_custom.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_encrypt_login.sh -->
# sources/security-integrity/fscrypt/cli-tests/t_encrypt_login.sh

## Purpose
Tests encryption using login passphrase protectors and associated recovery behavior.

## Control Flow and Integration
Runs user encryption with `--source=pam_passphrase`, reads generated recovery passphrase, resolves recovery and login protectors, tests unlocking with login and recovery passphrases, tests interactive login encryption, tests root encrypting on behalf of a user and metadata ownership, tests `--no-recovery`, tests root-filesystem login encryption without recovery, and negative cases such as naming a login protector. Later logic also exercises linked protector status by corrupting a link UUID.

## State and Risks
Touches PAM password verification, root-mounted login protector storage, linked protectors, ownership, recovery file creation, and cross-user metadata permissions. It is sensitive to prompt output and test PAM/user setup.

## Test Signals
Provides broad coverage for the most security-sensitive login-protector workflow, including recovery passphrase integration.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_encrypt_login.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_encrypt_raw_key.sh -->
# sources/security-integrity/fscrypt/cli-tests/t_encrypt_raw_key.sh

## Purpose
Tests encryption using raw 256-bit key protectors.

## Control Flow and Integration
Creates random 32-byte keys and encrypts from file and stdin, verifies wrong 16-byte keys fail from file and stdin, then encrypts with a raw key file, locks, unlocks from stdin, and checks status.

## State and Risks
Exercises `makeRawKey`, `promptForKeyFile`, fixed-length key reads, raw key protector metadata, and key-file length validation.

## Test Signals
Validates both supported raw-key input modes and negative length checks.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_encrypt_raw_key.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_lock.sh -->
# sources/security-integrity/fscrypt/cli-tests/t_lock.sh

## Purpose
Tests `fscrypt lock` behavior under normal, busy-file, cross-user, and loose-file conditions.

## Control Flow and Integration
Encrypts a directory, writes a file, locks it and verifies ciphertext/no-create behavior, unlocks and verifies contents, tries locking while a file descriptor is open and checks incomplete status, finishes locking after closing the file, tests locking while another user has unlocked and then with `--all-users`, and verifies operations fail on a locked loose regular file.

## State and Risks
Exercises kernel key removal, files-busy detection, status heuristics, all-users deprovisioning, and `metadata.ErrLockedRegularFile` error handling.

## Test Signals
Important end-to-end signal for keyring removal semantics and user-facing partial-lock diagnostics.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_lock.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_metadata.sh -->
# sources/security-integrity/fscrypt/cli-tests/t_metadata.sh

## Purpose
Tests advanced `fscrypt metadata` operations for manual protector and policy management.

## Control Flow and Integration
Creates three custom protectors, creates a policy with one protector, adds two more protectors using different unlock paths, displays status, removes two protectors from the policy, deletes one protector metadata file before removal to ensure policy update still works, and displays status again.

## State and Risks
Directly manipulates `.fscrypt` metadata and tests `AddProtector`/`RemoveProtector` command flows. Deleting a protector file simulates partial metadata loss.

## Test Signals
Provides coverage for multi-protector policies and force removal from policy even with missing protector metadata.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_metadata.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_not_enabled.sh -->
# sources/security-integrity/fscrypt/cli-tests/t_not_enabled.sh

## Purpose
Tests behavior when an ext4 filesystem supports encryption but the encryption feature is disabled, then tests enabling it.

## Control Flow and Integration
Disables the ext4 encrypt feature with `debugfs`, remounts, verifies global enabled count decreases, checks encrypt/unlock/lock fail, checks extra GRUB warning when `/boot/grub` appears on the filesystem, enables encryption with `tune2fs -O encrypt`, and verifies encryption succeeds.

## State and Risks
Mutates filesystem feature flags on loopback devices and relies on ext4 tools. It drives error suggestions from `errors.go`, especially GRUB and enablement guidance.

## Test Signals
Strong signal for support/enabled distinction and remediation messages.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_not_enabled.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_not_supported.sh -->
# sources/security-integrity/fscrypt/cli-tests/t_not_supported.sh

## Purpose
Tests behavior on a filesystem that does not support fscrypt encryption.

## Control Flow and Integration
Unmounts the ext4 test mount, mounts tmpfs, verifies `fscrypt setup` fails on tmpfs, creates a directory, and verifies `fscrypt encrypt` fails.

## State and Risks
Exercises `filesystem.ErrEncryptionNotSupported` paths and generic support suggestions.

## Test Signals
Confirms fscrypt does not create metadata or apply policies on unsupported filesystems.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_not_supported.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_passphrase_hashing.sh -->
# sources/security-integrity/fscrypt/cli-tests/t_passphrase_hashing.sh

## Purpose
Integration smoke test that passphrase hashing difficulty configured by `fscrypt setup --time` is not trivially fast.

## Control Flow and Integration
Runs global setup with default 1s hashing and encrypts five directories, expecting elapsed time greater than 3s. Then runs setup with `--time=5s`, encrypts one directory, and again expects more than 3s.

## State and Risks
Exercises config recreation, hashing cost calibration, and actual custom protector creation. Timings are intentionally loose but can still be sensitive to extremely fast or loaded systems.

## Test Signals
Protects against accidental near-zero Argon2 costs in user-facing setup.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_passphrase_hashing.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_setup.sh -->
# sources/security-integrity/fscrypt/cli-tests/t_setup.sh

## Purpose
Tests global and filesystem setup command behavior.

## Control Flow and Integration
Verifies global setup creates `fscrypt.conf`, global setup also creates root `.fscrypt`, rejects existing config on cancel or quiet mode, accepts replacement interactively and with `--force`, sets up a filesystem, rejects already setup filesystem, rejects filesystem setup without config, and rejects bad config file.

## State and Risks
Mutates global test config and `.fscrypt` metadata directories. Covers `createGlobalConfig`, `setupFilesystem`, confirmation handling, config parsing errors, and already-setup errors.

## Test Signals
Good coverage for setup idempotence, force/quiet semantics, and config prerequisite handling.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_setup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_single_user.sh -->
# sources/security-integrity/fscrypt/cli-tests/t_single_user.sh

## Purpose
Tests filesystem setup without `--all-users`, where only the setup user can create fscrypt metadata.

## Control Flow and Integration
Recreates root/data metadata and config in single-user mode, checks status as root and user, encrypts/locks/unlocks as root, encrypts as root with user's login protector and verifies the user can update policy and unlock, verifies user encryption fails when root owns metadata, then chowns mount metadata and lets the user run setup and encrypt successfully.

## State and Risks
Exercises setup mode ownership, metadata update fallback permissions, login protector ownership, and non-root restrictions.

## Test Signals
Important coverage for single-user deployment and root-on-behalf-of-user ownership correctness.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_single_user.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_status.sh -->
# sources/security-integrity/fscrypt/cli-tests/t_status.sh

## Purpose
Tests global, mountpoint, and directory status output when a filesystem is set up or not set up.

## Control Flow and Integration
Captures enabled/setup counts, checks global and mountpoint status as root and test user, verifies unencrypted directory status fails, removes `.fscrypt` metadata, verifies setup count decreases while enabled count remains, then verifies mountpoint and directory status failures on the not-setup filesystem.

## State and Risks
Depends on stable status table columns and helper parsing. Mutates metadata directory to simulate not-setup state.

## Test Signals
Covers `writeGlobalStatus`, `writeFilesystemStatus`, and error paths for unencrypted paths and not-setup mounts.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_status.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_unlock.sh -->
# sources/security-integrity/fscrypt/cli-tests/t_unlock.sh

## Purpose
Tests unlocking encrypted directories and metadata corruption failures.

## Control Flow and Integration
Encrypts with `--skip-unlock`, checks locked status and mount policy row, unlocks and creates data, cycles the mount to lock again, verifies wrong passphrase failure, unlocks successfully, corrupts policy metadata and expects unlock failure, then tests missing policy metadata, missing protector metadata, and swapped policy metadata between two directories.

## State and Risks
Directly edits `.fscrypt/policies` and `.fscrypt/protectors` to simulate corruption. Exercises `GetPolicyFromPath`, metadata mismatch detection, bad config/protector load errors, and keyring provisioning.

## Test Signals
Strong negative coverage for integrity between kernel policy data and fscrypt metadata.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_unlock.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_v1_policy.sh -->
# sources/security-integrity/fscrypt/cli-tests/t_v1_policy.sh

## Purpose
Tests deprecated v1 encryption policies using the user keyring.

## Control Flow and Integration
Sets up a clean session keyring, edits config to policy version 1, verifies root and invalid user-keyring scenarios fail, encrypts as test user, checks status as user and root, creates files, verifies user/root locking restrictions, locks with `--user`, tests incomplete lock detection with an open file, and finishes locking.

## State and Risks
Exercises user keyring access, session keyring linkage, v1 status heuristics, and root/user permission distinctions. Requires keyctl behavior to match assumptions.

## Test Signals
Critical compatibility coverage for older policy/keyring mode and partial-lock heuristics.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_v1_policy.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_v1_policy_fs_keyring.sh -->
# sources/security-integrity/fscrypt/cli-tests/t_v1_policy_fs_keyring.sh

## Purpose
Tests deprecated v1 policies configured to use the filesystem keyring.

## Control Flow and Integration
Edits config to enable `use_fs_keyring_for_v1_policies` and policy version 1. Verifies user encrypt without skip-unlock fails, user encrypt with `--skip-unlock` succeeds but remains locked, user unlock/lock fails, root unlock and lock succeed, and user can read when root has unlocked.

## State and Risks
Exercises `NeedsRootToProvision`, `ErrFsKeyringPerm`, v1 policy application without provisioning, and shared filesystem-keyring visibility.

## Test Signals
Validates the special v1 fs-keyring mode used for compatibility with newer kernel mechanisms.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cli-tests/t_v1_policy_fs_keyring.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cmd/fscrypt/commands.go -->
# sources/security-integrity/fscrypt/cmd/fscrypt/commands.go

## Purpose
Defines the fscrypt CLI command tree and implements user-facing workflows by orchestrating `actions`, keyring, filesystem, metadata, and prompt helpers.

## APIs, Types, and Control Flow
Top-level commands are `Setup`, `Encrypt`, `Unlock`, `Lock`, `Purge`, `Status`, and `Metadata`. `setupAction` creates global config and root metadata or sets up a specified filesystem. `encryptAction` delegates to `encryptPath`, then chmods encrypted directories to `0700` and prints locked/unlocked result. `encryptPath` parses target user, creates context, validates empty/encryptable directory, selects or creates a policy/protector, validates keyring prerequisites, optionally creates recovery passphrase, unlocks/provisions as needed, applies the policy, and writes recovery instructions. Deferred cleanup reverts newly created protectors/policies on error.

`validateKeyringPrereqs` enforces v1 user-keyring or filesystem-keyring requirements. `unlockAction` loads the path policy, validates keyring access, rejects already-unlocked state, unlocks the policy, and provisions it. `lockAction` deprovisions keys, maps keyring partial-removal errors to CLI errors, and uses v1 heuristics plus optional cache dropping. `purgeAction` confirms and removes all policy keys from a mount. `statusAction` dispatches global, mountpoint, or path status. Metadata subcommands create/destroy protectors and policies, change passphrases, add/remove protectors from policies, and dump debug metadata.

## State, Dependencies, and Integration
This file is the main integration layer. It mutates global config, `.fscrypt` metadata, directory policy xattrs, file modes, kernel keyrings, kernel caches, and recovery files. It depends on action objects for durable metadata semantics and command helpers for prompts, flags, errors, and formatting.

## Risks and Test Signals
The most important risks are cleanup correctness when multi-step encryption fails, destructive metadata commands, v1 keyring permission logic, and partial lock semantics. CLI tests in this subset exercise setup, encrypt variants, lock/unlock, metadata, status, v1 modes, and error suggestions.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cmd/fscrypt/commands.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cmd/fscrypt/errors.go -->
# sources/security-integrity/fscrypt/cmd/fscrypt/errors.go

## Purpose
Centralizes CLI error values, suggestion text, and usage-error formatting.

## APIs, Types, and Control Flow
Defines user-facing errors such as cancellation, destructive operation refusal, invalid source, passphrase mismatch, missing key/protector/user, already locked/unlocked, root requirements, and keyring permissions. Struct errors cover files-open, unlocked-by-other-users, and nonempty directory cases. `suggestEnablingEncryption` emits filesystem-specific guidance for ext4 and f2fs, including kernel config, page-size limits, and GRUB warning. `getErrorSuggestions` maps action, filesystem, metadata, crypto, keyring, and command errors to actionable remediation. `newExitError` wraps errors with command name and suggestion. `usageError` prints command help before returning failure.

## State, Dependencies, and Integration
Uses filesystem inspection, kernel version helpers, `unix.Statfs`, and CLI context. It integrates tightly with command handlers through `newExitError`, `expectedArgsErr`, `onUsageError`, and `checkRequiredFlags`.

## Risks and Test Signals
Suggestions must be accurate because they can recommend destructive commands such as `tune2fs` or cache dropping. Output wrapping affects golden CLI tests. Tests indirectly cover many messages via CLI expected outputs, especially not-enabled, setup, and usage cases.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cmd/fscrypt/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cmd/fscrypt/flags.go -->
# sources/security-integrity/fscrypt/cmd/fscrypt/flags.go

## Purpose
Defines all CLI flags, custom flag types, and helpers for parsing metadata identifiers and users.

## APIs, Types, and Control Flow
Custom `boolFlag`, `durationFlag`, and `stringFlag` implement `cli.Flag` plus formatting accessors used by help output. `allFlags` feeds formatting width computation and `universalFlags` adds verbose, quiet, and help everywhere. Flags include setup time, source, name, key file, user, protector, unlock-with, policy, force, skip-unlock, drop-caches, all-users, and no-recovery.

`matchMetadataFlag` parses `MOUNTPOINT:ID` via regex. `parseMetadataFlag` creates a context for that mountpoint. `getProtectorFromFlag` and `getPolicyFromFlag` load locked metadata objects. `parseUserFlag` returns explicit user or effective user.

## State, Dependencies, and Integration
Flag structs are package globals whose `Value` fields are populated by `urfave/cli`. They drive command behavior, prompt defaults, key collection, metadata lookup, and target user selection.

## Risks and Test Signals
Global mutable flags make tests and repeated invocations in one process sensitive to stale values, though the CLI process normally exits after one command. The metadata flag regex accepts printable mountpoints and alnum descriptors only. CLI tests cover many flag combinations.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cmd/fscrypt/flags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cmd/fscrypt/format.go -->
# sources/security-integrity/fscrypt/cmd/fscrypt/format.go

## Purpose
Formats CLI help text, flag usage, and wrapped paragraphs to terminal width.

## APIs, Types, and Control Flow
Package init computes the longest flag display and terminal width capped at 120 columns, defaulting to 80. `prettyFlag` extends `cli.Flag` with display metadata. `shortDisplay` formats `--name` or `--name=ARG`. `longDisplay` aligns flag descriptions and appends defaults. `wrapText` wraps paragraphs with padding while preserving blank lines and lines beginning with `>` as code blocks.

## State, Dependencies, and Integration
Global `lineLength`, `indentLength`, `maxShortDisplay`, and `flagPaddingLength` influence all help and error wrapping. Used by command setup, error messages, and string templates.

## Risks and Test Signals
Terminal width detection happens at init, so output can vary unless tests force 80 columns through `expect` and non-terminal fallback. Wrapping changes affect golden CLI output.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cmd/fscrypt/format.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cmd/fscrypt/fscrypt.go -->
# sources/security-integrity/fscrypt/cmd/fscrypt/fscrypt.go

## Purpose
Program entry point for the `fscrypt` CLI. It configures templates, environment overrides, global flags, commands, and common command setup.

## APIs, Types, and Control Flow
`main` installs help templates, reads `FSCRYPT_CONF`, `FSCRYPT_ROOT_MNT`, and `FSCRYPT_CONSISTENT_OUTPUT`, creates a `cli.App`, sets version and usage handling, installs global flags, hides the help subcommand, registers top-level commands, recursively calls `setupCommand`, and runs the app. `setupCommand` wraps descriptions, appends universal flags, installs usage handlers, and sets `setupBefore` on leaf commands. `setupBefore` routes logs and normal output based on verbose/quiet. `defaultAction` shows help or returns a usage error.

## State, Dependencies, and Integration
Environment variables are critical for tests and alternate installations. `FSCRYPT_CONF` redirects action config, `FSCRYPT_ROOT_MNT` redirects login protector storage, and `FSCRYPT_CONSISTENT_OUTPUT` makes descriptor ordering stable.

## Risks and Test Signals
Environment overrides are process-global and affect all subsequent operations. Quiet mode discards normal output but errors still return through CLI. Only a trivial Go test exists; behavior is mostly covered by CLI tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cmd/fscrypt/fscrypt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cmd/fscrypt/fscrypt_test.go -->
# sources/security-integrity/fscrypt/cmd/fscrypt/fscrypt_test.go

## Purpose
Stub Go test file for the command package.

## APIs and Test Signals
Contains `TestTrivial`, an always-passing test. It likely ensures the package participates in `go test` even though most meaningful command behavior is covered by shell CLI tests.

## Risks
Provides no behavioral coverage for command parsing, flags, or actions. Regression detection for this package relies primarily on the CLI test suite.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cmd/fscrypt/fscrypt_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cmd/fscrypt/keys.go -->
# sources/security-integrity/fscrypt/cmd/fscrypt/keys.go

## Purpose
Collects passphrases and raw keys from terminals, stdin, files, and PAM validation, then exposes them as `actions.KeyFunc` callbacks.

## APIs, Types, and Control Flow
Defines `existingKeyFn`, `oldExistingKeyFn`, `createKeyFn`, and `newCreateKeyFn` from `makeKeyFunc`. `passphraseReader.Read` reads stdin byte-by-byte, handles newline EOF, Ctrl-C/Ctrl-D cancellation, and backspace. `getPassphraseKey` disables terminal echo using raw mode when stdin is a terminal, prints prompts unless quiet, and creates a `crypto.Key`. `makeRawKey` reads 32-byte raw keys from stdin in non-interactive mode or from a prompted/flagged file with length validation. `makeKeyFunc` handles retry semantics, prompts based on protector source, confirms custom passphrases, validates login passphrases through PAM when creating, and rejects raw keys in passphrase-only flows.

## State, Dependencies, and Integration
Uses global flags for quiet mode and key file path. Integrates with `actions` protector/policy unlock and creation, `pam.IsUserLoginToken`, `crypto.Key` memory handling, and `metadata.InternalKeyLen`.

## Risks and Test Signals
Terminal raw mode restoration is essential. Quiet retry returns `ErrWrongKey` rather than prompting. Raw key length is strict. CLI tests cover custom, login, raw-key, and passphrase-change flows.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cmd/fscrypt/keys.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cmd/fscrypt/prompt.go -->
# sources/security-integrity/fscrypt/cmd/fscrypt/prompt.go

## Purpose
Handles interactive and quiet-mode prompts for confirmations, protector source/name selection, key files, and protector choice.

## APIs, Types, and Control Flow
`askQuestion` loops for yes/no input and defaults in quiet mode. `askConfirmation` honors `--force`, rejects destructive default-no prompts in quiet mode, prints warnings, and returns `ErrCanceled` on no. `usernameFromID`, `formatUsername`, and `formatInfo` provide display text for protector metadata. `promptForName` uses flag or prompt, skipping login protectors. `promptForSource` uses flag, quiet default, or numbered source list. `promptForKeyFile` uses flag, quiet error, or repeated file prompt. `promptForProtector` filters load errors, auto-selects a sole option, rejects quiet ambiguity, displays linked protector origin, and returns a selected index. `optionFn` implements `--unlock-with` matching or delegates to prompt selection.

## State, Dependencies, and Integration
Relies on global flags and `util.ReadLine`. It is central to CLI-to-action callbacks and user-visible status descriptions.

## Risks and Test Signals
Quiet mode defaults can silently select defaults or reject ambiguous actions. `promptForProtector` allows selecting an index with load error if manually entered, because the validation checks only range; later callers return the load error. CLI expect tests cover prompt text and flows.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cmd/fscrypt/prompt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cmd/fscrypt/protector.go -->
# sources/security-integrity/fscrypt/cmd/fscrypt/protector.go

## Purpose
Command-layer helper for creating and selecting protectors, especially ensuring login protectors live on the configured root mount.

## APIs, Types, and Control Flow
`createProtectorFromContext` prompts for source and name, requires `--user` when root creates login protectors, shows login setup warning, switches context to `LoginProtectorMountpoint` for login protectors, sets owner to target user when root, and calls `actions.CreateProtector`. `selectExistingProtector` prompts and loads a protector from an option. `expandedProtectorOptions` returns protectors on the current mount plus root login protectors not already seen, marking them as linked options. `modifiedContext` clones a context with mount replaced by `LoginProtectorMountpoint`.

## State, Dependencies, and Integration
Bridges CLI prompt/flag behavior with action protector creation and filesystem mount discovery. It controls cross-filesystem linked protector availability for encryption.

## Risks and Test Signals
Root login-protector creation without explicit user is rejected to avoid accidentally using root credentials. Linked option setup is subtle: root options are returned as selectable for non-root mounts. CLI login encryption tests cover these behaviors.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cmd/fscrypt/protector.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cmd/fscrypt/setup.go -->
# sources/security-integrity/fscrypt/cmd/fscrypt/setup.go

## Purpose
Implements global config creation and per-filesystem metadata setup for the setup command.

## APIs, Types, and Control Flow
`createGlobalConfig` requires root, prompts before replacing an existing config, removes it on confirmation, chooses policy version 2 on kernels at least 5.4 and version 1 otherwise, prints hashing customization text, calls `actions.CreateConfigFile`, and reports success. `setupFilesystem` creates a mountpoint context, checks for already setup state, asks whether all users can create metadata unless `--all-users`, maps that to `filesystem.WorldWritable` or `SingleUserWritable`, calls `Mount.Setup`, and prints permissions summary.

## State, Dependencies, and Integration
Writes global config and `.fscrypt` metadata directories. Depends on kernel version detection, action config creation, filesystem setup modes, current target user, and confirmation prompts.

## Risks and Test Signals
Policy v2 detection uses kernel version rather than a live policy-setting probe, so backports or unusual kernels may be misdetected. Setup tests cover replacement, quiet/force behavior, already setup, missing config, and bad config.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cmd/fscrypt/setup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cmd/fscrypt/status.go -->
# sources/security-integrity/fscrypt/cmd/fscrypt/status.go

## Purpose
Generates global, filesystem, and encrypted-path status output.

## APIs, Types, and Control Flow
`makeTableWriter` builds aligned tables. `encryptionStatus` maps support errors to display text. `policyUnlockedStatus` maps keyring status to `Yes`, `No`, partial, or unknown, including a v1 user-keyring heuristic when a path is available. `writeGlobalStatus` lists relevant filesystems, support status, fscrypt setup status, and totals. `writeOptions` prints protector descriptors, linked status, descriptions, or load errors. `writeFilesystemStatus` prints mount summary, setup mode, protectors, and policies. `writePathStatus` resolves context and policy for a path and prints policy/options/unlocked/protector details.

## State, Dependencies, and Integration
Read-only against mounts, metadata, and keyrings. Integrates with action context/policy/protector options and formatting helpers.

## Risks and Test Signals
Status output is both user-facing and parsed by CLI test helpers, so formatting changes have broad impact. v1 heuristic can report partial state conservatively. CLI status, lock, unlock, and metadata tests exercise this heavily.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cmd/fscrypt/status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/cmd/fscrypt/strings.go -->
# sources/security-integrity/fscrypt/cmd/fscrypt/strings.go

## Purpose
Stores CLI usage strings, help templates, argument labels, and pluralization.

## APIs, Types, and Control Flow
Defines `shortUsage`, argument label constants, text templates for app, command, and subcommand help, `plurals`, and `pluralize`. Templates use the global indent from `format.go` and `urfave/cli` template data.

## State, Dependencies, and Integration
These constants shape all help and usage output. `pluralize` is reused in errors and status text.

## Risks and Test Signals
`pluralize` assumes every non-singular word exists in `plurals`; unknown words produce empty text. Help output changes affect CLI golden output and user docs.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/cmd/fscrypt/strings.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/crypto/crypto.go -->
# sources/security-integrity/fscrypt/crypto/crypto.go

## Purpose
Implements fscrypt cryptographic primitives: key wrapping/unwrapping, HMAC authentication, descriptor computation, and passphrase hashing.

## APIs, Types, and Control Flow
Exports `ErrBadAuth`, `ErrRecoveryCode`, `ErrMlockUlimit`, `Wrap`, `Unwrap`, `ComputeKeyDescriptor`, and `PassphraseHash`. Internal helpers validate lengths, stretch an internal key into encryption and authentication keys with HKDF-SHA256, run AES-256-CTR, and compute HMAC-SHA256.

`Wrap` validates a 32-byte wrapping key, allocates encrypted key data, generates random IV, stretches the wrapping key, encrypts the secret key with AES-CTR, and stores HMAC over IV and ciphertext. `Unwrap` repeats stretching, verifies HMAC with constant-time comparison, allocates a blank key, and decrypts. Descriptor v1 is first 8 bytes of double SHA-512; descriptor v2 is kernel-compatible HKDF-SHA512 with `fscrypt\0\x01` info. `PassphraseHash` runs Argon2id with configured time, memory, and parallelism and copies output into a locked key.

## State, Dependencies, and Integration
Crypto state is in-memory `Key` objects from `key.go`, with explicit wiping. Persistent wrapped data is represented by `metadata.WrappedKeyData`. Action-layer protectors and policies depend on these primitives for all key wrapping and descriptors.

## Risks and Test Signals
Length validation panics in low-level helpers but public wrapping returns errors for bad wrapping keys. HKDF is unsalted by design for key splitting and descriptor compatibility. `PassphraseHash` assumes costs were validated elsewhere. Tests cover key creation/wiping, wrapping integrity, descriptor vectors, passphrase vectors, invalid costs, and benchmarks.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/crypto/crypto.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/crypto/crypto_test.go -->
# sources/security-integrity/fscrypt/crypto/crypto_test.go

## Purpose
Comprehensive tests and benchmarks for key construction, memory locking toggles, randomness smoke checks, key wrapping/unwrapping, descriptors, and Argon2 passphrase hashing.

## APIs and Control Flow
Defines `ConstReader`, fixed fake keys, passphrase hash test vectors, and helpers for length checks, compression checks, distinct-buffer checks, and wrap/unwrap equality. Tests cover reader-based keys, wiping, invalid/zero lengths, mlock toggles, resizing, random key generation, large key allocation with `ErrMlockUlimit` tolerance, distinct derived outputs, wrap data lengths, fixed and random wrap/unwrap, variable secret lengths, wrong wrapping key lengths, randomized IVs, authentication failure on key/ciphertext/IV/HMAC modification, v1/v2 descriptor vectors, bad descriptor version, Argon2 vectors, and invalid hashing costs. Benchmarks cover wrap, unwrap with and without mlock, random wrap/unwrap, and passphrase hashing at several cost profiles.

## State, Dependencies, and Integration
Tests use real `Key` memory behavior, random generation, AES/HMAC/HKDF/Argon2 implementations, and metadata constants. Some tests toggle global `UseMlock`.

## Risks and Test Signals
The test vectors are strong regression signals for crypto compatibility. Randomness compression is only a smoke test. Global `UseMlock` toggles must be restored to avoid cross-test contamination.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/crypto/crypto_test.go -->
