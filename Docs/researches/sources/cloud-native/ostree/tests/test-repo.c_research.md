# sources/cloud-native/ostree/tests/test-repo.c

## Purpose
This C unit test validates selected `OstreeRepo` object APIs: hashing/equality, min-free-space config parsing, inline regular file and symlink writing, autolock cleanup, recursive locking, lock misuse assertions, and inter-repo/thread lock conflict behavior.

## Important APIs, Types, And Functions
Important functions include `ostree_repo_create_at`, `ostree_repo_open_at`, `ostree_repo_hash`, `ostree_repo_equal`, `ostree_repo_copy_config`, `ostree_repo_write_config`, `ostree_repo_reload_config`, `ostree_repo_get_min_free_space_bytes`, `ostree_repo_write_regfile_inline`, `ostree_repo_write_symlink`, `ostree_repo_auto_lock_push`, `ostree_repo_lock_push`, and `ostree_repo_lock_pop`. The `Fixture` owns a `GLnxTmpDir`; `LockThreadData` coordinates the multithread test.

## Control Flow
Setup creates temporary repos. Hash and equality tests compare open repo objects, aliases, different repos, and closed repos. Min-free-space tests write valid and overflow config values and reload the repo. Write API tests write fixed regular-file contents with and without SELinux xattrs, reject an invalid expected checksum, and write a symlink with xattrs while checking exact object checksums. Lock tests cover RAII autolock, recursive lock push/pop on a single repo, subprocess assertion failures for invalid unlocks, conflict behavior between two repo handles, and multithread sequencing where exclusive locks block other handles until dropped.

## State And Persistence
Temporary archive repositories, config files, content objects, xattrs encoded in object metadata, symlink objects, and lock files are created under the tempdir. Subprocess tests intentionally fail to validate assertions.

## Dependencies And Integration Points
This integrates GLib testing, GObject repo identity, libglnx tempdir cleanup, object checksum generation, xattr metadata encoding, and file-lock semantics across repo instances and threads.

## Risks
Hash/equality must not claim equality for closed repos. Config parsing must detect integer overflow. Write APIs must keep checksum stability for xattrs and content. Lock recursion and cross-handle blocking are subtle, especially with shared versus exclusive modes and misuse diagnostics.

## Test Signals
GLib paths include `/repo/hash`, `/hash/closed`, `/equal`, `/get_min_free_space`, `/write_regfile_api`, `/autolock`, and six lock tests. Expected assertion stderr is part of the negative test contract.
