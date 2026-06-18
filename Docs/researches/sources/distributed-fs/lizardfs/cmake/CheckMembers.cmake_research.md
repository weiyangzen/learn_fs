# sources/distributed-fs/lizardfs/cmake/CheckMembers.cmake

## Purpose
This helper probes whether a C/C++ struct has particular members and records feature macros.

## Important APIs, Types, and Functions
`check_members(STRUCT MEMBERS HEADER)` builds variable names such as `LIZARDFS_HAVE_STRUCT_STAT_ST_BLOCKS`, calls `CHECK_STRUCT_HAS_MEMBER`, and warns plus sets the variable to `0` when absent.

## Control Flow and State
Each member probe feeds CMake configuration variables that become optional macros in `config.h`. Missing members are non-fatal and are expected on some platforms.

## Dependencies and Integration Points
`EnvTests.cmake` uses this for `struct stat`, `struct tm`, and `struct rusage`. The caller includes `CheckStructHasMember`.

## Risks and Edge Cases
The helper assumes CMake result variables compare numerically to `1`; unusual CMake false values could be awkward. It only supports one header argument string, so multi-header checks need caller-side setup.

## Test Signals
Warnings during configure indicate portability differences. Generated macros guide conditional compilation in the C++ source tree.
