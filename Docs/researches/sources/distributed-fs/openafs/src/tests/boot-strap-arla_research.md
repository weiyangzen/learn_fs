<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/boot-strap-arla -->
# sources/distributed-fs/openafs/src/tests/boot-strap-arla

## Purpose
Build stress test that unpacks and compiles an Arla release tree, including the `milko` subcomponent, inside the filesystem under test.

## Important APIs, Types, And Functions
Shell script using `FAST`, `AFSROOT`, `mkdir`, `gzip`, `tar`, `configure`, and `make`.

## Control Flow
Skips when `FAST` is set. Creates `src` and `obj`, extracts `arla-0.34.tar.gz` from `$AFSROOT`, configures from the object directory, runs `make`, enters `milko`, and builds again.

## State And Persistence
Creates source/object trees and build outputs in the current directory.

## Dependencies And Integration Points
Depends on an AFS mirror path under `$AFSROOT`, build tools, and enough workspace. It stresses metadata, directory traversal, hardlinks/symlinks as used by the build, and large file I/O.

## Risks And Test Signals
External archive availability and old build dependencies are brittle. Success is complete configure/build exit `0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/boot-strap-arla -->
