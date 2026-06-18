<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/crypto/random/org_apache_hadoop_crypto_random.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/crypto/random/org_apache_hadoop_crypto_random.h

## Purpose
This header provides shared includes and utility definitions for the OpenSSL secure random JNI implementation.

## Important APIs, Types, and Functions
It defines `UNUSED(x)` for suppressing callback parameter warnings and includes OpenSSL `crypto.h`, `engine.h`, `rand.h`, and `err.h`. Platform branches bring in `dlfcn.h`/`config.h` on Unix and `winutils.h` on Windows.

## Control Flow
There is no runtime flow. Conditional includes select the platform dynamic-loading support used by `OpensslSecureRandom.c`.

## State and Persistence
No state is declared or stored here.

## Dependencies and Integration Points
The header links Hadoop's native platform layer with OpenSSL random and engine APIs. It is included by the secure-random JNI source.

## Risks and Edge Cases
OpenSSL ENGINE headers are deprecated in newer OpenSSL versions, so future compiler configurations may warn or require compatibility macros. Platform include coverage must stay aligned with the C file's callback implementations.

## Test Signals
Build tests with OpenSSL 1.0, 1.1, and 3.x headers are the key signal for this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/crypto/random/org_apache_hadoop_crypto_random.h -->
