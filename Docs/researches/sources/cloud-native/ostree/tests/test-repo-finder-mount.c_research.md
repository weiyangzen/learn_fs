# sources/cloud-native/ostree/tests/test-repo-finder-mount.c

## Purpose
This C unit test validates `OstreeRepoFinderMount`, which discovers OSTree repositories on mounted volumes, including `.ostree/repos.d`, well-known repo paths, symlink aliases, collection filtering, and keyring mapping.

## Important APIs, Types, And Functions
Key types include `Fixture`, `OstreeRepoFinderMount`, `GVolumeMonitor`, mock `GMount` objects from `test-mock-gio.h`, `OstreeCollectionRef`, and `OstreeRepoFinderResult`. Helpers include `assert_create_repos_dir`, `assert_create_remote_va`, `assert_create_repo_dir`, `assert_create_repo_symlink`, and `assert_create_remote_config`. Tested APIs include `ostree_repo_finder_mount_new()` and `ostree_repo_finder_resolve_async/finish()`.

## Control Flow
The init test constructs the finder with default and mock monitors. The no-mount test resolves refs with an empty monitor and expects no results. The mixed-mount test creates non-removable, empty, and repository-bearing mock mounts, adds repos and symlinks under `.ostree/repos.d`, configures parent remotes for selected collection IDs, resolves six refs, and checks four canonicalized results with correct URI, keyring, checksum maps, and ignored unsafe/dangling symlinks. The well-known test creates repos at `ostree/repo` and `.ostree/repo` and verifies both are discovered and deduplicated.

## State And Persistence
Temporary mount roots, repository directories, summaries, symlinks, parent remote config, and generated commit checksums are persisted under a tempdir. Cleanup removes tempdir and parent repo fixture files.

## Dependencies And Integration Points
This integrates libglnx, GLib async machinery, mock GIO volume/mount classes, OSTree remote internals, collection refs, keyring resolution for collections, summary generation, and path canonicalization.

## Risks
Mount discovery must avoid non-removable media when appropriate, ignore repos not matching configured collections, handle aliases without duplicate results, reject dangling and out-of-mount symlinks, and map collection IDs to the correct remote keyring. GPG-disabled builds skip the collection/keyring heavy tests.

## Test Signals
GLib paths include `/repo-finder-mount/init`, `/no-mounts`, `/mixed-mounts`, and `/well-known` when GPGME is enabled. Result count and checksum/keyring assertions are the core validation.
