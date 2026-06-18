# sources/distributed-fs/lizardfs/cmake/CheckIncludes.cmake

## Purpose
This module probes for header availability and creates normalized `LIZARDFS_HAVE_*` variables for found includes.

## Important APIs, Types, and Functions
`check_includes(INCLUDES)` loops over include file names, converts each to a valid CMake identifier for `check_include_files`, stores `<include>_FOUND`, and when present defines an uppercase macro-style variable with slashes, dots, and dashes converted to underscores.

## Control Flow and State
Missing headers are accumulated and reported with a message after the loop. Found headers are exposed in the parent scope so `config.h.in` can produce `#define` lines. The function does not fail configuration on missing headers.

## Dependencies and Integration Points
It includes CMake's `CheckIncludeFiles` and is used by `EnvTests.cmake` for platform and optional headers such as socket, systemd, zlib, and ISA-L related files.

## Risks and Edge Cases
The function creates variables like `arpa/inet.h_FOUND`, which are not ideal CMake identifiers, alongside sanitized internal names. Missing required headers must be enforced elsewhere. Reporting is informational only.

## Test Signals
Signals are configuration messages for missing includes and generated macros such as `LIZARDFS_HAVE_SYS_SOCKET_H`.
