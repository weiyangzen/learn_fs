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
