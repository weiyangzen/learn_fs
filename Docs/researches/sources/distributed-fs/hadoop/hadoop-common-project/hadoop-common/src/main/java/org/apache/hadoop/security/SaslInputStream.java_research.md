# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SaslInputStream.java


Purpose: `SaslInputStream` wraps an `InputStream` with SASL unwrap processing when negotiated QOP requires integrity or privacy, while passing bytes through unchanged for authentication-only QOP.

Important APIs and types: It extends `InputStream` and implements `ReadableByteChannel`. Constructors accept either an initialized `SaslServer` or `SaslClient`. It overrides byte/array reads, skip, available, close, markSupported, isOpen, and channel `read(ByteBuffer)`.

Control flow: Construction inspects negotiated `Sasl.QOP`; any value other than `auth` enables wrapping. Wrapped reads consume a 4-byte big-endian unsigned length, read that many SASL token bytes, unwrap with the client or server, and serve from an internal output buffer. Zero-length unwrapped buffers are skipped in blocking read loops; EOF on the length read returns -1. Unwrapped mode delegates directly to the underlying `DataInputStream`.

State and persistence: State is per-stream: underlying input, SASL endpoint, wrap flag, token and length buffers, current unwrapped buffer, offsets, and open flag. `close()` disposes the SASL endpoint and closes the input.

Dependencies and integration: It depends on Java SASL, Hadoop classification annotations, and is used by Hadoop data/RPC paths that still rely on stream-based SASL framing.

Risks and test signals: Tests should cover auth pass-through, auth-int/auth-conf unwrap framing, EOF during token boundaries, zero-length tokens, ByteBuffer array and direct paths, disposal on SASL exceptions, and oversized length handling. A malformed length can allocate large arrays.
