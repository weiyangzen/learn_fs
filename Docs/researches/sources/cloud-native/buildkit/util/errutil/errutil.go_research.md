## sources/cloud-native/buildkit/util/errutil/errutil.go

Purpose: improves registry and remote pull error readability by expanding containerd `ErrUnexpectedStatus` responses into Docker error payloads or bounded response-body details.

Important APIs/types/functions: `WithDetails(error) error` is the package entry point. It detects `remoteserrors.ErrUnexpectedStatus`, tries to decode `docker.Errors`, and otherwise wraps the status with `verboseUnexpectedStatusError`. `formattedDockerError` formats one or many Docker errors and includes string `Detail` fields. Both wrappers implement `Unwrap` so callers can still use error inspection.

Control flow: nil errors pass through. Unexpected status bodies first take the structured Docker error path; failed or empty Docker decoding falls back to body detail extraction. `verboseUnexpectedStatusError.Error` prefers JSON `details`, otherwise prints the raw body with a 256-byte cap and truncation count.

State/persistence: stateless; only formats in-memory error body bytes. Dependencies: `encoding/json`, containerd remotes/docker error types, `pkg/errors`-compatible wrapping via standard `errors`.

Integration points: used near image registry resolution/fetch code to make daemon/client errors actionable without losing the underlying containerd status. Risks: body truncation can hide useful tail data; structured Docker errors with non-string details only show base error text; `formattedDockerError.Error` appends a trailing newline for multi-error cases. Test signals: no local test in this subset, so behavior depends on containerd error-shape compatibility.
