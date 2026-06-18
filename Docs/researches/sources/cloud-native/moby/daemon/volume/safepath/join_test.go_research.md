# sources/cloud-native/moby/daemon/volume/safepath/join_test.go

## Purpose
Cross-platform tests for safepath subpath containment and lifetime guarantees.

## Important APIs, Types, And Functions
Tests include `TestJoinEscapingSymlink`, `TestJoinGoodSymlink`, `TestJoinWithSymlinkReplace`, and `TestJoinCloseInvalidates`.

## Control Flow
Escaping tests create symlinks to root, absolute files, and relative `../../` targets and expect `ErrEscapesBase`. Good symlink tests create files/directories and symlinks inside the base and verify returned safe paths can read expected data. Replacement tests obtain a safe path, replace the original target with an escaping symlink on Unix, and assert the safe path still points to old content. Close tests ensure `IsValid` flips after `Close`.

## State And Persistence
Uses temporary directories, symlinks, and platform join cleanup; Linux tests may create temporary bind mounts through production code.

## Dependencies And Integration Points
Validates `Join`, `SafePath`, and typed errors used by mount setup for volume/image subpaths.

## Risks
Some Windows behavior differs because handles prevent deletion/replacement. Tests do not explicitly assert `Path` panics after close.

## Test Signals
Strong security signal for symlink escape rejection and TOCTOU resistance after successful join.
