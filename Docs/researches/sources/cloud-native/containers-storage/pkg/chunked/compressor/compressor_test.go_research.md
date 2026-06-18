<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/compressor/compressor_test.go -->
# sources/cloud-native/containers-storage/pkg/chunked/compressor/compressor_test.go

Purpose: tests hole detection state machine and no-compression writer shim.

Important APIs/types/functions: `TestHole`, `TestTwoHoles`, `TestNoCompressionWrite`, `TestNoCompressionClose`, `TestNoCompressionFlush`, `TestNoCompressionReset`, `errorWriter`, and `TestNoCompressionWriteError`.

Control flow: hole tests feed zero and mixed zero/nonzero byte streams into `holesFinder` with different thresholds and assert whether holes are coalesced or raw zeros are returned. No-compression tests verify writes append to destination, close/flush are nil, reset switches destinations, nil reset is allowed, and write errors propagate.

State/persistence: in-memory buffers only.

Dependencies/integration: directly exercises internal compressor helpers used by `writeZstdChunkedStream`.

Risks/test signal: protects sparse-zero chunk recognition and internal conversion writer behavior. It does not fully stream-test zstd:chunked manifest output.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/compressor/compressor_test.go -->
