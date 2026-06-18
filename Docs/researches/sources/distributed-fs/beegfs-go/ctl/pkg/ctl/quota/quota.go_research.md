# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/quota/quota.go

## Purpose
Provides thin management RPC wrappers for quota default limits, explicit quota limits, and streaming quota limit/usage retrieval.

## Important APIs, Types, And Functions
Exports `SetDefault`, `SetLimits`, `GetLimits`, and `GetUsage`.

## Control Flow
Each function obtains a management client. Set functions call unary RPCs and return only the error. Get functions call streaming RPCs and return the generated stream client.

## State And Persistence
No local state. Persistent quota state and usage data live in management/storage services.

## Dependencies And Integration Points
Depends on `config.ManagementClient` and protobuf management quota APIs. Consumers are expected to read from returned streams.

## Risks And Edge Cases
No local validation or stream draining. Callers must handle stream lifecycle, partial results, and service-level validation.

## Test Signals
No direct tests.
