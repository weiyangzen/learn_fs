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
