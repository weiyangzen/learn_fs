<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/crypto/random/OpensslSecureRandom.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/crypto/random/OpensslSecureRandom.c

## Purpose
`OpensslSecureRandom.c` implements the JNI backend for Hadoop's OpenSSL-backed secure random source. It dynamically loads OpenSSL RAND and ENGINE symbols, optionally configures legacy OpenSSL locking, and fills Java byte arrays with `RAND_bytes`.

## Important APIs, Types, and Functions
JNI exports are `initSR()` and `nextRandBytes(byte[])`. Internal helpers include `locks_setup()`, `locks_cleanup()`, platform locking callbacks, `pthreads_thread_id()`, `openssl_rand_init()`, `openssl_rand_clean()`, and `openssl_rand_bytes()`. It resolves `CRYPTO_malloc/free`, legacy `CRYPTO_num_locks` and callbacks, `ENGINE_load_rdrand`, `ENGINE_by_id/init/set_default/finish/free/cleanup`, `RAND_bytes`, and `ERR_get_error`.

## Control Flow
`initSR()` opens the configured OpenSSL library, resolves required symbols, and calls `openssl_rand_init()`. On OpenSSL before 1.1.0 it installs application-level thread locks and loads the `rdrand` engine. Initialization then tries to obtain and default the `"rdrand"` engine for random generation, but cleans up the engine if any step fails. `nextRandBytes()` validates the byte array, pins it with `GetByteArrayElements`, calls `RAND_bytes`, releases the array, and returns a boolean success flag.

## State and Persistence
Static function pointers and OpenSSL ENGINE/global RAND state persist for the process. Legacy lock arrays persist after setup; no Java-visible random state is stored in this file.

## Dependencies and Integration Points
It depends on OpenSSL crypto/engine/rand APIs, Hadoop dynamic loading, JNI byte arrays, pthreads or Windows mutexes, and Java `OpensslSecureRandom`. It integrates with CPU RDRAND through OpenSSL ENGINE where available.

## Risks and Edge Cases
OpenSSL 1.1+ internally manages locking, while older versions rely on correct callback setup. `initSR()` ignores the returned `ENGINE *`, so there is no later explicit cleanup path from Java. `nextRandBytes()` returns false on RAND failure but does not expose OpenSSL error details. Windows typedef syntax and legacy API availability are sensitive to compiler/OpenSSL versions.

## Test Signals
Tests should initialize with supported and missing OpenSSL libraries, generate nonzero byte arrays repeatedly across threads, verify null-array exceptions, simulate unavailable RDRAND, and run with OpenSSL 1.0 and newer libraries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/crypto/random/OpensslSecureRandom.c -->
