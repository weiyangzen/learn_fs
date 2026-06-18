<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/fs_lib.h -->
# sources/distributed-fs/openafs/src/tests/fs_lib.h

## Purpose
Runs a focused C filesystem test with entry points ``.

## Important APIs, Types, and Functions
AFS calls/macros: fs_lib, fs_getfid, fs_rmmount

## Control Flow
The file is consumed by the surrounding build/test harness as a static fixture or substituted script template.

## State and Persistence Behavior
Uses POSIX filesystem calls `fs_getfid, fs_rmmount`; state is usually a temporary file/tree in the current harness directory.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; AFS interfaces fs_lib, fs_getfid, fs_rmmount

## Risks and Test Signals
nonzero exit through `err`/`errx` is the primary test signal.

## Source Notes
Read as C header; 17 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/fs_lib.h -->
