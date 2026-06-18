<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/test/ScopeGuardTest.cpp -->
# sources/compression/zstd/contrib/pzstd/utils/test/ScopeGuardTest.cpp

## Purpose
This test checks the basic RAII behavior of `ScopeGuard`.

## Important APIs, Types, And Functions
It uses `makeScopeGuard`, `dismiss`, and destructor execution.

## Control Flow
One test creates a guard and dismisses it, ensuring the failure callback is not run. Another creates a guard that sets a flag and verifies the flag after scope exit.

## State And Persistence
Only local booleans are mutated. No persistence exists.

## Dependencies And Integration Points
It depends on GoogleTest and `utils/ScopeGuard.h`. It protects cleanup patterns used throughout pzstd.

## Risks
It does not cover move semantics or exception behavior.

## Test Signals
Passing tests show normal cleanup and dismissal work.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/test/ScopeGuardTest.cpp -->
