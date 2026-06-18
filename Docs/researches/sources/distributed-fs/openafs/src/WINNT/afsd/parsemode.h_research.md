# sources/distributed-fs/openafs/src/WINNT/afsd/parsemode.h

Purpose: declares the symbolic mode parser and the permission-bit masks it uses.

Important APIs/types/functions: exports `parsemode(char *symbolic, afs_uint32 oldmode)` and defines `USR_MODES`, `GRP_MODES`, `EXE_MODES`, and `ALL_MODES`, conditionally including `S_ISVTX` when available.

Control flow: no direct control flow. The macros determine what `parsemode.c` may preserve, clear, or set.

State/persistence: no runtime state.

Dependencies/integration: requires stat permission macros and OpenAFS integer types to be available in includers. Used by chmod-style command implementation.

Risks: macro definitions depend on platform availability of POSIX mode bits in the Windows build. If stat macros differ, parser behavior shifts.

Test signals: compile under all supported Windows toolchains and verify `ALL_MODES` includes/excludes sticky bit as expected.
