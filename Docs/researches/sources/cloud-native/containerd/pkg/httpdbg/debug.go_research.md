<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/httpdbg/debug.go -->
# sources/cloud-native/containerd/pkg/httpdbg/debug.go

Purpose: HTTP client debugging helpers for dumping requests/responses and attaching Go HTTP trace logging.

Important APIs and functions: `debugTransport.RoundTrip`, `DumpRequests`, `NewDebugClientTrace`, `traceTransport.RoundTrip`, `DumpTraces`, and `WithClientTrace`.

Control flow and state: `DumpRequests` wraps a client's transport with `debugTransport`, which uses `httputil.DumpRequestOut` and `DumpResponse` to write full request/response bytes to a provided writer or logger writer. `DumpTraces` wraps transport with a `httptrace.ClientTrace` that logs DNS start/done and connection events. `WithClientTrace` returns a context carrying the trace.

Dependencies and integration: uses standard `net/http`, `net/http/httptrace`, `net/http/httputil`, and containerd `log`. It is intended for ctr push/pull and HTTP client diagnostics.

Risks and test signals: request/response dumps can expose credentials or payloads if enabled inappropriately. `NewDebugClientTrace` assumes DNS results contain at least one address when no error is reported. No local tests were in the assigned set.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/httpdbg/debug.go -->
