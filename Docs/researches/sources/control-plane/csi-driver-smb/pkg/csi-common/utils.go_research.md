# sources/control-plane/csi-driver-smb/pkg/csi-common/utils.go

## Purpose
CSI utility helpers for endpoint parsing, capability object construction, log levels, and gRPC request/response logging.

## Important APIs, Types, and Functions
Functions include `ParseEndpoint`, `NewVolumeCapabilityAccessMode`, `NewControllerServiceCapability`, `NewNodeServiceCapability`, `getLogLevel`, and `logGRPC`.

## Control Flow
Endpoint parsing accepts `unix://` and `tcp://` prefixes. The interceptor logs method, sanitized request, error or sanitized response, lowering verbosity for common probe/stat calls.

## State and Persistence
No persistent state; writes logs through klog.

## Dependencies
Depends on CSI protobufs, grpc interceptor APIs, klog, and `protosanitizer.StripSecrets`.

## Integration Points
Used by `server.go` and capability setup in driver code.

## Risks and Edge Cases
Endpoint proto preserves original case, which may be rejected by `net.Listen` if uppercase. Logging still exposes non-secret request fields.

## Test Signals
`utils_test.go` covers valid/invalid endpoints, secret stripping, capability constructors, and log-level mapping.
