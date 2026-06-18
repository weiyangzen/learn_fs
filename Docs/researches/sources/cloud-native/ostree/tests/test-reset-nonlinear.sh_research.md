# sources/cloud-native/ostree/tests/test-reset-nonlinear.sh

## Purpose
This small shell test verifies `ostree reset` can reset a branch to a non-linear commit from another branch.

## Important APIs, Types, And Functions
It uses `setup_test_repository "archive"`, `$OSTREE commit -b testx`, and `$OSTREE reset test2 testx`.

## Control Flow
The script creates an archive repository fixture, commits a new branch `testx` from the files directory, returns to the tempdir, and resets `test2` to point at `testx`.

## State And Persistence
Branch refs `testx` and `test2` are modified in the temporary repository. Objects from the fixture and new commit persist until cleanup.

## Dependencies And Integration Points
This integrates ref reset behavior with commit graph ancestry rules. It ensures reset does not require the target commit to be a descendant of the original branch.

## Risks
If reset incorrectly enforces linear history, administrative workflows that repoint refs to unrelated commits would fail.

## Test Signals
The single TAP result `ok reset nonlinear` is printed after the reset succeeds.
