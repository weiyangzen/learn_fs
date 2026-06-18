# sources/cloud-native/composefs/tests/test-dump-filtered.sh

## Purpose
This shell test verifies `composefs-info dump` filtering behavior for selected file classes.

## Important APIs, Types, And Functions
It builds `special.dump` into an image using `mkcomposefs --from-file`, runs `composefs-info --filter=chardev --filter=inline --filter=whiteout dump`, counts output lines, and uses `assert_file_has_content`.

## Control Flow
Create tempdir, build image, dump with filters, assert exactly four lines, then match expected root, chardev, inline, and whiteout lines.

## State And Persistence
Only temporary files under a trap-managed tempdir.

## Dependencies And Integration Points
Depends on built tools, `special.dump`, and helpers from `test-lib.sh`.

## Risks
Regex expectations are coupled to dump textual format and fixture metadata.

## Test Signals
Validates filter semantics in tooling and correct preservation/classification of chardev, inline content, whiteout, and xattr metadata.
