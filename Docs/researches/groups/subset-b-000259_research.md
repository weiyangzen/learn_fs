# Group Research: subset-b-000259

This grouped report covers the subset-b-000259 OSTree test sources. Each file section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-export.sh -->
# sources/cloud-native/ostree/tests/test-export.sh

## Purpose
`test-export.sh` validates the `ostree export` tar path for libarchive-enabled builds. It checks whole-commit exports, `--subpath`, `--prefix`, combined prefix/subpath behavior, tar round-trip import, and preservation of hard-link relationships.

## Important APIs, Types, And Functions
The script uses `libtest.sh`, `skip_without_ostree_feature libarchive`, `setup_test_repository "archive"`, `ostree export`, `ostree commit --tree=tar=...`, `ostree diff --no-xattrs`, `tar xf`, `tar tvf`, and assertion helpers such as `assert_file_empty` and `assert_file_has_content`.

## Control Flow
It creates a no-xattr commit from `test2`, exports it in four layout variants, extracts each tarball, and diffs extracted trees against either the source commit or expected subdirectory. It then exports the original `test2`, imports it back as `test2-from-tar`, diffs the commits, and finally inspects the tar manifest for hard links under `baz/sub1` and `baz/sub2`.

## State And Persistence
All state is temporary under `test_tmpdir`: checkout directories, tarballs, extracted directories, `diff.txt`, and a tar manifest. Persistent OSTree state is limited to test refs in the temporary archive repo.

## Dependencies And Integration Points
Coverage crosses the CLI export command, libarchive tar writer, commit importer from tar, checkout/diff logic, hard-link metadata, and the common shell test harness.

## Risks And Test Signals
The test is sensitive to tar implementation output for hard-link manifest strings and to xattr support, so no-xattr comparisons are used for layout checks. Passing TAP output means exported trees match exactly, prefix/subpath do not shift content incorrectly, tar import preserves commit content, and hard links are emitted as links rather than duplicate files.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-export.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-find-remotes.sh -->
# sources/cloud-native/ostree/tests/test-find-remotes.sh

## Purpose
`test-find-remotes.sh` exercises `ostree find-remotes` for collection-aware repositories and GPG-verified file remotes. It verifies discovery, reporting, keyring selection, mirror refs, and optional pulling of found refs.

## Important APIs, Types, And Functions
The script depends on `gpgme`, `ostree_repo_init --collection-id`, signed commits and summaries, `remote add --collection-id --gpg-import`, `pull`, `pull --mirror`, `refs --collections`, `find-remotes --finders=config`, and `find-remotes --pull`.

## Control Flow
It creates two upstream collection repos with different collection IDs and keys, pulls one app and one OS ref into a normal local repo, and mirrors them into a mirror repo where collection refs land under `refs/mirrors`. For both local forms it runs `find-remotes` with one ref, multiple refs, new refs, and missing refs, then repeats the scenarios with `--pull`. Later it updates the OS collection and validates update discovery, and covers mismatched or absent results.

## State And Persistence
Temporary repos include `apps-collection`, `os-collection`, `local`, and `local-mirror`. State is stored in ref files, collection binding metadata, imported trusted keyrings, signed summaries, and checksum scratch files.

## Dependencies And Integration Points
This test integrates remote configuration, collection ID metadata, summary signatures, GPG key import, ref namespaces, and the finder/puller code paths which convert discovered collection refs into local refs.

## Risks And Test Signals
Output assertions are detailed and therefore sensitive to CLI wording, result ordering, and keyring filenames. Passing signals include correct `(collection, ref)` rendering, correct "not found" handling, no false "No results", successful pulls for found refs, and mirror repos preserving collection mirror ref locations.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-find-remotes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-fsck-collections.sh -->
# sources/cloud-native/ostree/tests/test-fsck-collections.sh

## Purpose
`test-fsck-collections.sh` validates `ostree fsck` consistency checks for collection refs, collection binding metadata, ref binding metadata, and back-reference validation.

## Important APIs, Types, And Functions
Helpers `set_up_repo_with_collection_id` and `set_up_repo_without_collection_id` create repos and commits with binding metadata. The script uses `ostree fsck`, `fsck --verify-bindings`, `fsck --verify-back-refs`, `refs --collections`, direct ref-file deletion, and commit-object counts.

## Control Flow
The test first checks a repo with a collection ID, deletes ordinary heads or mirror refs, and ensures fsck notices missing binding references only when the relevant verification mode is enabled. It then mutates remote collection IDs and requested refs to provoke binding failures. A second repo without a collection ID checks ordinary ref binding behavior and back-reference failures for missing refs.

## State And Persistence
The test mutates temporary repository state directly, including `refs/heads`, `refs/mirrors`, remote config, and commit metadata. Commit objects persist across ref deletions so fsck can validate reachability and binding relationships.

## Dependencies And Integration Points
It covers fsck's integration with commit metadata fields for ref and collection bindings, collection-aware ref namespaces, remote collection configuration, and repository object enumeration.

## Risks And Test Signals
The test relies on exact diagnostic messages for binding mismatches. Passing signals include `Validating refs...` and `Validating refs in collections...` phases appearing as expected, missing refs causing failures under verification flags, and normal fsck staying tolerant where binding checks are not requested.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-fsck-collections.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-fsck-delete.sh -->
# sources/cloud-native/ostree/tests/test-fsck-delete.sh

## Purpose
`test-fsck-delete.sh` verifies `ostree fsck --delete` behavior when repository objects are missing or corrupt enough to leave commits invalid. It checks both detection and cleanup.

## Important APIs, Types, And Functions
The script uses `ostree_repo_init`, `ostree commit`, `ostree pull-local`, direct object-file removal, `ostree fsck`, `ostree fsck --delete`, and assertions over stdout and stderr.

## Control Flow
It creates a source repo and a target repo, pulls a commit locally, removes one object from the target, and confirms plain fsck fails. It then runs fsck with `--delete`, expects diagnostics about deleting invalid commits, runs fsck again to confirm only the expected object error remains, restores or re-pulls state, and verifies final clean fsck output.

## State And Persistence
Temporary repos `f1`, `f2`, and working directories hold commits and object files. The core state transition is direct deletion of an object followed by fsck deleting invalid commit references or objects.

## Dependencies And Integration Points
This test integrates object storage layout, commit reachability, pull-local replication, fsck validation, and repair/delete semantics.

## Risks And Test Signals
Direct object deletion makes the test sensitive to object layout and selected file globbing. Passing signals include a failing fsck before repair, `--delete` returning failure while deleting invalid data, subsequent reduced error output, and eventually a clean fsck with empty stderr.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-fsck-delete.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-gpg-signed-commit.sh -->
# sources/cloud-native/ostree/tests/test-gpg-signed-commit.sh

## Purpose
`test-gpg-signed-commit.sh` is broad CLI coverage for GPG-signed commits. It validates adding, displaying, duplicating, deleting, and verifying commit signatures across normal, missing-key, expired-key, expired-subkey, missing-subkey, and revoked-key cases.

## Important APIs, Types, And Functions
The script uses `skip_without_ostree_feature gpgme`, `which_gpg`, `ostree gpg-sign`, `ostree show`, `ostree commit --gpg-sign --gpg-homedir`, `ostree show --gpg-homedir`, `gpg --quick-generate-key`, `--quick-add-key`, `--quick-set-expire`, `--export`, and test key IDs from `libtest.sh`.

## Control Flow
The first phase signs an existing commit, verifies show output, rejects duplicate signatures, signs with multiple keys, and deletes signatures one at a time and all at once. The second phase creates an isolated GPG home, generates primary keys and subkeys, exports a trusted keyring, signs a commit with combinations of keys, and changes key state to force missing public key, expired primary key, expired subkey, missing subkey, and revocation diagnostics.

## State And Persistence
State lives in temporary GPG homes, trusted keyring directories, generated revocation certificates, exported keyrings, and commit signature metadata in the test repo. Cleanup removes the temporary GPG home unless skipped by the harness.

## Dependencies And Integration Points
It integrates OSTree commit signing and signature display with GPGME/GnuPG trust and key status behavior. It also depends on version-specific GnuPG support for subkey expiration.

## Risks And Test Signals
The test is sensitive to installed GnuPG features, exact diagnostic wording, and local clock/key-expiration handling. Passing signals include correct signature counts, duplicate rejection, deletion counts, good/bad signature classification, primary key ID reporting, and correct skip behavior when subkey expiration is unsupported.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-gpg-signed-commit.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-gpg-verify-result.c -->
# sources/cloud-native/ostree/tests/test-gpg-verify-result.c

## Purpose
`test-gpg-verify-result.c` unit-tests `OstreeGpgVerifyResult`, the object that exposes GPGME verification details to OSTree callers. It validates counts, lookup, per-signature attributes, and valid-signature requirements across multiple signature states.

## Important APIs, Types, And Functions
Important helpers include `assert_no_gpg_error`, `assert_str_contains`, `TestFixture`, `test_fixture_setup`, and `test_fixture_teardown`. The tests call `ostree_gpg_verify_result_count_all`, `count_valid`, `lookup`, `get`, `get_all`, and `require_valid_signature`. GPGME APIs include `gpgme_data_new_from_file`, `gpgme_data_write`, `gpgme_op_verify`, and `gpgme_op_verify_result`.

## Control Flow
The fixture points `GNUPGHOME` at `tests/gpg-verify-data`, loads `lgpl2` plus either the full detached signature or selected signature fragments, runs `gpgme_op_verify`, and attaches the referenced verify result to the fixture. Individual tests inspect tuple type strings, common attributes, valid/expired/revoked/missing states, lookup by full and abbreviated fingerprint, and error text from `require_valid_signature`.

## State And Persistence
The test is read-only except for process environment updates. Verification state is held in the fixture's `OstreeGpgVerifyResult`, GPGME data buffers, and referenced `gpgme_verify_result_t`.

## Dependencies And Integration Points
It uses private OSTree GPG headers, GPGME, GLib test fixtures, and static test key/signature data. It validates the low-level result object used by CLI show, pull verification, and other signature reporting paths.

## Risks And Test Signals
The test depends on stable GPGME status interpretation and fixture files. Passing signals include expected all/valid counts, lowercase fingerprint lookup, exact `GVariant` tuple shape, correct fallback names for missing keys, and failure messages for expired, revoked, missing, or expired-signature cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-gpg-verify-result.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-help.sh -->
# sources/cloud-native/ostree/tests/test-help.sh

## Purpose
`test-help.sh` recursively verifies that OSTree CLI commands and subcommands expose usable help and usage output. It is a smoke test for command table wiring.

## Important APIs, Types, And Functions
The script defines `test_usage_output` and `test_recursive`, invokes `${CMD_PREFIX} ostree ... --help`, parses "Builtin Commands:" and subcommand sections, and uses shell conditionals plus TAP output.

## Control Flow
`test_recursive` walks command help text, finds listed subcommands, and recursively checks each subcommand's help. `test_usage_output` asserts usage/help content for the command being inspected. The script tracks whether expected subcommand sections were found and fails if the command tree cannot be traversed.

## State And Persistence
State is transient shell variables and captured help text. No repository or filesystem state is modified beyond temporary output files if the harness uses them.

## Dependencies And Integration Points
This test integrates the main `ostree` command dispatcher, builtin subcommand tables, option parser help generation, and shell parsing assumptions about help formatting.

## Risks And Test Signals
The test is intentionally wording-sensitive because it guards the user-facing help structure. Passing the single TAP test signals that top-level and nested commands accept `--help`, print usage information, and expose parseable subcommand lists.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-help.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-include-ostree-h.c -->
# sources/cloud-native/ostree/tests/test-include-ostree-h.c

## Purpose
`test-include-ostree-h.c` verifies that the public umbrella header `<ostree.h>` is self-contained and usable from C code.

## Important APIs, Types, And Functions
The file includes `config.h`, GLib, locale support, and `<ostree.h>`. Its `main` initializes locale/test infrastructure and returns GLib test status.

## Control Flow
There is minimal runtime flow; the build and compile step are the primary test. If the public header has missing dependencies, incompatible declarations, or ordering issues, compilation fails before execution.

## State And Persistence
No persistent state is created. Runtime state is limited to standard process initialization.

## Dependencies And Integration Points
This is a public API integration test for consumers including only `<ostree.h>` rather than private headers. It depends on installed/public include paths and GLib.

## Risks And Test Signals
The main risk is accidentally introducing a public header dependency that is not pulled in by the umbrella header. Passing compilation and execution indicates the exported C API remains include-safe for downstream applications.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-include-ostree-h.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-init-collections.sh -->
# sources/cloud-native/ostree/tests/test-init-collections.sh

## Purpose
`test-init-collections.sh` verifies repository initialization with a collection ID.

## Important APIs, Types, And Functions
It uses `ostree_repo_init repo --collection-id org.example.Collection` and `assert_file_has_content` against `repo/config`.

## Control Flow
The script creates a temporary repo, initializes it with a collection ID, and checks that the generated config contains the expected `collection-id` entry.

## State And Persistence
State is the temporary `repo` directory and its config file. No commits or objects are created.

## Dependencies And Integration Points
It covers the repository init helper in `libtest.sh` and the underlying `ostree init` collection configuration path consumed by collection-aware refs, fsck, pull, and find-remotes.

## Risks And Test Signals
The test is narrow and config-format-sensitive. Passing confirms collection IDs are persisted during init and available to later collection-aware operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-init-collections.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-kargs.c -->
# sources/cloud-native/ostree/tests/test-kargs.c

## Purpose
`test-kargs.c` unit-tests `OstreeKernelArgs`, including append, delete, replace, duplicate handling, empty values, key-only arguments, and quoted values with spaces.

## Important APIs, Types, And Functions
Tests call `ostree_kernel_args_new`, `append`, `delete`, `new_replace`, `to_strv`, cleanup support, and private inspection helpers `_ostree_kernel_arg_get_kargs_table`, `_ostree_kernel_arg_get_key_array`, `_ostree_kernel_args_entry_get_key`, and `_get_value`. Utility predicates compare keys and values inside GLib arrays/hash tables.

## Control Flow
`test_kargs_append` populates a kernel-args object and checks internal tables and emitted string vectors. `test_kargs_delete` checks missing-key failures, deletion by key, deletion by key/value, duplicates, no-value entries, and multi-token quoted inputs. `test_kargs_replace` checks invalid replacements, ambiguous multi-value replacement failure, and successful key/value replacement.

## State And Persistence
All state is in-memory inside `OstreeKernelArgs`, with GLib containers representing ordered args and key-to-values mappings. No persistent files are used.

## Dependencies And Integration Points
The file tests private kernel argument parsing used by deployment and bootloader code that mutates kernel command lines.

## Risks And Test Signals
Kernel arg parsing is whitespace- and quote-sensitive. Passing signals include correct differentiation between missing value and empty string, consistent table/vector updates after deletion, duplicate removal one entry at a time, and error propagation through `G_IO_ERROR_FAILED`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-kargs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-keyfile-utils.c -->
# sources/cloud-native/ostree/tests/test-keyfile-utils.c

## Purpose
`test-keyfile-utils.c` validates OSTree helper functions around `GKeyFile`: defaults for missing booleans/strings, optional sections, group copying, and tristate parsing.

## Important APIs, Types, And Functions
The tests exercise `ot_keyfile_get_boolean_with_default`, `ot_keyfile_get_value_with_default`, `ot_keyfile_get_value_with_default_group_optional`, `ot_keyfile_copy_group`, and `_ostree_parse_tristate`. `fill_keyfile` constructs the shared `GKeyFile`.

## Control Flow
Each test sets up expected calls and assertions. Invalid argument cases temporarily disable GLib fatal logging so `g_return_val_if_fail` paths can be checked. Group copy compares key counts and values. Tristate parsing accepts `maybe`, yes/no spellings, `1/0`, true/false, and rejects `foobar`.

## State And Persistence
State is a process-global `GKeyFile *g_keyfile` populated in `main`; temporary key files are in memory only. No disk persistence occurs.

## Dependencies And Integration Points
These helpers are used by OSTree config parsing, remote configuration, and option parsing. The test integrates with GLib error and logging behavior.

## Risks And Test Signals
The test catches regressions in default behavior for absent keys/sections and invalid input handling. Passing signals include no leaked fatal warnings, exact copied values, and correct `OtTristate` outputs.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-keyfile-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-libarchive-import.c -->
# sources/cloud-native/ostree/tests/test-libarchive-import.c

## Purpose
`test-libarchive-import.c` is a C unit/integration test for importing archives into an OSTree repo through the libarchive importer. It covers parent creation, device-file rejection or ignoring, OSTree filesystem conventions, xattrs, callback path semantics, and SELinux relabeling.

## Important APIs, Types, And Functions
Key helpers include `TestData`, `test_data_init`, `spawn_cmdline`, `test_archive_setup`, `import_write_and_ref`, `skip_if_no_xattr`, and `check_ostree_convention`. It uses `OstreeRepoImportArchiveOptions`, `archive_read_new`, `ostree_repo_commit_modifier_new`, `ostree_repo_commit_modifier_set_xattr_callback`, `ostree_repo_commit_modifier_set_sepolicy`, `ostree_sepolicy_new`, and xattr syscalls.

## Control Flow
The fixture creates a temporary repo and archive payload. Tests import archives with and without `autocreate_parents`, expect device-file errors unless `ignore_unsupported_content` is enabled, validate `/usr/etc` convention remapping, import xattrs from archive data, inject xattrs through callbacks, skip xattrs through commit modifiers, test callback paths with or without original archive entry names, and optionally verify SELinux labels outside containers.

## State And Persistence
State includes a temporary repo, archive fd, imported refs such as `bar`, `baz`, and `bob`, and checkout directories used to inspect contents and xattrs. SELinux checks consult host policy but do not persist policy changes.

## Dependencies And Integration Points
It integrates libarchive, `ostree_repo_import_archive_to_mtree` style import behavior, commit modifiers, xattr storage, SELinux policy, command-line checkout/ls, and the common C test helpers in `libostreetest`.

## Risks And Test Signals
The test has environment-dependent skips for xattrs, libarchive support, containers, and SELinux availability. Passing signals include correct import failures, parent auto-creation behavior, xattr round trips including embedded NULs, callback-selected xattrs, skipped xattrs, and SELinux context assignment on `/etc`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-libarchive-import.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-libarchive.sh -->
# sources/cloud-native/ostree/tests/test-libarchive.sh

## Purpose
`test-libarchive.sh` validates CLI archive imports through `ostree commit --tree=tar=...` for tar, cpio, stdin streams, statoverride, skip lists, multi-archive commits, empty archives, path filtering, pull size reporting, and UTF-8 paths.

## Important APIs, Types, And Functions
The script uses `skip_without_ostree_feature libarchive`, `setup_test_repository "bare"`, shell helpers `assert_valid_checkout` and `assert_valid_content`, `tar`, `cpio`, `ostree commit --tree=tar=...`, `--statoverride`, `--skip-list`, `checkout`, `ls`, `pull`, and content assertions.

## Control Flow
It builds a filesystem tree with regular files, hard links, symlinks, setuid candidate files, and skipped files. It commits tar/cpio archives from files and stdin, checks checkouts, tests repeated `--tree=tar=` inputs where later archives overwrite earlier paths, imports an archive containing a partial subtree, checks empty tar root metadata, tests path filtering and relocation into a subdir, pulls a repo and checks size accounting, and verifies non-ASCII filenames/symlink targets.

## State And Persistence
Temporary state includes archive files, statoverride and skip-list files, test refs, checkout directories, and a secondary repo for pull-size inspection.

## Dependencies And Integration Points
This script covers the CLI layer over libarchive import, commit modifier support, hard-link/symlink handling, repo object generation, checkout, remote pull, and UTF-8 path handling.

## Risks And Test Signals
It is sensitive to archive tool behavior, UID/GID formatting, and feature availability. Passing signals include correct content in all checkout variants, skipped files absent, statoverride modes applied, multi-archive overwrite semantics, size output matching expected object counts, and UTF-8 paths round-tripping.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-libarchive.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-local-pull-depth.sh -->
# sources/cloud-native/ostree/tests/test-local-pull-depth.sh

## Purpose
`test-local-pull-depth.sh` verifies `ostree pull-local --depth` semantics when copying commits from a local repository.

## Important APIs, Types, And Functions
The script uses `setup_test_repository "archive"`, `ostree_repo_init`, `ostree pull-local --depth=N`, `rev-parse`, object glob counts for `*.commit`, partial commit markers, direct deletion of refs/commit objects, and `fsck`.

## Control Flow
It initializes a second archive repo, pulls different depths from the source repo, and asserts the number of full and partial commits after each pull. It clears refs and commit objects between scenarios, checks depth-zero and depth-one behavior, and finally removes source commit objects to ensure an infinite-depth pull fails when required history is missing.

## State And Persistence
State is stored in `repo2` refs, commit objects, and `.commitpartial` markers. The test intentionally deletes refs and commit objects to reset or corrupt scenarios.

## Dependencies And Integration Points
It covers local pull traversal, parent-depth selection, partial commit marker management, and fsck compatibility for copied commits.

## Risks And Test Signals
Object-count assertions depend on the fixture history depth. Passing signals include expected full/partial commit counts at each depth and a failure when unlimited local history cannot be read from the source.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-local-pull-depth.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-local-pull.sh -->
# sources/cloud-native/ostree/tests/test-local-pull.sh

## Purpose
`test-local-pull.sh` tests local repository-to-repository pulls across archive, bare-user, GPG, and object-copy scenarios.

## Important APIs, Types, And Functions
The script uses `skip_without_user_xattrs`, `setup_test_repository`, `ostree_repo_init --mode=bare-user/archive`, `pull-local`, `fsck`, `refs`, optional GPG signing/verification, and direct object inspection.

## Control Flow
It creates several repos, pulls commits locally between modes, verifies pulled refs and content, exercises GPG-related paths when available, checks that pulling from a bare/user repo to archive works, and includes a final loop over source `.filez` objects to validate copied payload availability in another repo.

## State And Persistence
Temporary repos `repo2`, `repo3`, and later numbered repos hold copied objects and refs. Xattrs and user-mode object metadata are persisted in the repo object stores.

## Dependencies And Integration Points
Coverage spans repository mode conversion, local object copying, user xattr support, optional GPG metadata, checkout validation, and fsck.

## Risks And Test Signals
The test is environment-sensitive because user xattrs are required and GPG coverage is optional. Passing signals include clean fsck after each local pull, correct refs, readable checkouts, and no missing file content after object-store copying.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-local-pull.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-lzma.c -->
# sources/cloud-native/ostree/tests/test-lzma.c

## Purpose
`test-lzma.c` unit-tests OSTree's LZMA compressor and decompressor GConverter implementations.

## Important APIs, Types, And Functions
The core helper is `helper_test_compress_decompress`, which uses `_ostree_lzma_compressor_new`, `_ostree_lzma_decompressor_new`, `g_converter_input_stream_new`, `g_memory_input_stream_new_from_data`, `g_memory_output_stream_new_resizable`, and `g_output_stream_splice`.

## Control Flow
The helper compresses an input byte buffer into a memory output stream, converts the compressed data back through the decompressor, and compares the resulting bytes with the original input. Registered tests cover representative data sizes/content including empty or small data depending on compiled test cases.

## State And Persistence
All state is in-memory GLib streams and buffers. No files are written.

## Dependencies And Integration Points
It validates OSTree's LZMA stream wrappers used for archive/repository compression paths, plus GLib's converter stream integration.

## Risks And Test Signals
The important risk is converter state handling across splice boundaries and close flags. Passing signals include positive compressed byte counts, no GLib errors, and exact byte-for-byte decompression.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-lzma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-mock-gio.c -->
# sources/cloud-native/ostree/tests/test-mock-gio.c

## Purpose
`test-mock-gio.c` implements mock GIO volume-monitor objects used by tests that need controlled removable drive, volume, and mount topology.

## Important APIs, Types, And Functions
It defines `OstreeMockVolumeMonitor`, `OstreeMockVolume`, `OstreeMockDrive`, and `OstreeMockMount` with GObject/GIO interface boilerplate. Constructors include `ostree_mock_volume_monitor_new`, `ostree_mock_volume_new`, `ostree_mock_drive_new`, and `ostree_mock_mount_new`. Interface methods include monitor `get_mounts`/`get_volumes`, volume `get_name`/`get_drive`/`get_mount`, drive `is_removable`, and mount `get_name`/`get_root`.

## Control Flow
Class init functions install dispose handlers and interface vfuncs. Constructors allocate objects and ref/copy supplied mount, volume, drive, and root references. Dispose methods release owned lists and objects. Getter vfuncs return copied or referenced state to emulate GIO behavior.

## State And Persistence
State is in-memory GObject fields: monitor lists, volume name/drive/mount, drive removable flag, and mount name/root file. There is no persistence.

## Dependencies And Integration Points
The file integrates with GLib object type registration, GIO `GVolumeMonitor`, `GVolume`, `GDrive`, and `GMount` interfaces, and OSTree tests that need deterministic removable-media discovery.

## Risks And Test Signals
The main risk is incorrect reference ownership, which would cause leaks or dangling objects in tests. The signal is successful compilation and use by higher-level tests without GObject criticals, plus correct mock topology returned through standard GIO interfaces.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-mock-gio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-mock-gio.h -->
# sources/cloud-native/ostree/tests/test-mock-gio.h

## Purpose
`test-mock-gio.h` declares the mock GIO object types implemented in `test-mock-gio.c`.

## Important APIs, Types, And Functions
The header defines `OSTREE_TYPE_MOCK_VOLUME_MONITOR`, `OSTREE_TYPE_MOCK_VOLUME`, `OSTREE_TYPE_MOCK_DRIVE`, and `OSTREE_TYPE_MOCK_MOUNT`, plus typedefs for instance and class structs. It declares the four constructors for monitors, volumes, drives, and mounts.

## Control Flow
There is no runtime flow in the header. It provides declarations that let tests instantiate mocks and pass them through GIO interface APIs.

## State And Persistence
No state is defined here beyond opaque type declarations and constructor signatures.

## Dependencies And Integration Points
It includes GIO, GLib object headers, libglnx, and `ostree-types.h`, making the mock types available to OSTree test code without exposing implementation fields.

## Risks And Test Signals
ABI consistency with `test-mock-gio.c` matters. Passing build signals include type macros resolving, constructor prototypes matching implementation, and downstream tests compiling against the mock interfaces.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-mock-gio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-mutable-tree.c -->
# sources/cloud-native/ostree/tests/test-mutable-tree.c

## Purpose
`test-mutable-tree.c` unit-tests `OstreeMutableTree`, the in-memory tree builder used when composing commits.

## Important APIs, Types, And Functions
Tests cover `ostree_mutable_tree_new`, metadata and contents checksum setters/getters, `ostree_mutable_tree_walk`, `ostree_mutable_tree_ensure_parent_dirs`, `ostree_mutable_tree_ensure_dir`, `ostree_mutable_tree_replace_file`, and `ostree_mutable_tree_lookup`.

## Control Flow
Individual tests create mutable trees, set checksums, create or walk nested directories, validate error cases for non-directory path components, replace file entries, and verify lookups return expected child trees or file checksums.

## State And Persistence
All state is in-memory tree nodes and checksum strings. No repository is opened and no files are written.

## Dependencies And Integration Points
This tests the mutable tree abstraction used by commit, import, and archive code before final writes to an OSTree repository.

## Risks And Test Signals
Tree mutation bugs can misclassify files/directories or corrupt commit contents. Passing signals include correct parent directory creation, replacement behavior, checksum storage, and error reporting for invalid tree walks.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-mutable-tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-no-initramfs.sh -->
# sources/cloud-native/ostree/tests/test-no-initramfs.sh

## Purpose
`test-no-initramfs.sh` verifies deployment behavior for OS trees without initramfs images across supported boot file layouts.

## Important APIs, Types, And Functions
The script uses `setup_os_repository "archive-z2" "uboot"`, `ostree admin deploy`, `ostree admin upgrade`, bootloader entry inspection, helper `pull_test_tree`, helper `get_key_from_bootloader_conf`, and loops over layouts under `/usr/lib/modules`, `/usr/lib/ostree-boot`, and `/boot`.

## Control Flow
It first deploys a tree and checks the generated bootloader entry has the expected root argument and no `init=` entry. It then creates additional commits with kernels and no initramfs in each layout, upgrades/deploys them, and verifies bootloader entries and boot file installation stay correct.

## State And Persistence
State is a temporary sysroot, OS repository, bootloader entry files, deployment directories, and generated OS commit trees. Boot artifacts are persisted under the temporary sysroot.

## Dependencies And Integration Points
The test integrates admin deploy/upgrade code, bootloader config generation, kernel/initramfs discovery, u-boot layout handling, and OS repository fixture helpers.

## Risks And Test Signals
The risk is bootloader generation assuming an initramfs exists or losing kernel args. Passing signals include deployment success, no `init=` line when absent, correct root argument, and correct behavior across all tested boot layouts.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-no-initramfs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-oldstyle-partial.sh -->
# sources/cloud-native/ostree/tests/test-oldstyle-partial.sh

## Purpose
`test-oldstyle-partial.sh` checks fsck behavior for legacy partial commit markers.

## Important APIs, Types, And Functions
It uses `setup_fake_remote_repo1 "archive"`, initializes a repo, creates an old-style partial marker/ref state, runs `ostree fsck`, and asserts output about verified commit objects and partial commits not verified.

## Control Flow
The script creates an empty local repo, arranges a partial commit marker in the format older OSTree versions used, runs fsck, and verifies fsck reports zero commit objects verified and one partial commit skipped.

## State And Persistence
State is a temporary repo with partial-commit metadata but no complete commit content.

## Dependencies And Integration Points
It targets backward compatibility in fsck's partial-commit discovery and reporting logic.

## Risks And Test Signals
The test guards against treating old partial markers as corrupt complete commits. Passing signals are the expected fsck output lines and no unexpected verification of incomplete commits.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-oldstyle-partial.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-osupdate-dtb.sh -->
# sources/cloud-native/ostree/tests/test-osupdate-dtb.sh

## Purpose
`test-osupdate-dtb.sh` validates device-tree blob handling during OS updates and deployments.

## Important APIs, Types, And Functions
It uses `setup_os_repository "archive" "syslinux"`, creates DTB files under module directories including `dtb` and `dtb/overlays`, commits OS content, runs admin deploy/upgrade, and asserts files under `sysroot/boot/ostree`.

## Control Flow
The test deploys an initial tree without DTBs, verifies only the kernel is installed and no DTB files exist, then adds DTBs to a later tree and upgrades. It verifies boot directory generation changes from one to two boot checksums and that the expected number of `.dtb` files appears.

## State And Persistence
State is a temporary OS repo, sysroot, module directory content, boot checksum directories, kernel files, and DTB files.

## Dependencies And Integration Points
It covers admin deployment, boot artifact copying, syslinux layout behavior, and DTB discovery under kernel module paths.

## Risks And Test Signals
The test is sensitive to boot directory naming and DTB discovery rules. Passing signals include no stale DTBs for the first deployment and correct DTB propagation after upgrade.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-osupdate-dtb.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-ot-opt-utils.c -->
# sources/cloud-native/ostree/tests/test-ot-opt-utils.c

## Purpose
`test-ot-opt-utils.c` unit-tests option utility error reporting.

## Important APIs, Types, And Functions
It uses a custom `printerr` capture string and tests `ot_util_usage_error` from `ot-opt-utils.h`.

## Control Flow
The test redirects or captures printerr output, calls `ot_util_usage_error` with invalid usage input, and asserts the generated error text and return/error state match expectations.

## State And Persistence
State is limited to an in-memory `GString *printerr_str` and `GError` values. No files are written.

## Dependencies And Integration Points
This validates helper behavior used by CLI option parsing paths to report usage failures consistently.

## Risks And Test Signals
The test is wording-sensitive but intentionally so for CLI diagnostics. Passing signals include a populated usage error, expected stderr text, and no unexpected GLib assertion failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-ot-opt-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-ot-tool-util.c -->
# sources/cloud-native/ostree/tests/test-ot-tool-util.c

## Purpose
`test-ot-tool-util.c` unit-tests small command-line parsing helpers used by OSTree tools.

## Important APIs, Types, And Functions
The file tests `ot_parse_boolean` and `ot_parse_keyvalue` from `ot-tool-util.h`, using GLib assertions and error checks.

## Control Flow
`test_ot_parse_boolean` checks accepted boolean spellings and invalid values. `test_ot_parse_keyvalue` checks splitting of `key=value` strings, missing separator errors, empty values or keys as applicable, and returned allocations.

## State And Persistence
All state is local strings, booleans, and `GError` instances.

## Dependencies And Integration Points
These helpers are used by CLI and remote/config option parsing, where consistent key/value and boolean handling prevents ambiguous user input.

## Risks And Test Signals
Passing signals include correct parse results, allocated key/value outputs, and errors for malformed inputs. The main risk is relaxing parsing in a way that silently accepts bad CLI options.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-ot-tool-util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-ot-unix-utils.c -->
# sources/cloud-native/ostree/tests/test-ot-unix-utils.c

## Purpose
`test-ot-unix-utils.c` validates Unix utility helpers for path/filename validation and human-readable durations.

## Important APIs, Types, And Functions
It tests `ot_util_path_split_validate`, `ot_util_filename_validate`, and `ot_format_human_duration` or equivalent duration formatting from `ot-unix-utils.h` and `ot-gio-utils.h`.

## Control Flow
The path test validates accepted relative paths and rejects empty, absolute, parent-traversal, or malformed paths. The filename test checks single path component constraints. The duration test checks formatting for seconds/minutes/hours style values.

## State And Persistence
No persistent state exists; all data are local strings, arrays, and errors.

## Dependencies And Integration Points
These utilities protect repository object/path handling and user-facing time formatting in CLI output.

## Risks And Test Signals
Path validation is security-sensitive because it prevents traversal or invalid names. Passing signals include rejection of dangerous path forms and stable human-duration strings.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-ot-unix-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-otcore.c -->
# sources/cloud-native/ostree/tests/test-otcore.c

## Purpose
`test-otcore.c` unit-tests core helpers for Ed25519 key handling and root argument/config preparation.

## Important APIs, Types, And Functions
The file includes `otcore.h` and defines tests such as `test_ed25519`, `test_prepare_root_cmdline`, and `test_prepare_root_config`.

## Control Flow
The Ed25519 test validates expected parsing/formatting behavior for public key material. The root command-line and config tests build input strings/config snippets and verify helper output for prepared root arguments, including expected substitutions and defaults.

## State And Persistence
All state is local GLib strings, variants/config objects, and errors. No repository or sysroot is modified.

## Dependencies And Integration Points
The helpers are used by signature verification and boot/root preparation paths in OSTree core code.

## Risks And Test Signals
Passing signals include valid key parsing, rejection of malformed data, and stable root argument generation. Regressions here can affect boot configuration and signature-related command behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-otcore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-parent.sh -->
# sources/cloud-native/ostree/tests/test-parent.sh

## Purpose
`test-parent.sh` verifies parent commit relationships and pulling signed parent history.

## Important APIs, Types, And Functions
The script requires user xattrs and GPGME, uses `setup_test_repository "archive"`, `ostree gpg-sign`, `ostree commit`, `ostree_repo_init`, `remote add`, `pull`, and assertions over failure/success.

## Control Flow
It signs commits in the main repo, creates additional repos, pulls refs and parent history, and checks that a repo lacking required signed parent state fails where expected while correctly configured pulls succeed.

## State And Persistence
Temporary repos hold refs, signed commits, parent links, and trusted GPG state. State changes are limited to the test working directory.

## Dependencies And Integration Points
The test covers commit parent metadata, GPG verification during pull, remote configuration, and archive repo fixture content.

## Risks And Test Signals
The test is sensitive to GPG availability and parent traversal rules. Passing signals include expected pull failures for missing/untrusted parent cases and successful pulls when parent/signature requirements are satisfied.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-parent.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-payload-link.sh -->
# sources/cloud-native/ostree/tests/test-payload-link.sh

## Purpose
`test-payload-link.sh` verifies payload-link detection/reporting for commits that can use reflink-like shared payloads.

## Important APIs, Types, And Functions
It probes `cp --reflink=always`, uses `ostree commit`, payload-link output inspection, `assert_streq`, and TAP helpers.

## Control Flow
The script first checks whether the filesystem supports reflinks. If so, it creates files/directories, commits content in a way that should produce payload-link metadata, lists payload links, and asserts exactly one payload-link entry appears.

## State And Persistence
State is temporary files `foo`, `bar`, directory `d`, the repository objects created by commit, and `payload-links.txt`.

## Dependencies And Integration Points
It covers filesystem reflink capability, OSTree commit payload-link generation, and CLI listing of payload links.

## Risks And Test Signals
The test may skip or behave differently on filesystems without reflinks. Passing signals include one and only one payload-link line, indicating duplicate payload detection works without over-reporting.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-payload-link.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pem.c -->
# sources/cloud-native/ostree/tests/test-pem.c

## Purpose
`test-pem.c` unit-tests PEM block parsing for embedded public key data.

## Important APIs, Types, And Functions
The file defines sample Ed25519 public key bytes and PEM strings, then tests `_ostree_read_pem_block` from `ostree-blob-reader-private.h`.

## Control Flow
The valid test parses a normal PEM block and one with extra whitespace, then compares decoded bytes with expected Ed25519 data. The invalid test covers empty input, missing trailer, label mismatch, and other malformed PEM cases, expecting errors.

## State And Persistence
All state is static byte/string constants, local buffers, and errors. No files are read or written.

## Dependencies And Integration Points
This validates parsing used by signature/key loading paths, especially for ASCII-armored key material.

## Risks And Test Signals
PEM parsing must reject malformed labels and truncated data without accepting ambiguous input. Passing signals are exact decoded bytes for valid blocks and errors for invalid variants.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pre-signed-pull.sh -->
# sources/cloud-native/ostree/tests/test-pre-signed-pull.sh

## Purpose
`test-pre-signed-pull.sh` verifies pulling a pre-generated Ed25519-signed repository and rejecting a repository signed with an untrusted or wrong key.

## Important APIs, Types, And Functions
It checks `has_ostree_feature sign-ed25519`, extracts `pre-signed-pull-data.tar.gz`, initializes a repo, configures remotes/keys from the fixture, runs `ostree pull`, and asserts Ed25519 verification errors.

## Control Flow
If Ed25519 signing support is unavailable, the single TAP test is skipped. Otherwise the fixture archive is unpacked, a local repo is initialized, a good pull path is exercised, and a bad upstream pull is expected to fail with a signature verification message.

## State And Persistence
State consists of unpacked fixture repositories, temporary local repo config, imported keys, and pulled refs/objects.

## Dependencies And Integration Points
It integrates static signed test data, Ed25519 signature verification, pull verification, and remote configuration.

## Risks And Test Signals
The fixture must remain in sync with verification code. Passing signals include successful good pull and an error matching `ed25519: Signature couldn't be verified with: key` for bad pulls.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pre-signed-pull.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-prune-collections.sh -->
# sources/cloud-native/ostree/tests/test-prune-collections.sh

## Purpose
`test-prune-collections.sh` validates prune behavior for collection refs and mirror refs.

## Important APIs, Types, And Functions
It defines `set_up_repo`, uses `ostree_repo_init --collection-id`, `commit`, collection/mirror ref manipulation, `ostree prune`, `prune --delete-commit`, and output assertions for total/deleted objects.

## Control Flow
The setup creates a repo with collection-bound commits and refs. The test first verifies that deleting a commit still referenced by collection metadata fails or leaves no unreachable objects. It then removes refs in controlled ways and confirms prune either preserves reachable collection objects or deletes unreachable objects.

## State And Persistence
Repository state includes commit objects, ordinary refs, collection refs under mirror namespaces, and temporary checksum files. The script directly removes `refs/mirrors` for one scenario.

## Dependencies And Integration Points
It covers prune reachability analysis with collection-aware refs, delete-commit semantics, and object deletion accounting.

## Risks And Test Signals
The test guards against pruning commits reachable only through collection refs. Passing signals include `No unreachable objects` while collection refs exist and deletion counts only after those refs are removed.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-prune-collections.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-prune.sh -->
# sources/cloud-native/ostree/tests/test-prune.sh

## Purpose
`test-prune.sh` is broad regression coverage for `ostree prune`, including dry-run output, depth pruning, tombstone commits, static deltas, partial repos, parent repos, date retention, branch-specific depth, commit-only pruning, and concurrent commit/prune behavior.

## Important APIs, Types, And Functions
Helpers include `assert_repo_has_n_commits`, `assert_repo_has_n_non_commit_objects`, `assert_has_n_objects`, `reinitialize_datesnap_repo`, and `reinitialize_commit_only_test_repo`. The script uses `ostree prune`, `--delete-commit`, `--refs-only`, `--static-deltas-only`, `--keep-younger-than`, `--retain-branch-depth`, `--only-branch`, `--depth`, `--commit-only`, `static-delta generate`, and TAP helpers.

## Control Flow
It builds fixture histories, verifies dry-run leaves object counts unchanged, prunes depths with and without tombstones, generates and prunes static deltas, checks partial repo handling, validates parent repo object retention, constructs dated branch histories for retention rules, exercises invalid depth/ref errors, and then tests commit-only pruning against multiple branch/delete combinations. A final loop commits and prunes repeatedly to catch race regressions.

## State And Persistence
Temporary repos hold object stores, refs, tombstone commits, static delta directories, parent links, date-stamped commits, and branch histories. Several scenarios reset repos from snapshot repos.

## Dependencies And Integration Points
This test integrates prune reachability, ref traversal, commit metadata timestamps, static delta storage, parent repository lookup, tombstone configuration, and object deletion accounting.

## Risks And Test Signals
Object-count tests are fixture-sensitive but catch real reachability regressions. Passing signals include expected commit/non-commit counts after each prune mode, correct error messages for invalid combinations, static delta counts, and stable behavior under repeated commit/prune operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-prune.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-bare.sh -->
# sources/cloud-native/ostree/tests/test-pull-bare.sh

## Purpose
`test-pull-bare.sh` runs the shared HTTP pull regression suite against a `bare` destination repository.

## Important APIs, Types, And Functions
It sources `libtest.sh`, calls `setup_fake_remote_repo1 "archive"`, sets `repo_mode=bare`, and sources `${test_srcdir}/pull-test.sh`.

## Control Flow
The wrapper prepares a fake archive HTTP remote, selects the destination repo mode, and delegates all test flow to `pull-test.sh`, which covers normal pulls, mirror pulls, fsck, static delta refusal in archive mirror scenarios, invalid remote schemes, bareuseronly safety checks, corruption handling, path traversal rejection, and optional GPG cases.

## State And Persistence
State is created by the shared pull suite under `test_tmpdir`, including a `repo` initialized as bare and several mirror/cache repos.

## Dependencies And Integration Points
This is the bare-mode integration lane for the central pull suite, covering object storage with hardlinks/metadata rather than user-only xattrs.

## Risks And Test Signals
Risks and signals are inherited from `pull-test.sh`; the wrapper specifically ensures those behaviors work for bare repositories.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-bare.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-bareuser.sh -->
# sources/cloud-native/ostree/tests/test-pull-bareuser.sh

## Purpose
`test-pull-bareuser.sh` runs the shared HTTP pull suite against a `bare-user` destination repository.

## Important APIs, Types, And Functions
It uses `skip_without_user_xattrs`, `setup_fake_remote_repo1 "archive"`, sets `repo_mode=bare-user`, and sources `pull-test.sh`.

## Control Flow
After ensuring user xattrs are available, the wrapper creates the fake remote, selects bare-user mode, and executes the shared pull suite. The shared suite adjusts checkout flags for bare-user repos and runs the same pull, mirror, corruption, traversal, and optional GPG checks.

## State And Persistence
Temporary repo state includes bare-user object metadata encoded in user xattrs and the shared suite's remote, mirror, and cache repos.

## Dependencies And Integration Points
This validates that the central pull code works when destination metadata is represented in user xattrs, important for unprivileged use.

## Risks And Test Signals
The wrapper skips without user xattr support. Passing signals mirror `pull-test.sh` plus successful bare-user checkout/fsck behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-bareuser.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-bareuseronly.sh -->
# sources/cloud-native/ostree/tests/test-pull-bareuseronly.sh

## Purpose
`test-pull-bareuseronly.sh` runs the shared HTTP pull suite against a `bare-user-only` destination repository with canonical permissions.

## Important APIs, Types, And Functions
It uses `skip_without_user_xattrs`, `setup_fake_remote_repo1 "archive" "--canonical-permissions"`, sets `repo_mode=bare-user-only`, and sources `pull-test.sh`.

## Control Flow
The wrapper prepares an archive remote whose commits use canonical permissions, then delegates to the shared pull suite. The shared suite sets commit and checkout flags appropriate for bare-user-only repositories and includes explicit safe/unsafe `--bareuseronly-files` checks.

## State And Persistence
Temporary state is the bare-user-only repo, user-xattr object metadata, canonical-permission remote objects, and shared test artifacts.

## Dependencies And Integration Points
It validates unprivileged storage constraints, canonical permission handling, and shared pull behavior in the most restrictive repo mode.

## Risks And Test Signals
The suite is skipped without user xattrs. Passing signals include successful normal pulls and rejection of unsafe setuid content for bare-user-only files.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-bareuseronly.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-basicauth.sh -->
# sources/cloud-native/ostree/tests/test-pull-basicauth.sh

## Purpose
`test-pull-basicauth.sh` verifies HTTP basic authentication handling during pulls.

## Important APIs, Types, And Functions
It uses `skip_without_ostree_httpd`, `setup_fake_remote_repo1 "archive" "" "--require-basic-auth"`, `ostree remote add` with authenticated and unauthenticated URLs, `ostree pull`, and assertions for HTTP 401 failures.

## Control Flow
The script initializes a repo, configures remotes with no credentials, bad credentials, and correct credentials, then verifies unauthenticated and bad-auth pulls fail with 401 while authenticated pulls succeed.

## State And Persistence
State includes the fake HTTP server requiring basic auth, temporary local repo config, and error logs.

## Dependencies And Integration Points
It covers libcurl/libsoup HTTP authentication plumbing, remote URL parsing with credentials, and pull error reporting.

## Risks And Test Signals
The test depends on the trivial HTTP server auth feature. Passing signals include 401 diagnostics for missing/bad credentials and successful pull with valid credentials.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-basicauth.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-c.c -->
# sources/cloud-native/ostree/tests/test-pull-c.c

## Purpose
`test-pull-c.c` unit-tests the C API `ostree_repo_pull` for repeated pulls and recovery after pull errors.

## Important APIs, Types, And Functions
`TestData` owns an `OstreeRepo`. `test_data_init` uses `ot_test_setup_repo`, `ot_test_run_libtest`, `g_file_get_contents`, and `ostree_repo_remote_change` to configure an HTTP `origin` with GPG verification disabled. Tests call `ostree_repo_pull`.

## Control Flow
`test_pull_multi_nochange` pulls `main` three times and expects no errors after the first no-change pull. `test_pull_multi_error_then_ok` loops over successful pulls, repeated failures for `nosuchbranch`, and another successful pull, checking that errors do not poison later API calls.

## State And Persistence
The test creates a temporary repo and fake HTTP remote through libtest. Pulls persist refs and objects in the repo; bad pulls keep errors local.

## Dependencies And Integration Points
It bridges C API consumers with the shell fixture remote and validates remote configuration through `ostree_repo_remote_change`.

## Risks And Test Signals
The critical risk is stale pull state after errors. Passing signals include repeated no-op success and successful pulls after multiple expected failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-collections.sh -->
# sources/cloud-native/ostree/tests/test-pull-collections.sh

## Purpose
`test-pull-collections.sh` validates pull and pull-local behavior for collection-aware refs and collection binding metadata.

## Important APIs, Types, And Functions
Helpers include `do_commit`, `do_summary`, `do_collection_ref_show`, `ensure_no_collection_ref`, `do_join`, `ensure_collection_ref`, `do_remote_add`, `do_pull`, and `do_local_pull`. The script uses `ostree_repo_init`, commits with collection/ref binding metadata, summaries, remotes, pull, pull-local, refs, and mirror pulls.

## Control Flow
It creates repos with and without collection IDs, local and remote variants, commits refs with valid and invalid binding metadata, and checks whether collection refs are created or omitted as appropriate. It then attempts pulls that should fail for bad collection bindings and confirms mirror pulls do not rewrite existing summaries unexpectedly.

## State And Persistence
State includes multiple repos, collection IDs, summary files/signatures, local and remote refs, collection mirror refs, and checksum comparisons for summaries.

## Dependencies And Integration Points
It integrates collection ID config, commit binding metadata, summary updates, normal pull, local pull, mirror behavior, and ref namespace storage.

## Risks And Test Signals
Binding validation is subtle: wrong collection IDs or refs must fail without corrupting local refs. Passing signals include expected collection ref creation, failure of bad binding pulls, and stable summary content in mirror subset pulls.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-collections.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-commit-only.sh -->
# sources/cloud-native/ostree/tests/test-pull-commit-only.sh

## Purpose
`test-pull-commit-only.sh` verifies `ostree pull --commit-metadata-only` style behavior, where commit metadata can be fetched without content objects.

## Important APIs, Types, And Functions
It uses `setup_fake_remote_repo1 "archive"`, `ostree_repo_init`, `ostree pull`, commit-object counts, and fsck/prune-style object inspection.

## Control Flow
The script initializes a local repo, pulls only commit metadata from the remote, asserts commit object counts, checks that content object counts remain absent or zero, and verifies subsequent behavior around refs and metadata-only state.

## State And Persistence
State is a temporary repo containing commit objects and refs but intentionally lacking full file content for metadata-only pulls.

## Dependencies And Integration Points
This covers pull options that support metadata-only discovery, partial repository state, and object type filtering.

## Risks And Test Signals
The risk is accidentally fetching content or creating unusable refs without intended partial semantics. Passing signals are exact commit counts and absence of unintended content objects.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-commit-only.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-contenturl.sh -->
# sources/cloud-native/ostree/tests/test-pull-contenturl.sh

## Purpose
`test-pull-contenturl.sh` verifies remotes whose summary metadata points content fetches at a separate content URL.

## Important APIs, Types, And Functions
It uses an HTTP fixture, optional GPG signing, `setup_fake_remote_repo1`, summary mutation/configuration for content URLs, a separate `httpd-content` server tree, `remote add`, `pull`, `fsck`, and optional verification setup.

## Control Flow
The script starts with an archive remote, prepares separate content hosting, removes or adjusts summary/signature files as needed, initializes a client repo, configures GPG verification based on feature availability, pulls from the remote, and verifies the resulting repo.

## State And Persistence
State includes original metadata server content, separate content URL directory, summary files and signatures, client repo refs/objects, and temporary HTTP server paths.

## Dependencies And Integration Points
It integrates remote summary parsing, contenturl handling, HTTP object fetching, optional GPG summary verification, and fsck.

## Risks And Test Signals
The risk is fetching metadata from one server but content from the wrong location, or breaking signature semantics. Passing signals include successful pull and fsck with content served from the alternate URL.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-contenturl.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-corruption.sh -->
# sources/cloud-native/ostree/tests/test-pull-corruption.sh

## Purpose
`test-pull-corruption.sh` validates pull-time detection of corrupted remote objects.

## Important APIs, Types, And Functions
It requires `gjs`, uses `setup_fake_remote_repo1`, defines `do_corrupt_pull_test`, mutates remote object bytes, runs `ostree pull`, checks `corrupted-status.txt`, and gates some cases on user xattrs.

## Control Flow
The helper corrupts selected remote objects, attempts pulls into fresh repos, and expects pull failures with checksum/corruption diagnostics. It runs variants for different repo modes or object types, skipping where environment support is missing.

## State And Persistence
State includes corrupted copies of remote objects, temporary client repos, status/error files, and restored or recreated remote state between cases.

## Dependencies And Integration Points
It covers HTTP pull integrity verification, object checksum validation, repo mode differences, and test corruption tooling implemented with GJS.

## Risks And Test Signals
The test is sensitive to fixture object selection and GJS availability. Passing signals include explicit "Changed byte" evidence and pull failures that identify corrupted content instead of accepting bad objects.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-corruption.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-depth.sh -->
# sources/cloud-native/ostree/tests/test-pull-depth.sh

## Purpose
`test-pull-depth.sh` verifies remote `ostree pull --depth` behavior over HTTP.

## Important APIs, Types, And Functions
It uses `setup_fake_remote_repo1 "archive"`, `ostree_repo_init`, `ostree pull --depth=N origin main`, object counts for commit and partial commit markers, ref cleanup, direct deletion of remote commit objects, and expected failure checks.

## Control Flow
The script pulls increasing depths and checks how many commit objects and partial markers exist. It resets refs and commit objects between scenarios, checks depth-zero and depth-one semantics, and then removes remote commit objects before an unlimited-depth pull to ensure missing history fails.

## State And Persistence
State is a local repo with refs, commit objects, and partial markers, plus the fake HTTP remote whose commit objects are deliberately removed in the final negative test.

## Dependencies And Integration Points
It covers remote history traversal, commit-parent fetching, partial commit markers, and error handling for incomplete remotes.

## Risks And Test Signals
Expected counts are tied to fixture history length. Passing signals include correct full commit counts for each depth and failure when remote history is unavailable for unlimited depth.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-depth.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-large-metadata.sh -->
# sources/cloud-native/ostree/tests/test-pull-large-metadata.sh

## Purpose
`test-pull-large-metadata.sh` verifies that pulls reject metadata objects exceeding the configured maximum size.

## Important APIs, Types, And Functions
The script uses `setup_fake_remote_repo1 "archive"`, `rev-parse`, `dd if=/dev/zero bs=1M count=130` to overwrite a commit object, `ostree_repo_init`, `ostree pull`, and assertion for "exceeded maximum".

## Control Flow
It locates the remote commit object for `main`, replaces it with a 130 MiB zero-filled file, initializes a fresh local repo, attempts to pull, and expects failure with a maximum-size diagnostic.

## State And Persistence
State is the deliberately oversized remote commit object and the local repo that should remain without a successful pull.

## Dependencies And Integration Points
It covers pull metadata fetch limits, object validation before storage, HTTP/local file serving behavior, and error reporting.

## Risks And Test Signals
The test uses a large temporary file and is sensitive to size thresholds. Passing signals include pull failure and an error containing "exceeded maximum".
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-large-metadata.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-localcache.sh -->
# sources/cloud-native/ostree/tests/test-pull-localcache.sh

## Purpose
`test-pull-localcache.sh` verifies pulls using a local cache repository to avoid fetching objects already present locally.

## Important APIs, Types, And Functions
It uses `setup_fake_remote_repo1 "archive"`, a `repo-local` archive cache, helper `init_repo`, commits to the remote, `ostree pull --localcache-repo=...`, `rev-parse`, and output assertions about metadata/content fetched versus local counts.

## Control Flow
The script initializes a cache repo with existing remote content, creates fresh client repos, pulls with the local cache enabled, and checks fetch statistics. It then updates the remote, pulls again with cache assistance, and verifies the resulting commit checksum matches.

## State And Persistence
State includes the cache repo, client repo, remote commits, working `files` directories, and output logs.

## Dependencies And Integration Points
It covers pull's object lookup against an auxiliary local repository, fetch progress accounting, and fallback to remote for missing objects.

## Risks And Test Signals
The test is sensitive to progress wording and object counts. Passing signals include expected "local" object counts in output and matching final commit checksums.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-localcache.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-metalink.sh -->
# sources/cloud-native/ostree/tests/test-pull-metalink.sh

## Purpose
`test-pull-metalink.sh` validates pulling via a metalink remote, including summary discovery, alternate URL fallback, hash/size verification, malformed metalink errors, and parsing with irrelevant nested elements.

## Important APIs, Types, And Functions
The script uses `OSTREE_HTTPD`, `setup_fake_remote_repo1`, generates `metalink.xml`, computes MD5/SHA256/SHA512 and size for `summary`, configures `remote add ... metalink=URL`, runs `pull`, `remote refs`, and helper `test_metalink_pull_error`.

## Control Flow
It starts a second HTTP server for metalink data, creates a metalink with bad and missing URLs before the valid summary URL to test fallback, pulls successfully, and checks remote refs. It then mutates the metalink for invalid hash format, wrong checksum, wrong size, missing verification, missing URL, malformed XML, and nested unknown elements.

## State And Persistence
State includes metalink XML files, copied original summaries, a bad summary file, local repos recreated between negative tests, and HTTP server port/address files.

## Dependencies And Integration Points
It integrates metalink XML parsing, HTTP fallback selection, summary verification, remote refs discovery through `ostree_repo_remote_fetch_summary`, and pull.

## Risks And Test Signals
The test is XML and diagnostic sensitive. Passing signals include successful fallback to the valid URL, correct `main` refs, and specific failures for hash, checksum, size, verification, URL, and malformed document cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-metalink.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-mirror-summary.sh -->
# sources/cloud-native/ostree/tests/test-pull-mirror-summary.sh

## Purpose
`test-pull-mirror-summary.sh` verifies that mirror pulls copy summary metadata, summary signatures, and additional summary-indexed files correctly.

## Important APIs, Types, And Functions
It optionally signs commits with GPG, uses `setup_fake_remote_repo1`, creates extra files referenced by summary metadata, initializes archive mirror repos, runs `ostree pull --mirror`, checks `repo/summary` and `repo/summary.sig`, and tests truncated signature behavior.

## Control Flow
The script mirrors a remote and checks summary presence plus copied extra files. If GPG is unavailable, signature-specific checks are skipped. With GPG, it verifies signed summary mirroring, failure when signature verification is required but unavailable/bad, and behavior when summary signatures are truncated or missing.

## State And Persistence
State includes remote summary and summary signature files, extra file directories under the HTTP repo, archive mirror repos, and checkout copies used to inspect mirrored content.

## Dependencies And Integration Points
It covers mirror-mode summary copying, summary signatures, additional metadata files, GPG verification, and checkout of mirrored refs.

## Risks And Test Signals
The test is sensitive to GPG availability and signature file corruption. Passing signals include mirrored summaries/signatures where expected, extra files present with expected content, and failure for invalid signed summary scenarios.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-mirror-summary.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-mirrorlist.sh -->
# sources/cloud-native/ostree/tests/test-pull-mirrorlist.sh

## Purpose
`test-pull-mirrorlist.sh` validates pulling from a mirrorlist remote with multiple content mirrors and fallback behavior.

## Important APIs, Types, And Functions
The script uses `OSTREE_HTTPD`, `setup_fake_remote_repo1`, helper `setup_mirror`, deletes selected `.filez` objects from mirrors, writes a `mirrorlist` file, configures a remote with mirrorlist URL, and runs `ostree pull`.

## Control Flow
It creates three content mirrors, removes different objects to force fallback across mirrors, writes a mirrorlist pointing at them, and pulls into fresh repos for several scenarios, including successful fallback and expected errors when mirrors cannot satisfy requests.

## State And Persistence
State includes mirror directories, deleted object files, mirrorlist text, local client repos, and remote config.

## Dependencies And Integration Points
It covers mirrorlist parsing, HTTP object fetch fallback, object integrity validation, and pull retry behavior across multiple base URLs.

## Risks And Test Signals
The test relies on deterministic object selection and HTTP serving. Passing signals include successful pulls when at least one mirror has each object and failures when mirror coverage is insufficient.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-mirrorlist.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-override-url.sh -->
# sources/cloud-native/ostree/tests/test-pull-override-url.sh

## Purpose
`test-pull-override-url.sh` verifies `ostree pull --url=...` can override a configured remote URL.

## Important APIs, Types, And Functions
It uses an HTTP fixture, `setup_fake_remote_repo1`, creates a mirror server tree, `ostree_repo_init`, `remote add`, `pull --depth=-1`, `pull --url=...`, `refs`, and `cmp` over commit lists.

## Control Flow
The script creates a mirror repo with the same commits as the original, starts serving it under a different URL, initializes a client repo configured for the original remote, removes the original served repo to force failure, then pulls successfully with `--url` pointing at the mirror and compares pulled commits.

## State And Persistence
State includes original and mirror served repos, commit list files, local client repo, and HTTP server directories.

## Dependencies And Integration Points
It covers command-line URL override, remote config fallback, full-depth pulling, and HTTP repository compatibility.

## Risks And Test Signals
The test ensures `--url` is used for network access without changing ref semantics. Passing signals include failure without override after original removal, success with override, and matching commit lists.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-override-url.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-repeated.sh -->
# sources/cloud-native/ostree/tests/test-pull-repeated.sh

## Purpose
`test-pull-repeated.sh` validates HTTP pull retry behavior for repeated transient server errors.

## Important APIs, Types, And Functions
It requires `OSTREE_HTTPD`, optionally signs commits if GPGME is available, uses `setup_fake_remote_repo1` with `--random-500s` or `--random-408s`, `ostree pull --network-retries=N`, `assert_fail`, and repeated loops.

## Control Flow
The test first configures a remote that almost always returns HTTP 500 and verifies a zero-retry pull fails. It then runs many pulls against a 50 percent failure remote to ensure retries eventually succeed, and repeats the same pattern for HTTP 408 request timeouts. TAP cases cover no-retry failures, repeated successful retries, and mirror or normal pull variants.

## State And Persistence
State includes fake HTTP remotes with randomized error injection, fresh archive repos per scenario, error logs, and optional signed commit metadata.

## Dependencies And Integration Points
It covers network retry policy, HTTP status classification, pull idempotency, optional GPG verification under retries, and mirror-mode pulls.

## Risks And Test Signals
Randomized failures can be probabilistic, so loops and retry counts are chosen to expose retry regressions. Passing signals include expected immediate failures with `--network-retries=0` and successful repeated pulls with retries enabled.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-repeated.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-resume.sh -->
# sources/cloud-native/ostree/tests/test-pull-resume.sh

## Purpose
`test-pull-resume.sh` verifies pull resumption after interrupted or failed HTTP transfers using range requests.

## Important APIs, Types, And Functions
It uses `skip_without_ostree_httpd`, `setup_fake_remote_repo1 "archive" "" "--force-range-requests"`, initializes repos, repeatedly runs `ostree pull`, and finishes with `ostree fsck`.

## Control Flow
The script creates a repo, performs pulls in a retry loop intended to exercise resume state, and checks whether fsck succeeds after the resumable transfer completes. It cleans temporary repo paths afterward.

## State And Persistence
State includes partially downloaded objects in the repo tmp area, HTTP range request state, final refs/objects, and error output from failed attempts.

## Dependencies And Integration Points
It covers HTTP range requests, temporary object staging, resume/retry logic, and final fsck validation.

## Risks And Test Signals
The test depends on the HTTP fixture forcing range behavior. Passing signals include eventual successful pull and clean fsck, demonstrating partial downloads do not corrupt final objects.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-resume.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-sizes.sh -->
# sources/cloud-native/ostree/tests/test-pull-sizes.sh

## Purpose
`test-pull-sizes.sh` verifies pull progress/output size accounting when summaries include generated object sizes.

## Important APIs, Types, And Functions
It sets `OSTREE_NO_XATTRS=1`, uses `setup_fake_remote_repo1 "archive" "--generate-sizes"`, initializes a repo, runs pulls/show operations, and asserts output for compressed size, unpacked size, and object counts.

## Control Flow
The script performs an initial pull and checks needed/total sizes equal the full summary totals. It then performs subsequent pulls where some or all objects are already present and checks that needed sizes decrease to partial and then zero while totals remain stable.

## State And Persistence
State is the local repo's object cache and output files such as `show.txt`. Remote summary metadata contains generated size information.

## Dependencies And Integration Points
It covers summary size metadata generation, pull progress accounting, no-xattr archive fixtures, and CLI display formatting.

## Risks And Test Signals
The test is exact-output sensitive and accounts for regular/non-breaking spaces in size strings. Passing signals include expected compressed/unpacked byte totals and object needed/total counts for cold, partial, and no-op pulls.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-pull-sizes.sh -->
