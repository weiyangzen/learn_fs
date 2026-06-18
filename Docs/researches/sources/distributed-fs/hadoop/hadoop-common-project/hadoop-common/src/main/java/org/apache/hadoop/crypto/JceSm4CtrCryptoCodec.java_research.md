# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/JceSm4CtrCryptoCodec.java

## Purpose
`JceSm4CtrCryptoCodec` is the JCE-backed implementation of Hadoop's SM4 CTR no-padding crypto codec. It specializes the shared `JceCtrCryptoCodec` base class for the `CipherSuite.SM4_CTR_NOPADDING` suite and creates JCE `Cipher`-based encryptors/decryptors for stream encryption paths that use SM4 instead of AES.

## Important APIs and types
The public class extends `JceCtrCryptoCodec`. Its key overrides are `getLogger()`, `getCipherSuite()`, `calculateIV(byte[], long, byte[])`, `createEncryptor()`, and `createDecryptor()`. `createEncryptor()` constructs `JceCtrCipher` with `Cipher.ENCRYPT_MODE`, the configured provider, the SM4 cipher suite, and algorithm name `"SM4"`. `createDecryptor()` mirrors this with `Cipher.DECRYPT_MODE`.

## Control flow
Construction has no local initialization. During configuration, inherited `JceCtrCryptoCodec.setConf()` selects the JCE provider and random source. Consumers call `calculateIV()`, which delegates to the base CTR IV arithmetic using the suite block size. Encryption/decryption creation delegates to the nested base cipher wrapper, which initializes a JCE `Cipher` and processes `ByteBuffer` data.

## State and persistence
This class has only a static logger. Runtime provider, random generator, and cipher state live in `JceCtrCryptoCodec` and `JceCtrCipher`. It persists no keys or configuration.

## Dependencies and integration points
It depends on Java Cryptography Extension (`javax.crypto.Cipher`) and Hadoop's `CipherSuite`, `Encryptor`, and `Decryptor` abstractions. It is chosen by `CryptoCodec` configuration paths where SM4 CTR is enabled and a suitable JCE provider, commonly Bouncy Castle or another SM4-capable provider, is available.

## Risks
The main compatibility risk is provider support: default JDK providers may not implement `"SM4/CTR/NoPadding"` or algorithm `"SM4"`. Misconfigured provider selection will surface as `GeneralSecurityException` from encryptor/decryptor creation. CTR IV correctness depends on the inherited block-size-specific calculation and caller-provided IV length. This class also assumes SM4 key material length and cipher name are consistent with `CipherSuite.SM4_CTR_NOPADDING`.

## Test signals
Useful tests instantiate the codec with an SM4-capable JCE provider, assert the cipher suite and IV calculation against known vectors, encrypt/decrypt direct and heap-backed stream data through Hadoop crypto streams, and verify missing provider behavior fails clearly.
