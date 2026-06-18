# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CrcUtil.java

Purpose: `CrcUtil` implements low-level CRC arithmetic and formatting helpers for composing CRC32/CRC32C values.

Important APIs and types: constants include multiplicative identity and CRC polynomials. Methods include package-private `multiplyMod`, public `getMonomial`, `composeWithMonomial`, `compose`, `intToBytes`, `writeInt`, `readInt`, `toSingleCrcString`, and `toMultiCrcString`.

Control flow: `getMonomial` computes `x^(lengthBytes*8)` under the provided polynomial mod function using exponentiation by squaring. `compose` derives a monomial for the second data length and XORs it with the second CRC after modular multiplication. Byte helpers read/write big-endian ints and formatting helpers validate CRC byte counts.

State and persistence behavior: stateless utility.

Dependencies and integration points: used by `CrcComposer` and checksum debug paths; relies on mod functions from `PureJavaCrc32`/`PureJavaCrc32C` via callers.

Risks: CRC arithmetic is bit-order sensitive; constants are reversed-polynomial forms. `writeInt`/`readInt` only check upper bounds, not negative offsets. Formatting helpers throw for invalid byte lengths.

Test signals: cover monomial identity and negative length, known CRC composition vectors for CRC32 and CRC32C, big-endian read/write bounds, single/multiple CRC formatting, and multiply modular arithmetic against reference implementations.
