<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/hijack.go -->
# sources/cloud-native/moby/client/hijack.go

Purpose: implements HTTP connection upgrade/hijack support for attach, exec attach, and raw daemon dialing.

Important APIs/types/functions: `postHijacked`, `DialHijack`, `setupHijackConn`, `hijackedConn`, `hijackedConnCloseWriter`, `NewHijackedResponse`, `HijackedResponse`, `CloseWriter`, `HijackedResponse.Close`, `MediaType`, and `CloseWrite`.

Control flow: `postHijacked` JSON-encodes a body, builds a request, and calls `setupHijackConn`. `setupHijackConn` adds `Connection: Upgrade`/`Upgrade`, dials using the client dialer, enables TCP keepalive when possible, writes/reads the HTTP request through a custom round tripper, requires `101 Switching Protocols`, preserves already-buffered bytes, and wraps the connection to preserve `CloseWrite` when supported. `DialHijack` exposes a lower-level request upgrade using caller-provided URL/protocol/meta headers.

State and integration behavior: no persistence, but it creates caller-owned network connections. `HijackedResponse.Close` and `CloseWrite` are lifecycle hooks for callers.

Dependencies: `net`, `bufio`, `net/http`, OpenTelemetry HTTP transport, and client request/header helpers.

Risks and test signals: risks include leaked connections on partial failures, dropping buffered data after HTTP upgrade, losing half-close support, and keepalive behavior on long-lived streams. `hijack_test.go` focuses on TLS close-writer behavior; exec/attach tests indirectly exercise request setup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/hijack.go -->
