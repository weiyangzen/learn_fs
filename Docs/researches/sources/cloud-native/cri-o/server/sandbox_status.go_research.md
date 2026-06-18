# sources/cloud-native/cri-o/server/sandbox_status.go

Purpose: implements CRI `PodSandboxStatus`, including network IP projection, namespace options, evented PLEG fields, and verbose runtime spec info.

Important APIs and functions: `PodSandboxStatus`, `toPodIPs`, and `createSandboxInfo`.

Control flow: resolves sandbox or returns gRPC NotFound. Builds status from sandbox state/labels/annotations/metadata and namespace options. If pod events are enabled, attaches timestamp and container statuses. First sandbox IP becomes `Network.Ip`; remaining IPs become `AdditionalIps`. Verbose mode serializes infra container image/pid/spec or only spec for spoofed infra containers.

State and persistence: read-only over sandbox/container state, except container status collection may call other server APIs that refresh or compute state.

Dependencies and integration: CRI status API, evented PLEG support, OCI container spec/state, goccy JSON, gRPC status codes.

Risks: verbose info depends on infra container availability and serializability. Evented PLEG container-status lookup can make status slower and introduce additional errors.

Test signals: `sandbox_status_test.go` covers success, multiple IPs, empty ID error, and verbose info serialization including runtime spec and image.
