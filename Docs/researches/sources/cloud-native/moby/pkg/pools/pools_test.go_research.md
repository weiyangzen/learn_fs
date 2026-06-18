# sources/cloud-native/moby/pkg/pools/pools_test.go

Purpose: unit coverage for pooled bufio readers/writers and the internal byte buffer pool.

APIs and flow: tests obtain objects from `BufioReader32KPool`/`BufioWriter32KPool`, read/write small buffers, return objects, and assert reset side effects. Custom `simpleReaderCloser` and `simpleWriterCloser` verify wrapper close propagation.

State and persistence: tests exercise in-memory pool state only; no persistent files beyond transient buffers.

Dependencies and integration: uses `gotest.tools/v3/assert` plus stdlib `bytes`, `bufio`, `io`, and `strings`.

Risks and signals: intentionally expects a panic when flushing a writer after it has been reset to nil, documenting the no-use-after-put contract. It does not assert `Copy` directly.
