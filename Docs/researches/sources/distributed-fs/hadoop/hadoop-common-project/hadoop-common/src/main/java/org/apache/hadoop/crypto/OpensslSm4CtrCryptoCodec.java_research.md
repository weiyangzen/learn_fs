# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/OpensslSm4CtrCryptoCodec.java

## Purpose
`OpensslSm4CtrCryptoCodec` is the native OpenSSL-backed SM4 CTR codec. It mirrors the AES OpenSSL codec but adds explicit support probing and optional OpenSSL engine selection for SM4 deployments.

## Important APIs and types
It extends `OpensslCtrCryptoCodec`, returns `CipherSuite.SM4_CTR_NOPADDING`, and overrides `setConf(Configuration)` to read `HADOOP_SECURITY_OPENSSL_ENGINE_ID_KEY`. `createEncryptor()` and `createDecryptor()` create `OpensslCtrCipher` instances with the configured engine id. The constructor checks OpenSSL loading and `OpensslCipher.isSupported()` for SM4 CTR.

## Control flow
Construction fails if native OpenSSL did not load or the native library lacks SM4 CTR support. Configuration delegates random setup to the base class and stores the engine id. IV calculation uses inherited CTR arithmetic with the SM4 block size. Encryptor/decryptor creation passes the suite and engine id to the native cipher wrapper.

## State and persistence
The class has only static logging and inherited in-memory codec state. Engine id is configuration-derived state used by future cipher instances. No keys or metadata are persisted.

## Dependencies and integration points
It depends on OpenSSL native support compiled with SM4, `OpensslCipher`, `CipherSuite`, and Hadoop common configuration keys. It integrates with Hadoop codec selection for SM4 encrypted streams.

## Risks
SM4 support varies by OpenSSL version/build, making runtime detection critical. Misconfigured engine ids can prevent cipher initialization. The class throws runtime exceptions during construction, so configuration validation may surface late when a codec is first instantiated.

## Test signals
Tests should cover unsupported SM4 native builds, valid engine-id propagation, SM4 round trips with direct buffers, IV calculation parity with JCE SM4, and constructor behavior when OpenSSL loading fails.
