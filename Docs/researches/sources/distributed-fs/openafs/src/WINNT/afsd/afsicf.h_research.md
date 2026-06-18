# sources/distributed-fs/openafs/src/WINNT/afsd/afsicf.h

## Purpose

`afsicf.h` exposes the Windows firewall configuration entry point for OpenAFS components and defines the selector for the server port set.

## Important APIs, Types, and Functions

- `long icf_CheckAndAddAFSPorts(int portset);` is declared with C linkage when included from C++.
- `AFS_PORTSET_SERVER` is defined as `0`, selecting the predefined AFS server ports in `afsicf.cpp`.

## Control Flow

There is no executable control flow. Callers pass `AFS_PORTSET_SERVER` to configure server rules, or a concrete callback port value to configure the client cache manager callback port.

## State and Persistence Behavior

The header itself has no state. Its exported function causes persistent Windows Firewall rule changes in the implementation.

## Dependencies and Integration Points

The `extern "C"` wrapper makes the C++ implementation callable from C code. It integrates service/install code with `afsicf.cpp`.

## Risks

- The parameter name `portset` can obscure the dual meaning: `0` is a selector, nonzero values are actual client callback ports.
- Only `AFS_PORTSET_SERVER` is named; there is no symbolic client selector, so callers must know to pass a port number.

## Test Signals

- C and C++ build tests should include this header and link against `afsicf.cpp`.
- API tests should cover `AFS_PORTSET_SERVER`, default client callback port 7001, and non-default callback ports.
