# subset-b-008330 Research

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/src/reverse_fs.rs -->
# sources/security-integrity/encfs/src/reverse_fs.rs

Purpose: implements `ReverseFs`, a reverse-direction FUSE filesystem that presents an encrypted virtual view over a plaintext source tree. It is the opposite of `EncFs`: callers see encrypted names and ciphertext bytes while the backing directory stores plaintext.

Important APIs/types/functions: `ReverseFs::new` captures source path, cipher, config, in-memory config bytes, and config file metadata. `ReverseFileHandle` stores an open plaintext file plus the per-file IV used for virtual encryption. `resolve_source_path` decrypts each incoming FUSE path component and tracks chained directory IV state. `ciphertext_size_for_plaintext` and `read_encrypted` use `BlockLayout` and `BlockCodec` to map plaintext file reads into virtual ciphertext ranges. `metadata_to_filetype` and `system_time_from_metadata_secs` adapt Unix metadata to `fuse_mt` structures.

Control flow: FUSE `getattr`, `readdir`, `open`, `read`, and `readlink` translate encrypted virtual paths back to source paths, then either report transformed metadata or synthesize encrypted content. `read` special-cases `/.encfs7`, otherwise clones a handle under a mutex, drops the lock, bounds the request by computed ciphertext size, and encrypts only the requested blocks. `readdir` skips source dotfiles and adds a virtual root `.encfs7`.

State and persistence: the filesystem is read-only. Persistent state remains in the plaintext source tree; runtime state is limited to a mutex-protected file-handle map and atomic handle counter. The virtual config file is backed by `config_bytes`, `config_mtime`, `config_uid`, and `config_gid`, not a source path lookup.

Dependencies and integration points: depends on `fuse_mt`, `libc`, Unix metadata extensions, `SslCipher`, `BlockLayout`, and `BlockCodec`. It integrates with the `encfsr` binary and with forward `EncFs` for round-trip validation. It assumes `unique_iv=false` for reverse mode and uses `external_iv_chaining` to choose whether directory IVs feed file IV encryption.

Risks: `resolve_source_path` uses `to_str`, so non-UTF-8 encrypted path components return `EILSEQ`; this may be acceptable for EncFS name encodings but narrows byte-path compatibility. `read_encrypted` computes `end_block` as `(offset + size - 1) / block_size`, so callers must not pass `size=0`. Dotfile skipping hides all source dotfiles, not only config files. `metadata.blocks()` is reported from plaintext metadata even when virtual ciphertext size differs. Read-only operations return `EROFS`, but xattr read/list behavior is mixed (`ENODATA`/`ENOSYS`).

Test signals: covered by `encfsr_test.rs` for CLI gating and by `encfsr_live_test.rs` for encrypted readdir, ciphertext stat size, read-only write failure, path resolution, virtual config exposure, V6/V7 round-trips, symlink target encryption, and streaming.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/src/reverse_fs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/src/security.rs -->
# sources/security-integrity/encfs/src/security.rs

Purpose: provides process-level hardening helpers intended to reduce key-material exposure through core dumps, ptrace/proc memory reads, debugger attachment, and swap.

Important APIs/types/functions: `harden_process()` is the public startup hook and calls `disable_core_dumps()` plus `set_nondumpable()`. `lock_memory()` is a separate public hook that calls `mlockall(MCL_CURRENT | MCL_FUTURE)`. Platform-specific `set_nondumpable()` branches use Linux `prctl(PR_SET_DUMPABLE, 0)`, FreeBSD `procctl(PROC_TRACE_CTL_DISABLE)`, and macOS `ptrace(PT_DENY_ATTACH)`.

Control flow: each helper calls a libc primitive inside `unsafe`, checks for nonzero return codes, and logs warnings rather than returning errors or aborting. `harden_process()` intentionally does not call `lock_memory()`, leaving memory locking opt-in because it may require elevated limits or capabilities.

State and persistence: changes apply to the current process and, for `mlockall(MCL_FUTURE)`, future mappings. No repository or config state is persisted. Failure state is only logged.

Dependencies and integration points: depends on `libc` and `log::warn`. It should be called early in `main()` before sensitive keys are derived or loaded. It complements crypto code but does not wipe secrets itself.

Risks: warning-only failures can leave the process less hardened without preventing normal operation. `mlockall` can fail under default `RLIMIT_MEMLOCK`; tests or low-memory environments may observe warnings. The macOS `PT_DENY_ATTACH` behavior can disrupt debugging. No Windows equivalent is provided.

Test signals: this file has no direct tests in the subset. Its behavior is mostly platform integration and should be validated by startup smoke tests that assert no fatal regressions, plus manual or privileged checks for memory-lock/core-dump settings.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/src/security.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/tests/argon2_calibration_test.rs -->
# sources/security-integrity/encfs/tests/argon2_calibration_test.rs

Purpose: validates the timing model used for Argon2id calibration, ensuring time-cost increases when a low-cost derivation is too fast and remains unchanged when the configured derivation is already slow enough.

Important APIs/types/functions: both tests call `SslCipher::derive_key_argon2id(password, salt, memory_cost, time_cost, parallelism, key_len)`. `test_argon2_calibration_basic` measures one iteration, computes expected calibrated iterations for a one-second target, and asserts the arithmetic. `test_argon2_no_calibration_if_already_slow` measures a heavier parameter set and checks the simulated no-change path when it already exceeds one second.

Control flow: the first test skips the strong timing assertion if a single 8 MiB iteration is already unexpectedly slow, then runs the derived calibrated time cost and requires at least 300 ms as a tolerant lower bound. The second test only asserts equality when the initial 64 MiB, time-cost 3, parallelism 4 derivation exceeds one second; otherwise it prints that calibration would increase time cost.

State and persistence: no files are written. All state is local timing measurements and derived keys.

Dependencies and integration points: depends on `anyhow`, `SslCipher`, and wall-clock timing. It indirectly exercises the Argon2id dependency and default calibration assumptions used by config creation and password upgrades.

Risks: timing tests are inherently environment-sensitive. The basic test tolerates variability heavily, so it verifies arithmetic more than an exact security target. Slow or overloaded CI can turn these into no-op-ish paths.

Test signals: provides a performance-regression signal for Argon2 parameter calibration and a correctness signal that parameter changes actually invoke the KDF successfully.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/tests/argon2_calibration_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/tests/argon2_integration_test.rs -->
# sources/security-integrity/encfs/tests/argon2_integration_test.rs

Purpose: integration coverage for Argon2id-backed EncFS config creation, serialization, loading, cipher derivation, PBKDF2 backward compatibility, and parameter sensitivity.

Important APIs/types/functions: uses `EncfsConfig`, `ConfigType`, `Interface`, `KdfAlgorithm`, `SslCipher::new`, `derive_key_argon2id`, `encrypt_key`, `EncfsConfig::save`, `EncfsConfig::load`, and `EncfsConfig::get_cipher`. Constants `DEFAULT_ARGON2_MEMORY_COST`, `DEFAULT_ARGON2_TIME_COST`, and `DEFAULT_ARGON2_PARALLELISM` define expected defaults.

Control flow: `test_argon2id_config_creation_and_loading` derives a user key blob, encrypts a deterministic volume key, builds a V6 config marked `KdfAlgorithm::Argon2id`, saves to a temp XML file, reloads, asserts Argon2 fields, verifies correct password succeeds, and wrong password fails. `test_pbkdf2_backward_compatibility` loads `encfs6-std.xml` and asserts PBKDF2 fields remain the default for legacy XML. `test_argon2_parameter_sensitivity` derives keys with different memory/time costs and asserts each output differs.

State and persistence: writes a temporary XML config under `std::env::temp_dir()` and removes it. Fixture state is read-only.

Dependencies and integration points: integrates config serialization, KDF selection, OpenSSL cipher setup, and XML fixture parsing.

Risks: deterministic salts and keys are appropriate for tests but not production. The temp filename uses process id, so parallel test processes could collide if run in the same temp directory with identical pids in containers.

Test signals: strong regression signal for Argon2 schema round-trip, wrong-password authentication failure, and preservation of PBKDF2 compatibility.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/tests/argon2_integration_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/tests/config_check.rs -->
# sources/security-integrity/encfs/tests/config_check.rs

Purpose: asserts the `encfs` binary exits nonzero when invoked against a backing directory that lacks a config file.

Important APIs/types/functions: imports the shared `live` helper for unique temp directories and uses `std::process::Command` to run `CARGO_BIN_EXE_encfs`. The single test is `test_missing_config_returns_error`.

Control flow: creates a temp root with `mnt` and `backing`, runs `encfs -f <backing> <mount_point>`, cleans the temp root, then asserts the status is unsuccessful and includes stdout/stderr in the failure message.

State and persistence: creates and removes temporary directories. It does not mount through the live helper or require `ENCFS_LIVE_TESTS`; it invokes the binary directly and expects early validation failure.

Dependencies and integration points: depends on Cargo-provided binary path and the CLI config-loading path. It is an integration test for user-facing error behavior rather than internal config parsing.

Risks: if the binary blocks waiting for input before detecting missing config, the test may hang because `Command::output()` waits for completion. The `env!("CARGO_BIN_EXE_encfs")` fallback is compile-time and can fail outside Cargo integration-test contexts.

Test signals: guards against accidentally creating a new filesystem or mounting successfully when no `.encfs*` config exists.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/tests/config_check.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/tests/config_compatibility.rs -->
# sources/security-integrity/encfs/tests/config_compatibility.rs

Purpose: broad compatibility suite for EncFS config formats and encrypted fixture readability across V5 binary configs, V6 XML standard mode, and V6 XML paranoia mode.

Important APIs/types/functions: helper `load_and_verify_config` loads `EncfsConfig` and derives a cipher. `decrypt_path_result` adapts `EncFs::decrypt_path` error codes to `anyhow`. `read_and_hash_file` opens encrypted fixture files, decrypts path IV and file header, constructs `FileDecoder`, reads plaintext, and returns SHA1. Tests cover `test_v5_binary_config_format`, `test_v6_xml_config_format_standard`, `test_v6_xml_config_format_paranoia`, cipher/key-size/mode/feature/KDF/block-name checks, cross-version loading, and random-access read operations.

Control flow: each test selects fixture roots, loads config with password `test`, asserts config fields, derives `SslCipher`, constructs `EncFs`, decrypts known encrypted names, and often verifies SHA1 `4240880c2ecba8d2315bad8b27b8674cc59b268c` for `DESIGN.md`. Paranoia tests additionally assert nonzero path IV and block MAC handling.

State and persistence: reads fixture files only. No persistent writes occur.

Dependencies and integration points: depends on fixture layout under `tests/fixtures` and `tests/fixtures/encfs142`, SHA1 hashing, `FileDecoder`, and `EncFs` path decryption.

Risks: tests panic if fixtures are missing, so fixture packaging is required. Some tests duplicate setup and only verify available AES fixtures; Blowfish is acknowledged but not covered. Hash checks lock expected plaintext content.

Test signals: high-value compatibility signal for config parsing, KDF behavior, header IV derivation, block MAC stripping, chained/external IV features, and random-access file decode.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/tests/config_compatibility.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/tests/config_v5_save_test.rs -->
# sources/security-integrity/encfs/tests/config_v5_save_test.rs

Purpose: regression test ensuring V5 configs are not silently saved as V6 XML when their version field is modified.

Important APIs/types/functions: uses `EncfsConfig::load`, `EncfsConfig::save`, and `ConfigType::V5`. The single test is `test_v5_config_save_errors_correctly`.

Control flow: copies `tests/fixtures/encfs142/.encfs5` into a temp directory, loads it, asserts V5 type, mutates `version` to a newer V6-like value, then calls `save`. It expects an error containing "not yet implemented", asserts `.encfs6.xml` was not created, and verifies the original binary file does not start with an XML prolog.

State and persistence: creates a temp directory, copies a fixture, and removes the temp directory. It intentionally checks on-disk side effects after failed save.

Dependencies and integration points: depends on the V5 fixture and config save/load code. It protects the migration boundary between legacy binary configs and XML configs.

Risks: skips with `Ok(())` if the fixture is absent, so missing fixture coverage can hide regressions. The error-string assertion is brittle if wording changes.

Test signals: strong guard against destructive or misleading V5 save behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/tests/config_v5_save_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/tests/encfsr_live_test.rs -->
# sources/security-integrity/encfs/tests/encfsr_live_test.rs

Purpose: ignored live FUSE tests for `encfsr`, the reverse-mode binary backed by `ReverseFs`. It verifies encrypted virtual namespace behavior and ciphertext compatibility by mounting `encfsr` and, in round-trip cases, mounting forward `encfs` on top of the reverse mount.

Important APIs/types/functions: `make_encfsr_config`, `setup_source_dir`, `EncfsrMountGuard::mount`, `make_encfsr_config_with_mac`, `setup_block_boundary_files`, and `live_config_from_encfs` create fixtures and manage child processes. Tests include encrypted readdir, stat ciphertext sizing, EROFS writes, path resolution, V6 block-boundary round-trip, virtual `.encfs7`, external IV chaining, V7 AES-GCM-SIV round-trip, symlink round-trip, and multi-GB streaming.

Control flow: the guard checks `ENCFS_LIVE_TESTS`, unmount tools, spawns `encfsr --foreground --stdinpass`, drains output, writes password, polls `/proc/self/mountinfo`, and unmounts on drop. Tests create plaintext source directories, save configs, mount reverse view, inspect encrypted names or bytes, and optionally use `live::MountGuard` as a decrypting mount.

State and persistence: creates temp source and mount directories, writes configs and plaintext fixtures, and removes temp roots. Runtime process state is guarded by a global live lock.

Dependencies and integration points: depends on FUSE availability, Cargo `encfsr` binary, `/proc/self/mountinfo`, unmount tools, `EncfsConfig`, `SslCipher`, `BlockLayout`, and the shared live forward-mount harness.

Risks: ignored tests require privileges/environment and can be slow; the multi-GB test needs substantial disk and time. Mount readiness depends on Linux mountinfo and path canonicalization. Some assertions assume root directory IV 0 and known config properties.

Test signals: strongest end-to-end signal for `ReverseFs` correctness, especially streaming encrypted reads, read-only semantics, metadata sizing, V6/V7 compatibility, and symlink/config virtual file behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/tests/encfsr_live_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/tests/encfsr_test.rs -->
# sources/security-integrity/encfs/tests/encfsr_test.rs

Purpose: non-live CLI regression tests for the `encfsr` binary. They validate help/version output, argument parsing, config validation, and progress to mount-attempt code without requiring a working FUSE mount.

Important APIs/types/functions: `encfsr_bin`, `write_test_config`, `copy_std_fixture`, `write_v7_config`, `write_valid_encfsr_config`, and `run_encfsr`. Config helpers construct V6 PBKDF2 and V7 Argon2 configs with deterministic key material. Tests cover `--help`, `--version`, missing source directory, missing config file, rejection of `unique_iv=true`, acceptance of chained name IV when `unique_iv=false`, passthrough FUSE opts after `--`, and absence of the old "not yet implemented" placeholder.

Control flow: helpers create temp dirs/configs, spawn `encfsr` with optional stdin password, collect stdout/stderr, and assert status and error text. Some tests intentionally use missing source or mount directories so execution fails at a known validation/mount step.

State and persistence: writes temporary config files/directories and cleans them. It does not mount or require live environment.

Dependencies and integration points: depends on Cargo binary path, `EncfsConfig::standard_v7`, `set_v7_key`, config save, PBKDF2 derivation, and clap-style CLI parsing.

Risks: stderr substring assertions are brittle. Some helpers are dead code but document alternate config paths. Tests that expect a mount-attempt failure rely on the absence of a mount directory rather than mocking FUSE.

Test signals: guards user-facing reverse-mode CLI contract and config gating, especially `unique_iv=false` acceptance and trailing FUSE option parsing.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/tests/encfsr_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/tests/fixtures/encfs6-paranoia.xml -->
# sources/security-integrity/encfs/tests/fixtures/encfs6-paranoia.xml

Purpose: V6 XML EncFS fixture representing paranoia mode. It is used by compatibility and live tests to validate parsing, PBKDF2 key derivation, external IV chaining, and per-block MAC behavior.

Important data fields: `version` 20100713, creator `EncFS 1.9.5`, cipher `ssl/aes` major 3, name algorithm `nameio/block` major 4, `keySize` 256, `blockSize` 1024, `uniqueIV` 1, `chainedNameIV` 1, `externalIVChaining` 1, `blockMACBytes` 8, `allowHoles` 1, `encodedKeySize` 52, a 20-byte salt, `kdfIterations` 5711682, and `desiredKDFDuration` 3000.

Control flow role: the fixture is consumed by `EncfsConfig::load`; tests then derive a cipher with password `test`, decrypt known encrypted paths, use path IVs for file header decryption, and verify plaintext hashes or live mount behavior.

State and persistence: static fixture. It should remain byte-stable because expected hashes and encrypted filenames depend on its key material and mode bits.

Dependencies and integration points: integrates with V6 XML parser, AES-256 OpenSSL setup, PBKDF2, block-name decoding, `FileDecoder`, and `EncFs` external IV handling.

Risks: accidental edits break broad compatibility tests. High KDF iteration count can make tests slower. Because it contains test key material, it must not be mistaken for production secret handling.

Test signals: central fixture for paranoia mode tests in `config_compatibility.rs`, `live_mount.rs`, and reverse round-trip setup.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/tests/fixtures/encfs6-paranoia.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/tests/fixtures/encfs6-std.xml -->
# sources/security-integrity/encfs/tests/fixtures/encfs6-std.xml

Purpose: V6 XML EncFS fixture representing standard mode. It validates baseline compatibility for AES-192, block name encoding, unique IVs, chained name IVs, PBKDF2, and no block MAC overhead.

Important data fields: `version` 20100713, creator `EncFS 1.9.5`, cipher `ssl/aes` major 3, name algorithm `nameio/block` major 4, `keySize` 192, `blockSize` 1024, `plainData` 0, `uniqueIV` 1, `chainedNameIV` 1, `externalIVChaining` 0, `blockMACBytes` 0, `allowHoles` 1, `encodedKeySize` 44, a 20-byte salt, `kdfIterations` 1389869, and `desiredKDFDuration` 500.

Control flow role: loaded by config tests and live mount helpers, then used to derive a cipher with password `test`. Known encrypted names decrypt to fixture plaintext such as `DESIGN.md`, and file contents hash to expected values.

State and persistence: static fixture. It must be kept in sync with encrypted fixture data in the same directory.

Dependencies and integration points: exercises the XML parser, PBKDF2 KDF defaulting, AES-192, `EncFs::decrypt_path`, and file decode without block MAC bytes.

Risks: fixture drift breaks deterministic path/hash assertions. Its high PBKDF2 iteration count can be noticeable in test runtime. Tests assume the password is `test`.

Test signals: primary standard-mode fixture for compatibility, live mount, config backward-compatibility, and reverse-mode tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/tests/fixtures/encfs6-std.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/tests/legacy.rs -->
# sources/security-integrity/encfs/tests/legacy.rs

Purpose: focused legacy V5 decode test that loads a binary `.encfs5` fixture, derives a legacy cipher, decrypts a known encrypted path, and reads/decrypts file contents.

Important APIs/types/functions: `EncfsConfig::load`, `SslCipher::derive_key_legacy`, `EncfsConfig::get_cipher`, `EncFs::new`, `EncFs::decrypt_path`, `SslCipher::decrypt_header`, and `FileDecoder::new/read_at`.

Control flow: locates `tests/fixtures/encfs142/.encfs5`, loads config, prints diagnostic config details, derives legacy key material for visibility, builds `EncFs`, decrypts a hard-coded nested encrypted path, opens the encrypted file, decrypts its 8-byte header using path IV only if external IV chaining is enabled, streams content through `FileDecoder`, and asserts plaintext is valid UTF-8.

State and persistence: reads fixture files only. Output is diagnostic `println!` data for test logs.

Dependencies and integration points: depends on V5 binary config parser, legacy KDF, encrypted fixture path stability, `FileExt::read_at`, and file decoder compatibility with V5 metadata.

Risks: panics if fixture is missing. It checks content validity but not exact expected plaintext, so some semantic regressions could pass if output remains UTF-8.

Test signals: valuable smoke/regression signal for the legacy V5 load/decrypt path and legacy KDF integration.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/tests/legacy.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/tests/live/mod.rs -->
# sources/security-integrity/encfs/tests/live/mod.rs

Purpose: shared harness for ignored live FUSE tests. It gates live execution, creates temporary backing/mount directories, loads fixture config metadata, mounts the `encfs` binary, and cleans up.

Important APIs/types/functions: `LIVE_ENV`, `LiveConfig`, `LiveConfigKind`, `live_lock`, `live_enabled`, `manifest_dir`, `fixtures_dir`, `load_live_config`, `data_block_size`, `unique_temp_dir`, `path_has_tool`, `MountGuard::mount`, `MountGuard::mount_existing_backing_root`, `init_backing_root`, `list_non_dot_entries_recursive`, and `backing_single_ciphertext_file`.

Control flow: `MountGuard` checks `ENCFS_LIVE_TESTS`, serializes with a global mutex, copies the selected fixture to a backing root, spawns `encfs -f -S` with optional `-r`, writes the password to stdin, drains stdout/stderr into bounded tails, polls `/proc/self/mountinfo`, and unmounts via `fusermount3`, `fusermount`, or `umount` on drop.

State and persistence: creates temp directories using pid/time/counter; may preserve externally supplied backing roots until caller cleanup; holds child process state and mount status in the guard.

Dependencies and integration points: depends on Cargo `encfs` binary, Linux mountinfo, FUSE/unmount tools, fixture configs, `EncfsConfig`, and Unix paths.

Risks: Linux-specific mount detection; live tests can hang or fail under restricted CI. `init_backing_root` copies all fixture kinds to `.encfs6.xml`, so V7 behavior depends on consumers setting kind/path correctly. Cleanup is best-effort.

Test signals: enables the live suites to validate actual kernel/FUSE behavior rather than only direct trait calls.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/tests/live/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/tests/live_mount.rs -->
# sources/security-integrity/encfs/tests/live_mount.rs

Purpose: ignored end-to-end tests for the forward `encfs` FUSE mount. They exercise real kernel file operations against standard and paranoia configs.

Important APIs/types/functions: local helpers `require_live`, `pattern_bytes`, `read_all`, `read_range`, `libc_truncate`, `expected_physical_size`, and `ciphertext_single_file_size`. Major scenario helpers include `run_basic_io`, `run_truncate_matrix`, `run_truncate_extend_write_after_hole`, `run_rename_tests`, and `run_symlink_tests_standard`.

Control flow: tests mount through `live::MountGuard`, perform real filesystem operations (`write`, `seek`, `truncate`, `rename`, `symlink`, `chmod`, `utimensat`, `statvfs`, tar unpack), and compare plaintext reads plus backing ciphertext sizes. Several tests run the same scenario for standard and paranoia modes; others verify read-only mount `EROFS`, wrong password failure, invalid encrypted backing names skipped in readdir, and simplified pjd-fstest utime cases.

State and persistence: creates live mounts, backing roots, files, directories, symlinks, tar archives, and metadata changes; cleanup is handled by guards and explicit temp removal.

Dependencies and integration points: depends on FUSE, `encfs` binary, libc syscalls, `tar` crate, fixture configs, and the live harness. It validates integration beyond direct `FilesystemMT` method calls.

Risks: ignored by default because it needs `ENCFS_LIVE_TESTS=1`, mount permissions, unmount tools, and stable timing. Some tests allow implementation-specific errno ranges. Real kernel caching can affect rename visibility, so the strongest checks occur after remount.

Test signals: broadest forward-mount behavioral signal for data integrity, truncation/hole zero-fill, ciphertext sizing, rename remount persistence, symlink handling, metadata operations, read-only enforcement, and tar extraction.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/tests/live_mount.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/tests/mknod_test.rs -->
# sources/security-integrity/encfs/tests/mknod_test.rs

Purpose: verifies `EncFs::mknod` supports FIFO creation and reports named-pipe type correctly through `getattr` and `readdir`.

Important APIs/types/functions: `setup_fs` creates an `EncFs` with deterministic AES-192 key/IV and `EncfsConfig::test_default`. `req` creates a static `RequestInfo`. Tests use `FilesystemMT::mknod`, `getattr`, and `readdir`. `S_IFIFO` encodes POSIX FIFO mode.

Control flow: `test_mknod_fifo_getattr_returns_named_pipe` creates a FIFO, checks FUSE attributes for `FileType::NamedPipe` and permission bits, then inspects the encrypted backing entry with Unix `FileTypeExt::is_fifo`. `test_mknod_fifo_readdir_reports_named_pipe` creates a FIFO and asserts the plaintext virtual directory entry reports `NamedPipe`.

State and persistence: creates temporary root directories and backing FIFO nodes, then removes them.

Dependencies and integration points: depends on Unix FIFO support, encrypted name translation in `EncFs`, and metadata-to-FUSE file type mapping.

Risks: Unix-only behavior; special node creation may require platform support and could behave differently under restricted filesystems. The test only covers FIFOs, not block or character devices.

Test signals: guards special-file type preservation through creation, metadata, and directory listing.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/tests/mknod_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/tests/open_trunc_test.rs -->
# sources/security-integrity/encfs/tests/open_trunc_test.rs

Purpose: regression test for opening an existing encrypted file with `O_TRUNC`; the implementation must regenerate a valid 8-byte file header immediately and allow subsequent writes to decrypt correctly.

Important APIs/types/functions: directly uses `EncFs::create`, `write`, `release`, and `open` with `O_WRONLY | O_TRUNC`. Verification uses a separate `SslCipher`, `FileExt::read_at`, `SslCipher::decrypt_header`, and `FileDecoder`.

Control flow: creates a file, writes initial data, releases it, finds the encrypted backing file, asserts it is larger than the header, opens the virtual path with truncate flags, asserts physical size is exactly 8 bytes, writes new data, releases, decrypts the regenerated header and content, and compares plaintext with new data.

State and persistence: writes temporary encrypted backing data and removes the temp root.

Dependencies and integration points: validates interaction among open flags, header generation, file truncation, block encoding, and decoder compatibility.

Risks: finds the physical file by taking the first directory entry, which assumes only one backing file. Uses deterministic test keys and default config with external IV disabled.

Test signals: strong guard against corrupting empty/truncated encrypted files or leaving missing/zero headers after `O_TRUNC`.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/tests/open_trunc_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/tests/passwd_upgrade_test.rs -->
# sources/security-integrity/encfs/tests/passwd_upgrade_test.rs

Purpose: verifies password/KDF upgrade from PBKDF2-backed config data to Argon2id-backed config data while preserving the decrypted volume key.

Important APIs/types/functions: uses `EncfsConfig`, `ConfigType`, `Interface`, `KdfAlgorithm`, Argon2 constants, `SslCipher`, and `getrandom::fill`. The test derives a PBKDF2 user key, encrypts a deterministic volume key, builds a V6 config, decrypts it with the old password, re-encrypts the same volume key under Argon2id parameters and a new password, saves/reloads, and validates the new cipher.

Control flow: constructs cipher/name interfaces, salt, volume key/IV blob, and PBKDF2-encrypted key data for `test_password_123`. After verifying the original config works, it derives the old wrapping key, decrypts the volume blob, generates a fresh 20-byte salt, switches KDF metadata to Argon2id defaults, derives a new wrapping key for `new_password_456`, re-encrypts the volume blob, asserts the old password fails and the new password succeeds, then persists and reloads the config to assert `KdfAlgorithm::Argon2id`.

State and persistence: writes an upgraded temp config and cleans it up.

Dependencies and integration points: integrates KDF derivation, key wrapping, config schema fields, save/load, and `get_cipher`.

Risks: test uses deterministic volume material and simulated upgrade logic rather than invoking a dedicated CLI command, so it validates primitives more than command wiring. The temp filename is pid-based and could collide in unusual parallel runs.

Test signals: protects key-material continuity across KDF migration and checks Argon2 field persistence.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/tests/passwd_upgrade_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/tests/permissions_test.rs -->
# sources/security-integrity/encfs/tests/permissions_test.rs

Purpose: verifies file, directory, and symlink permission reporting/creation behavior in `EncFs`.

Important APIs/types/functions: `setup_fs`, `req`, `FilesystemMT::mkdir`, `create`, `release`, `symlink`, and `getattr`. Unix `MetadataExt::mode` checks backing permissions for some cases.

Control flow: directory tests create modes such as 0700, 0750, 0755, and 0500 and check backing metadata or virtual attrs. File tests create modes such as 0600, 0640, 0644, 0400, and 0755, release handles, then verify modes. Symlink tests assert `FileType::Symlink` and permission bits 0777. The mixed test creates a directory, file, and symlink in one tree and verifies each type retains its expected mode.

State and persistence: creates temporary encrypted backing entries and removes them. Tests are sensitive to actual filesystem permissions and umask, so selected modes avoid common umask-cleared bits.

Dependencies and integration points: depends on Unix permission APIs, encrypted path mapping, `getattr` mode reporting, and creation code applying requested modes.

Risks: comments note `DirBuilder::mode` and `OpenOptions::mode` can be umask-affected; this is why mode cases are conservative. Symlink permission semantics vary by Unix platform, but the test expects 0777.

Test signals: guards against permission regression in `mkdir`, `create`, `symlink`, and `getattr` for mixed directory contents.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/tests/permissions_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/tests/rename_symlink_in_dir_test.rs -->
# sources/security-integrity/encfs/tests/rename_symlink_in_dir_test.rs

Purpose: regression tests for renaming directories that contain symlinks when chained name IV is enabled. The target bug was recursive directory copy/rename failing or not re-encrypting symlink targets correctly.

Important APIs/types/functions: `setup_fs` creates default `EncFs` with chained name IV, `req` supplies request metadata, and tests use `mkdir`, `symlink`, `create`, `release`, `readlink`, `rename`, and `getattr`.

Control flow: `test_rename_directory_containing_symlink_with_chained_name_iv` creates `/parent` with a symlink and file, validates readlink before rename, renames to `/renamed_parent`, then validates readlink, old path absence, and regular file presence. `test_rename_nested_directory_with_symlinks_chained_name_iv` creates `/outer/inner` with symlinks at both levels, renames `/outer` to `/moved`, and verifies both symlink targets still decrypt to the original relative targets.

State and persistence: creates temp backing trees and removes them.

Dependencies and integration points: depends on directory rename implementation, recursive copy/delete behavior, symlink encryption/decryption, and name-IV recalculation.

Risks: uses direct trait calls rather than a kernel mount, so it does not cover lookup cache effects. Only default config is tested.

Test signals: high-value integrity signal for directory rename with symlink children under IV-chained name encryption.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/tests/rename_symlink_in_dir_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/tests/symlink_type_test.rs -->
# sources/security-integrity/encfs/tests/symlink_type_test.rs

Purpose: verifies symlinks created through `EncFs::symlink` are reported as `FileType::Symlink` by both `getattr` and `readdir`.

Important APIs/types/functions: constructs deterministic `SslCipher` and `EncFs`, then uses `FilesystemMT::symlink`, `getattr`, and `readdir`.

Control flow: creates a temp root, creates a symlink named `mysymlink` to `target_file`, calls `getattr` on the virtual path and asserts `attr.kind == FileType::Symlink`, then lists the parent directory and asserts the matching directory entry also has kind `Symlink`.

State and persistence: writes one encrypted backing symlink under temp root, then removes the root.

Dependencies and integration points: depends on symlink creation, encrypted name mapping, metadata conversion, and directory entry type reporting.

Risks: direct trait-level test only; live symlink behavior is separately covered. It assumes Unix symlink support.

Test signals: focused regression for a prior bug where symlinks were reported as regular files.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/tests/symlink_type_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/tests/truncate_corrupt_test.rs -->
# sources/security-integrity/encfs/tests/truncate_corrupt_test.rs

Purpose: regression tests for encrypted file truncation and extension around partial blocks, MAC tags, and sparse/hole behavior.

Important APIs/types/functions: uses deterministic `EncFs` setup, `create`, `write`, `truncate`, `release`, `FileExt::read_at`, `SslCipher::decrypt_header`, and `FileDecoder`.

Control flow: `test_truncate_corrupts_partial_block` writes 1074 bytes, releases, truncates to 500 bytes, decrypts the physical file, and asserts the remaining plaintext equals the original prefix. It targets corruption caused by decrypting a formerly full CBC block as a partial block. `test_truncate_extend_then_append_preserves_block0_tag` enables `allow_holes`, writes a partial block payload, extends to two data blocks, appends after the hole, then decrypts and asserts original prefix, zero-filled hole, and appended payload.

State and persistence: writes temporary backing files and removes temp roots.

Dependencies and integration points: exercises block encoder/decoder, file headers, logical/physical size translation, MAC tag preservation, and hole zero-fill semantics.

Risks: physical file discovery assumes a single backing entry. Tests use fixed 1024 block size and 8 MAC bytes via defaults.

Test signals: strong data-integrity guard for truncation bugs that can silently corrupt encrypted contents.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/tests/truncate_corrupt_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/tests/unique_iv_check.rs -->
# sources/security-integrity/encfs/tests/unique_iv_check.rs

Purpose: ensures V6 XML configs with `<uniqueIV>0</uniqueIV>` are accepted by `EncfsConfig::load`.

Important APIs/types/functions: writes an inline XML config to a temp file and calls `EncfsConfig::load`, then checks `config.unique_iv == false`.

Control flow: the test builds an XML string with AES-192, block name encoding, `uniqueIV` 0, chained name IV 1, external IV chaining 0, no MAC bytes, PBKDF2 fields, and encoded key/salt data. It writes the file, loads it, removes it, and asserts successful parse with false unique IV.

State and persistence: temporary XML file only.

Dependencies and integration points: validates config parser and validation rules used by reverse mode, because `encfsr` requires `unique_iv=false`.

Risks: only parsing is tested; it does not derive the cipher or mount/read with this inline config. XML fixture key material is copied from a test source.

Test signals: guards against overly strict validation rejecting reverse-compatible configs.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/tests/unique_iv_check.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/tests/write_compat_test.rs -->
# sources/security-integrity/encfs/tests/write_compat_test.rs

Purpose: verifies write compatibility across legacy-like and paranoia-like configurations, plus `fstat` and `statfs` behavior.

Important APIs/types/functions: `setup_test_fs` parameterizes AES major version, key size, block size, block MAC bytes, chained name IV, and external IV chaining. Tests use `create`, `write`, `getattr`, `unlink`, `release`, `statfs`, and manual `FileDecoder` verification.

Control flow: `test_write_legacy_v2` writes and decrypts data with major 2, AES-192, no chained IV, no MAC. `test_write_paranoia` writes under AES-256, 8-byte MAC, chained and external IV, recovers filename IV from encrypted backing name, then decrypts header/content. `test_fstat_support` validates size through handle and path, then unlinks while open and confirms handle-based getattr still works while path getattr fails. `test_statfs_support` checks root statfs returns plausible values.

State and persistence: creates temp roots and encrypted backing files, then removes them.

Dependencies and integration points: covers write path, header IV handling, name IV derivation, handle table semantics, unlink-open behavior, and statvfs translation.

Risks: uses synthetic configs rather than historical fixtures for legacy write. Directory entry discovery assumes a small controlled temp root.

Test signals: important compatibility signal for writes across config modes and for POSIX-style metadata behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/tests/write_compat_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/tests/write_test.rs -->
# sources/security-integrity/encfs/tests/write_test.rs

Purpose: basic direct-driver write test for `EncFs`, validating create/write/reopen persistence by decrypting the physical encrypted file manually.

Important APIs/types/functions: constructs `EncfsConfig`, `SslCipher`, and `EncFs`; uses `create`, `write`, `release`, `open`; verifies via `FileExt::read_at`, `SslCipher::decrypt_header`, and `FileDecoder`.

Control flow: creates temp root, configures AES-192 with deterministic key/IV and MAC bytes 8, creates `test.txt`, writes `hello world`, locates the encrypted file, decrypts the header with external IV 0, decodes content, releases the handle, opens the virtual path again, and re-decodes to ensure persistence.

State and persistence: writes one encrypted backing file and removes the temp root.

Dependencies and integration points: validates the write path, file header generation, block MAC layout, and path encryption enough for reopen.

Risks: verification locates the first backing entry rather than deriving the encrypted path. It tests a single small write and does not cover partial overwrite or multi-block behavior.

Test signals: foundational smoke test for encrypted write/readback at the trait level.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/tests/write_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/encfs/tests/xattr_test.rs -->
# sources/security-integrity/encfs/tests/xattr_test.rs

Purpose: verifies extended attribute support through `EncFs`: setting, getting, listing, removing, on-disk name prefixing, binary/empty/unicode values, and round trips.

Important APIs/types/functions: `setup_fs`, `req`, `create`, `release`, `setxattr`, `getxattr`, `listxattr`, `removexattr`, and `fuse_mt::Xattr`. `test_xattr_on_disk_storage` uses libc `llistxattr` and `OsStrExt` to inspect backing attributes.

Control flow: tests create a file, apply multiple xattrs in namespaces such as `user`, `security`, and `trusted`, retrieve data, parse null-separated list output, remove attrs, and verify absence. The disk-storage test checks raw backing xattr names start with `user.encfs.`. The round-trip test includes binary bytes, empty values, and UTF-8 bytes.

State and persistence: writes xattrs to temporary encrypted backing files and removes temp roots.

Dependencies and integration points: depends on OS xattr support, permissions for non-user namespaces, encrypted xattr naming/value logic, and FUSE xattr response conventions.

Risks: `security.*` and `trusted.*` attributes may require privileges or be unsupported on some filesystems. The test assumes xattr APIs are available and that `getxattr(..., size=0)` returns data, not only size.

Test signals: broad coverage for xattr translation and cleanup, with an extra privacy signal that raw names are stored under an EncFS-specific prefix.
<!-- END_FILE_RESEARCH: sources/security-integrity/encfs/tests/xattr_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/.github/workflows/ci.yml -->
# sources/security-integrity/fscrypt/.github/workflows/ci.yml

Purpose: GitHub Actions CI definition for `fscrypt`, covering Go builds, 32-bit build, integration tests, cgroup integration, CLI tests, generated-code checks, formatting, and linting.

Important jobs: `build` runs `make` across Go 1.23, 1.24, and 1.25. `build-32bit` builds with `CGO_ENABLED=1 GOARCH=386` and i386 PAM headers. `run-integration-tests` installs filesystem/key dependencies, runs `make test-setup`, links keyrings with `keyctl link @u @s`, then runs `make test` and teardown. `test-cgroup-integration` builds a package test binary and runs it inside Docker with CPU/memory constraints. `run-cli-tests` installs `expect` and runs `make cli-test`. `generate-format-and-lint` runs `make tools`, `make gen`, `make format`, `make lint`, and file-change checks.

Control flow: workflow triggers on pushes and pull requests to `master`. Jobs run independently on Ubuntu latest with checkout and setup-go. A commented architecture matrix documents why qemu-based integration is disabled.

State and persistence: CI creates build outputs, loopback test filesystems, Docker containers, generated files, and tool binaries within runner workspace; no repo state persists except job artifacts/logs.

Dependencies and integration points: depends on GitHub Actions, apt packages (`libpam0g-dev`, `e2fsprogs`, `keyutils`, `shellcheck`, etc.), Docker, Go toolchain, Makefile targets, kernel fscrypt/keyctl support.

Risks: `actions/setup-go@v2` is old even while using new Go versions. Integration jobs require privileged kernel features that may shift on hosted runners. `make test-teardown` is not guarded with `always()`, so failure before teardown may leave runner-local mounts until VM cleanup.

Test signals: defines the authoritative CI coverage expected for fscrypt source changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/.github/workflows/ci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/Makefile -->
# sources/security-integrity/fscrypt/Makefile

Purpose: central build, test, generation, lint, coverage, install, and tool-bootstrap logic for `fscrypt` and `pam_fscrypt`.

Important targets/variables: `VERSION`, `NAME`, `PAM_NAME`, `BIN`, `PAM_MODULE`, `CFLAGS`, `GO_LINK_FLAGS`, `VERSION_FLAG`, `FILES`, `GO_FILES`, `C_FILES`, `PROTO_FILES`. Build targets produce `bin/fscrypt` and `bin/pam_fscrypt.so`. `gen` runs protoc, `format` runs goimports and clang-format, `lint` runs go vet/staticcheck/misspell/shellcheck, `test` runs `go test -p 1 ./...`, `test-setup` creates/mounts an ext4 image with encryption, `cli-test` runs sudo CLI tests, `coverage.out` merges per-package coverage, and install targets place binaries, PAM module/config, and bash completion.

Control flow: `default` builds binary and PAM module; `all` runs tools, generation, default, format, lint, and tests. Build commands add git tag or fallback version into `main.version`, apply `-trimpath` if supported, and pass C flags through cgo. Tool targets build Go helpers or download/copy `protoc` based on architecture.

State and persistence: writes under `bin`, `/tmp/fscrypt-image`, `/tmp/fscrypt-mount`, installation prefixes, coverage files, and generated protobuf files. `test-setup` uses sudo mount; `test-teardown` unmounts and deletes.

Dependencies and integration points: integrates Go modules, cgo, PAM, m4, protobuf, ext4 fscrypt support, shellcheck, staticcheck, misspell, goimports, clang-format, sudo, and CLI test scripts.

Risks: `TAG_VERSION := $(shell git describe --tags)` can fail noisily without tags. `test-setup` assumes sudo and loop mounts are available. Downloading `protoc` during builds requires network. Install paths default to `/usr/local` and may need root.

Test signals: Makefile targets are the CI contract and local developer entry points for build correctness, generated-file cleanliness, and integration test setup.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/actions/callback.go -->
# sources/security-integrity/fscrypt/actions/callback.go

Purpose: defines callback interfaces used by fscrypt actions to obtain keys from callers and choose protectors for unlocking policies.

Important APIs/types/functions: `ProtectorInfo` wraps `metadata.ProtectorData` and exposes read-only accessors `Descriptor`, `Source`, `Name`, and `UID`. `KeyFunc` asks the caller for a passphrase or raw 256-bit key, with a retry flag. `getWrappingKey` returns raw keys directly for `SourceType_raw_key` and otherwise hashes passphrases with `crypto.PassphraseHash`. `unwrapProtectorKey` loops until `crypto.Unwrap` succeeds, the callback errors, or a non-auth error occurs. `ProtectorOption` augments `ProtectorInfo` with `LinkedMount` and `LoadError`. `OptionFunc` lets callers choose a protector option by index.

Control flow: unwrapping starts with `retry=false`, obtains a wrapping key, attempts unwrap, wipes the wrapping key, returns protector key on success, sets retry on `crypto.ErrBadAuth`, and propagates other errors. Passphrase inputs are wiped after hashing.

State and persistence: no persistence. Sensitive callback-returned keys are expected to be wiped by consumers; this file explicitly wipes passphrases after hashing and wrapping keys after unwrap.

Dependencies and integration points: depends on `crypto`, `filesystem`, `metadata`, `github.com/pkg/errors`, and `log`. It is a core action-layer abstraction between UI/CLI prompting and metadata/key unwrapping.

Risks: raw key sources trust the callback to return correctly sized high-entropy keys. `unwrapProtectorKey` can loop indefinitely if the callback keeps returning wrong keys without error. Logging protector descriptors may be useful for diagnostics but is metadata exposure.

Test signals: no direct tests in this subset, but behavior should be covered by action tests that simulate wrong passphrase retry, callback errors, raw key sources, passphrase wiping, and option selection.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/actions/callback.go -->
