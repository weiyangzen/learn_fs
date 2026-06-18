<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/recovery/Makefile -->
# sources/compression/zstd/contrib/recovery/Makefile

## Purpose
This Makefile builds the `recover_directory` helper for splitting a multi-frame zstd archive back into per-frame files.

## Important APIs, Types, And Functions
Targets compile `recover_directory.c` against the local zstd library and provide cleaning/build rules. Variables select compiler, flags, and zstd library paths.

## Control Flow
The default build compiles the C source and links with zstd utility/library objects. Clean targets remove generated artifacts.

## State And Persistence
It creates the recovery executable and intermediate build files.

## Dependencies And Integration Points
It depends on make, a C compiler, and zstd library/util sources. It is the build entry for `recover_directory.c`.

## Risks
Relative paths and static-link expectations must match the zstd tree. It is a contrib tool, so build coverage may be less frequent than core zstd.

## Test Signals
Successful build plus manual recovery on multi-frame archives validates the Makefile path.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/recovery/Makefile -->
