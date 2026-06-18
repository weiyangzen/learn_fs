# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/CrcComposer.java

Purpose: `CrcComposer` composes multiple per-chunk CRC values into one or more CRCs representing concatenated data ranges, with optional stripe boundaries.

Important APIs and types: factories `newCrcComposer` and `newStripedCrcComposer`; update overloads for byte arrays, `DataInputStream`, and single CRC integers; `digest()` returns composed CRC bytes.

Control flow: construction selects the CRC polynomial mod function from `DataChecksum.Type`, precomputes a monomial for the hint length, and initializes stripe state. Updates read big-endian CRCs, compose with either the precomputed hint monomial or a freshly computed monomial, advance current stripe position, flush to `digestOut` at exact stripe boundaries, and reject stripe overrun. `digest` flushes any partial stripe and resets output/current state.

State and persistence behavior: mutable current composite CRC, current stripe position, digest output buffer, fixed type/length hints. No persistence.

Dependencies and integration points: used by HDFS checksum combination paths; depends on `DataChecksum`, `CrcUtil`, and CRC implementations' `mod` functions.

Risks: only CRC32/CRC32C types are valid. Input byte lengths must be multiples of 4. Stripe length must align with update byte counts or an exception is thrown. Calling `digest` resets accumulated output.

Test signals: cover single and multiple CRC composition, hint and non-hint lengths, byte-array/DataInputStream inputs, striped exact/partial boundaries, overrun exception, invalid byte length, and digest reset behavior.
