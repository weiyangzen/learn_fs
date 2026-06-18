
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/SplitCompressionInputStream.java

## Purpose
`SplitCompressionInputStream` is the base class for compressed input streams whose actual readable range may be adjusted to codec-specific boundaries.

## Important APIs and Types
It extends `CompressionInputStream` and stores `start` and `end`. Public methods are `getAdjustedStart()` and `getAdjustedEnd()`; protected setters allow codecs to adjust these values.

## Control Flow
The constructor initializes the wrapped input stream and the requested/adjusted range. Subclasses perform all actual decompression and may call setters when aligning to block boundaries.

## State and Persistence
State is only the adjusted start/end offsets in the compressed stream. No persistence is performed.

## Dependencies and Integration
Returned by `SplittableCompressionCodec.createInputStream`; `BZip2Codec`'s split stream is the primary implementation in this subset. Hadoop input formats use adjusted offsets to coordinate split ownership.

## Risks
If a codec does not correctly adjust start/end, record readers can duplicate or drop records at split boundaries. The base class does not enforce end-of-split reads itself.

## Test Signals
`TestBZip2Codec` validates split stream positions for bzip2. Broader MapReduce line reader tests provide integration signals for split handling.
