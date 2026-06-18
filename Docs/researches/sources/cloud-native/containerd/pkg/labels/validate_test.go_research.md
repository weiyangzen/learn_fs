# sources/cloud-native/containerd/pkg/labels/validate_test.go

Purpose: boundary tests for label key/value size validation.

Important APIs/types/functions: `TestValidLabels` checks ordinary values and a total size just below `maxSize`. `TestInvalidLabels` checks an oversized key/value pair and verifies invalid-argument classification. `TestLongKey` validates long-key truncation and exact-size boundaries.

Control flow: tests build strings with `strings.Repeat`, call `Validate`, and compare nil, nonnil, or sentinel error classification through `errdefs`.

State/persistence: no external state.

Dependencies/integration: uses `testing`, `strings`, `errdefs`, and testify `assert`.

Risks: tests focus on ASCII strings, so they do not document multibyte byte-count behavior. The equality assertion style for nil errors is less idiomatic but still effective.

Test signals: protects the 4096-byte total limit, the allowed exact-boundary behavior, and preservation of `errdefs.ErrInvalidArgument` wrapping for API callers.
