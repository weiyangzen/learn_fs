<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/errors.go -->
# sources/cloud-native/moby/client/errors.go

Purpose: defines client-specific error wrappers and version-gating helpers used by endpoint methods and request handling.

Important APIs/types/functions: `errConnectionFailed`, `IsErrConnectionFailed`, `connectionFailed`, `objectNotFoundError`, `requiresVersion`, `httpError`, and `httpErrorFromStatusCode`.

Control flow: connection failures wrap a formatted daemon reachability message so callers can classify with `errors.As`. Object-not-found errors implement a `NotFound` marker. `requiresVersion` triggers client version negotiation when needed and compares the negotiated client version against a required API version. `httpError` wraps lower-level errors and cooperates with `errors.Is`/errdefs via status codes.

State and integration behavior: no persistence. Depends on containerd errdefs/errhttp, standard error wrapping, HTTP status codes, and internal version comparison.

Risks and test signals: risks are losing error classification across wrapping, failing feature gates before negotiation, and mismatched HTTP status mapping. Signals are spread across endpoint tests and request/client tests that assert `cerrdefs.Is*` and `IsErrConnectionFailed`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/errors.go -->
