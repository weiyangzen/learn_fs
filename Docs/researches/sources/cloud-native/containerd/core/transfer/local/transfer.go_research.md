# sources/cloud-native/containerd/core/transfer/local/transfer.go

## Purpose
This file defines the concrete local transfer service and dispatch matrix for source/destination combinations.

## Important APIs, Types, and Functions
`localTransferService` holds content store, image store, upload/download/unpack limiters, and `TransferConfig`. `NewTransferService` constructs it. `Transfer` dispatches pull, push, export, tag, echo, and import. `withLease` creates a default 24-hour lease if none is already on the context. `TransferConfig` carries leases, concurrency limits, duplication suppression, base handlers, unpack platforms, verifiers, and registry config path.

## Control Flow
`Transfer` applies transfer options, type-switches on source and destination interfaces, and calls the operation-specific method. Unsupported matrices return `ErrNotImplemented` with stringified endpoint names.

## State and Persistence
Service state is references to stores and config. `withLease` persists temporary leases through the configured lease manager and deletes them on operation completion.

## Dependencies and Integration Points
This is the hub for `core/transfer` contracts, content/images/leases, `unpack`, image verifier, and semaphore limiters. It is likely instantiated by transfer plugins.

## Risks
Dispatch relies on interface implementation, so an endpoint implementing multiple interfaces can change route selection. Lease deletion errors are returned by deferred cleanup only in operation methods that check them explicitly; this file provides the cleanup function.

## Test Signals
Covered indirectly by transfer operation tests and integration pull/import/export workflows.
