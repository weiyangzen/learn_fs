# sources/cloud-native/containerd/core/sandbox/proxy/controller.go

## Purpose
Implements `sandbox.Controller` by proxying calls to the containerd sandbox controller gRPC API.

## APIs, Flow, State, Dependencies, Risks, And Tests
`NewSandboxController` stores a controller client and sandboxer name. `Create` applies create options, converts sandbox metadata to proto, and sends rootfs, options, netns path, annotations, sandbox metadata, and sandboxer. `Start`, `Platform`, `Stop`, `Shutdown`, `Status`, `Metrics`, and `Update` perform request/response mapping and native error conversion. `Wait` retries `Unavailable` gRPC errors with exponential backoff from 128 ms up to 4096 ms until success or context cancellation.

No local persistence exists. State is remote controller state and the sandboxer name. Dependencies include sandbox service API, mount proto conversion, typeurl, errgrpc/errdefs, metrics API, and image-spec platform.

Integration is the remote client path for sandbox lifecycle management. Risks include timeout seconds truncation, `Wait` returning the last unavailable error on context cancellation, missing sandboxer in `Update`, and backoff delaying cancellation responsiveness. Test signals include fake gRPC controller method mapping, unavailable retry behavior, field update propagation, and error conversion.
