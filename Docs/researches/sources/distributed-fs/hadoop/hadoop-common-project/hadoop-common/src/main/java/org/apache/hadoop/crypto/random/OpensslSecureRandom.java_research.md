# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/random/OpensslSecureRandom.java

## Purpose
`OpensslSecureRandom` is a `Random` implementation backed by OpenSSL secure random JNI when available, with Java `SecureRandom` fallback. It supplies random bytes for Hadoop crypto codecs.

## Important APIs and types
The class extends `java.util.Random`. Public APIs are constructor, static `isNativeCodeLoaded()`, `nextBytes(byte[])`, and overridden `setSeed(long)` and protected `next(int)`. Native methods are `initSR()` and `nextRandBytes(byte[])`.

## Control flow
The static initializer checks Hadoop native-code loading and OpenSSL build support, then calls native `initSR()` and sets `nativeEnabled` on success. Construction creates a fallback `SecureRandom` only when native support is unavailable. `nextBytes()` uses native `nextRandBytes()` when enabled and falls back if native generation fails. `next(int)` validates bit count, fills enough random bytes, assembles an integer, and right-shifts to the requested bit width. `setSeed()` is ignored because the generator self-seeds.

## State and persistence
State is static native-enabled status and optional per-instance fallback `SecureRandom`. No random state is persisted by Java code.

## Dependencies and integration points
It depends on `NativeCodeLoader`, `PerformanceAdvisory`, Hadoop preconditions, and native OpenSSL bindings. It is the default random class for `OpensslCtrCryptoCodec`.

## Risks
If native initialization partially fails, fallback must be non-null before `nextBytes()` calls; constructor handles this for new instances. Ignoring `setSeed()` is intentional but differs from deterministic `Random` expectations. Native `nextRandBytes()` failure silently falls back, which is safe but can hide performance degradation.

## Test signals
Tests should cover native unavailable fallback, `isNativeCodeLoaded()`, `nextBytes()` fills arrays, `next(int)` bounds and bit masking, `setSeed()` no-op behavior, and configured use through OpenSSL codecs.
