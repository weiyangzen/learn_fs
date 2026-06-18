# sources/distributed-fs/seaweedfs/weed/s3api/s3api_copy_size_calculation.go

Purpose: Calculates expected target and actual sizes for S3 copy operations across encryption/compression scenarios and copy strategies.

Important APIs/types/functions: `CopySizeCalculator`, `EncryptionType`, `NewCopySizeCalculator`, `CalculateTargetSize`, `CalculateActualSize`, `getSourceEncryptionType`, `getDestinationEncryptionType`, `isCompressedEntry`, `SizeTransitionInfo`, `GetSizeTransitionInfo`, `OptimizedSizeCalculation`, and `CalculateOptimizedSizes`.

Control flow: construction reads source file size and compression indicators from `filer_pb.Entry`, detects source encryption from entry metadata, and destination encryption from request headers. Size calculation returns source size for all encryption transitions because IV/encryption metadata is stored outside object bytes; compressed entries return `-1` target size to force streaming/unknown sizing. Strategy-specific optimized calculation adjusts preallocation/streaming flags.

State and persistence: read-only helper; no persistence. It consumes object entry attributes/extended metadata and request headers.

Dependencies and integration: depends on filer entry attributes, SSE helper functions (`IsSSECEncrypted`, `IsSSEKMSRequest`, etc.), and `UnifiedCopyStrategy` constants from the copy implementation. Used by copy paths to choose direct/preallocated versus streaming behavior.

Risks: compressed detection is heuristic (`Extended["compression"]` and a small MIME list). Future encryption formats with actual byte overhead would need updates. Nil entry/attributes are not guarded here. Unknown compressed target size can force less efficient streaming.

Test signals: no direct tests in this subset. Copy integration tests should validate behavior across encrypted and compressed objects.
