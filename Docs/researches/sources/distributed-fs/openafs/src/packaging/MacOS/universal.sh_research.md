<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/universal.sh -->
# sources/distributed-fs/openafs/src/packaging/MacOS/universal.sh

## Purpose
Creates a universal Darwin 8 destination tree by combining separate PowerPC and x86 OpenAFS build outputs. It copies both architecture trees into `u_darwin_80` and uses `lipo` to replace selected binaries with fat binaries.

## Important APIs, Types, And Functions
This is a small shell script using `tar`, `find`, `rm`, and `lipo`. It expects a top directory containing `ppc_darwin_80/dest` and `x86_darwin_80/dest`; `DIRLIST` identifies server binaries, client binaries, libraries, `afsd`, and the kext executable.

## Control Flow
The script validates that a top directory argument exists, resolves it and the current directory, creates `u_darwin_80`, overlays PPC and x86 trees with tar pipelines, then iterates every file found under each listed destination subpath. For each file it deletes the copied output and runs `lipo <ppc-file> <x86-file> -create -output <universal-file>`.

## State And Persistence
It creates or mutates `u_darwin_80` in the current directory and assumes that output name is free. It does not clean an existing output tree before `mkdir`, so reruns can fail or merge stale state.

## Dependencies And Integration Points
The script belongs to the historical macOS packaging path for Darwin 8/Tiger universal binaries. It depends on architecture-specific OpenAFS dest trees and Apple `lipo`.

## Risks And Test Signals
Risks include unquoted paths, hard-coded Darwin 8 architecture names, no validation that all files exist in both inputs, and broad file iteration that assumes every found file is a Mach-O object acceptable to `lipo`. Test signals include successful creation from clean PPC/x86 dest trees and `lipo -info` showing expected architectures for all binaries in `DIRLIST`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/universal.sh -->
