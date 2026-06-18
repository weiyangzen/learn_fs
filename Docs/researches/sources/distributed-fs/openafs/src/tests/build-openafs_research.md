<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/build-openafs -->
# sources/distributed-fs/openafs/src/tests/build-openafs

## Purpose
Builds OpenAFS 1.2.2 from a tarball inside the filesystem under test and runs a translated error-table helper as a post-build signal.

## Important APIs, Types, And Functions
Uses `${FS} sq . 0`, optional `FAST`, `/usr/tmp` archive cache, `wget`, `generic-build`, and `translate_et`.

## Control Flow
Sets quota on current directory to unlimited, skips when `FAST` is set, copies or downloads the OpenAFS tarball, invokes generic-build, and runs `openafs-1.2.2/src/finale/translate_et 180480`.

## State And Persistence
Creates tarball copy/download and a full OpenAFS build tree in the current directory.

## Dependencies And Integration Points
Requires an `fs` command path, network or cached tarball, compiler toolchain, and generic-build.

## Risks And Test Signals
Network URL and vintage source are brittle. Uses `>& 4`, which is shell-specific. Success includes build completion and `translate_et` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/build-openafs -->
