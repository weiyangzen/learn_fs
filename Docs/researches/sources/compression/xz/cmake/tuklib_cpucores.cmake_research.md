# sources/compression/xz/cmake/tuklib_cpucores.cmake

## Purpose
This module detects how tuklib should determine available CPU cores and applies the corresponding compile definitions.

## Important APIs and Control Flow
`tuklib_cpucores_internal_check()` tries platform methods in order: Windows/Cygwin handled in C, glibc `sched_getaffinity` with `CPU_COUNT`, FreeBSD `cpuset_getaffinity`, BSD `sysctl` excluding QNX, `sysconf`, and HP-UX `pstat_getdynamic`. It caches `TUKLIB_CPUCORES_DEFINITIONS`. `tuklib_cpucores(TARGET_OR_ALL)` runs detection once, caches `TUKLIB_CPUCORES_FOUND`, warns if none found, and adds definitions to a target or globally.

## State, Dependencies, and Integration
The module uses `CheckCSourceCompiles`, `CheckIncludeFile`, `CMakePushCheckState`, and `tuklib_common.cmake`. Results are CMake internal cache variables consumed by `src/common/tuklib_cpucores.c`.

## Risks and Test Signals
Detection ordering is important because some APIs compile but are wrong on specific systems. The top-level CMake build treats failure as a hard error for expected platforms, so CI across Linux, BSDs, macOS, Windows, and Solaris is meaningful coverage.
