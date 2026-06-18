# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CryptoCodec.java`

## Purpose

`CryptoCodec` is the abstract base for Hadoop cryptographic codecs. It encapsulates cipher-suite identity, encryptor/decryptor creation, CTR IV calculation, and secure random generation.

## Important APIs and Types

Static factories are `getInstance(Configuration)` and `getInstance(Configuration,CipherSuite)`. The private `getCodecClasses` reads configured codec class names. Abstract methods are `getCipherSuite`, `createEncryptor`, `createDecryptor`, `calculateIV`, and `generateSecureRandom`. The class also implements `Configurable` and `Closeable`.

## Control Flow

`getInstance(conf)` reads the configured cipher suite key and converts it to `CipherSuite`. `getInstance(conf,suite)` obtains candidate codec classes from suite-specific configuration keys, instantiates each with `ReflectionUtils.newInstance`, and returns the first instantiated codec whose reported suite name matches the requested suite. Unavailable or mismatched classes are logged at performance-advisory debug level and skipped.

## State and Persistence

The abstract class owns no fields except a static logger. Concrete codecs own provider, random, and cipher state. There is no persistence.

## Dependencies and Integration Points

It depends on Hadoop configuration constants, reflection utilities, `PerformanceAdvisory`, and Guava-compatible `Splitter`. It integrates directly with `CryptoInputStream`, `CryptoOutputStream`, HDFS encryption zones, and codec class configuration keys for AES and SM4.

## Risks

Factory lookup returns null when no usable codec is configured, so callers must fail clearly. Candidate instantiation exceptions are swallowed into debug logs, which can hide provider or classpath failures unless debug logging is enabled. Suite matching compares names rather than enum identity. Codec implementations must make `generateSecureRandom` thread-safe.

## Test Signals

Tests should cover default AES/SM4 class discovery, invalid class names, classes not extending `CryptoCodec`, unavailable provider failures, suite mismatch filtering, null return behavior, and configuration-driven factory selection.
