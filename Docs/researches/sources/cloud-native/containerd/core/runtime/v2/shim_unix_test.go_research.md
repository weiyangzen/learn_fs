# sources/cloud-native/containerd/core/runtime/v2/shim_unix_test.go

## Purpose
Validates Unix shim log copy error filtering.

## APIs, Flow, State, Dependencies, Risks, And Tests
`TestCheckCopyShimLogError` checks that before context cancellation, `fifo.ErrReadClosed` and nil are returned unchanged. After cancellation, `fifo.ErrReadClosed` and `os.ErrClosed` are suppressed to nil, while nil and unrelated FIFO errors remain unchanged.

The test has no persistence. It depends on context cancellation, `os`, and `github.com/containerd/fifo`.

This guards against noisy logs during expected shutdown while preserving real copy errors. A notable edge is that the test expects nil to remain nil after cancellation, which is both suppression-compatible and normal behavior.
