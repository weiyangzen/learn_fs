# sources/cloud-native/containerd/internal/cri/instrument/instrumented_service.go

## Purpose

This file wraps the CRI runtime and image gRPC services with containerd-specific request instrumentation. It is the outer service layer that enforces initialization, attaches the containerd namespace to request contexts, logs CRI request/response outcomes, records trace errors for important lifecycle calls, sanitizes selected image errors, and converts internal errors to gRPC status errors.

## Important APIs, Types, and Functions

`criService` is the wrapped dependency and embeds `GRPCServices` plus `IsInitialized`. `GRPCServices` embeds `runtime.RuntimeServiceServer` and `runtime.ImageServiceServer`. `instrumentedService` embeds the unimplemented CRI service servers and delegates to `c criService`. `NewService` returns the wrapper. `checkInitialized` returns gRPC `Unavailable` until the underlying service is ready.

The file implements all CRI runtime/image endpoints visible in this source set: pod sandbox lifecycle, port-forward, container lifecycle, exec/attach, resource updates, image operations, stats, status, version, runtime config, log reopen, checkpoint, event streaming, pod sandbox metrics, and pod resource updates.

## Control Flow

Every unary method starts with `checkInitialized`, logs request metadata, defers outcome logging, calls the underlying service, and returns `errgrpc.ToGRPC(err)`. Most calls wrap the context with `ctrdutil.WithNamespace(ctx)` before delegation; `ListMetricDescriptors`, `ListPodSandboxMetrics`, and `RuntimeConfig` call through with the original context. Lifecycle-heavy calls also record the final error on the tracing span. Image calls sanitize errors before gRPC conversion to avoid leaking sensitive registry data.

`GetContainerEvents` is the server-streaming exception: it checks initialization, uses the stream context for logging, delegates directly to `in.c.GetContainerEvents`, then converts the returned error.

## State and Persistence Behavior

The wrapper is stateless apart from the service pointer. It does not persist CRI state, mutate stores, or own lifecycle resources. Its durable effect is indirect: every delegated call runs in the intended containerd namespace, so store and content operations hit the CRI namespace consistently.

## Dependencies and Integration Points

It depends on CRI protobuf servers, `errdefs`/`errgrpc`, containerd logging, CRI util namespace helpers, and tracing. It is registered wherever the CRI plugin exposes runtime and image gRPC services. It integrates with all server implementation files by delegating to the same CRI service interface.

## Risks and Edge Cases

Adding a new CRI method without the initialization guard or namespace injection would create inconsistent behavior. Logging full request objects can expose useful operational context but must avoid secrets; image errors are explicitly sanitized, while other method logs depend on request content. The few methods that do not namespace-wrap their context should remain intentional because changing that may alter metadata or metrics behavior.

## Test Signals

Useful tests assert initialization failure returns gRPC unavailable, delegated calls receive a namespaced context, errors are gRPC converted, image errors are sanitized, and tracing/logging hooks run on success and failure. Integration tests should verify every CRI endpoint remains reachable through this wrapper.
