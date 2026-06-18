# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSEa.cpp

## Purpose

`AFSEa.cpp` implements the redirector library dispatch handlers for extended attributes: `IRP_MJ_QUERY_EA` and `IRP_MJ_SET_EA`. OpenAFS on this path does not support EAs, so both handlers consistently return `STATUS_EAS_NOT_SUPPORTED` after tracing and completing the IRP.

## Important APIs, types, and functions

- `AFSQueryEA(PDEVICE_OBJECT, PIRP)` is the query-EA dispatch handler. It retrieves the current stack location only for trace context, emits a file-object trace message, completes the request with `STATUS_EAS_NOT_SUPPORTED`, catches exceptions, and returns that status.
- `AFSSetEA(PDEVICE_OBJECT, PIRP)` is the set-EA dispatch handler. It follows the same pattern and also returns `STATUS_EAS_NOT_SUPPORTED`.
- Both functions use `IoGetCurrentIrpStackLocation`, `AFSDbgTrace`, `AFSCompleteRequest`, `AFSExceptionFilter`, and `AFSDumpTraceFilesFnc`.

## Control flow

Each function initializes `ntStatus` to `STATUS_EAS_NOT_SUPPORTED`, fetches `pIrpSp`, enters a guarded block, logs the file object pointer, completes the IRP with the unsupported status, and returns. If an exception occurs, the exception handler logs the exception and dumps traces; the status remains the unsupported-EA status because no alternate status is assigned in the handler.

## State and persistence behavior

These handlers do not allocate memory, mutate FCB/CCB state, call the AFS service, or persist any metadata. They only complete the incoming IRP. The absence of EA support is therefore stateless and uniform for all file objects.

## Dependencies and integration points

The file depends on common dispatch support from `AFSCommon.h`, especially tracing, request completion, and exception filtering. It integrates with the driver's major-function dispatch table as the implementation for query/set EA requests. It deliberately does not integrate with create/open, object information, cache, service, or directory code.

## Risks and edge cases

- The behavior is intentionally simple, but callers expecting Windows EA semantics will always receive unsupported status.
- Completion occurs inside the `__try` block. If completion itself faults, the exception path logs/dumps but does not attempt a second completion.
- Any future EA support would need to add buffer probing/validation, service contracts, metadata persistence, and access checks; none of that scaffolding exists here.

## Test signals

Tests should verify that query-EA and set-EA IRPs complete exactly once with `STATUS_EAS_NOT_SUPPORTED`, that the returned status is independent of file type and open mode, that tracing does not require a non-null file object beyond what `IoGetCurrentIrpStackLocation` supplies, and that unsupported EA behavior does not alter FCB/CCB reference counts or service state.
