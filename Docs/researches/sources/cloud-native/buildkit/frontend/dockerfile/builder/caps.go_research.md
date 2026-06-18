# sources/cloud-native/buildkit/frontend/dockerfile/builder/caps.go

Purpose: validates requested Dockerfile frontend capabilities and decides whether unsupported caps should allow syntax forwarding.

Important APIs: `enabledCaps` lists supported capability strings; `validateCaps(req)` returns `(forward bool, err error)`.

Control flow: comma-separated requested capabilities are split, optional `+forward` suffix is recognized, and unsupported caps produce an unsupported frontend cap error wrapped as gRPC `Unimplemented`. If unsupported with `+forward`, the function records that forwarding is allowed and continues; otherwise it returns immediately.

State and persistence: no state beyond the static capability map.

Dependencies and integration: used early by `Build` before syntax forwarding. Depends on BuildKit errdefs, grpc error wrappers, stack enabling, and gRPC codes.

Risks and test signals: risks include capability list drift with Dockerfile image labels/docs and parsing whitespace. Build forwarding integration tests are the primary signal.
