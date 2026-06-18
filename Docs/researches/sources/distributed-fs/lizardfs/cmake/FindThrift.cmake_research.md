# sources/distributed-fs/lizardfs/cmake/FindThrift.cmake

## Purpose
This module locates Apache Thrift headers, library, and optionally compiler, with Boost headers as a prerequisite.

## Important APIs, Types, and Functions
Inputs include `THRIFT_ROOT` and requested `Thrift_FIND_COMPONENTS`. Outputs include `THRIFT_FOUND`, `THRIFT_INCLUDE_DIRS`, `THRIFT_LIBRARIES`, and `THRIFT_COMPILER`. It searches environment and CMake root hints plus legacy `/opt/thrift-0.9.x` paths.

## Control Flow and State
If Boost headers are unavailable, it either fatals for required finds or returns after a status message. It builds a `REQUIRED_ITEMS` list based on requested components: `library`, `compiler`, or default library components. Unknown components fatal. `find_package_handle_standard_args` computes success.

## Dependencies and Integration Points
`Libraries.cmake` calls `find_package(Thrift COMPONENTS library)` and treats Thrift as optional. When found, code can use Thrift include/library variables for components that need RPC support.

## Risks and Edge Cases
The module does not version-check Thrift. It uses older hard-coded search hints. It requires Boost even for compiler-only scenarios because the Boost check happens before component handling.

## Test Signals
Configure status messages report found or missing Thrift. Link/compile of Thrift-enabled code validates variables when optional support is enabled.
