<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/client_test.go -->
# sources/cloud-native/moby/pkg/plugins/client_test.go

Purpose: unit tests for plugin HTTP client behavior. Tests cover failed connection retry/abort, fail-once retry, echo request/response JSON, backoff math, scheme normalization, client timeout construction, streaming responses, file sending, request timeout propagation, and status-error handling. State includes local HTTP test servers, request wrappers, buffers, and timing windows. Dependencies are httptest, JSON, plugin transport, TLS options, and gotest assertions. Risks covered include retry timing and request construction; tests may be timing-sensitive but use shortened special timeouts. Test signal is strong for plugin client protocol behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/client_test.go -->
