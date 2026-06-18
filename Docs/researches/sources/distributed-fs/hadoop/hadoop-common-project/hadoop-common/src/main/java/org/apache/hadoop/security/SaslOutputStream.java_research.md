# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/SaslOutputStream.java


Purpose: `SaslOutputStream` wraps outgoing bytes with SASL when negotiated QOP requires integrity or privacy and otherwise delegates directly to the underlying output stream.

Important APIs and types: It extends `OutputStream`. Constructors accept either initialized `SaslServer` or `SaslClient`, inspect `Sasl.QOP`, and buffer wrapped output with a 64 KiB `BufferedOutputStream`. It overrides single-byte and array writes, flush, and close.

Control flow: In pass-through mode writes go directly to `outStream`. In wrapped mode, writes call `saslServer.wrap()` or `saslClient.wrap()`, then write a 4-byte length prefix followed by the wrapped token. Single-byte writes reuse a one-byte input buffer. `close()` disposes the SASL endpoint after flushing/closing behavior in the implementation.

State and persistence: State is per-stream: underlying output, SASL endpoint, wrap flag, one-byte buffer, and latest token buffer. It has no durable persistence.

Dependencies and integration: It depends on Java SASL and Hadoop classification annotations. It pairs with `SaslInputStream` in stream-based Hadoop protocols.

Risks and test signals: Tests should cover auth pass-through, wrapped framing, flush behavior, dispose on close, client and server variants, and SASL exceptions. Large writes are wrapped as one token, so negotiated max buffer constraints matter at callers.
