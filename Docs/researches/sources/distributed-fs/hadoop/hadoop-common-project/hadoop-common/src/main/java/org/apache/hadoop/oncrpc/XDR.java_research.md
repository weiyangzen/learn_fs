# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/XDR.java

Purpose: utility buffer for encoding and decoding External Data Representation messages per RFC 4506, plus ONC RPC TCP record-mark helpers.

Important APIs/types/functions: constructors, `State`, `asReadOnlyWrap`, `buffer`, `size`, primitive read/write methods, fixed/variable opaque read/write, string read/write, `verifyLength`, `recordMark`, `writeMessageTcp`, `writeMessageUdp`, `fragmentSize`, `isLastFragment`, and test-only `getBytes`.

Control flow: read methods assert `READING`; write methods ensure capacity and append big-endian values. Opaque reads/writes align to four-byte boundaries. `ensureFreeSpace` doubles buffer capacity until enough space remains. TCP message writing flips a duplicate of the write buffer and prepends a record mark; UDP writing copies a read-state buffer.

State and persistence: owns a mutable `ByteBuffer` and immutable read/write state; no persistence.

Dependencies and integration: foundational for all RPC, security, and portmap serialization. Uses Netty `ByteBuf` wrappers for transport.

Risks: state misuse throws precondition failures. `writeMessageUdp` requires reading state, while most writers produce writing state, so callers must wrap appropriately. `ensureFreeSpace` capacity math is unusual and should remain covered by growth tests. `readFixedOpaque` allocates exact-size arrays from wire lengths.

Test signals: `TestXDR` covers alignment, primitive/string/opaque round trips, record marks, fragment parsing, and capacity expansion.
