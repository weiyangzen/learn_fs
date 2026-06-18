# sources/distributed-fs/alluxio/core/server/proxy/src/test/java/alluxio/proxy/s3/S3RangeSpecTest.java

Purpose: `S3RangeSpecTest` verifies byte-range parsing behavior used by S3 object GET responses.

Important tests cover invalid ranges (`bytes=100`, reversed range, zero suffix), ranges beyond object size, normal inclusive ranges, prefix ranges (`bytes=100-`), and suffix ranges (`bytes=-200`). Control flow constructs range specs through `S3RangeSpec.Factory.create`, then checks `getLength(objectSize)` and `getOffset(objectSize)`. The expected behavior is inclusive end offsets, clipped ranges near EOF, and zero length/offset for unsatisfiable ranges.

State and persistence are absent; this is pure parser/math behavior. Dependencies are JUnit and the production `S3RangeSpec` class. Integration signal: S3 GET/HEAD handlers rely on this math for partial content and range-not-satisfiable behavior. Risks covered include off-by-one errors and suffix/prefix edge cases. Gaps include multiple ranges, whitespace, non-byte units, extremely large values, and explicit HTTP status/header behavior.
