# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoOutputStreamClosing.java

## Purpose

`TestCryptoOutputStreamClosing` verifies whether `CryptoOutputStream` closes its wrapped `OutputStream` according to the constructor's close-underlying-stream flag, including the failure path where flushing during close throws.

## Important APIs and types

- `CryptoCodec.getInstance(new Configuration())` initializes a codec once for all tests.
- `CryptoOutputStream(OutputStream, CryptoCodec, byte[] key, byte[] iv, long streamOffset, boolean closeOutputStream)` is the constructor under test.
- Mockito mocks/spies verify wrapped stream `close()` calls and inject `flush()` failure.
- `LambdaTestUtils.intercept` asserts the expected `IOException`.

## Control flow

`testOutputStreamClosing` constructs a crypto stream with `closeOutputStream=true`, closes it, and verifies the wrapped stream is closed. `testOutputStreamNotClosing` repeats with `false` and verifies no wrapped close. `testUnderlyingOutputStreamClosedWhenExceptionClosing` spies the crypto stream so `flush()` throws during close, intercepts the exception, and verifies the wrapped stream is still closed in the cleanup path.

## State and persistence behavior

State is in mocked streams and one static codec. No bytes are written and no files are persisted. The key and IV arrays are zero-filled test arrays.

## Dependencies and integration points

The test integrates `CryptoOutputStream` close semantics with generic Java `OutputStream`, Hadoop `CryptoCodec`, Mockito, and Hadoop's lambda exception helper. Correct behavior matters for filesystem streams because closing or preserving the wrapped stream is caller-controlled.

## Risks and edge cases

- The tests do not verify idempotent double-close behavior or whether exceptions from the wrapped stream close are suppressed or propagated correctly.
- The flush failure is injected by spying on `CryptoOutputStream`, not by a real codec/output failure.
- No encrypted data is written, so buffer-finalization behavior during close is not covered here.

## Test signals

The key signals are positive close propagation, negative close suppression, and close propagation despite an earlier close-time flush exception.
