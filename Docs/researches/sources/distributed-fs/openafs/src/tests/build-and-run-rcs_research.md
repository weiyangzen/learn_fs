<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/build-and-run-rcs -->
# sources/distributed-fs/openafs/src/tests/build-and-run-rcs

## Purpose
Builds GNU RCS from a tarball and runs a simple check-in/check-out workflow to stress build, hardlink/archive, and file update behavior.

## Important APIs, Types, And Functions
Shell script using `gzip`, `tar`, `mkdir`, `configure`, `make`, `ci`, `co`, and `wc`.

## Control Flow
Extracts `rcs-5.7.tar.gz` from `$AFSROOT`, configures/builds in a separate object directory, creates `testfile`, performs three `ci -u` and `co -l` cycles with appended rows, and verifies the file has three lines.

## State And Persistence
Creates source/object directories, build outputs, RCS archive files, and testfile artifacts.

## Dependencies And Integration Points
Uses fd 4 for build logs, `$MAKEFLAGS`, `$AFSROOT`, and POSIX build tools. Stresses AFS behavior with real-world build tools.

## Risks And Test Signals
External archive and legacy RCS build dependencies are brittle. Success is final `wc -l` matching `3 testfile`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/build-and-run-rcs -->
