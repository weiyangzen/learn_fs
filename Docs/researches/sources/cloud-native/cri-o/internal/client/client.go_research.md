# sources/cloud-native/cri-o/internal/client/client.go

## Purpose
HTTP client for CRI-O daemon debug/info endpoints over a Unix socket.

## Important APIs, Types, and Functions
CrioClient interface exposes DaemonInfo, ContainerInfo, ConfigInfo, GoRoutinesInfo, HeapInfo. New configures http.Transport DialContext to unix socket with path length check. doGetRequest issues GET and reads response. Methods target server info/config/goroutines/heap/container paths and JSON-decode typed results where needed.

## Control Flow
Caller creates client for socket path, each method builds GET request with context, reads body, checks status, and decodes or returns strings/bytes.

## State and Persistence
No persistent state except reusable http.Client and socket path.

## Dependencies
Depends on net/http over Unix sockets, syscall path size, pkg/types, server endpoint constants.

## Integration Points
Used by crio status/debug tooling and tests needing daemon introspection.

## Risks and Edge Cases
No response size limits; no client timeout except dial timeout; path length limit is platform-specific; errors include raw body/status behavior depending implementation.

## Test Signals
Indirect tests through CLI/debug endpoint usage; socket path validation is a direct signal.
