<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/crypto/org_apache_hadoop_crypto.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/crypto/org_apache_hadoop_crypto.h

## Purpose
This header provides shared OpenSSL cipher JNI definitions for Hadoop native crypto. It centralizes handle casts, algorithm constants, key/IV sizes, and platform includes.

## Important APIs, Types, and Functions
Important macros are `CONTEXT()`, `JLONG()`, and `LONG_TO_ENGINE()` for converting between Java `long` handles and OpenSSL pointers. Constants define `KEY_LENGTH_128`, `KEY_LENGTH_256`, `IV_LENGTH`, `ENCRYPT_MODE`, `DECRYPT_MODE`, `AES_CTR`, `SM4_CTR`, `NOPADDING`, and `PKCSPADDING`.

## Control Flow
The header has only compile-time platform branches. Unix includes `dlfcn.h` and `config.h`; Windows includes `winutils.h`; all builds include OpenSSL AES, EVP, and ERR headers.

## State and Persistence
No state is stored here. It defines the pointer encoding used by `OpensslCipher.c` to let Java own native context lifetimes.

## Dependencies and Integration Points
It integrates Java cipher constants with OpenSSL's C API and Hadoop's native dynamic-loader support. Any Java constant changes must remain compatible with these C constants.

## Risks and Edge Cases
Pointer-to-`jlong` conversions assume `ptrdiff_t` can safely round-trip pointer values in the target JVM/native ABI. Unsupported padding and algorithms are still enumerated, so implementation files must continue to reject them explicitly.

## Test Signals
Compile tests should cover Unix and Windows include paths. Runtime crypto tests validate that Java constant values map to the intended C cipher and padding branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/crypto/org_apache_hadoop_crypto.h -->
