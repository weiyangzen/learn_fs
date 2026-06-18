# sources/cloud-native/containerd/internal/cri/config/streaming.go

## Purpose

`streaming.go` converts CRI server streaming settings into `k8s.io/cri-streaming` configuration, including optional TLS setup.

## Important APIs, Types, and Functions

- `streamListenerMode` values are `x509KeyPairTLS`, `selfSignTLS`, and `withoutTLS`.
- `getStreamListenerMode` validates TLS flag/key/cert combinations and chooses a mode.
- `(*ServerConfig).StreamingConfig` resolves bind address/port, parses idle timeout, selects TLS mode, and returns streaming config.
- `newTLSCert` generates a self-signed certificate using hostname and interface IPs.

## Control Flow

`StreamingConfig` fills missing address with Kubernetes bind-address resolution, overlays configured idle timeout on the default streaming config, computes TLS mode, loads configured cert/key or generates a self-signed cert when TLS is enabled without files, and sets `TLSConfig` accordingly.

## State and Persistence Behavior

The function returns in-memory config. Self-signed certificates are generated at runtime and not persisted by this file.

## Dependencies and Integration Points

It depends on Go TLS/network APIs, Kubernetes network/cert utilities, and CRI streaming defaults. It is used by the CRI server streaming endpoint for exec/attach/port-forward.

## Risks and Edge Cases

Misconfigured key/cert combinations are rejected. Self-signed cert generation depends on hostname and interface address enumeration. Missing port/address handling must produce a valid `host:port` string.

## Test Signals

`streaming_test.go` validates listener mode selection for default, configured x509, self-signed, and invalid TLS combinations.
