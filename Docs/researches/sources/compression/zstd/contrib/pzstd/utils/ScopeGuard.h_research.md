<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/ScopeGuard.h -->
# sources/compression/zstd/contrib/pzstd/utils/ScopeGuard.h

## Purpose
`ScopeGuard.h` implements a small RAII cleanup helper for pzstd.

## Important APIs, Types, And Functions
`ScopeGuard<Function>` stores a callable, runs it in the destructor unless dismissed, and `makeScopeGuard` infers the template type.

## Control Flow
Callers create guards after acquiring files, queues, or other resources. Normal scope exit or early returns trigger cleanup; `dismiss` disables it after ownership is released manually.

## State And Persistence
State is the callable and an active/dismissed flag. No persistence exists.

## Dependencies And Integration Points
`Pzstd.cpp` uses scope guards for file closes, queue finishing, error printing, and progress clearing. `Options.cpp` uses it for recursive file-list cleanup.

## Risks
Destructor callables should not throw. Captured references must remain valid until guard destruction.

## Test Signals
`ScopeGuardTest.cpp` checks dismissal and execution on scope exit.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/ScopeGuard.h -->
