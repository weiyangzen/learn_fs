# sources/distributed-fs/beegfs/common/source/common/pch.h

## Purpose
Provides a precompiled-header include set for common C/C++ standard library headers used across BeeGFS common code.

## Important APIs, Types, And Functions
No project APIs are defined. It includes assertions, errno, C stdlib/string/integer headers, algorithms, chrono, memory, mutex/condition variables, thread, vector, set, map, unordered containers, and utility.

## Control Flow
No runtime control flow.

## State, Persistence, And Dependencies
No state. It reduces compile overhead when PCH is enabled.

## Integration Points
Included by build configuration rather than normal source logic.

## Risks
Adding project headers here can increase rebuild blast radius or hide missing direct includes; currently it stays limited to common standard headers.

## Test Signals
Build with and without PCH should produce the same diagnostics for source files.
