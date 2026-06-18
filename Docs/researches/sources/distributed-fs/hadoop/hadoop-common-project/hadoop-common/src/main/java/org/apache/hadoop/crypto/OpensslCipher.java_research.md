# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/OpensslCipher.java

## Purpose
`OpensslCipher` is Hadoop's private JNI wrapper around OpenSSL cipher contexts. It currently supports AES CTR and SM4 CTR with no padding and presents a small cipher-like API to the OpenSSL crypto codecs.

## Important APIs and types
The class exposes `ENCRYPT_MODE`, `DECRYPT_MODE`, `getLoadingFailureReason()`, `getInstance(String)`, `getInstance(String, String)`, `isSupported(CipherSuite)`, `init(int, byte[], byte[])`, `update(ByteBuffer, ByteBuffer)`, `doFinal(ByteBuffer)`, `clean()`, and native `getLibraryName()`. Internal enums `AlgMode` and `Padding` map transformation components to native ordinal identifiers. The nested `Transform` holds parsed algorithm, mode, and padding strings.

## Control flow
The static initializer checks `NativeCodeLoader.buildSupportsOpenssl()` and calls native `initIDs()`. Any failure is retained in `loadingFailureReason`, allowing codec constructors to fail early. `getInstance()` tokenizes transformations like `AES/CTR/NoPadding`, validates algorithm/mode/padding, initializes a native context, optionally initializes an OpenSSL engine, and returns a wrapper. `init()` passes mode, key, IV, algorithm, padding, and engine to native code. `update()` validates direct buffers and initialized context, calls native update with positions/remaining sizes, then advances input to limit and output by returned length. `doFinal()` finalizes/reset native state. `clean()` frees native context and engine handles.

## State and persistence
Instance state is the native `context`, selected `alg` and `padding`, and optional native `engine`. It is memory/resource state only; nothing is persisted. `finalize()` calls `clean()`, but callers should prefer explicit cleanup by owning cipher wrappers where possible.

## Dependencies and integration points
It depends on Hadoop native code, OpenSSL, `NativeCodeLoader`, `PerformanceAdvisory`, and Hadoop `Preconditions`. It is used by `OpensslCtrCryptoCodec.OpensslCtrCipher` and by SM4 support checks in `OpensslSm4CtrCryptoCodec`.

## Risks
Direct buffers are mandatory; heap buffers cause argument failures. Native resource lifecycle relies on `clean()` and finalization, so long-lived leaks are possible if wrappers are abandoned. Transformation parsing is strict and only accepts exactly three slash-separated components. Engine initialization can fail or select unavailable OpenSSL engines. Any native exception behavior must preserve Java buffer position invariants.

## Test signals
Test vectors should validate AES CTR and SM4 CTR transformations, invalid transformation parsing, unsupported suites, non-direct buffer rejection, finalization/cleanup idempotence, engine-id paths, and constructor behavior when native libraries are absent.
