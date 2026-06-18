# sources/cloud-native/ostree/tests/test-pull-summary-caching.sh

## Purpose
This test verifies that signed remote summary files and their signatures are cached and reused across repeated pulls. It specifically guards against unnecessary redownloads by comparing cache file inode numbers.

## Important APIs, Types, And Functions
The script uses `skip_without_ostree_feature gpgme`, `setup_fake_remote_repo2`, `ostree commit`, `ostree summary -u`, `ostree remote add --set=gpg-verify-summary=true`, and `ostree pull`. It uses `stat -c %i` to detect replacement of cache files.

## Control Flow
After enabling repo caching by unsetting `OSTREE_SKIP_CACHE`, the script creates a signed remote with extra `other` and `yet-another` branches, updates and signs the summary, initializes an archive client repo, configures summary verification, and pulls `origin other`. It records inodes for `repo/tmp/cache/summaries/origin` and `.sig`, performs the same pull again, and asserts that both inodes are unchanged.

## State And Persistence
The important persistent state is the client summary cache under `repo/tmp/cache/summaries/`. The remote stores signed commits, refs, `summary`, and `summary.sig`. No per-test global state should leak except the temporary GPG home supplied by the harness.

## Dependencies And Integration Points
This integrates GPGME signing, summary regeneration, summary verification, pull caching, and local HTTP service. It depends on filesystem inode semantics, so it is Unix-specific and assumes the cache directory is not transparently recreated by the filesystem.

## Risks
Summary cache update logic must avoid rewriting valid cached files on repeated pulls, otherwise clients do extra I/O and can invalidate cache coherency assumptions. The test also risks false negatives on filesystems with unusual inode behavior, but the OSTree test suite generally runs on local Unix filesystems.

## Test Signals
The single TAP result is `ok pull caches the summary files`. Any cache rewrite, missing summary, missing signature, or GPGME-unavailable environment causes skip or failure.
