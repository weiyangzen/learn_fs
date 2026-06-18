# sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/CreateStageBulkRequest.hh

## Purpose
`CreateStageBulkRequest.hh` is a compatibility include for the create-stage action declaration now provided by the consolidated `TapeActions.hh`.

## Important APIs, Types, and Functions
The header includes `mgm/http/rest-api/action/tape/TapeActions.hh` and then contains `using CreateStageBulkRequest = CreateStageBulkRequest;` inside the REST namespace.

## Control Flow
There is no request-time control flow in this header. Its intended role is to let code include the historical per-action path while resolving the class declaration from `TapeActions.hh`.

## State and Persistence Behavior
The header defines no state and performs no persistence. Runtime behavior lives in `CreateStageBulkRequest.cc` and the class declaration in `TapeActions.hh`.

## Dependencies and Integration Points
It depends on `mgm/Namespace.hh` and `TapeActions.hh`. It is included by `CreateStageBulkRequest.cc` and possibly by older registration code that has not moved to the consolidated header.

## Risks
The self-referential alias form is suspicious: because `TapeActions.hh` declares `CreateStageBulkRequest` in the same namespace, `using CreateStageBulkRequest = CreateStageBulkRequest;` can be redundant at best and a compile-surface risk depending on compiler/name-lookup rules. This header should be covered by compile tests before refactoring.

## Test Signals
Tests should compile this header alone, include it after `TapeActions.hh`, include it before code that instantiates `CreateStageBulkRequest`, and verify no duplicate-declaration or alias diagnostics occur on supported compilers.
