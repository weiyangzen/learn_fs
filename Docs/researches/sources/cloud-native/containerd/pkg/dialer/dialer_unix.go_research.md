<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/dialer/dialer_unix.go -->
# sources/cloud-native/containerd/pkg/dialer/dialer_unix.go

Purpose: Unix socket address formatting and dialing for the shared dialer.

Important APIs and functions: `DialAddress`, `isNoent`, and platform `dialer`.

Control flow and state: `DialAddress` prepends `unix://`; `dialer` trims that prefix and calls `net.DialTimeout("unix", ...)`; `isNoent` recognizes `syscall.ENOENT`.

Dependencies and integration: used by gRPC clients connecting to Unix-domain containerd sockets.

Risks and test signals: string prefix handling is simple; malformed addresses are passed to `net.DialTimeout`. Retry behavior for missing sockets is implemented in common code.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/dialer/dialer_unix.go -->
