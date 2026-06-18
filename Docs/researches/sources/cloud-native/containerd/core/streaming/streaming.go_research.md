# sources/cloud-native/containerd/core/streaming/streaming.go

## Purpose
This file declares the core streaming interfaces used by transfer and proxy subsystems.

## Important APIs, Types, and Functions
`Stream` is a bidirectional object stream carrying `typeurl.Any` values with `Send`, `Recv`, and `Close`. `StreamGetter` retrieves streams by ID, `StreamCreator` creates them, and `StreamManager` combines retrieval with `Register`.

## Control Flow
There is no implementation. The interfaces define how higher-level packages can exchange typed messages and byte-stream protocol frames without depending on a concrete transport.

## State and Persistence
No state is stored here. Implementations decide stream lifetime and buffering.

## Dependencies and Integration Points
The package depends only on `context` and `typeurl`. It is implemented by local managers and proxy clients and consumed by transfer archive, registry, and progress streaming code.

## Risks
The interface has no backpressure or cancellation semantics beyond implementation behavior and `Close`; callers must layer flow control where needed.

## Test Signals
Concrete behavior is covered in transfer streaming tests and proxy integration paths rather than this definition file.
