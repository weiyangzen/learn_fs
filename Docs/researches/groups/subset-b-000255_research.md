# subset-b-000255 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-commit.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-commit.c

## Purpose
Implements `ostree commit`, the CLI path for importing one or more filesystem trees into an OSTree repository, producing a commit object, optionally attaching metadata and signatures, and optionally updating a branch ref. It is the main user-facing bridge from directories, tar archives, or existing refs into the repository object store.

## Important APIs, Types, And Functions
The entry point is `ostree_builtin_commit()`. Option state covers commit message fields, parent/ref selection, tree sources, stat/skip filters, SELinux policy, fsync, timestamp, signing, generated sizes, and composefs metadata. `CommitFilterData`, `handle_statoverride_line()`, `handle_skiplist_line()`, and `commit_filter()` implement per-path metadata rewriting and skipping. `commit_editor()` integrates `ot_editor_prompt()` to derive subject/body text. `parse_keyvalue_strings()`, `add_collection_binding()`, `add_ref_binding()`, and `fill_bindings()` build commit metadata. The implementation uses `OstreeMutableTree`, `OstreeRepoCommitModifier`, `OstreeSePolicy`, `OstreeSign`, libarchive import helpers, and repository transaction APIs.

## Control Flow
The command parses options and opens a writable repo, loads optional statoverride and skip-list files, validates that either `--branch` or `--orphan` was supplied, and resolves the parent from `--parent` or the target branch. It builds metadata and detached metadata from command-line `KEY=VALUE` inputs and optional parent metadata preservation, rejects conflicting owner/canonical/SELinux options, then creates a commit modifier if filtering, labeling, ownership, xattr, or permission behavior is needed. It prepares a transaction, optionally scans hardlinks, creates or seeds an mtree from `--base`, normalizes implicit path input to `--tree=dir=...`, and overlays each `dir=`, `tar=`, or `ref=` source into the mtree. After unmatched statoverride or skip-list checks, it writes the mtree, optionally skips the commit if unchanged from the parent, fills bindings/bootable/composefs metadata, writes the commit with normal or overridden timestamp, writes detached metadata, signs with signapi or GPG keys, updates the branch ref, commits the transaction, and prints either the checksum or table statistics.

## State And Persistence
Persistent effects include new content, directory metadata, directory tree, commit, detached metadata, signatures, and ref updates in the repo. `--consume` can delete imported local content. `--disable-fsync` changes repository durability behavior for the run. `--skip-if-unchanged` avoids writing a new commit and reuses the parent checksum. The function aborts any repository transaction on exit, including after successful commit where abort is harmless because no transaction remains active.

## Dependencies And Integration Points
This file integrates `ostree-repo-private.h`, libarchive import code, `ostree-sign`, `ot-editor`, `parse-datetime`, SELinux policy loading, and the public `OstreeRepo` commit APIs. It coordinates with ref binding verification used by fsck/pull, composefs metadata consumers, bootable commit metadata, static signature verification, and shell completion/man pages noted in comments.

## Risks And Edge Cases
The path has many option interactions: invalid parent handling, branch directory conflicts, unsigned orphan commits, tar filters requiring libarchive, SELinux-from-base being invalid with tar, and canonical permissions conflicting with nonzero owner overrides. `commit_filter()` removes matched statoverride/skip entries; unmatched entries become hard errors, which is useful but can surprise users after most import work has run. Inline private keys are supported but discouraged. Timestamp parsing truncates to seconds. Because transaction abort is unconditional, future changes must preserve commit/abort semantics carefully.

## Test Signals
Useful signals include committing `dir=`, `tar=`, and `ref=` sources; statoverride and skip-list success and unmatched failures; branch parent resolution; `--skip-if-unchanged`; generated table stats; metadata, detached metadata, bindings, and bootable metadata inspection via `ostree show`; signing and verification; SELinux policy labeling; and transaction cleanup after induced import failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-commit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-config.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-config.c

## Purpose
Implements `ostree config`, a small CLI for reading and mutating repository configuration keys. It supports `get`, `set`, and `unset` operations using either `section.key` syntax or an explicit `--group` option.

## Important APIs, Types, And Functions
`ostree_builtin_config()` is the entry point. `split_key_string()` validates and splits `section.key` inputs. The command uses `OstreeRepo`, `GKeyFile`, `ostree_repo_get_config()`, `ostree_repo_copy_config()`, `ostree_repo_write_config()`, and `ostree_repo_write_config_and_reload()`.

## Control Flow
After option parsing, the command requires an operation argument and computes the allowed argument count, with `set` needing one extra value. For `set`, it resolves the group/key pair, copies the repository config, writes the string value, and writes plus reloads the repository config. For `get`, it reads the active config and prints the string value. For `unset`, it copies config, removes the key, ignores missing group/key errors, and writes the config only when removal actually occurred. Unknown operations are reported as errors.

## State And Persistence
`set` persists changes to the repository config and reloads it into the repo object. `unset` persists only when a key was found and removed; missing keys leave disk unchanged. `get` is read-only. The file does not manage transactions because repository config writes are separate from object/ref transactions.

## Dependencies And Integration Points
The command depends on GLib `GKeyFile`, shared option parsing, and repository config helpers. The config it edits is consumed by remote setup, collection IDs, pull behavior, summary generation, signing configuration, and other libostree features.

## Risks And Edge Cases
The argument-count check only rejects too many arguments; each operation has its own missing-argument checks. Without `--group`, keys must contain a dot. Values are always strings, so non-string typed config data is not modeled here. `unset` uses `ostree_repo_write_config()` rather than write-and-reload, so callers relying on immediate in-memory reload behavior should verify the broader repo API expectations.

## Test Signals
Tests should cover set/get/unset with and without `--group`, invalid key syntax, missing operation or arguments, unknown operation, missing key removal being nonfatal, and persistence across reopening the repository.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-create-usb.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-create-usb.c

## Purpose
Implements `ostree create-usb`, which mirrors selected collection-ref pairs from the current repository to a repository located on a mounted removable device. It creates an archive-mode destination repo if needed and prepares it for later discovery by mount-based repo finders.

## Important APIs, Types, And Functions
`ostree_builtin_create_usb()` drives the command. It validates `OstreeCollectionRef` inputs, creates/open the destination with `ostree_repo_create_at()`, pulls with `ostree_repo_pull_with_options()`, regenerates summary metadata with `ostree_repo_regenerate_summary()`, and may create `.ostree/repos.d` symlinks. It uses `glnx_opendirat()`, fd-relative mkdir/symlink calls, `OstreeAsyncProgress`, and `OSTREE_REPO_PULL_FLAGS_MIRROR`.

## Control Flow
The command requires a mount path and at least one complete `COLLECTION-ID REF` pair. `--commit` is allowed only for a single pair. It opens the mount root, records its device, validates refs, creates the destination path under the mount root, creates an archive repo, confirms the destination is on the same device and not the source repo, marks it writable, and applies optional fsync disabling. It builds a `collection-refs` pull option containing collection ID, ref name, and optional commit override, then mirror-pulls from the source repository URI. On pull failure it aborts the destination transaction. After a successful pull, it regenerates summary metadata and creates a symlink under `.ostree/repos.d` for non-standard repo locations if one is not already present.

## State And Persistence
The command writes a destination OSTree repository under the mount, including objects, refs, summary metadata, and optional discovery symlinks. It does not alter source repo content. The destination is archive mode to support filesystems without Unix xattrs and to compress content for removable media.

## Dependencies And Integration Points
It integrates with collection-ref validation, local `file://` pulls, mount repository discovery (`OstreeRepoFinderMount`), summary consumers, and console progress. It depends on `ostree-remote-private.h` data types and libglnx fd-relative filesystem utilities.

## Risks And Edge Cases
The destination must be a descendant of the mount path by device check, which prevents accidentally writing elsewhere but may reject unusual bind-mount layouts. Symlink creation tries 100 generated names and then fails. The success message assumes all requested refs were copied because pull failures abort the operation. Summary regeneration is currently required due to finder assumptions documented in the file.

## Test Signals
Tests should verify argument validation, single-commit override rules, destination-not-source protection, same-device descendant enforcement, archive repo creation, copied collection refs, summary presence, generated symlink behavior for custom repo paths, and operation on non-xattr-capable media.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-create-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-diff.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-diff.c

## Purpose
Implements `ostree diff`, comparing two revisions or filesystem directories and optionally reporting object reachability statistics. With one argument it compares the argument's parent revision to the argument itself.

## Important APIs, Types, And Functions
`ostree_builtin_diff()` is the entry point. `parse_file_or_commit()` maps absolute or `./` paths to `GFile`s and other inputs to commit roots via `ostree_repo_read_commit()`. `reachable_set_intersect()` and `object_set_total_size()` support `--stats`. The implementation uses `ostree_diff_dirs_with_options()`, `ostree_diff_print()`, `ostree_repo_traverse_commit()`, and `ostree_repo_query_object_storage_size()`.

## Control Flow
The command parses options and requires at least one revision/directory argument. If only one is supplied, it appends `^` to form the source. If neither `--stats` nor `--fs-diff` is set, filesystem diff is enabled by default. Filesystem diff resolves both inputs, creates modified/removed/added arrays, applies xattr and owner override options, computes the diff, and prints it. Stats mode resolves both revisions, traverses each commit's reachable objects, prints object counts, intersects the sets, computes total storage size for common objects, and prints the formatted total.

## State And Persistence
The command is read-only. It creates transient `GFile`, `GPtrArray`, and reachability hash-table data structures but does not mutate refs, objects, or repository configuration.

## Dependencies And Integration Points
This file integrates the CLI with libostree diff and traversal APIs. It also accepts local filesystem trees, making it a comparison bridge between checked-out directories and repository commits. Owner override options feed `OstreeDiffDirsOptions` to normalize local file ownership during comparison.

## Risks And Edge Cases
Path detection is simple: only absolute paths and `./` prefixes are treated as files; other relative paths are interpreted as revisions. Stats mode requires both inputs to be resolvable revisions, not arbitrary directories. Object size summation can be expensive for large histories. Ignoring xattrs can hide security-relevant differences.

## Test Signals
Signals include default parent-vs-rev diff, explicit two-revision diff, directory-vs-directory diff, `--no-xattrs`, owner UID/GID normalization, stats counts and common size, invalid revision/path failures, and mixed path/revision behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-diff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-export.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-export.c

## Purpose
Implements `ostree export`, which streams a commit or subdirectory of a commit as an uncompressed GNU tar archive to stdout or a specified output path.

## Important APIs, Types, And Functions
`ostree_builtin_export()` is the entry point. It uses libarchive write APIs, `ostree_repo_read_commit()`, `ostree_repo_load_variant()`, `ostree_commit_get_timestamp()`, and `ostree_repo_export_tree_to_archive()`. `OstreeRepoExportArchiveOptions` carries xattr, timestamp, and path-prefix settings.

## Control Flow
After parsing options and requiring a commit argument, the libarchive-enabled path creates an archive writer, hardcodes GNU tar format and no filter, opens either `--output` or stdout, reads the target commit root and commit object, copies the commit timestamp into export options, resolves `--subpath` if provided, attaches `--prefix`, and exports the tree into the archive. It closes the archive and propagates libarchive errors. Without libarchive support it returns a not-supported error.

## State And Persistence
The repository is read-only. Persistent output is the optional archive file; otherwise bytes are written to stdout. Archive entry timestamps are derived from commit metadata rather than current time.

## Dependencies And Integration Points
This command depends on `HAVE_LIBARCHIVE`, `ostree-libarchive-private.h`, `OstreeRepoFile`, and repo export helpers. It is the inverse of commit tar import paths and provides interoperability with tar-based tooling.

## Risks And Edge Cases
The format and filter are intentionally fixed, so compression and alternate archive formats are not exposed here. `--no-xattrs` can drop metadata. `--subpath` relies on resolving within the commit root; invalid paths fail during export. Builds without libarchive compile the command but always fail at runtime with a clear unsupported error.

## Test Signals
Tests should validate archive creation to stdout and file, exported GNU tar readability, commit timestamp propagation, subpath exports, prefix rewriting, xattr inclusion/exclusion, missing commit argument, invalid subpath, and behavior in builds without libarchive.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-find-remotes.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-find-remotes.c

## Purpose
Implements `ostree find-remotes`, which searches configured, mounted, and optionally LAN-advertised repositories for requested collection-ref pairs and can pull the discovered refs into the current repository.

## Important APIs, Types, And Functions
`ostree_builtin_find_remotes()` is the main entry point. Helpers format timestamps and result mappings (`uint64_secs_to_iso8601()`, `format_ref_to_checksum()`), access private remote URLs (`remote_get_uri()`), track found refs (`add_keys_to_set_if_non_null()`), validate finder selections (`validate_finders_list()`), and bridge async APIs (`get_result_cb()`). The command uses `OstreeRepoFinderConfig`, `OstreeRepoFinderMount`, optional `OstreeRepoFinderAvahi`, `ostree_repo_find_remotes_async()/finish()`, and `ostree_repo_pull_from_remotes_async()/finish()`.

## Control Flow
The command opens a writable repo, requires complete `COLLECTION-ID REF` pairs, rejects `--mirror` without `--pull`, applies fsync/cache-dir options, validates refs, and builds a NULL-terminated `OstreeCollectionRef` array. If `--finders` is supplied, it validates non-empty, non-duplicate names and constructs finder objects in the requested order, starting Avahi when LAN discovery is enabled. It locks the console, creates progress for TTYs, starts asynchronous remote discovery, manually iterates the default main context until completion, prints each result's URI, finder, keyring, priority, summary timestamp, and ref-to-checksum mapping, reports unfound refs, and returns unless `--pull` is set. Pull mode builds options, adds mirror flags if requested, asynchronously pulls from all finder results, waits similarly, and prints success.

## State And Persistence
Discovery is read-only apart from cache-dir usage and progress state. Pull mode writes objects, refs, and metadata to the current repository. `--disable-fsync` weakens write durability for the operation. LAN finder startup touches Avahi state outside the repo.

## Dependencies And Integration Points
The command integrates repo finder plugins, remote private data, collection-ref APIs, pull-from-remotes APIs, Avahi when compiled, mount discovery used by `create-usb`, and console progress. It relies on summary metadata from candidate remotes.

## Risks And Edge Cases
The async API is driven by a manual main-context loop, so callbacks must always complete to avoid hanging. `remote_get_uri()` asserts that remote options contain a URL. `add_keys_to_set_if_non_null()` stores keys owned by result hash tables, so the found set must not outlive results. Avahi failures are downgraded to warnings by removing the finder. `--finders` rejects duplicates, and no results is considered a successful lookup.

## Test Signals
Tests should cover finder list validation, config/mount discovery, Avahi-disabled error handling, no-result output, partial found/unfound refs, pull and mirror-pull behavior, cache-dir/fsync options, malformed collection IDs or refs, and result ordering/format stability.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-find-remotes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-fsck.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-fsck.c

## Purpose
Implements `ostree fsck`, validating repository refs, collection refs, commit bindings, optional back references, and reachable object integrity. It can report all corruption, delete corrupted objects, mark partial commits, and add tombstones for commits whose parents are missing.

## Important APIs, Types, And Functions
`ostree_builtin_fsck()` orchestrates the command. `fsck_one_object()` verifies a single object, reports missing/corrupt parents, optionally deletes corrupt objects, and marks parent commits partial. `fsck_reachable_objects_from_commits()` traverses non-partial commits and validates reachable objects with progress. `fsck_commit_for_ref()` validates ref targets and optional bindings. `fsck_one_commit()` validates back references and gathers tombstone candidates. Private binding verification is reached through `ostree_cmd__private__()->ostree_repo_verify_bindings()`.

## Control Flow
The command parses options, lists normal refs, checks each ref's commit and optional binding metadata, lists local collection refs and checks them similarly, then enumerates all commit objects. It loads every commit, validates optional back references, records partial and fsck-partial counts, optionally collects tombstones, and adds only non-partial commits to the set for full object traversal. It traverses reachable objects from those commits, fscks each object, and updates progress. If tombstone mode is enabled, it enables tombstone commits and deletes selected commit objects. Finally it reports partial commits, fails on found corruption or fsck-partial commits, and prints success otherwise.

## State And Persistence
Normal validation is read-only. `--delete` removes corrupted objects and marks commits partial with `OSTREE_REPO_COMMIT_STATE_FSCK_PARTIAL`. `--add-tombstones` enables tombstone support and deletes missing-parent commits to create tombstones. Partial state persists in commit state metadata.

## Dependencies And Integration Points
This file depends on repository traversal, object fsck, commit state, collection refs, binding metadata, tombstone support, and console progress. It enforces invariants relied on by pull, commit binding verification, prune, and repository serving.

## Risks And Edge Cases
`--all` continues after corrupt non-missing objects but still fails at the end. Missing objects with parent information trigger partial marking for parent commits except when the missing object is itself a commit. `--verify-back-refs` implies binding verification. Collection refs are checked excluding remotes, while prune has a FIXME about collection refs in one branch. `n_fsck_partial` failure text uses `n_partial`, which may overstate the fsck-partial count.

## Test Signals
Tests should inject missing content, corrupt objects, missing commits, invalid ref bindings, invalid back references, partial commits, tombstone creation, delete behavior, quiet output, all-errors behavior, and collection-ref validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-fsck.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-gpg-sign.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-gpg-sign.c

## Purpose
Implements legacy `ostree gpg-sign`, adding or deleting GPG signatures stored in commit detached metadata.

## Important APIs, Types, And Functions
`ostree_builtin_gpg_sign()` is the command entry. `usage_error()` prints help for argument failures. `delete_signatures()` reads detached metadata, looks up the private `_OSTREE_METADATA_GPGSIGS_NAME` signature array, verifies signatures to map key IDs to signature indexes, removes matching signatures, and writes updated detached metadata. Signing uses `ostree_repo_sign_commit()`.

## Control Flow
The command requires a commit and at least one GPG key ID, resolves the commit, and either deletes matching signatures or appends new signatures. Delete mode reads detached metadata, extracts signatures, verifies the commit to get an `OstreeGpgVerifyResult`, matches provided key IDs to signature indexes, removes unique matched entries, removes the metadata key if no signatures remain, writes the new detached metadata, and prints the count. Add mode loops over key IDs and signs the resolved commit using the optional GPG homedir.

## State And Persistence
The command persists changes only to detached metadata associated with the commit. Delete mode may remove the GPG signature metadata key entirely. Add mode appends GPG signatures. It does not update commit objects, refs, or summaries.

## Dependencies And Integration Points
It depends on GPGME-enabled libostree APIs, private core metadata names, `OstreeGpgVerifyResult`, detached metadata read/write APIs, and repository revision resolution. It is conditionally declared in `ot-builtins.h` when GPGME is enabled.

## Risks And Edge Cases
Delete mode is low-level and depends on the signature array ordering matching verify-result ordering. It rereads detached metadata indirectly through verification. If verification fails, deletion fails even if raw metadata exists. Missing signature metadata is treated as zero deletions. This command is GPG-specific, whereas newer signapi behavior is implemented in `ot-builtin-sign.c`.

## Test Signals
Tests should cover signing with one and multiple keys, deleting one signature among many, deleting absent key IDs, no-signature metadata, custom GPG homedir, invalid commit, verification failure during deletion, and metadata key removal when all signatures are deleted.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-gpg-sign.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-init.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-init.c

## Purpose
Implements `ostree init`, creating a new repository with a selected storage mode and optional collection ID.

## Important APIs, Types, And Functions
`ostree_builtin_init()` is the entry point. It uses `ostree_repo_mode_from_string()`, `ostree_repo_set_collection_id()`, and `ostree_repo_create()`. Options are `--mode` and `--collection-id`.

## Control Flow
The command parses options while allowing the shared option layer to construct the target `OstreeRepo`, converts the mode string to an `OstreeRepoMode`, sets the collection ID on the repo object, and creates the repository in that mode. Any invalid mode, collection ID, or filesystem creation error aborts.

## State And Persistence
Successful execution creates the repository directory structure, config, object store layout, and collection ID configuration if supplied. It does not create refs, commits, or summaries.

## Dependencies And Integration Points
The file is a thin CLI wrapper over repo creation APIs. The selected mode affects later commit, checkout, pull, and object storage behavior. The collection ID is consumed by collection refs, summary metadata, commit binding, find-remotes, and create-usb workflows.

## Risks And Edge Cases
The default mode is `bare`, which may not be suitable for unprivileged or archive distribution use. Invalid collection IDs are expected to be rejected by the repo API. Re-running on an existing repo depends on `ostree_repo_create()` semantics outside this file.

## Test Signals
Signals include creation for each supported mode, invalid mode rejection, collection ID persistence in config, opening the created repo, and behavior when the target path already exists or is unwritable.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-log.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-log.c

## Purpose
Implements `ostree log`, printing a commit and recursively walking parent commits to show history.

## Important APIs, Types, And Functions
`ostree_builtin_log()` resolves the starting revision. `log_commit()` loads a commit variant, prints it with `ot_dump_object()`, obtains its parent with `ostree_commit_get_parent()`, and recurses. `OstreeDumpFlags` controls raw output.

## Control Flow
The command parses `--raw`, requires a revision, resolves it to a checksum, and calls `log_commit()`. Each recursive call loads the commit object. If a parent is missing during recursion, it prints a marker indicating history beyond that commit was not fetched and stops successfully. Other load failures propagate. Loaded commits are dumped, then parent recursion continues until there is no parent.

## State And Persistence
The command is read-only. It allocates variants and strings while walking history and writes formatted history to stdout.

## Dependencies And Integration Points
It depends on repository revision resolution, commit object loading, parent extraction, and the shared dump helpers in `ot-dump.c`. Its missing-parent behavior is important for shallow pulls or partial local history.

## Risks And Edge Cases
Recursion depth follows commit history and could be large. Only missing parents during recursive history are downgraded to a message; a missing starting commit is fatal. Raw mode delegates byte-swapped variant formatting to dump helpers.

## Test Signals
Tests should cover linear history output, root commits without parents, shallow history missing a parent, invalid revisions, raw output, and formatting consistency with `ostree show` for commit objects.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-ls.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-ls.c

## Purpose
Implements `ostree ls`, listing file metadata for paths inside a commit, with optional recursion, checksums, xattrs, and NUL-separated filename output.

## Important APIs, Types, And Functions
`ostree_builtin_ls()` reads a commit root. `print_one_argument()` resolves requested paths relative to the root. `print_directory_recurse()` enumerates directories. `print_one_file_text()` formats type, mode, owner, size, checksums, xattrs, path, and symlink target. `print_one_file_binary()` implements `--nul-filenames-only`.

## Control Flow
The command requires a commit, reads its root as an `OstreeRepoFile`, and either lists requested paths or `/`. For each path it queries fast file info without following symlinks, prints that entry, and if it is a directory, recurses indefinitely for `--recursive`, one level for default directory listing, or not at all for `--dironly`. Text output resolves repo file checksums before formatting. Binary output writes the path bytes followed by NUL.

## State And Persistence
The command is read-only. It walks virtual repository file objects and prints metadata to stdout. Xattr variants are read transiently when requested.

## Dependencies And Integration Points
It depends on `OstreeRepoFile`, GIO file enumeration/query APIs, `OSTREE_GIO_FAST_QUERYINFO`, and repo-file checksum/xattr helpers. Output is a user-facing inspection surface for commit contents created by commit, pull, or static delta application.

## Risks And Edge Cases
Recursive listing can be large. Invalid GIO file types are treated as hard errors in text mode. `--checksum` prints both directory contents checksum and object checksum for directories, which consumers must parse carefully. NUL mode prints only filenames, not metadata. Path resolution is relative to the commit root and errors are prefixed with the requested path.

## Test Signals
Tests should cover regular files, directories, symlinks, special files, default one-level directory listing, recursive and dironly modes, checksums, xattrs, NUL output, missing paths, and invalid commit resolution.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-ls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-prune.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-prune.c

## Purpose
Implements `ostree prune`, deleting or reporting unreachable objects and supporting explicit commit deletion, static-delta pruning, depth-based retention, branch-specific retention, branch filtering, age-based retention, and commit-only pruning.

## Important APIs, Types, And Functions
`ostree_builtin_prune()` is the entry point. `delete_commit()` ensures an explicit commit is not referenced before deleting it as a tombstone commit. `traverse_keep_younger_than()` builds a reachable set down a parent chain until commits are older than a parsed timestamp. The command uses `ostree_repo_prune()`, `ostree_repo_prune_static_deltas()`, `ostree_repo_traverse_commit_with_flags()`, `ostree_repo_prune_from_reachable()`, and exclusive repo locking.

## Control Flow
After parsing, the command requires writability unless `--no-prune`. If `--delete-commit` is set, it rejects `--no-prune`, then either prunes static deltas for that commit or verifies the commit is not referenced and deletes it. Without `--delete-commit`, `--static-deltas-only` is rejected. It builds prune flags and either delegates to the classic prune API when no advanced retention options are present, or manually computes reachability under an exclusive lock. The advanced path parses `--keep-younger-than`, parses `--retain-branch-depth` entries, lists refs, converts `--only-branch` into retain rules for all other refs, traverses refs according to per-branch or global depth/age rules, and prunes from the reachable set. It prints total objects and deleted or would-delete counts.

## State And Persistence
Normal prune deletes unreachable objects unless `--no-prune`. Explicit commit deletion enables tombstone commits and deletes the commit object. Static-delta-only mode deletes delta artifacts. Advanced prune holds an exclusive lock to avoid racing new content against reachability computation.

## Dependencies And Integration Points
The command integrates repo traversal, pruning APIs, tombstone support, static delta metadata, ref listing, date parsing, and repo locking. Its output and behavior are important for repository maintenance, mirror management, and storage reclamation.

## Risks And Edge Cases
Advanced pruning currently lists normal refs and has a FIXME about collection refs. `--only-branch` first verifies each named branch exists. Date parsing is user-facing and errors can block cleanup. Incorrect retention rules can delete history. `--commit-only` avoids traversing content and uses both traversal and prune flags. Static-deltas-only is intentionally restricted to explicit commit deletion.

## Test Signals
Tests should cover dry-run/no-prune counts, classic depth prune, explicit commit deletion rejection while referenced, tombstone creation, static delta pruning, keep-younger-than traversal, retain-branch-depth parsing and behavior, only-branch interactions, commit-only pruning, and concurrent lock behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-prune.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-pull-local.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-pull-local.c

## Purpose
Implements `ostree pull-local`, copying refs and objects from a local repository path into the current repository using the same pull machinery as remote pulls with a `file://` source URI.

## Important APIs, Types, And Functions
`ostree_builtin_pull_local()` is the command entry. It builds pull flags and options for `ostree_repo_pull_with_options()`. `noninteractive_console_progress_changed()` suppresses intermediate progress but allows final status retrieval. The command uses `ostree_repo_list_refs()` to clone all refs when none are specified.

## Control Flow
The command opens a writable destination repo, requires a source repository path, converts absolute or relative paths to a `file://` URI, applies pull flags for untrusted verification, bare-user-only file checks, and commit-metadata-only mode, and disables fsync if requested. With no explicit refs, it opens the source repo and lists all normal refs; otherwise it uses the provided refs. It builds a `GVariant` pull option dictionary containing flags, refs, optional remote override, static delta settings, GPG verification toggles, binding verification toggle, depth, disabled signapi verification for local pulls, and optional per-object fsync. It runs the pull with TTY or noninteractive progress, prints final status for non-TTYs, finishes progress, and aborts any open transaction on exit.

## State And Persistence
The destination repo receives copied commits, metadata, content objects, and refs according to pull options. Source repo state is read-only. Local pulls always disable signapi verification unless users model the source as a remote with configured signature verification. Fsync options affect durability.

## Dependencies And Integration Points
This command shares the pull engine with `ostree pull`, while adding local source discovery and all-ref cloning. It integrates with GPG verification, static deltas, commit binding verification, and per-object fsync behavior.

## Risks And Edge Cases
When no refs are supplied, only normal refs are listed; a FIXME notes missing collection-ref support. Relative paths are joined with the current directory without URI escaping. Using `--remote` only overrides refspec naming; it does not configure a remote. Disabling signapi verification is a deliberate local-pull policy that can surprise users expecting signature enforcement.

## Test Signals
Tests should cover cloning all refs, pulling selected refs, relative and absolute source paths, remote override, untrusted checksum verification, static-delta require/disable options, GPG verification toggles, depth behavior, final noninteractive progress output, and transaction abort after failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-pull-local.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-pull.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-pull.c

## Purpose
Implements `ostree pull`, fetching refs, commits, objects, summaries, and optional static deltas from a configured remote or refspec into the current repository.

## Important APIs, Types, And Functions
`ostree_builtin_pull()` is the command entry. `gpg_verify_result_cb()` prints GPG verification results while temporarily unlocking the console. `dry_run_console_progress_changed()` formats static-delta dry-run size/part information. `noninteractive_console_progress_changed()` suppresses progress spam. The command builds a large `a{sv}` option dictionary for `ostree_repo_pull_with_options()`.

## Control Flow
The command opens a writable repo, requires a remote or refspec, applies fsync/cache-dir settings, builds pull flags for mirror, commit-only, trusted/untrusted HTTP, and bare-user-only files, and rejects `--dry-run` unless static deltas are required. It parses either a remote name plus optional branches, or a `REMOTE:REF` refspec. Branch arguments may include `@CHECKSUM` commit overrides, which are validated and split into parallel refs and override arrays. It then builds pull options for URL override, subpaths, flags, refs, depth, progress frequency, network retry/low-speed/concurrency settings, retry-all toggle, static delta controls, dry-run, timestamp checks, commit overrides, local cache repos, per-object fsync, binding verification, HTTP headers, and appended user agent. It installs progress callbacks, optionally connects GPG verify result output for TTYs, runs the pull, prints final noninteractive status, finishes progress, asserts dry-run progress happened, disconnects signals, and returns.

## State And Persistence
Successful pulls write objects, commit metadata, refs, summaries, and possibly static delta results to the local repository. Mirror mode writes mirror-suitable refs and fetches all refs when none are specified by the pull engine. Cache-dir and localcache repos affect object sourcing. The command itself does not explicitly abort transactions, relying on pull API behavior.

## Dependencies And Integration Points
This is the CLI front end to libostree's remote fetcher, HTTP stack, static delta engine, GPG verification signals, timestamp validation, binding verification, and progress system. It consumes remote configuration and is used by update, mirror, CI, and repository synchronization workflows.

## Risks And Edge Cases
Branch `@CHECKSUM` overrides require careful array alignment. `--disable-retry-on-network-errors` maps to an option named `retry-all-network-errors` with boolean false. HTTP headers must be `NAME=VALUE`. Dry-run depends on static delta metadata and asserts a progress callback. Trust flags can weaken integrity verification, especially `--http-trusted`. Refspec parsing distinguishes remotes by presence of `:`, which affects remote names containing colons.

## Test Signals
Tests should cover remote and refspec parsing, branch checksum overrides, mirror and commit-only flags, dry-run requiring static deltas and printing size data, timestamp checks, HTTP headers, URL override, subpath single and multiple forms, network option propagation, local cache repos, GPG verify output, and failure cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-pull.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-refs.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-refs.c

## Purpose
Implements `ostree refs`, listing, creating, deleting, and aliasing refs, with optional revision output and collection-ref support.

## Important APIs, Types, And Functions
`ostree_builtin_refs()` dispatches per prefix/revision. `do_ref()` handles normal refs and aliases. `do_ref_with_collections()` handles collection refs. `collection_ref_cmp()` sorts collection refs. The implementation uses `ostree_repo_list_refs()`, `ostree_repo_list_refs_ext()`, `ostree_repo_set_ref_immediate()`, `ostree_repo_set_alias_ref_immediate()`, `ostree_repo_list_collection_refs()`, and `ostree_repo_set_collection_ref_immediate()`.

## Control Flow
The command parses options and, if arguments are provided, processes each as a prefix or existing revision. Delete and create modes enforce safer arity: deletes require at least one prefix and creates require exactly one existing revision. Normal listing loads refs or aliases, sorts names, and prints names, `name -> alias`, or `name<TAB>revision`. Create mode checks whether the new ref already exists, honors `--force`, parses the new refspec, and either creates an alias to an existing ref or resolves the source revision and writes a new ref. Delete mode lists matching refs, rejects deletion if a matching ref has an active alias, parses each refspec, and clears it. Collection mode lists, creates, or deletes collection refs, treating `collection:ref` syntax as an input convention for creation.

## State And Persistence
Listing is read-only. Create, alias, and delete persist ref changes immediately. The entry point aborts any repository transaction on exit, although these helpers use immediate ref APIs rather than explicit transactions.

## Dependencies And Integration Points
The command integrates normal refs, remote refspec parsing, alias refs, collection refs, revision resolution, and validation helpers. It is a key companion to commit, reset, pull, prune, and summary generation.

## Risks And Edge Cases
Collection create intentionally abuses refspec syntax by treating the left side as collection ID. Deleting a ref with active aliases fails to avoid dangling aliases. Alias creation cannot target remote refs and requires the target ref to exist. Existing directory conflicts during resolve are cleared so lower-level ref writing can handle them. Collection deletion lists with `OSTREE_REPO_LIST_REFS_EXT_NONE`, so remote and local behavior should be checked carefully.

## Test Signals
Tests should cover sorted listing, revision output, prefix filtering, alias listing/creation/replacement, delete rejection with aliases, forced create replacement, remote refspec parsing, collection ref listing/creation/deletion, invalid collection IDs, and safe errors for missing required prefixes.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-refs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-remote.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-remote.c

## Purpose
Implements the `ostree remote` command dispatcher. It selects a remote subcommand, adjusts arguments, prints help for missing or unknown subcommands, and invokes the corresponding implementation from `ot-remote-builtins.h`.

## Important APIs, Types, And Functions
`remote_subcommands[]` declares subcommands such as `add`, `delete`, `show-url`, `list`, GPG key operations, cookie operations when HTTP support exists, `refs`, and `summary`. `remote_option_context_new_with_commands()` builds the help summary. `ostree_builtin_remote()` parses out the first non-option command and dispatches through `OstreeCommand`.

## Control Flow
The dispatcher scans `argv` from index 1, removing the first non-option argument as the subcommand name while preserving other options and stopping at `--`. It then searches the static command table. If not found, it builds a context, lets shared option parsing handle global options such as version/help, emits a missing or unknown subcommand error, prints help, and returns false. For a valid subcommand it updates `g_get_prgname()` to include the subcommand, constructs a sub-invocation, and calls the subcommand function with the adjusted argc/argv.

## State And Persistence
The dispatcher itself is stateless except for mutating the process program name and argv layout. Persistent effects depend on the selected subcommand, such as remote config, GPG keys, cookies, or remote queries.

## Dependencies And Integration Points
It depends on `ot-main.h` command invocation conventions through `ot-builtins.h`, remote builtin declarations, compile-time GPG and HTTP feature gates, and shared option parsing. This file is the public CLI routing layer for remote management.

## Risks And Edge Cases
Argument rewriting is in-place, so future options that look like commands must preserve the first non-option rule. `--` stops command discovery, which can produce no subcommand. Feature-gated commands disappear from help and dispatch when compiled without GPGME or HTTP support. Help/error behavior relies on shared option parsing not consuming normal remote subcommands.

## Test Signals
Tests should verify dispatch to each compiled subcommand, missing and unknown subcommand help, global help/version behavior, options before and after the subcommand, `--` behavior, and feature-gated command visibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-remote.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-reset.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-reset.c

## Purpose
Implements `ostree reset`, moving an existing normal ref to a target commit.

## Important APIs, Types, And Functions
`ostree_builtin_reset()` is the only function. It uses `ostree_repo_list_refs()` to validate the ref exists, `ostree_repo_resolve_rev()` to resolve the target, and `ostree_repo_prepare_transaction()`, `ostree_repo_transaction_set_ref()`, and `ostree_repo_commit_transaction()` to persist the ref update.

## Control Flow
The command parses options, opens a writable repo, requires `REF COMMIT`, lists known refs, rejects unknown refs, resolves the target revision to a checksum, prepares a transaction, queues the ref update, commits the transaction, and aborts any remaining transaction state on exit.

## State And Persistence
Successful execution changes one normal ref to point at the resolved target checksum. It does not create new refs and does not support collection refs, as noted by a FIXME. Objects are not written; the target must already resolve.

## Dependencies And Integration Points
This is a simple ref mutation command integrated with repository transactions and revision resolution. It overlaps conceptually with `ostree refs --create --force` but requires the ref already exist.

## Risks And Edge Cases
Collection refs are unsupported. The error domain/code for invalid refs uses `G_IO_ERROR` for both domain and code in the source, which looks suspicious because the code should normally be a `GIOErrorEnum`. Unknown refs are rejected before target resolution, so it cannot be used to create a ref.

## Test Signals
Tests should cover moving an existing ref, rejecting missing args, rejecting unknown refs, rejecting invalid target revisions, transaction rollback after induced commit failure, and documenting collection-ref unsupported behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-rev-parse.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-rev-parse.c

## Purpose
Implements `ostree rev-parse`, resolving revision names to commit checksums, plus a `--single` mode for repositories expected to contain exactly one commit object.

## Important APIs, Types, And Functions
`ostree_builtin_rev_parse()` is the entry point. It uses `ostree_repo_resolve_rev()` for normal arguments and `ostree_repo_list_commit_objects_starting_with()` plus `ostree_object_name_deserialize()` for `--single`.

## Control Flow
After parsing, `--single` rejects additional arguments, lists all commit objects, fails if none or more than one are found, deserializes the sole object name, asserts it is a commit, prints the checksum, and returns. Normal mode requires at least one revision argument, resolves each to a checksum, and prints one checksum per line.

## State And Persistence
The command is read-only. It prints resolved checksums and allocates transient object-list data.

## Dependencies And Integration Points
It is a CLI wrapper around libostree revision resolution and object enumeration. Scripts can use it before reset, diff, static delta generation, or other commands requiring stable checksums.

## Risks And Edge Cases
`--single` counts all commit objects, not refs, so repositories with unreferenced commits fail as multiple. Normal mode stops at the first resolution error. The command does not expose collection-ref-specific resolution options.

## Test Signals
Tests should cover resolving branches, checksums, parent syntax, multiple arguments, missing argument errors, `--single` success with one commit object, and `--single` failures for zero or multiple commit objects.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-rev-parse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-show.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-show.c

## Purpose
Implements `ostree show`, a multipurpose inspection command for commit/object variants, metadata keys, related commits, commit size metadata, arbitrary GVariant files, and commit GPG signatures.

## Important APIs, Types, And Functions
`ostree_builtin_show()` dispatches option-specific behavior. Helpers include `do_print_variant_generic()`, `do_print_related()`, `get_metadata()`, `do_list_metadata_keys()`, `do_print_metadata_key()`, `do_print_sizes()`, `print_object()`, and `print_if_found()`. It uses `ot_dump_object()`, `ot_dump_variant()`, commit metadata APIs, object-size metadata APIs, GPG verification APIs, and `ostree_repo_load_file()` for file objects.

## Control Flow
The command requires one object argument. Metadata key modes resolve the revision and print or list normal/detached metadata. Related mode loads the commit and prints related commit names/checksums. Variant type mode reads an arbitrary file descriptor as the requested GVariant type. Size mode resolves the commit and totals archived/unpacked sizes from commit object-size metadata, separating missing local objects as needed. Default mode treats non-checksum inputs as revisions and prints the commit; checksum inputs are searched as commit, dir-meta, and dir-tree objects, and if none are found, loaded as a file object and formatted with type, size/target, mode, uid/gid, and xattrs. Commit printing may also verify and describe GPG signatures unless no signature exists.

## State And Persistence
The command is read-only. It maps/loads variants, file metadata, xattrs, and GPG verification results, and writes formatted data to stdout/stderr.

## Dependencies And Integration Points
This file is the main consumer of `ot-dump.c` helpers. It integrates repository object loading, revision resolution, detached metadata, object-size metadata, GPG homedir and remote verification settings, and file object inspection. It complements `log`, `summary`, `ls`, and `fsck`.

## Risks And Edge Cases
Option modes are mutually exclusive by if/else order rather than explicit validation, so if multiple options are passed only the first matching branch runs. `--print-hex` only changes byte-array metadata output. `--no-byteswap` affects variant formatting. GPG no-signature is ignored, while other verification errors are fatal. File-object fallback only happens for checksum-looking inputs.

## Test Signals
Tests should cover commit display by ref and checksum, object type search order, file object fallback for regular files and symlinks, metadata list/print for normal and detached metadata, byte-array hex output, related commits, variant file printing, sizes metadata, raw/no-byteswap behavior, and GPG verification output/errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-show.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-sign.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-sign.c

## Purpose
Implements `ostree sign`, the non-GPG signapi command for signing commits and verifying commit signatures, defaulting to Ed25519 when available.

## Important APIs, Types, And Functions
`ostree_builtin_sign()` is the command entry. `usage_error()` prints help for argument failures. The implementation uses `ostree_sign_get_by_name()`, `ostree_sign_set_sk()`, `ostree_sign_set_pk()`, `ostree_sign_add_pk()`, `ostree_sign_load_pk()`, `ostree_sign_commit()`, `ostree_sign_commit_verify()`, `ostree_sign_read_sk()`, and `OstreeBlobReader`.

## Control Flow
The command requires a commit. Signing mode requires at least one key ID unless a keys file is used; verify mode may use provided public key IDs, a keys file, or system configuration. It resolves the commit, initializes the selected sign type, and loops over key arguments. In verify mode it tries each key as a public key and returns success on the first valid signature. In signing mode it treats each key argument as a secret key string and signs. Verify mode then optionally loads public keys from a file or system/custom key directory and verifies. Signing mode optionally reads multiple encoded secret keys from a file and signs with each. If verify mode finds no valid signatures and no lower-level error remains, it returns a "No valid signatures found" error. Successful verification clears earlier per-key errors.

## State And Persistence
Signing persists signatures in commit detached metadata through signapi. Verification is read-only. The command does not update refs or summaries.

## Dependencies And Integration Points
It depends on `ostree-sign`, private core definitions, GLib file streams, and optional Ed25519 build support for keys-file/keys-dir options. It overlaps with commit-time signing and static delta signature verification.

## Risks And Edge Cases
The `--delete` option is declared but not implemented in control flow in this file, so users may expect deletion that does not occur. Verification ignores keys that cannot be set and continues, clearing errors if a later key succeeds. Keys from command-line strings are sensitive. File reading checks regular-file status for signing files but verification file loading is delegated to signapi.

## Test Signals
Tests should cover signing with string keys, signing with multiple file keys, verifying with explicit public keys, verifying from keys-file and keys-dir/system config, unsupported sign types, no-valid-signature errors, error clearing after later success, and the current behavior of the declared `--delete` option.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-sign.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-static-delta.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-static-delta.c

## Purpose
Implements the `ostree static-delta` dispatcher and subcommands for listing, showing, deleting, generating, applying offline, verifying, indexing, and reindexing static deltas.

## Important APIs, Types, And Functions
`ostree_builtin_static_delta()` dispatches subcommands from `static_delta_subcommands[]`. Subcommand handlers include `ot_static_delta_builtin_list()`, `indexes()`, `reindex()`, `show()`, `delete()`, `generate()`, `apply_offline()`, and `verify()`. The file uses private command hooks for static delta dump/delete/query, public repo APIs for list/generate/reindex/apply/verify, and `OstreeSign` for signapi signatures.

## Control Flow
The dispatcher finds the first non-option command or help flag, prints top-level usage for help/missing/unknown commands, adjusts the program name, and invokes the handler with the original argc/argv. List and indexes parse options, list delta names or indexes, and print empty markers when none exist. Reindex calls `ostree_repo_static_delta_reindex()` with optional `--to`. Show and delete require a delta ID at `argv[2]` and call private dump/delete functions. Generate requires a `to` revision by option or positional argument, derives the from source from `--empty`, `--from`, or `to^`, resolves revisions, optionally skips existing deltas, computes metadata endianness, builds generation parameters for sizes, bsdiff, inline parts, output filename, signing keys from arguments and file, and sign type, then calls `ostree_repo_static_delta_generate()`. Apply-offline opens a writable repo, optionally builds a signature verifier from keys, prepares a transaction, executes the offline delta with signature verification, and commits. Verify builds a verifier and calls `ostree_repo_static_delta_verify_signature()`.

## State And Persistence
List, indexes, show, and verify are read-only. Delete removes delta files. Generate writes static delta metadata/parts to the repo or a target directory. Reindex updates static delta indexes. Apply-offline writes objects and metadata into the repo transactionally. Signature options persist on generated delta metadata.

## Dependencies And Integration Points
This file integrates static delta generation/application, private delta maintenance commands, repository transactions, object fetching workflows, signapi key loading, and CLI help conventions. Generated deltas are consumed by pull, create-usb, and mirror workflows.

## Risks And Edge Cases
Subhandlers expect the subcommand to remain at `argv[1]`, so required operands start at `argv[2]`. Numeric size options use `g_ascii_strtoull()` without explicit validation of trailing text. `--empty` conflicts with `--from`. Apply-offline clears the sign engine if no default public keys are available and no explicit key source was provided, allowing unsigned/offline behavior depending on API semantics. Generate key-file parsing treats each line as a key string and may add allocated strings to a non-freeing `GPtrArray`.

## Test Signals
Tests should cover top-level help and unknown commands, list/index empty and populated output, show/delete by delta ID, generate from parent/from/empty, if-not-exists skip, endian options, bsdiff/inline/size parameters, output directory generation, signing from args and file, offline apply with and without signature keys, verify success/failure, and reindex filtering by target revision.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-static-delta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-summary.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-summary.c

## Purpose
Implements `ostree summary`, updating repository summary metadata and viewing or querying the local summary file.

## Important APIs, Types, And Functions
`ostree_builtin_summary()` is the entry point. `build_additional_metadata()` parses `KEY=VALUE` arguments as GVariant text into an `a{sv}` dictionary. `get_summary_data()` reads the repo's `summary` file as `GBytes`. The command uses `ostree_repo_regenerate_metadata()`, `ot_dump_summary_bytes()`, `ot_dump_summary_metadata_keys()`, and `ot_dump_summary_metadata_key()`.

## Control Flow
The command initializes signapi when `--sign` keys are supplied. In update mode it requires repo writability, parses optional additional metadata, builds metadata options for GPG key IDs, GPG homedir, signapi secret keys, and sign type, then regenerates repository metadata. View/raw mode reads the summary file and dumps it, with raw mode setting `OSTREE_DUMP_RAW`. Metadata list and print modes read the summary and delegate to dump helpers. If no operation option is supplied, it returns an error asking for `-u`.

## State And Persistence
Update mode writes or replaces summary metadata and signatures. View, raw, list-metadata-keys, and print-metadata-key are read-only. Additional metadata becomes part of the regenerated summary.

## Dependencies And Integration Points
This file connects repository summary generation, GPG signing, signapi signing, raw summary parsing, and user-facing dump helpers. Summary files are consumed by remote clients, find-remotes, pull, static delta discovery, and create-usb.

## Risks And Edge Cases
Additional metadata values must parse as GVariant text, not plain strings. Multiple operation flags are resolved by if/else order, with update taking precedence. `get_summary_data()` reads the `summary` file directly via `repo_dir_fd`, so missing summaries produce open errors. The local `OstreeSign *sign` is only used to validate sign type existence; actual signing options are passed to repo metadata generation.

## Test Signals
Tests should cover update with no metadata, update with additional metadata, GPG and signapi signing options, view and raw output, missing summary errors, listing and printing metadata keys, invalid `KEY=VALUE`, invalid variant values, and no-option error behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-summary.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtins.h -->
# sources/cloud-native/ostree/src/ostree/ot-builtins.h

## Purpose
Declares the public builtin function prototypes for the `ostree` CLI command table. It provides a uniform signature for command implementations across this directory.

## Important APIs, Types, And Functions
The `BUILTINPROTO(name)` macro expands to `gboolean ostree_builtin_name(int argc, char **argv, OstreeCommandInvocation *invocation, GCancellable *cancellable, GError **error)`. The header declares builtins for admin, cat, config, checkout, checksum, commit, diff, export, find-remotes, create-usb, optional gpg-sign, init, log, pull, pull-local, ls, prune, refs, reset, fsck, sign, show, static-delta, summary, rev-parse, remote, and write-refs.

## Control Flow
There is no runtime control flow. The preprocessor includes `config.h` and `ot-main.h`, defines the macro, emits declarations, conditionally includes `gpg_sign` when GPGME is enabled, undefines the macro, and closes GLib extern "C" guards.

## State And Persistence
The header has no runtime state or persistence. Its compile-time state is the feature-gated declaration set controlled by configuration macros.

## Dependencies And Integration Points
It is included by builtin implementation files and the main command registration code. The uniform signature aligns all CLI functions with `OstreeCommandInvocation`, cancellation, and GLib error propagation.

## Risks And Edge Cases
Feature gates must match command table entries and implementation compilation or builds will fail. Adding/removing a builtin requires updating this header, the command table, docs, and shell completion. The macro hides the full signature, so readers must expand it mentally when navigating.

## Test Signals
Build coverage is the primary signal: all declared builtins must link under each feature matrix. CLI smoke tests for command availability should match declarations, especially GPGME-disabled builds.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtins.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-dump.c -->
# sources/cloud-native/ostree/src/ostree/ot-dump.c

## Purpose
Provides shared formatting helpers for OSTree CLI commands that dump variants, commit objects, summary files, summary metadata keys, and GPG key variants.

## Important APIs, Types, And Functions
Public functions are `ot_dump_variant()`, `ot_dump_object()`, `ot_dump_summary_bytes()`, `ot_dump_summary_metadata_keys()`, `ot_dump_summary_metadata_key()`, and `ot_dump_gpg_key()`. Internal helpers include `format_timestamp()`, `uint64_secs_to_iso8601()`, `dump_indented_lines()`, `dump_commit()`, `dump_summary_ref()`, `dump_summary_refs()`, `strptr_cmp()`, and `dump_gpg_subkey()`.

## Control Flow
`ot_dump_variant()` byte-swaps variants on little-endian systems before printing, matching OSTree's big-endian serialized metadata convention. `ot_dump_object()` prints object type/checksum, optionally prints unswapped or raw variants, and pretty-prints commit objects. Commit dumping extracts subject, body, timestamp, parent, content checksum, and optional version. Summary dumping parses `OSTREE_SUMMARY_GVARIANT_FORMAT`, optionally raw-dumps, prints refs under the main collection ID and collection map, then prints recognized metadata keys with friendly labels and timestamps. Metadata key listing sorts keys before printing. Metadata key printing looks up a key and dumps its value. GPG key dumping validates the variant type, prints primary key/subkeys with timestamps and status flags, and prints UIDs plus update URLs.

## State And Persistence
All functions are read-only formatters. They allocate transient variants/strings and write to stdout. `dump_commit()` calls `errx(1)` on invalid timestamps, which exits the process rather than returning an error.

## Dependencies And Integration Points
The file depends on OSTree core variant formats, repo private summary constants, static delta summary keys, admin checksum version extraction, GLib date/time/variant APIs, and CLI commands such as `show`, `log`, `summary`, and remote GPG key listing.

## Risks And Edge Cases
Endianness handling is central: default output byte-swaps for readability, while callers can request unswapped/raw output through flags. Invalid summary checksum bytes are printed as error text rather than failing the whole dump. Recognized summary keys are pretty-printed; unknown keys use generic `g_variant_print()`. Process exit from `dump_commit()` is harsher than GLib error propagation and should be considered before reusing it in library-like contexts.

## Test Signals
Tests should cover variant byte-swapping, commit pretty output, raw and unswapped object output, summary refs with and without collection maps, pretty labels for last-modified/expires/mode/tombstones/static-deltas, sorted metadata key listing, missing metadata key errors, valid and invalid checksum bytes, and GPG key formatting for revoked/expired/invalid keys and UIDs.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-dump.h -->
# sources/cloud-native/ostree/src/ostree/ot-dump.h

## Purpose
Declares shared dump/formatting APIs used by OSTree CLI commands to render variants, objects, summaries, summary metadata, and GPG keys.

## Important APIs, Types, And Functions
`OstreeDumpFlags` defines `OSTREE_DUMP_NONE`, `OSTREE_DUMP_RAW`, and `OSTREE_DUMP_UNSWAPPED`. Declared functions are `ot_dump_variant()`, `ot_dump_object()`, `ot_dump_summary_bytes()`, `ot_dump_summary_metadata_keys()`, `ot_dump_summary_metadata_key()`, and `ot_dump_gpg_key()`.

## Control Flow
The header has no runtime control flow. It includes GIO and `ostree-core.h`, defines the flags enum, and exposes the formatter prototypes implemented in `ot-dump.c`.

## State And Persistence
No state is stored here. The flags influence output behavior in callers but do not imply persistence.

## Dependencies And Integration Points
Consumers include `ot-builtin-show.c`, `ot-builtin-log.c`, `ot-builtin-summary.c`, and remote key listing code. The header exposes `GVariant`, `GBytes`, `OstreeObjectType`, and GLib error conventions to callers.

## Risks And Edge Cases
`OSTREE_DUMP_NONE` is defined as `(1 << 0)` rather than zero, so code must not assume "none" means no bits set. Callers generally initialize flags to `OSTREE_DUMP_NONE` and OR additional bits, and implementations check only RAW/UNSWAPPED. Any future flag checks must account for this unusual value.

## Test Signals
Build and command tests should verify all dump consumers compile and that raw/unswapped flags behave as expected. Unit coverage around `OSTREE_DUMP_NONE` should prevent future bitmask assumptions from changing output unintentionally.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-dump.h -->
