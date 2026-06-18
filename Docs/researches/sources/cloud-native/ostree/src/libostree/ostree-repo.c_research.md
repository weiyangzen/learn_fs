# sources/cloud-native/ostree/src/libostree/ostree-repo.c

## Purpose
Implements the central `OstreeRepo` GObject: construction/open/create paths, repository locking, config and remote management, object loading/enumeration, GPG signing and verification, summary/metadata regeneration, temporary staging directories, and small public accessors for collection IDs, repo finders, bootloader settings, and writability. It is the broad coordination layer around OSTree's content-addressed repository layout rather than the low-level object writer, ref writer, pull engine, or static delta implementation.

## Important APIs, Types, And Functions
- `OstreeRepo`, `OstreeRepoClass`, `ostree_repo_new`, `ostree_repo_new_default`, `ostree_repo_new_for_sysroot_path`, `ostree_repo_open`, `ostree_repo_open_at`, `ostree_repo_create`, and `ostree_repo_create_at` form the object and lifecycle API.
- `ostree_repo_lock_push`, `ostree_repo_lock_pop`, `OstreeRepoAutoLock`, `push_repo_lock`, `pop_repo_lock`, `do_repo_lock`, and `do_repo_unlock` implement recursive shared/exclusive repo locking over `.lock`.
- `OstreeRepoAutoTransaction` helpers wrap `ostree_repo_prepare_transaction`, `ostree_repo_commit_transaction`, and `ostree_repo_abort_transaction` so transactions auto-abort if the guard is dropped.
- Remote APIs include `_ostree_repo_get_remote`, `_ostree_repo_get_remote_inherited`, `_ostree_repo_add_remote`, `_ostree_repo_remove_remote`, `ostree_repo_get_remote_*_option`, `ostree_repo_remote_add`, `ostree_repo_remote_delete`, `ostree_repo_remote_change`, `ostree_repo_remote_list`, `ostree_repo_remote_get_url`, GPG import/list-key helpers, and `ostree_repo_remote_fetch_summary`.
- Config paths include `ostree_repo_get_config`, `ostree_repo_copy_config`, `ostree_repo_write_config`, `ostree_repo_write_config_and_reload`, `reload_core_config`, `reload_remote_config`, `reload_sysroot_config`, and `ostree_repo_reload_config`.
- Object APIs include `ostree_repo_load_file`, `_ostree_repo_load_file_bare`, `ostree_repo_load_object_stream`, `ostree_repo_has_object`, `ostree_repo_delete_object`, `ostree_repo_fsck_object`, `ostree_repo_load_variant`, `ostree_repo_load_variant_if_exists`, `ostree_repo_load_commit`, `ostree_repo_list_objects`, and `ostree_repo_list_commit_objects_starting_with`.
- Signing and verification APIs include `ostree_repo_sign_commit`, `ostree_repo_append_gpg_signature`, `ostree_repo_add_gpg_signature_summary`, `ostree_repo_gpg_sign_data`, `ostree_repo_verify_commit`, `ostree_repo_verify_commit_ext`, `ostree_repo_verify_commit_for_remote`, `ostree_repo_gpg_verify_data`, `ostree_repo_verify_summary`, and `_ostree_repo_verify_bindings`.
- Summary and metadata APIs include `ostree_repo_regenerate_summary`, `ostree_repo_regenerate_metadata`, `_ostree_repo_maybe_regenerate_summary`, `summary_add_ref_entry`, and `regenerate_metadata`.
- Utility accessors include `ostree_repo_get_path`, `ostree_repo_get_dfd`, `ostree_repo_hash`, `ostree_repo_equal`, `ostree_repo_get_mode`, `ostree_repo_get_min_free_space_bytes`, `ostree_repo_get_parent`, `ostree_repo_get_collection_id`, `ostree_repo_set_collection_id`, `ostree_repo_get_default_repo_finders`, and `ostree_repo_get_bootloader`.

## Control Flow
Opening a repo starts by deriving a boot-ID-scoped staging directory prefix, opening the repo and `objects` directories, recording device/inode identity, detecting writability, FUSE status, owner uid, temp/cache directories, and whether the repo is the system repo. It then reads `config` into a `GKeyFile`, reloads core settings, remotes, and sysroot settings, and only then marks `self->inited`.

Creation is idempotent around the presence of `objects/`: `repo_create_at_internal` creates the repo root, writes a minimal `[core]` config with version/mode and optional collection ID, creates state directories, probes `bare-user` xattr support, and returns an open fd. Existing repos are opened without changing mode or config.

Locking flows through `ostree_repo_lock_push/pop`. Writable repos use `.lock`; non-writable repos and `core.locking=false` bypass locking. Blocking mode uses direct lock calls, while timeout mode retries nonblocking once per second until `core.lock-timeout-secs`. Internal counters allow nested shared/exclusive acquisitions and keep the real kernel lock at the strongest required state until matching pops downgrade or unlock it.

Remote changes validate names, choose either repo `config` or a sysroot/remotes.d `.conf` file, map `a{sv}` options into keyfile entries, write the chosen keyfile atomically enough for the target API, then update the in-memory `remotes` hash. Reloading remotes clears the hash, adds `[remote "..."]` groups from repo config, and appends regular `.conf` files from the resolved remotes directory. Lookup falls back through `parent_repo` where appropriate.

Object loads first search loose object paths in `objects/`, then an active commit staging directory, then the parent repo. Metadata objects are parsed as typed `GVariant`s, with optional commit partial-state detection through commitpartial marker files and an opt-in dirmeta memory cache. File objects dispatch by repo mode: archive objects are parsed from compressed content streams; bare modes use filesystem stat/open/xattrs, `user.ostreemeta`, synthesized bare-user-only metadata, or split xattr link objects.

Summary regeneration takes a shared repo lock, optionally creates and signs a repository metadata commit when a collection ID is configured, builds sorted refs and collection-ref maps, inserts static-delta digests and metadata keys, reindexes static deltas, writes `summary` and optional signatures into a temp dir, then renames them into place. If no signature is generated, stale `summary.sig` is removed to avoid publishing mismatched metadata.

GPG verification builds an `OstreeGpgVerifier` from the remote keyring, remotes.d keyring, parent repo keyrings, configured `gpgkeypath`, optional global keyrings, and explicit extra keyrings. Commit verification loads the commit and detached metadata, concatenates detached signature packets, then verifies against all remote keyrings or the named remote. Signing writes detached signatures back into commit metadata, summary signatures, or arbitrary signature byte output.

## State And Persistence
Persistent repo state lives under the repo root: `config`, `objects/`, `tmp/`, `state/`, `refs/`, `extensions/`, `summary`, `summary.sig`, remote keyrings, static deltas, commitpartial markers, and optional remotes.d files under sysroot configuration. The object store layout is mode-sensitive, with loose object suffixes such as `.file`, `.filez`, `.dirtree`, `.dirmeta`, `.commit`, and `.payload-link`.

In-memory state includes the open directory fds, parsed config, remote hash table guarded by `remotes_lock`, transaction state guarded by `txn_lock`, recursive repo lock counters guarded by `lock.mutex`, dirmeta cache guarded by `cache_lock`, collection ID, default repo finders, min-free-space policy, fsync policy, bootloader/sysroot options, parent repo pointer, and temporary staging directory metadata.

Durability behavior is config-driven. `_ostree_repo_file_replace_contents` uses datasync unless fsync is disabled. `_ostree_repo_syncfs` syncs the whole repo fd, logging timing for system repos. `_ostree_repo_update_mtime` bumps repo mtime so clients can notice ref updates. Summary replacement stages files in a tmpdir before renaming to keep `summary` and signatures consistent.

## Dependencies And Integration Points
This file depends heavily on GLib/GIO/GObject, libglnx fd-relative filesystem helpers, Linux `fcntl`/`flock`/`syncfs`/`statfs`/`statvfs`, OSTree core object formats, repo private helpers, ref APIs, pull APIs, static-delta APIs, sysroot APIs, GPG verifier/signing helpers, and optional GPGME. Public CLI commands and other libostree modules consume these APIs: pull uses remote config and verification, fsck uses object loading and binding verification, static-delta compilation uses file/object streams, sysroot code creates/opens the system repo, and repo finders use remotes, summaries, and collection IDs.

## Risks And Edge Cases
Locking correctness depends on callers pairing push/pop with the same lock type. Mismatches are treated as programmer errors and may abort. Timeout mode sleeps synchronously, so callers using it on latency-sensitive threads need to account for blocking behavior. Kernel OFD locks fall back to `flock` only on `EINVAL`, so unusual filesystems can still surface lock errors.

Config reload has broad side effects: it can open a parent repo recursively, clear and rebuild remotes, change fsync behavior, alter object metadata semantics through xattr/fsverity/composefs options, and modify default repo finder behavior. `ostree_repo_write_config_and_reload` validates by temporarily installing the new config in memory, but the final write path still has the same limitations as keyfile serialization and repo-local conflict checks.

Remote handling has two storage locations, repo config and remotes.d, and intentionally rejects writing a repo-config remote that is already defined in an external file. File-style remotes starting with `file://` bypass normal remote option lookup and disable GPG verification for compatibility.

Object loading is mode-specific and filesystem-sensitive. Bare-user requires `user.ostreemeta`; bare mode depends on xattr availability unless disabled; split-xattrs requires the companion xattrs object. Staged transaction objects can shadow or supplement committed objects. Parent repo fallback means absence checks may not be local-only unless flags explicitly suppress parents.

Summary generation deliberately defaults `auto-update-summary` to false because multiple writers can commit concurrently. Enabling it can still only make the update atomic within a transaction, not coordinate a whole fleet of concurrent ref updates. Signature generation is careful to remove mismatched signatures, but failures between rename operations are still a critical publication path to test.

GPG code is compiled out when `OSTREE_DISABLE_GPGME` is set. When enabled, it manages temporary GPG homes and kills agents on cleanup, imports key material through temporary pubring files, and deduplicates commit signatures by verifying existing metadata before signing. Errors in keyring lookup, ambiguous key IDs, malformed signatures, or missing detached metadata propagate directly to callers.

## Test Signals
`tests/test-repo.c` exercises create/open identity, fd-relative APIs, collection and min-free-space behavior, and extensive recursive/shared/exclusive lock semantics including invalid pop cases and cross-repo contention. `tests/test-config.sh` covers CLI config handling for `core.lock-timeout-secs`. `tests/test-auto-summary.sh` checks that ref changes do not update summaries by default and do update them when `core.auto-update-summary` is enabled.

`tests/test-basic-c.c` and shell basic tests provide signals for opening repos, loading file objects, commit behavior, and injected `OSTREE_REPO_TEST_ERROR` paths. `tests/test-pull-summary-sigs.sh`, `tests/test-signed-pull-summary.sh`, `tests/test-commit-sign-sh-ext.c`, and remote GPG CLI tests cover summary signature verification, invalid-cache injection, commit signing, and key import/list behavior. `tests/test-repo-finder-config.c` and `tests/test-repo-finder-mount.c` cover summary regeneration, archive repo creation, and remote integration used by repo finders.
