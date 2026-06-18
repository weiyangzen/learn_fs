# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/OpensslCtrCryptoCodec.java

## Purpose
`OpensslCtrCryptoCodec` is the shared base class for OpenSSL-backed CTR-mode Hadoop codecs. It centralizes IV counter arithmetic, configurable random generation, resource cleanup, and the `Encryptor`/`Decryptor` implementation that delegates to `OpensslCipher`.

## Important APIs and types
The class extends `CryptoCodec` and has configuration/random/engine fields with getters/setters. Important methods are `calculateIV(byte[], long, byte[], int)`, `setConf(Configuration)`, `generateSecureRandom(byte[])`, `close()`, and abstract `getLogger()`. The nested `OpensslCtrCipher` implements both `Encryptor` and `Decryptor`, with constructors accepting mode, `CipherSuite`, and optional engine id.

## Control flow
`setConf()` records configuration, instantiates the configured random class from `HADOOP_SECURITY_SECURE_RANDOM_IMPL_KEY`, defaults to `OpensslSecureRandom`, and falls back to Java `SecureRandom` on failure. `calculateIV()` adds the 64-bit counter to the tail of the initial IV as a big-endian block counter with carry propagation. `OpensslCtrCipher.init()` validates key/IV and initializes the native cipher. `encrypt()` and `decrypt()` both call `process()`, which invokes `OpensslCipher.update()`. If update returns fewer bytes than input, it marks `contextReset` and calls `doFinal()`.

## State and persistence
Codec state is configuration, a random generator, and optional OpenSSL engine id. Cipher state is native OpenSSL context in each nested cipher plus a boolean `contextReset`. There is no persistence; `close()` only closes random generators that implement `Closeable`.

## Dependencies and integration points
It depends on `CryptoCodec`, Hadoop `ReflectionUtils`, `OpensslSecureRandom`, `IOUtils`, `CipherSuite`, and `OpensslCipher`. Concrete subclasses provide AES or SM4 suite selection and logger instances.

## Risks
The IV calculation must exactly match JCE and stream offset logic; off-by-one or endian mistakes corrupt encryption compatibility. `OpensslCipher` requires direct buffers, so integration through `CryptoInputStream`/`CryptoOutputStream` must preserve direct-buffer usage. Random implementation configuration can fail and silently fall back to Java `SecureRandom`, which is correct but may alter performance. `process()` treats short update as unusual; test coverage should confirm context reset behavior.

## Test signals
Tests should compare IV calculation to known counter values, validate AES/SM4 round trips through concrete subclasses, exercise configured random classes and close behavior, assert `isContextReset()` on forced short native updates, and verify no state persists across independent encryptor/decryptor instances.
