<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/ssl/TestDelegatingSSLSocketFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/ssl/TestDelegatingSSLSocketFactory.java

## Purpose
Tests that `DelegatingSSLSocketFactory` can initialize the OpenSSL-backed default factory when the native Hadoop build and platform support it.

## Important APIs, Types, And Functions
The test uses `NativeCodeLoader.isNativeCodeLoaded`, `NativeCodeLoader.buildSupportsOpenssl`, `DelegatingSSLSocketFactory.initializeDefaultFactory`, `getDefaultFactory`, and `SSLChannelMode.OpenSSL`.

## Control Flow
JUnit assumptions skip the test unless native code and OpenSSL support are available. The test initializes the default factory in OpenSSL mode and expects the provider name to include `openssl`. If initialization fails with a `NoSuchAlgorithmException` cause, it is treated as an environment incompatibility and downgraded to an assumption failure.

## State And Persistence
The test mutates the static default factory inside `DelegatingSSLSocketFactory`; it does not write files.

## Dependencies And Integration Points
Depends on Hadoop native library loading, WildFly/OpenSSL provider availability, AssertJ, and JUnit assumptions. It validates the native TLS provider integration point rather than generic JSSE behavior.

## Risks
Because behavior is environment-dependent, this test can be skipped on many systems. Static factory mutation can leak across tests if the production class does not isolate or reset state.

## Test Signals
The primary signal is a default factory provider name containing `openssl`; skip signals are missing native/OpenSSL support or a known incompatible provider algorithm.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/ssl/TestDelegatingSSLSocketFactory.java -->
