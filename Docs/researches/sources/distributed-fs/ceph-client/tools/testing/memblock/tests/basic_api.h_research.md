# sources/distributed-fs/ceph-client/tools/testing/memblock/tests/basic_api.h

## Purpose
`basic_api.h` is the public header for the memblock basic API test suite. It provides a guarded declaration of the suite entry point and includes the shared memblock test harness header.

## Important APIs, Types, And Functions
The only declared API is `int memblock_basic_checks(void);`. The file includes `common.h`, so any translation unit including this header also receives the common assertion macros, memblock setup helpers, and shared test constants.

## Control Flow
There is no runtime control flow in this header. Its compile-time role is to connect the test runner or other test translation units to the implementation in `basic_api.c`.

## State And Persistence
The header defines no state. It exposes a function whose implementation mutates the global memblock state and depends on reset helpers.

## Dependencies And Integration Points
The include guard `_MEMBLOCK_BASIC_H` prevents duplicate declarations. The dependency on `common.h` ties this API to the local test harness rather than to a standalone memblock interface.

## Risks
The header is intentionally minimal. Its main risk is unnecessary coupling: including it pulls in all of `common.h`, including Linux and kselftest headers. That is acceptable for the local test tree but would be too broad for a production interface.

## Test Signals
The file itself has no executable checks. A build failure here would indicate declaration/header dependency drift; runtime signals come from `memblock_basic_checks()`.
