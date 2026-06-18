## sources/cloud-native/containers-storage/pkg/ioutils/buffer_test.go

Purpose: unit tests for `fixedBuffer`.

Important APIs/types/functions: `TestFixedBufferCap`, `TestFixedBufferLen`, `TestFixedBufferString`, `TestFixedBufferWrite`, and `TestFixedBufferRead`.

Control flow: constructs buffers with fixed capacity, writes/reads known byte sequences, checks capacity/length/string behavior, and validates `errBufferFull` when capacity is exhausted.

State and persistence: in-memory only.

Dependencies and integration points: protects assumptions used by `BytesPipe` buffer pooling and flow control.

Risks: tests do not cover `io.ErrShortWrite` branch or direct reset reuse from pools.

Test signals: solid coverage for normal internal buffer behavior; local execution blocked by missing Go toolchain.
