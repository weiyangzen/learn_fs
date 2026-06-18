<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/dialer/dialer_windows.go -->
# sources/cloud-native/containerd/pkg/dialer/dialer_windows.go

Purpose: Windows named-pipe address formatting and dialing for the shared dialer.

Important APIs and functions: `DialAddress`, `isNoent`, and platform `dialer`.

Control flow and state: addresses are slash-normalized, prefixed with `npipe://` if needed, trimmed before dialing, and passed to `winio.DialPipe` with timeout.

Dependencies and integration: depends on Microsoft `go-winio`; used for containerd named pipe gRPC connections on Windows.

Risks and test signals: path normalization must preserve Windows named pipe semantics. Missing-pipe retry is driven by `os.IsNotExist` through common code.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/dialer/dialer_windows.go -->
