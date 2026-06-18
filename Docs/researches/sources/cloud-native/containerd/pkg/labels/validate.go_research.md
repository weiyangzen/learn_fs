# sources/cloud-native/containerd/pkg/labels/validate.go

Purpose: enforces the containerd label size limit for key plus value.

Important APIs/types/functions: constants `maxSize = 4096` and `keyMaxLen = 64`; `Validate(k, v)` computes byte length of key and value, returns nil when at or below the limit, and returns an `errdefs.ErrInvalidArgument`-wrapping error when above the limit. Long keys are truncated to 64 bytes in the error message.

Control flow: one size check. If invalid, optionally shorten the key used in the diagnostic, then format a descriptive error with wrapped invalid-argument sentinel.

State/persistence: no state. It protects persisted label metadata by rejecting oversized inputs before storage.

Dependencies/integration: depends on `github.com/containerd/errdefs` so callers can classify validation failure through `errdefs.IsInvalidArgument` or `errors.Is`.

Risks: uses `len` byte counts, not rune counts, which is correct for storage but can surprise callers with multibyte labels. It validates only total size, not key syntax or reserved prefixes.

Test signals: `validate_test.go` covers valid boundaries, oversized labels, error classification, and long-key diagnostic truncation behavior.
