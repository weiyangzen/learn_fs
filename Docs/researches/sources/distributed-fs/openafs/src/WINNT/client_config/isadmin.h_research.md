# sources/distributed-fs/openafs/src/WINNT/client_config/isadmin.h

## Purpose
`isadmin.h` declares platform/admin detection helpers used during application startup.

## Important APIs, Types, and Functions
It exposes `BOOL IsWindowsNT(void)` and `BOOL IsAdmin(void)`.

## Control Flow
Consumers call `IsWindowsNT` to select NT versus Win9x UI/service behavior and `IsAdmin` to gate service-control and configuration permissions.

## State and Persistence Behavior
The header itself has no state. The implementation caches both decisions in static variables.

## Dependencies and Integration Points
`main.cpp` includes this header directly and writes the results into `GLOBALS g`; tabs subsequently consult those flags rather than calling these functions repeatedly.

## Risks and Edge Cases
The header assumes `BOOL` is already defined by included Windows/OpenAFS headers. It does not document the permissive "missing AFS Client Admins group means admin" policy implemented in `isadmin.cpp`.

## Test Signals
Compile coverage is sufficient for the header. Behavioral tests belong to `isadmin.cpp` and should verify UI gating in `main.cpp`/`tab_general.cpp`.
