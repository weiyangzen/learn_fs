
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/BZip2Constants.java

## Purpose
`BZip2Constants` holds shared constants for the pure-Java bzip2 compressor and decompressor.

## Important APIs and Types
It is an interface with package/public historical constants for block size, alphabet size, Huffman limits, run markers, group sizes, selector counts, overshoot bytes, sentinel return values `END_OF_BLOCK` and `END_OF_STREAM`, and the `rNums` randomization table.

## Control Flow
There is no executable control flow. Implementations reference constants during sorting, Huffman coding, randomization, and BYBLOCK sentinel handling.

## State and Persistence
All fields are static final interface constants. The `rNums` array is mutable at runtime because Java array contents are not immutable, and the source comments call this out as a historical weakness.

## Dependencies and Integration
Implemented by `CBZip2InputStream` and `CBZip2OutputStream`. `BZip2Codec` checks `END_OF_BLOCK` sentinel values from `CBZip2InputStream`.

## Risks
Public mutable `rNums` can be modified by malicious or buggy code in the same JVM, corrupting randomized block handling. Changing sentinel values or format constants would break pure-Java bzip2 compatibility.

## Test Signals
BZip2 stream tests indirectly exercise constants through block generation, block marker scanning, and randomized/non-randomized decompression paths.
