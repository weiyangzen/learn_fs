# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/DelegationWriteHandler.java

## Purpose
`DelegationWriteHandler` is the first receiver for a gRPC write stream. It inspects the first write command and delegates the rest of the stream to the correct concrete handler: Alluxio block, UFS file, or UFS fallback block.

## Important APIs, Types, and Functions
`createWriterHandler()` switches on `request.getCommand().getType()` and constructs `BlockWriteHandler`, `UfsFileWriteHandler`, or `UfsFallbackBlockWriteHandler`. `onNext()` lazily creates the handler and either passes a raw polled buffer from the marshaller or the protobuf request. `onError`, `onCompleted`, and `onCancel` forward to the concrete handler if one exists.

## Control Flow, State, and Persistence
The delegate is fixed by the first message in the stream. This class does not persist write data; persistence is handled by the selected handler. It keeps user info and the domain-socket flag so the concrete handler can set metrics and access controls.

## Dependencies and Integration Points
It integrates `DataMessageMarshallerProvider`, `WriteRequestMarshaller`, `DefaultBlockWorker`, `UfsManager`, authenticated user info, and all write handler variants.

## Risks and Test Signals
Risks include invalid command type, inconsistent later stream messages, no-op completion/cancel before a first message, and raw-buffer lifecycle errors. Tests should verify handler selection for all command types, zero-copy buffer handoff, invalid command rejection, and cancellation propagation before and after first data.
