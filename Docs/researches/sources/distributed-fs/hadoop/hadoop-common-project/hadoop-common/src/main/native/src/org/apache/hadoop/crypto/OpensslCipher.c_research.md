<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/crypto/OpensslCipher.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/crypto/OpensslCipher.c

## Purpose
`OpensslCipher.c` implements the JNI backend for Hadoop's OpenSSL cipher provider. It dynamically loads OpenSSL EVP symbols and exposes AES-CTR and optional SM4-CTR direct-buffer encryption/decryption to Java.

## Important APIs, Types, and Functions
JNI entry points include `initIDs()`, `initContext()`, `initEngine()`, `init()`, `update()`, `doFinal()`, `clean()`, `getLibraryName()`, and `isSupportedSuite()`. Static helpers `loadAesCtr()`, `loadSm4Ctr()`, `getEvpCipher()`, `check_update_max_output_len()`, and `check_doFinal_max_output_len()` hide algorithm selection and output-size checks. Function pointers cache OpenSSL symbols such as `EVP_CIPHER_CTX_new/free/reset/cleanup`, `EVP_CipherInit_ex`, `EVP_CipherUpdate`, `EVP_CipherFinal_ex`, AES CTR constructors, SM4 CTR, `OPENSSL_init_crypto`, and ENGINE functions.

## Control Flow
`initIDs()` opens `HADOOP_OPENSSL_LIBRARY`, resolves ABI-version-specific symbols, loads cipher constructors, and initializes OpenSSL configuration for newer OpenSSL. `initContext()` validates algorithm and padding and allocates an `EVP_CIPHER_CTX`. `init()` validates key and IV lengths, creates or reuses a context, extracts Java byte arrays, selects the EVP cipher by algorithm and key length, calls `EVP_CipherInit_ex`, disables padding for `NoPadding`, and returns the native pointer as `jlong`. `update()` and `doFinal()` operate on Java direct buffers after prechecking output capacity. `clean()` frees context and optional ENGINE handles.

## State and Persistence
State is process-local: a loaded library handle, cached function pointers, and native `EVP_CIPHER_CTX`/`ENGINE` pointers held by Java as `long` handles. No ciphertext, key, or IV is persisted by this file beyond the OpenSSL context lifetime.

## Dependencies and Integration Points
It depends on `org_apache_hadoop_crypto.h`, OpenSSL EVP/ENGINE headers, Hadoop dynamic-symbol macros, direct NIO buffers, and Java constants for algorithm and padding. It integrates with Java `OpensslCipher` and the configured native library name.

## Risks and Edge Cases
OpenSSL ABI drift is central: the file branches for OpenSSL 1.0, 1.1, and 3.0 symbol names. The Windows branch appears to request `"ENGINE_by_free"` instead of `"ENGINE_free"`, which would break ENGINE cleanup symbol loading there. Direct-buffer address failures throw internal errors, and Java must keep buffer bounds correct. SM4 support depends on compile-time and runtime OpenSSL support.

## Test Signals
Tests should cover AES-128/256 CTR encrypt/decrypt round trips, SM4 availability gating, invalid key/IV sizes, non-direct buffer rejection, short output buffers, OpenSSL 1.1/3 symbol resolution, ENGINE id success/failure, and `getLibraryName()` returning the resolved library path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/crypto/OpensslCipher.c -->
