<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/dialer/dialer.go -->
# sources/cloud-native/containerd/pkg/dialer/dialer.go

Purpose: context-aware dial helper for containerd local endpoints with retry-on-not-found behavior.

Important APIs and functions: `ContextDialer`, unexported `timeoutDialer`, and `dialResult`.

Control flow and state: `ContextDialer` derives timeout from context deadline, then `timeoutDialer` starts a goroutine repeatedly calling platform `dialer` until success/non-ENOENT error or stop. If timeout fires, it closes the stop channel and asynchronously closes any late connection.

Dependencies and integration: platform files provide Unix socket or Windows named-pipe dialing and `isNoent`. Used as a gRPC dialer for containerd endpoints.

Risks and test signals: when timeout is zero, `time.After(0)` can fire immediately, so callers without deadlines rely on platform dial timing. Retry delay is fixed at 10 ms for missing sockets/pipes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/dialer/dialer.go -->
