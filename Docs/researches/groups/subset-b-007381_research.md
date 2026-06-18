# subset-b-007381 research

This grouped report covers Hadoop common native C/JNI support for exceptions, OpenSSL crypto, bzip2/zlib compression, ISA-L erasure coding, NativeIO, Unix domain sockets, and Unix group mapping. Each section preserves the source path and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/exception.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/exception.c

## Purpose
`exception.c` centralizes small JNI exception-construction helpers used by Hadoop native code. It lets native call sites build Java exceptions without leaving an intermediate pending JNI exception and provides `terror()` as the common errno-to-text helper.

## Important APIs, Types, and Functions
The exported helpers are `newExceptionV()`, `newException()`, `newRuntimeException()`, `newIOException()`, and `terror()`. `newExceptionV()` does the real work: it locates a Java exception class, resolves the `(String)` constructor, formats a `printf`-style message with `vsnprintf`, creates the Java string and exception object, clears any construction-time pending JNI exception, and returns the throwable object for the caller to throw. The convenience wrappers bind specific class names or variadic argument handling.

## Control Flow
Callers usually build an exception object and then invoke `Throw`. Formatting first probes the required buffer length with a one-byte stack buffer, allocates heap storage for the final message, and releases local references on exit. If class lookup, constructor lookup, string creation, or object construction fails, the function captures and clears the pending exception so the caller receives a throwable object instead of a still-pending JNI state.

## State and Persistence
The file keeps no persistent state. All allocation is transient per exception creation, and `terror()` returns either `strerror()` output or legacy `sys_errlist` strings depending on platform/glibc feature checks.

## Dependencies and Integration Points
It depends on JNI, C varargs, standard formatting, and Hadoop's `org_apache_hadoop.h` macros. It is consumed by native IO, Unix socket, erasure-code, and security JNI files for consistent Java exception messages.

## Risks and Edge Cases
The helper assumes exception classes expose a one-argument string constructor. `msg = malloc(need + 1)` is not explicitly checked before the second `vsnprintf`, so severe allocation failure is a native crash risk. `terror()` has compatibility branches for glibc and non-glibc behavior; unsupported libc combinations could return less useful messages.

## Test Signals
Useful tests exercise formatted messages, missing class/constructor paths, very long messages, errno text under glibc and musl, and JNI callers that verify no unexpected pending exception remains after helper return.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/exception.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/exception.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/exception.h

## Purpose
`exception.h` declares Hadoop native exception helpers and the errno string helper. It is the shared contract for C/JNI files that want to create Java exceptions without duplicating JNI lookup and formatting logic.

## Important APIs, Types, and Functions
The header declares `newExceptionV()`, `newException()`, `newRuntimeException()`, `newIOException()`, and `terror()`. It also defines `TYPE_CHECKED_PRINTF_FORMAT`, which expands to GCC's `format(printf, ...)` attribute on non-Windows builds and to a stub on Windows.

## Control Flow
There is no executable control flow in the header. Compile-time flow is platform-conditional: non-Windows callers get format-string checking for the variadic helpers; Windows callers compile without the GCC attribute.

## State and Persistence
The header owns no state. It only exposes function prototypes and a temporary annotation macro that is undefined at the end of the file.

## Dependencies and Integration Points
It includes JNI types, `stdarg.h`, and Hadoop native platform definitions. The declarations are used by socket, NativeIO, group mapping, erasure-code, and other JNI wrappers that throw Java exceptions.

## Risks and Edge Cases
The comments promise no pending exceptions on return, which places a strong behavioral contract on `exception.c`. Callers must still explicitly throw the returned `jthrowable`; forgetting that step silently drops errors.

## Test Signals
Builds should show printf-format warnings for mismatched format arguments on Unix-like toolchains. Runtime tests should verify helper-created Java exception classes and messages from representative JNI wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/exception.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/bzip2/Bzip2Compressor.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/bzip2/Bzip2Compressor.c

## Purpose
`Bzip2Compressor.c` is the JNI compressor backend for Hadoop's bzip2 codec. It dynamically loads libbz2, caches Java field IDs, owns a native `bz_stream`, and compresses from Java direct input buffers into direct output buffers.

## Important APIs, Types, and Functions
JNI exports are `initIDs()`, `init()`, `deflateBytesDirect()`, `getBytesRead()`, `getBytesWritten()`, `end()`, and `getLibraryName()`. Cached symbol pointers include `BZ2_bzCompressInit`, `BZ2_bzCompress`, and `BZ2_bzCompressEnd`. Cached fields include `stream`, direct buffer references, offsets/lengths, `finish`, `finished`, and `directBufferSize`.

## Control Flow
`initIDs()` maps `"system-native"` to `HADOOP_BZIP2_LIBRARY` or uses a caller-supplied name, opens the library with `dlopen`, resolves symbols, and stores field IDs. `init()` allocates and zeroes `bz_stream`, initializes it with Java block size and work factor, and maps bzip2 errors to Java exceptions. `deflateBytesDirect()` retrieves the stream and Java direct buffer addresses, recalibrates `next_in`, `avail_in`, `next_out`, and `avail_out`, calls `BZ2_bzCompress` with `BZ_RUN` or `BZ_FINISH`, updates Java offsets and remaining length, and marks `finished` on `BZ_STREAM_END`.

## State and Persistence
The native stream persists until Java calls `end()`. Library function pointers and Java field IDs are process-static. Byte counters live in `bz_stream` and are exposed as 64-bit values composed from high/low bzip2 counters.

## Dependencies and Integration Points
It depends on libbz2, Hadoop dynamic-symbol macros, direct NIO buffers, Java `Bzip2Compressor`, and the shared bzip2 header's pointer conversion macros.

## Risks and Edge Cases
Direct-buffer address failure returns zero without throwing, relying on Java-side control flow. Library handles are not closed. Java must guarantee valid offsets and buffer sizes. `end()` frees even after successful `BZ2_bzCompressEnd`; double-closing the same handle would be unsafe.

## Test Signals
Round-trip compression/decompression, finish handling, partial-buffer progress, invalid block/work-factor errors, byte counters beyond 4 GiB, custom library name loading, and native close behavior are important tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/bzip2/Bzip2Compressor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/bzip2/Bzip2Decompressor.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/bzip2/Bzip2Decompressor.c

## Purpose
`Bzip2Decompressor.c` is the JNI decompressor backend for Hadoop's bzip2 codec. It loads libbz2 dynamically, manages `bz_stream` handles, and inflates compressed direct-buffer data into Java direct buffers.

## Important APIs, Types, and Functions
JNI exports include `initIDs()`, `init()`, `inflateBytesDirect()`, `getBytesRead()`, `getBytesWritten()`, `getRemaining()`, and `end()`. It resolves `BZ2_bzDecompressInit`, `BZ2_bzDecompress`, and `BZ2_bzDecompressEnd`, and caches fields for stream handle, compressed input buffer, offsets/lengths, uncompressed output buffer, output buffer size, and finished flag.

## Control Flow
`initIDs()` selects the bzip2 library name, loads it, resolves symbols, and caches field IDs. `init()` allocates and initializes a `bz_stream` with the Java conserve-memory flag. `inflateBytesDirect()` reads Java field state, obtains direct buffer addresses, sets `next_in`, `avail_in`, `next_out`, and `avail_out`, calls `BZ2_bzDecompress`, updates consumed input and remaining length, returns produced output bytes, and marks `finished` on stream end.

## State and Persistence
The native `bz_stream` persists through the Java decompressor lifecycle. Counters and remaining input live in the stream and Java object fields. No data is persisted outside memory.

## Dependencies and Integration Points
It depends on libbz2, JNI direct buffers, Hadoop's dynamic-symbol and exception macros, and Java `Bzip2Decompressor`.

## Risks and Edge Cases
Malformed data maps to `IOException` with a null message. Direct-buffer lookup failure returns zero without explaining the failure. Java offset/length validation is assumed. `getRemaining()` reports `avail_in`, so correctness depends on `inflateBytesDirect()` consistently updating Java-side compressed buffer fields.

## Test Signals
Tests should cover valid decompression, truncated and invalid magic data, conserve-memory mode, EOF marking, remaining-byte reporting, small output buffers, and teardown on both success and failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/bzip2/Bzip2Decompressor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/bzip2/org_apache_hadoop_io_compress_bzip2.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/bzip2/org_apache_hadoop_io_compress_bzip2.h

## Purpose
This header defines common bzip2 JNI plumbing for Hadoop native compression.

## Important APIs, Types, and Functions
It includes libbz2 and JNI headers, defines a default `HADOOP_BZIP2_LIBRARY` of `libbz2.so.1` when not configured, and provides `BZSTREAM()`/`JLONG()` pointer conversion macros.

## Control Flow
There is no runtime flow. The include guard and conditional library-name definition are compile-time only.

## State and Persistence
No state is stored here. The pointer conversion macros define the representation of native `bz_stream *` handles in Java `long` fields.

## Dependencies and Integration Points
It is consumed by the bzip2 compressor and decompressor C files and aligns them with Java stream-handle fields.

## Risks and Edge Cases
The header is Unix-oriented because it includes `dlfcn.h` and uses a Unix-style default library name. Pointer round-tripping assumes the native pointer width fits in `jlong`.

## Test Signals
Build tests should verify configured and default libbz2 names, and runtime codec tests validate stream-handle conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/bzip2/org_apache_hadoop_io_compress_bzip2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/zlib/ZlibCompressor.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/zlib/ZlibCompressor.c

## Purpose
`ZlibCompressor.c` implements Hadoop's native zlib compressor JNI backend. It dynamically loads zlib, creates `z_stream` instances, supports dictionaries, compresses direct buffers, and reports stream counters/library identity.

## Important APIs, Types, and Functions
JNI exports include `initIDs()`, `init()`, `setDictionary()`, `deflateBytesDirect()`, `getBytesRead()`, `getBytesWritten()`, `reset()`, `end()`, and `getLibraryName()`. It resolves `deflateInit2_`, `deflate`, `deflateSetDictionary`, `deflateReset`, and `deflateEnd`. On Windows, `LoadZlibTryHadoopNativeDir()` tries the native Hadoop DLL directory before falling back to system paths.

## Control Flow
`initIDs()` opens zlib and caches symbol pointers plus Java field IDs. `init()` allocates and zeroes `z_stream`, then calls `deflateInit2_` using Java compression level, strategy, and window bits. `setDictionary()` pins a Java byte array and passes the requested slice to zlib. `deflateBytesDirect()` pulls Java object fields, obtains direct buffer addresses, sets zlib input/output pointers, calls `deflate` with `Z_NO_FLUSH` or `Z_FINISH`, updates Java input offset/remaining fields, and marks the Java object finished when `Z_STREAM_END` occurs.

## State and Persistence
`z_stream` is lifecycle state stored in a Java `long`. Static field IDs and function pointers persist process-wide. Stream counters and zlib internal state persist until `reset()` or `end()`.

## Dependencies and Integration Points
It depends on zlib, JNI direct buffers, Hadoop platform config, `winutils` on Windows, and Java `ZlibCompressor`.

## Risks and Edge Cases
Direct-buffer failures return zero rather than throwing. Library handles are not closed. Dictionary calls use critical array sections and must remain short. Java must avoid using a stream after `end()`. Window bits and strategy validation is delegated to zlib and mapped to broad Java exceptions.

## Test Signals
Tests should cover compression round trips, gzip/raw/window-bit variants, dictionaries, finish and reset, counters, short output buffers, missing zlib library, Windows load fallback, and invalid level/strategy behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/zlib/ZlibCompressor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/zlib/ZlibDecompressor.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/zlib/ZlibDecompressor.c

## Purpose
`ZlibDecompressor.c` implements Hadoop's native zlib decompressor JNI backend. It dynamically loads inflate symbols, manages `z_stream` handles, supports dictionaries, and inflates direct-buffer input into direct-buffer output.

## Important APIs, Types, and Functions
JNI exports are `initIDs()`, `init()`, `setDictionary()`, `inflateBytesDirect()`, `getBytesRead()`, `getBytesWritten()`, `getRemaining()`, `reset()`, and `end()`. It resolves `inflateInit2_`, `inflate`, `inflateSetDictionary`, `inflateReset`, and `inflateEnd`, and shares the Windows zlib loader from the compressor file.

## Control Flow
`initIDs()` loads zlib and caches field IDs. `init()` allocates a zeroed stream and initializes inflate with Java window bits. `setDictionary()` pins a byte array and calls `inflateSetDictionary`. `inflateBytesDirect()` obtains Java buffer fields and direct addresses, recalibrates zlib input/output pointers, calls `inflate` with `Z_PARTIAL_FLUSH`, maps `Z_STREAM_END`, `Z_OK`, `Z_NEED_DICT`, `Z_BUF_ERROR`, `Z_DATA_ERROR`, and `Z_MEM_ERROR` to Java state or exceptions, and updates compressed input offsets/remaining bytes.

## State and Persistence
The native `z_stream` is held as a Java long until reset or end. Java fields hold `needDict`, `finished`, input offsets, and remaining input. Static function pointers and field IDs are process-wide.

## Dependencies and Integration Points
It depends on zlib, JNI direct buffers, Hadoop native macros, and Java `ZlibDecompressor`.

## Risks and Edge Cases
The code allocates `z_stream` then calls `memset` before checking whether allocation succeeded, which is a null-dereference risk on allocation failure. Direct-buffer failures return zero silently. Dictionary and data errors depend on zlib messages that may be null. Java must coordinate `needDict` and remaining input state correctly.

## Test Signals
Tests should include valid inflate, raw/gzip modes via window bits, dictionary-needed flows, corrupted data, reset reuse, small output buffers, missing zlib symbols, and allocation-failure hardening.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/zlib/ZlibDecompressor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/zlib/org_apache_hadoop_io_compress_zlib.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/zlib/org_apache_hadoop_io_compress_zlib.h

## Purpose
This header provides shared zlib JNI definitions for Hadoop's native zlib compressor and decompressor.

## Important APIs, Types, and Functions
It includes zlib/zconf and JNI headers, sets `HADOOP_ZLIB_LIBRARY` to `L"zlib1.dll"` on Windows, and defines `ZSTREAM()` and `JLONG()` for native pointer and Java long conversion.

## Control Flow
Compile-time platform branches select Unix dynamic loading or Windows library naming. No runtime logic exists in the header.

## State and Persistence
No state is stored here. The macros define how `z_stream *` state is represented in Java fields.

## Dependencies and Integration Points
It is included by both zlib native implementation files and must stay compatible with Java stream handle fields.

## Risks and Edge Cases
Pointer conversion assumes safe pointer-to-`jlong` round trips. Windows and Unix library naming differ, so build configuration must provide the correct `HADOOP_ZLIB_LIBRARY` when defaults are not sufficient.

## Test Signals
Cross-platform build tests and zlib codec round trips validate this header's contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/zlib/org_apache_hadoop_io_compress_zlib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/dump.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/dump.c

## Purpose
`dump.c` implements diagnostic print helpers for Hadoop's native ISA-L erasure coders. It formats buffers and coding matrices for verbose debugging.

## Important APIs, Types, and Functions
Functions include `dump()`, `dumpMatrix()`, `dumpCodingMatrix()`, `dumpEncoder()`, and `dumpDecoder()`. The encoder and decoder dumpers consume `IsalEncoder` and `IsalDecoder` internals such as `encodeMatrix`, `invertMatrix`, `decodeMatrix`, `erasedIndexes`, and `decodeIndex`.

## Control Flow
The functions are straightforward nested loops over byte buffers or matrix dimensions. `dumpEncoder()` prints coding dimensions and the encode matrix. `dumpDecoder()` prints erasure and decode indexes, then encode, invert, and decode matrices.

## State and Persistence
No state is stored. Output is written to stdout with `printf`, so diagnostics are process-local and transient.

## Dependencies and Integration Points
It depends on erasure-code headers and is called from `erasure_coder.c` when the Java side enables verbose dump through `allowVerboseDump()`.

## Risks and Edge Cases
The dump functions do not validate dimensions or null pointers. Logging to stdout from native code can be noisy in production and interleave under concurrency.

## Test Signals
Verbose encoder/decoder tests should show correctly dimensioned matrix output for representative RS configurations and erasure patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/dump.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/dump.h

## Purpose
`dump.h` declares native erasure-code diagnostic dump helpers.

## Important APIs, Types, and Functions
It declares `dumpEncoder()`, `dumpDecoder()`, `dump()`, `dumpMatrix()`, and `dumpCodingMatrix()`. The prototypes refer to `IsalEncoder` and `IsalDecoder` types from the erasure coder layer.

## Control Flow
There is no runtime control flow. The header only exposes diagnostic functions to implementation files.

## State and Persistence
No state is declared.

## Dependencies and Integration Points
It includes standard C headers and is expected to be used with `erasure_coder.h` in callers. It is part of the verbose debugging path for native RS coding.

## Risks and Edge Cases
The header relies on coder types being visible before or through included translation-unit ordering. If included alone before type declarations, it can fail to compile.

## Test Signals
Compile tests with warning settings and verbose erasure-code runs validate the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/dump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/erasure_code.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/erasure_code.c

## Purpose
`erasure_code.c` is a thin Hadoop wrapper over dynamically loaded ISA-L erasure-code functions. It decouples the rest of the native erasure-code implementation from direct ISA-L linkage.

## Important APIs, Types, and Functions
It implements `h_ec_init_tables()`, `h_ec_encode_data()`, and `h_ec_encode_data_update()`. Each function delegates to the corresponding function pointer in global `isaLoader`.

## Control Flow
There is no algorithmic flow in this file. Callers must ensure `load_erasurecode_lib()` has initialized `isaLoader` before calling these wrappers.

## State and Persistence
The only state touched is external global `isaLoader`, owned by `isal_load.c`. No per-call state is retained.

## Dependencies and Integration Points
It depends on `isal_load.h` and `erasure_code.h`. `erasure_coder.c` uses these wrappers when building parity or recovery outputs.

## Risks and Edge Cases
If `isaLoader` is null or a symbol pointer is missing, calls will crash. There is no local argument validation for dimensions, buffers, or table sizes.

## Test Signals
Tests should load ISA-L successfully before encode/decode calls and verify failure behavior when the library is missing is caught at `loadLibrary`, not at wrapper invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/erasure_code.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/erasure_code.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/erasure_code.h

## Purpose
`erasure_code.h` declares ISA-L-compatible erasure-code table generation and encoding interfaces used by Hadoop's native RS implementation.

## Important APIs, Types, and Functions
The public functions are `h_ec_init_tables()`, `h_ec_encode_data()`, and `h_ec_encode_data_update()`. They operate on GF(2^8) coefficient tables, source pointer arrays, and coding-output pointer arrays.

## Control Flow
The header documents expected call order: generate tables with `h_ec_init_tables()` from coding coefficients, then pass those tables to full or incremental encoding routines.

## State and Persistence
No state is declared. The caller owns coefficient arrays, generated `gftbls`, source buffers, and output buffers.

## Dependencies and Integration Points
It is consumed by `erasure_coder.c` and backed by `erasure_code.c` delegation into dynamically loaded ISA-L functions.

## Risks and Edge Cases
The API assumes callers provide table storage of `32 * k * rows` bytes and valid source/output pointer arrays. Incorrect dimensions or missing ISA-L initialization can cause memory corruption or crashes.

## Test Signals
Known-answer RS parity tests, decode/recovery tests, table-size checks, and address-sanitized invalid-dimension tests are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/erasure_code.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/erasure_coder.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/erasure_coder.c

## Purpose
`erasure_coder.c` implements Hadoop's native Reed-Solomon encode/decode control logic on top of ISA-L GF and erasure-code primitives. It builds Cauchy encode matrices, prepares decode matrices, caches decoder state, and invokes ISA-L vector operations.

## Important APIs, Types, and Functions
Implemented APIs are `initCoder()`, `allowVerbose()`, `initEncoder()`, `initDecoder()`, `encode()`, `decode()`, `clearDecoder()`, and `generateDecodeMatrix()`. Internal helpers include `initEncodeMatrix()`, `compare()`, and `processErasures()`.

## Control Flow
Encoder initialization creates a Cauchy encode matrix and precomputes parity tables from rows below the data identity portion. `encode()` zeros parity outputs and calls `h_ec_encode_data()`. Decoder initialization builds the same encode matrix. Each decode call maps available non-null inputs into `decodeIndex`, skips matrix regeneration when the erasure pattern is unchanged, otherwise clears per-call state, records erased indexes, inverts the selected data matrix, builds rows for missing data or parity, initializes GF tables, and calls `h_ec_encode_data()` to reconstruct outputs.

## State and Persistence
`IsalEncoder` persists the encode matrix and parity `gftbls`. `IsalDecoder` persists encode matrix plus cached decode indexes, erasure flags, erased indexes, temporary/invert/decode matrices, generated tables, and real input pointers. This state lives inside native coder objects owned by Java and freed by JNI wrappers.

## Dependencies and Integration Points
It depends on `gf_util`, `erasure_code`, `dump`, and `erasure_coder.h`. JNI encoder/decoder files allocate wrapper structs embedding `IsalEncoder` or `IsalDecoder`.

## Risks and Edge Cases
`MMAX` and `KMAX` statically bound all arrays; Java must not request configurations beyond those limits. `decode()` ignores the return from `processErasures()`, so matrix-generation failures do not stop recovery. `generateDecodeMatrix()` does not check the invert return value. Null input handling assumes enough non-null inputs are present.

## Test Signals
Tests should cover RS encode known answers, single and multiple erased data/parity recovery, repeated decode with identical erasures to exercise caching, oversized data/parity unit rejection in Java, and failure cases for too many erasures or insufficient inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/erasure_coder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/erasure_coder.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/erasure_coder.h

## Purpose
`erasure_coder.h` defines native state structures and function prototypes for Hadoop's ISA-L-backed erasure coders.

## Important APIs, Types, and Functions
Constants `MMAX` and `KMAX` bound all-unit and data-unit sizes. `IsalCoder` stores verbosity and data/parity/all-unit counts. `IsalEncoder` adds `gftbls` and `encodeMatrix`. `IsalDecoder` adds matrices, erasure flags/indexes, decode indexes, erased count, and real input pointers. Prototypes expose init, encode, decode, clear, and decode-matrix generation routines.

## Control Flow
The header describes the object lifecycle used by JNI wrappers: initialize a coder, call encode/decode repeatedly, optionally enable verbose dumps, and free the wrapper allocation from the JNI destroy method.

## State and Persistence
All arrays are embedded in the coder structs and persist for the native object lifetime. Decoder per-call arrays are reused and cleared when erasure patterns change.

## Dependencies and Integration Points
It is included by the C erasure algorithm files and JNI bridge files. The first field of RS/XOR wrapper structs is intentionally compatible with `IsalCoder *` access through `nativeCoder`.

## Risks and Edge Cases
The static array sizes are hard limits; exceeding them corrupts memory if Java-side validation fails. The cast-based wrapper pattern requires `IsalCoder` or a struct containing it first in memory.

## Test Signals
Configuration-limit tests, ASAN runs, repeated encode/decode reuse, and Java native-coder pointer lifecycle tests validate this header's contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/erasure_coder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/gf_util.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/gf_util.c

## Purpose
`gf_util.c` wraps ISA-L Galois-field utility functions behind Hadoop-prefixed functions.

## Important APIs, Types, and Functions
It implements `h_gf_mul()`, `h_gf_inv()`, `h_gf_gen_rs_matrix()`, `h_gf_gen_cauchy_matrix()`, `h_gf_invert_matrix()`, and `h_gf_vect_mul()`. All delegate directly to function pointers on global `isaLoader`.

## Control Flow
There is no local algorithmic control flow. Calls synchronously invoke the dynamically loaded ISA-L symbol.

## State and Persistence
No state is owned here. It reads the external `isaLoader` global.

## Dependencies and Integration Points
`erasure_coder.c` uses these wrappers to build Cauchy matrices, invert decode matrices, and multiply GF coefficients.

## Risks and Edge Cases
Missing library initialization or unresolved symbols cause null-function-pointer crashes. Caller-provided buffers and matrix dimensions are not validated here.

## Test Signals
Unit tests should verify GF multiply/inverse known values, Cauchy matrix generation, matrix inversion, vector multiply alignment behavior, and missing-library initialization errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/gf_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/gf_util.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/gf_util.h

## Purpose
`gf_util.h` declares Hadoop-prefixed wrappers for ISA-L GF(2^8) utility routines used in erasure coding.

## Important APIs, Types, and Functions
The declared APIs cover scalar multiply/inverse, Reed-Solomon and Cauchy matrix generation, matrix inversion, and vector multiply using a precomputed GF table.

## Control Flow
The header documents call expectations: matrix generators fill coefficient arrays, inversion returns nonzero on singular input, and vector multiply expects precomputed constants and aligned buffers.

## State and Persistence
No state is declared. Callers own all arrays and buffers.

## Dependencies and Integration Points
It provides the matrix and GF contract used by `erasure_coder.c`, backed by `gf_util.c` and `isal_load.c`.

## Risks and Edge Cases
The vector multiply contract requires length and buffers aligned to 32 bytes, which the wrappers do not enforce. Cauchy matrix generation is chosen for invertibility, but invalid dimensions still risk downstream errors.

## Test Signals
Known GF arithmetic, matrix invertibility, 32-byte alignment behavior, and RS recovery tests validate this API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/gf_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/isal_load.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/isal_load.c

## Purpose
`isal_load.c` dynamically loads the Intel ISA-L library and resolves the GF and erasure-code symbols needed by Hadoop native erasure coding.

## Important APIs, Types, and Functions
It defines global `IsaLibLoader *isaLoader`, internal `load_functions()`, public `load_erasurecode_lib()`, and `build_support_erasurecode()`. Resolved symbols include `gf_mul`, `gf_inv`, `gf_gen_rs_matrix`, `gf_gen_cauchy1_matrix`, `gf_invert_matrix`, `gf_vect_mul`, `ec_init_tables`, `ec_encode_data`, and `ec_encode_data_update`.

## Control Flow
`load_erasurecode_lib()` is idempotent if `isaLoader` already exists. Otherwise it allocates the loader, opens `HADOOP_ISAL_LIBRARY`, clears loader errors, resolves all required functions, discovers the actual library path with `dladdr` or Windows APIs, and stores a duplicated library name. Errors are returned through the caller-provided string buffer.

## State and Persistence
The loader, dynamic library handle, function pointers, and library name persist process-wide. The code never frees or unloads the ISA-L library.

## Dependencies and Integration Points
It depends on Hadoop platform config, `dlopen`/`LoadLibrary`, and `isal_load.h`. `jni_common.c` calls it from Java `ErasureCodeNative.loadLibrary()`.

## Risks and Edge Cases
If allocation succeeds but `dlopen` fails, `isaLoader` remains allocated with missing symbols; subsequent calls return early because `isaLoader != NULL`, potentially leaving a permanently broken loader. `calloc` is not checked before `memset`. The function call `load_functions(isaLoader->libec)` passes an argument to a no-argument function in the visible source, which is a compile-time mismatch in strict C. Windows filename handling uses an unallocated `filename` pointer.

## Test Signals
Tests should cover missing ISA-L library, missing individual symbols, repeat load after failure, successful library-name reporting, and encode/decode only after successful load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/isal_load.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/isal_load.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/isal_load.h

## Purpose
`isal_load.h` declares the ISA-L dynamic loader structure, symbol typedefs, loading macros, and public loader functions.

## Important APIs, Types, and Functions
`IsaLibLoader` stores the loaded library handle, library name, GF function pointers, and erasure-code function pointers. `EC_LOAD_DYNAMIC_SYMBOL` abstracts `dlsym`/`GetProcAddress`. Public functions are `build_support_erasurecode()` and `load_erasurecode_lib()`.

## Control Flow
The header's macros return an error string from the caller when a symbol cannot be resolved. Platform branches define compatible function pointer calling conventions.

## State and Persistence
It declares external global `isaLoader`, which persists after initialization in `isal_load.c`.

## Dependencies and Integration Points
It is included by wrapper files (`gf_util.c`, `erasure_code.c`, `jni_common.c`) and binds them to dynamic ISA-L symbols without direct library linkage.

## Risks and Edge Cases
The symbol-loading macro relies on a local `isaLoader` global and a caller returning `const char *`; misuse in other function shapes would be unsafe. Build support is controlled by `HADOOP_ISAL_LIBRARY`, so compile-time and runtime availability can diverge.

## Test Signals
Cross-platform compile tests, symbol-resolution failure tests, and Java load-library behavior validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/isal_load.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_common.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_common.c

## Purpose
`jni_common.c` provides shared JNI utilities for the native erasure-code raw coders. It loads ISA-L, stores/retrieves native coder pointers, and maps Java direct-buffer arrays plus offsets to native pointer arrays.

## Important APIs, Types, and Functions
Functions are `loadLib()`, `setCoder()`, `getCoder()`, `getInputs()`, and `getOutputs()`. They operate on Java fields/methods `nativeCoder` and `allowVerboseDump()`.

## Control Flow
`loadLib()` delegates to `load_erasurecode_lib()` and throws `UnsatisfiedLinkError` if an error string is returned. `setCoder()` locates the Java `nativeCoder` field and stores a native pointer. `getCoder()` reads verbosity through a Java callback, gets `nativeCoder`, and updates the native coder's verbose flag. `getInputs()` and `getOutputs()` validate array lengths, copy Java int offsets, obtain each direct buffer address, add offsets, and fill native pointer arrays.

## State and Persistence
No static state is owned here. Native coder pointers persist in Java object fields, while buffer pointer arrays are per-call data owned by wrapper structs.

## Dependencies and Integration Points
It depends on ISA-L loading, `erasure_coder.h`, JNI direct buffers, and Java raw-coder classes. All RS/XOR JNI files use these utilities.

## Risks and Edge Cases
The buffer helpers do not check `GetDirectBufferAddress()` for null before offset arithmetic, so non-direct buffers can cause invalid pointers. Local references from `GetObjectArrayElement()` are not deleted in the loops. If an exception is thrown during field/method lookup, later code may continue unless callers check pending exceptions.

## Test Signals
Tests should cover null native coder after destroy, non-direct buffers, bad array lengths, offset handling, verbose mode propagation, missing `nativeCoder` field, and library-load failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_common.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_common.h

## Purpose
`jni_common.h` declares shared JNI utility functions for native erasure-code raw coders.

## Important APIs, Types, and Functions
It exposes `loadLib()`, `setCoder()`, `getCoder()`, `getInputs()`, and `getOutputs()`, plus includes JNI and `erasure_coder.h`.

## Control Flow
There is no runtime flow in the header. It defines the utility surface that RS and XOR native wrappers call during initialization, encode/decode, and destruction.

## State and Persistence
No state is declared here except the native pointer contract implied by `setCoder()`/`getCoder()`.

## Dependencies and Integration Points
It sits between Java raw-coder classes and native erasure-code structs.

## Risks and Edge Cases
Consumers must pass arrays of the expected sizes and direct buffers. The header does not encode constness or ownership, so misuse can corrupt Java-owned buffers.

## Test Signals
Compile tests for all JNI coder files and runtime encode/decode tests with offset arrays validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_erasure_code_native.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_erasure_code_native.c

## Purpose
`jni_erasure_code_native.c` exposes global native ISA-L erasure-code library operations to Java.

## Important APIs, Types, and Functions
JNI exports are `ErasureCodeNative.loadLibrary()` and `ErasureCodeNative.getLibraryName()`.

## Control Flow
`loadLibrary()` calls shared `loadLib()`, which initializes the ISA-L loader or throws `UnsatisfiedLinkError`. `getLibraryName()` checks `isaLoader` and throws if the library has not been loaded; otherwise it returns the stored resolved library name as a Java string.

## State and Persistence
It reads global `isaLoader` initialized by `isal_load.c`. No additional state is stored.

## Dependencies and Integration Points
It depends on `jni_common.h`, `isal_load.h`, and Java `ErasureCodeNative`. Java callers should invoke `loadLibrary()` before native raw coders are used.

## Risks and Edge Cases
If the loader is partially initialized after a failed load, `getLibraryName()` behavior depends on `isaLoader->libname` being set. There is no unload path.

## Test Signals
Tests should cover library-name calls before and after load, missing-library errors, and successful native RS/XOR coder creation after load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_erasure_code_native.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_rs_decoder.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_rs_decoder.c

## Purpose
`jni_rs_decoder.c` is the JNI wrapper for Hadoop's native Reed-Solomon raw decoder.

## Important APIs, Types, and Functions
It defines wrapper struct `RSDecoder` containing `IsalDecoder decoder` plus input and output pointer arrays. JNI exports are `initImpl()`, `decodeImpl()`, and `destroyImpl()`.

## Control Flow
`initImpl()` allocates and zeroes `RSDecoder`, initializes the embedded decoder, and stores the pointer in Java `nativeCoder`. `decodeImpl()` retrieves the native coder, rejects use after close, reads erased indexes, maps all data/parity input direct buffers and output buffers, calls `decode()`, and releases the erased-index array. `destroyImpl()` frees the wrapper and clears the Java native pointer.

## State and Persistence
The embedded `IsalDecoder` persists across decode calls and caches decode matrices for repeated erasure patterns. Java owns the lifecycle through the native pointer field.

## Dependencies and Integration Points
It depends on `jni_common`, `erasure_coder`, and Java `NativeRSRawDecoder`. It reconstructs erased data or parity chunks into Java direct output buffers.

## Risks and Edge Cases
`malloc` is not checked before `memset`. If `decode()` fails internally, the JNI wrapper does not inspect a return code. Direct-buffer validity and erased-index bounds are assumed to be validated by Java.

## Test Signals
Tests should cover single/multiple erased data and parity chunks, repeated erasure patterns, decode after destroy, invalid erased indexes, and insufficient available inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_rs_decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_rs_encoder.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_rs_encoder.c

## Purpose
`jni_rs_encoder.c` is the JNI wrapper for Hadoop's native Reed-Solomon raw encoder.

## Important APIs, Types, and Functions
It defines `RSEncoder`, embedding `IsalEncoder encoder` and arrays of input/output pointers. JNI exports are `initImpl()`, `encodeImpl()`, and `destroyImpl()`.

## Control Flow
`initImpl()` allocates, zeroes, initializes the encoder, and stores the native pointer in Java. `encodeImpl()` retrieves the coder, rejects closed instances, maps data inputs and parity outputs from direct-buffer arrays plus offsets, and calls `encode()`. `destroyImpl()` frees the native wrapper and clears `nativeCoder`.

## State and Persistence
The `IsalEncoder` stores encode matrix and GF tables for reuse across calls. Pointer arrays are overwritten on each encode call.

## Dependencies and Integration Points
It integrates Java `NativeRSRawEncoder` with `erasure_coder.c` and ISA-L through `jni_common`.

## Risks and Edge Cases
Allocation failure is not checked. Java must guarantee input/output array sizes, direct buffers, valid offsets, and supported data/parity counts. Encode return value is ignored.

## Test Signals
Known-answer parity tests, offset handling, repeated calls, closed-coder errors, non-direct buffer rejection, and max-unit boundary tests are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_rs_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_xor_decoder.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_xor_decoder.c

## Purpose
`jni_xor_decoder.c` implements the JNI wrapper for Hadoop's native XOR raw decoder, used for single-parity XOR reconstruction.

## Important APIs, Types, and Functions
It defines `XORDecoder` with an `IsalCoder`, input pointer array, and output pointer array. JNI exports are `initImpl()`, `decodeImpl()`, and `destroyImpl()`.

## Control Flow
`initImpl()` allocates and initializes the basic coder state. `decodeImpl()` retrieves the coder, maps all data plus parity inputs and output buffers, zeroes the first output, then XORs every non-null input byte into that output. `destroyImpl()` frees the native wrapper and clears the Java pointer.

## State and Persistence
Only the basic unit counts persist in `IsalCoder`; no GF tables are needed. Pointer arrays are per-call state inside the wrapper.

## Dependencies and Integration Points
It depends on `jni_common` for direct-buffer mapping and Java `NativeXORRawDecoder`.

## Risks and Edge Cases
Only `outputs[0]` is reconstructed, matching single-parity XOR assumptions. Erased indexes are accepted in the signature but not used directly. Allocation and direct-buffer failures are not robustly checked.

## Test Signals
Tests should cover recovery of any single missing data/parity chunk, decode after destroy, null inputs for erased chunks, offset correctness, and invalid multi-parity configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_xor_decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_xor_encoder.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_xor_encoder.c

## Purpose
`jni_xor_encoder.c` implements the JNI wrapper for Hadoop's native XOR raw encoder.

## Important APIs, Types, and Functions
It defines `XOREncoder`, containing an `IsalCoder`, data input pointers, and parity output pointers. JNI exports are `initImpl()`, `encodeImpl()`, and `destroyImpl()`.

## Control Flow
`initImpl()` allocates and initializes basic unit counts. `encodeImpl()` retrieves the native coder, maps direct-buffer inputs and outputs, copies the first input chunk into `outputs[0]`, then XORs each remaining data input into that parity buffer. `destroyImpl()` frees and clears the native pointer.

## State and Persistence
The native object persists only unit-count metadata and reusable pointer arrays. No matrices or dynamic libraries are involved in the XOR algorithm itself.

## Dependencies and Integration Points
It uses `jni_common` and Java `NativeXORRawEncoder`. It shares the same raw-coder lifecycle as the RS JNI wrappers.

## Risks and Edge Cases
The code assumes at least one data input and one parity output. It only writes the first parity output, so Java must restrict XOR coding to one parity unit. Allocation and non-direct-buffer failures are not fully guarded.

## Test Signals
Parity known-answer tests, offset tests, repeated encode calls, closed-coder error handling, and Java validation for parity count are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/jni_xor_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/NativeIO.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/NativeIO.c

## Purpose
`NativeIO.c` is Hadoop common's broad JNI bridge for native filesystem, file descriptor, permission, memory, and optional persistent-memory operations. It exposes POSIX and Windows operations through Java `NativeIO` inner classes and normalizes native errors into `NativeIOException`.

## Important APIs, Types, and Functions
Initialization APIs include `initNative()`, `initNativePosix()`, and `initNativeWindows()`. POSIX methods include `fstat`, `stat`, `posix_fadvise`, `sync_file_range`, `mlock_native`, `open`, `chmodImpl`, `getUserName`, `getGroupName`, `mmap`, `munmap`, rename/link, memlock-limit, and PMDK methods. Windows methods include file/directory creation with mode, owner lookup, file pointer movement, access checks, working-set extension, unbuffered copy, rename/link wrappers, and security/stat helpers. Internal helpers initialize Java stat classes, NativeIOException classes, errno enum mapping, file descriptor helpers, and optional password/group lookup locking.

## Control Flow
Initialization caches global class references, constructors, file-descriptor fields, errno enum mapping, constants, and optional PMDK state. POSIX wrappers convert Java strings or file descriptors to native values, call one system API, then map failures through `throw_ioe()`. User/group lookup optionally enters `pw_lock_object`, allocates reentrant lookup buffers, retries on `ERANGE`, validates returned pointers, and converts names to Java strings. PMDK methods load libpmem, map/create/unmap/copy/sync persistent memory regions, and construct Java `PmemMappedRegion` objects.

## State and Persistence
Static global references cache Java classes/constructors and `pw_lock_object`. File descriptors and mmap/PMDK addresses persist outside this file after being returned to Java. PMDK loader state persists process-wide. There is no filesystem persistence except operations intentionally performed on caller-specified paths.

## Dependencies and Integration Points
It depends on POSIX syscalls, Windows winutils wrappers, `file_descriptor`, `errno_enum`, `exception`, and optional `pmdk_load`. It is a central integration point for Hadoop Java NativeIO, HDFS short-circuit/persistent memory paths, and platform-specific file permission behavior.

## Risks and Edge Cases
The file has many platform branches, so behavior differs substantially across Unix, FreeBSD, macOS, and Windows. Several PMDK format strings print 64-bit addresses/lengths with `%x`. `pmem_region_deinit()` attempts to delete a method ID as a global reference, which is not a valid JNI reference. `mmap()` does not check pending exceptions from `fd_get()`. User/group lookup depends on correct optional locking for platforms with non-threadsafe NSS behavior.

## Test Signals
Tests should cover init/deinit idempotence, POSIX constants, stat/fstat permission fields, errno enum mapping, file open/chmod/rename/link, fadvise and sync-file-range availability, mlock and memlock limits, mmap/munmap, Windows create/access/owner operations, PMDK supported/unsupported states, and concurrent user/group lookups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/NativeIO.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/SharedFileDescriptorFactory.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/SharedFileDescriptorFactory.c

## Purpose
`SharedFileDescriptorFactory.c` creates anonymous, pre-sized file descriptors backed by temporary files and deletes stale temporary files for Hadoop shared-memory use cases.

## Important APIs, Types, and Functions
JNI exports are `deleteStaleTemporaryFiles0()` and `createDescriptor0()`. Internal helper `zero_fully()` writes zero-filled buffers to size the file. A static `pthread_mutex_t g_rand_lock` serializes `rand()` usage.

## Control Flow
Stale cleanup opens a target directory, scans entries, and unlinks files whose names start with the supplied prefix. Descriptor creation builds a path from directory, prefix, and random suffix; opens it with `O_CREAT | O_EXCL | O_RDWR`; retries on name collision or interrupt; unlinks the file immediately after opening; writes zeroes up to requested length; seeks back to start; and wraps the fd in a Java `FileDescriptor`.

## State and Persistence
Only the random mutex is static. Created files are unlinked after opening, so storage persists only as long as the descriptor remains open. The fd is returned to Java for lifecycle management.

## Dependencies and Integration Points
It depends on Unix filesystem APIs, `file_descriptor`, and exception helpers. It is compiled only under `UNIX` and supports Java `SharedFileDescriptorFactory`.

## Risks and Edge Cases
On `EEXIST`, the code retries without changing `rnd`, which can spin forever if the same generated path persists. `rand()` is not seeded here. `zero_fully()` does not handle `write()` returning zero. Error messages sometimes use the directory path instead of the full target path.

## Test Signals
Tests should cover descriptor creation length/content, unlink-after-open semantics, stale cleanup by prefix, collision handling, path-too-long errors, interrupted writes/opens, and close cleanup from Java.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/SharedFileDescriptorFactory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/errno_enum.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/errno_enum.c

## Purpose
`errno_enum.c` maps native errno integer values to Hadoop's Java `Errno` enum for `NativeIOException`.

## Important APIs, Types, and Functions
It defines `errno_mapping_t`, static `ERRNO_MAPPINGS`, `errno_enum_init()`, `errno_enum_deinit()`, internal `errno_to_string()`, and public `errno_to_enum()`.

## Control Flow
Initialization caches global references to `java.lang.Enum` and Hadoop `Errno`, plus the static `Enum.valueOf(Class,String)` method. `errno_to_enum()` converts an errno integer to a string name, creates a Java string, and invokes `Enum.valueOf` to obtain the enum constant. Unrecognized errno values map to `"UNKNOWN"`.

## State and Persistence
Global class refs and method ID persist between init and deinit. The mapping table is static read-only data.

## Dependencies and Integration Points
It is initialized from `NativeIO.c` and used by `throw_ioe()` to construct Java `NativeIOException` with an enum errno value.

## Risks and Edge Cases
Only a subset of errno values is listed. If Java `Errno.UNKNOWN` is missing, unknown native errors will create a pending Java exception. Platform-specific errno names may not exist on all Unix variants, depending on headers and enum definitions.

## Test Signals
Tests should verify common errno values, unknown errno mapping, initialization/deinitialization idempotence, and Java enum consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/errno_enum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/errno_enum.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/errno_enum.h

## Purpose
`errno_enum.h` declares the native errno-to-Java-enum mapping API.

## Important APIs, Types, and Functions
It declares `errno_enum_init()`, `errno_enum_deinit()`, and `errno_to_enum()`.

## Control Flow
There is no runtime flow. Callers are expected to initialize before converting errno values and deinitialize when native state is torn down.

## State and Persistence
No state is declared in the header, but the implementation owns global JNI references.

## Dependencies and Integration Points
It is included by `NativeIO.c` and participates in `NativeIOException` construction.

## Risks and Edge Cases
Callers must not invoke `errno_to_enum()` before successful initialization. The API returns a JNI object and can leave pending exceptions if Java enum lookup fails.

## Test Signals
NativeIO init and representative IOError tests validate this header's contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/errno_enum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/file_descriptor.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/file_descriptor.c

## Purpose
`file_descriptor.c` provides shared JNI helpers for converting between native file descriptors/handles and `java.io.FileDescriptor` objects.

## Important APIs, Types, and Functions
Public functions are `fd_init()`, `fd_deinit()`, `fd_get()`, and `fd_create()`. Static cached values include global `FileDescriptor` class ref, the `fd` field on Unix, the `handle` field on Windows, and the no-argument constructor.

## Control Flow
`fd_init()` finds and globally references `java/io/FileDescriptor`, resolves fields and constructor, and returns early if already initialized. `fd_get()` validates non-null Java objects and reads the platform field. `fd_create()` constructs a new Java `FileDescriptor` and sets the native fd/handle field. `fd_deinit()` releases the global class reference and clears cached IDs.

## State and Persistence
Cached JNI class and field/method IDs persist process-wide between init and deinit. Returned Java `FileDescriptor` objects own only the numeric descriptor value, not the OS lifecycle by themselves.

## Dependencies and Integration Points
Many JNI files use these helpers: NativeIO, DomainSocket, SharedFileDescriptorFactory, and descriptor-passing socket code.

## Risks and Edge Cases
The cached field names depend on JDK internals (`fd`/`handle`) and can be sensitive to Java version/module access. `fd_create()` does not mark ownership semantics; Java callers must avoid double close or leaked descriptors.

## Test Signals
Tests should wrap and unwrap descriptors on Unix and Windows, validate null-object exceptions, and exercise descriptor passing and NativeIO-created descriptors across supported JDKs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/file_descriptor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/file_descriptor.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/file_descriptor.h

## Purpose
`file_descriptor.h` declares shared JNI file descriptor conversion helpers.

## Important APIs, Types, and Functions
It declares `fd_init()`, `fd_deinit()`, and platform-specific `fd_get()`/`fd_create()` signatures using `int` on Unix and `long` on Windows.

## Control Flow
There is no runtime flow. Platform branches expose the correct native handle type to callers.

## State and Persistence
The header declares no state, but callers rely on implementation-level cached JNI refs.

## Dependencies and Integration Points
It is included by NativeIO, DomainSocket, and shared descriptor factory code.

## Risks and Edge Cases
Callers must use the platform-correct type and initialize before use. Mixing Unix and Windows assumptions would truncate handles or read the wrong Java field.

## Test Signals
Cross-platform build tests and descriptor round-trip tests validate the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/file_descriptor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/pmdk_load.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/pmdk_load.c

## Purpose
`pmdk_load.c` dynamically loads libpmem/PMDK symbols used by NativeIO persistent-memory support.

## Important APIs, Types, and Functions
It defines global `PmdkLibLoader *pmdkLoader` and `int pmdkLoaded`, internal `load_functions()`, and public `load_pmdk_lib()`. Resolved symbols are `pmem_map_file`, `pmem_unmap`, `pmem_is_pmem`, `pmem_drain`, `pmem_memcpy_nodrain`, and `pmem_msync`.

## Control Flow
`load_pmdk_lib()` clears the error buffer, returns early when already loaded, allocates the loader if necessary, opens `HADOOP_PMDK_LIBRARY`, resolves required functions, discovers the actual library path with `dladdr`, stores a duplicated library name, and marks `pmdkLoaded`.

## State and Persistence
The loader, library handle, function pointers, library name, and loaded flag persist process-wide. The file never unloads libpmem.

## Dependencies and Integration Points
It is used by `NativeIO.c` when `HADOOP_PMDK_LIBRARY` is compiled in, enabling PMDK map/copy/sync JNI methods.

## Risks and Edge Cases
If `dlopen` fails after allocating `pmdkLoader`, later calls can retry because `pmdkLoaded` remains unset, but the partially allocated loader remains. Allocation is not checked. `pmdkLoaded` is not synchronized, so concurrent initialization could race. Windows branches reference `GetModuleFileName` despite the header primarily defining Unix symbol types.

## Test Signals
Tests should cover PMDK absent/present states, missing symbols, repeated load calls, concurrent initialization, and NativeIO PMDK method behavior after load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/pmdk_load.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/pmdk_load.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/pmdk_load.h

## Purpose
`pmdk_load.h` declares the PMDK dynamic loader structure, function pointer types, symbol-loading macro, and load entry point.

## Important APIs, Types, and Functions
`PmdkLibLoader` stores the library handle, library name, and pointers to required libpmem functions. `PMDK_LOAD_DYNAMIC_SYMBOL` resolves a symbol from `pmdkLoader->libec`. Public API is `load_pmdk_lib()`, and external global `pmdkLoader` is declared.

## Control Flow
The macro returns an error string from the calling loader function when a required symbol cannot be found. The header itself has compile-time Unix branches for libpmem typedefs.

## State and Persistence
It declares `pmdkLoader`, which points to process-wide loader state after initialization.

## Dependencies and Integration Points
It is included by PMDK loader implementation and `NativeIO.c` PMDK operations.

## Risks and Edge Cases
The loader struct field name `libec` is inherited from erasure-code style naming and can obscure that it stores libpmem. Symbol typedefs are only defined under `UNIX`, limiting portability unless guarded by build configuration.

## Test Signals
Builds with and without `HADOOP_PMDK_LIBRARY`, missing-symbol tests, and PMDK map/unmap JNI tests validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/pmdk_load.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/net/unix/DomainSocket.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/net/unix/DomainSocket.c

## Purpose
`DomainSocket.c` implements Hadoop's Unix-domain socket JNI operations, including server/client socket creation, path security validation, socket options, array/direct-buffer I/O, and file-descriptor passing with `SCM_RIGHTS`.

## Important APIs, Types, and Functions
JNI exports include `anchorNative()`, `validateSocketPathSecurity0()`, `bind0()`, `socketpair0()`, `accept0()`, `connect0()`, `setAttribute0()`, `getAttribute0()`, `close0()`, `closeFileDescriptor0()`, `shutdown0()`, `sendFileDescriptors0()`, `receiveFileDescriptors0()`, `readArray0()`, `available0()`, `writeArray0()`, and `readByteBufferDirect0()`. Key helpers include `errnoToSocketExceptionName()`, `newSocketException()`, `flexBufInit()`, `setup()`, `javaMillisToTimeVal()`, `write_fully()`, and `cmsghdr_with_fds`.

## Control Flow
`setup()` creates an AF_UNIX stream socket, copies and validates the path length, sets SIGPIPE suppression where available, and either connects or unlinks/binds/chmods/listens. Path security validation walks parent path components and rejects world-writable, unsafe group-writable, or unsafe owner-writable directories after optional skipped components. I/O methods copy Java arrays into stack-or-heap flexible buffers or use direct-buffer addresses, retry interrupted syscalls, translate EOF to Java `-1`, and map errno to socket exceptions. Descriptor passing builds a control message carrying up to 16 fds and sends at least one byte; receive creates Java `FileDescriptor` objects and closes received fds on error.

## State and Persistence
No global socket state is stored beyond file descriptor helper initialization. OS socket descriptors persist in Java as integers or `FileDescriptor` objects. Flexible buffers are per-call stack/heap allocations.

## Dependencies and Integration Points
It depends on Unix sockets, `poll`-style socket options, `ioctl(FIONREAD)`, Hadoop exception helpers, and `file_descriptor`. It backs Java `DomainSocket` used by HDFS short-circuit and local IPC paths.

## Risks and Edge Cases
`sendFileDescriptors0()` sets `jfdsLen = 0` before formatting the error for too many fds, hiding the original length. `receiveFileDescriptors0()` derives received fd count from `aux.hdr.cmsg_len` without validating control-message headers or truncation flags. Path security uses string tokenization and `stat`, so symlink races are possible. `setup()` closes fd only when `fd > 0`, leaking fd 0 on rare paths.

## Test Signals
Tests should cover bind/connect/accept/socketpair, path length and security rejection, buffer and timeout options, EOF behavior, SIGPIPE-safe writes, descriptor passing count limits and cleanup, direct-buffer reads, and concurrent close/shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/net/unix/DomainSocket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/net/unix/DomainSocketWatcher.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/net/unix/DomainSocketWatcher.c

## Purpose
`DomainSocketWatcher.c` implements a small JNI-managed poll set for watching Unix-domain sockets for readability or hangup.

## Important APIs, Types, and Functions
It defines `struct fd_set_data` with allocated size, used size, and a flexible `pollfd` array. JNI exports are `anchorNative()`, `FdSet.alloc0()`, `FdSet.add()`, `FdSet.remove()`, `FdSet.getAndClearReadableFds()`, `FdSet.close()`, and `doPoll0()`.

## Control Flow
`anchorNative()` caches the Java `FdSet.data` long field. `alloc0()` allocates a minimum two-fd poll set. `add()` grows the native allocation by doubling when needed and appends a `POLLIN | POLLHUP` entry. `remove()` swaps the last entry into the removed slot. `doPoll0()` calls `poll()` and treats `EINTR` as no descriptors ready. `getAndClearReadableFds()` counts entries with `POLLIN` or `POLLHUP`, creates a Java int array, fills it, and clears returned `revents`.

## State and Persistence
The native `fd_set_data` allocation is owned by the Java `FdSet.data` field until `close()`. No process-global fd state is stored besides the cached field ID.

## Dependencies and Integration Points
It depends on `poll(2)`, JNI, and Hadoop exception helpers. Java `DomainSocketWatcher` uses it to multiplex many local sockets.

## Risks and Edge Cases
`add()` sets `nd->alloc_size = nd->alloc_size * 2` after `realloc`, using the copied old value but relying on it remaining valid. The code does not guard against adding duplicate fds. Thread safety must be provided by the Java watcher because the native set has no locking.

## Test Signals
Tests should add/remove fds, grow beyond the initial capacity, detect readable and hung-up sockets, handle EINTR, reject removing absent fds, and verify `close()` nulls native state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/net/unix/DomainSocketWatcher.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/JniBasedUnixGroupsMapping.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/JniBasedUnixGroupsMapping.c

## Purpose
`JniBasedUnixGroupsMapping.c` implements Unix JNI group lookup for Hadoop security. It resolves the Unix groups associated with a user and returns Java string arrays.

## Important APIs, Types, and Functions
JNI exports are `anchorNative()` and `getGroupsForUser()`. It caches Java `logError(int,String)` and `java.lang.String` class references. Internal `logError()` reports group-id lookup failures back to Java. It uses `hadoop_user_info_*` and `hadoop_group_info_*` helper APIs.

## Control Flow
`anchorNative()` caches method/class references. `getGroupsForUser()` optionally enters the global `pw_lock_object`, converts the Java username, allocates user info, fetches passwd data, returns an empty array for unknown users, obtains group IDs, allocates an initial Java array sized to the gid count, resolves each gid to a group name, logs failures for individual gids, and compacts the Java array if some groups could not be resolved.

## State and Persistence
Static method/class references persist after anchoring. `pw_lock_object` is shared with NativeIO's password/group lookup workaround. User and group info allocations are per-call and freed before return.

## Dependencies and Integration Points
It depends on Unix passwd/group facilities through Hadoop helper wrappers, `exception.c`, and Java `JniBasedUnixGroupsMapping`. It integrates with Hadoop authorization and user/group mapping services.

## Risks and Edge Cases
Global `g_string_clazz` is not freed in this file. Some local references in compaction paths depend on JVM local-reference capacity. Partial group lookup failures are logged and omitted rather than failing the whole lookup. Thread safety depends on optional `pw_lock_object` initialization by NativeIO.

## Test Signals
Tests should cover existing users, unknown users, users with many groups, failed gid-to-name lookups, concurrent lookups with and without the lock workaround, and Java `logError` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/JniBasedUnixGroupsMapping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/JniBasedUnixGroupsMappingWin.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/JniBasedUnixGroupsMappingWin.c

## Purpose
`JniBasedUnixGroupsMappingWin.c` provides the Windows JNI implementation for Hadoop's group mapping class. It retrieves local Windows groups for a user and returns them as Java strings, while `anchorNative()` remains a no-op placeholder.

## Important APIs, Types, and Functions
JNI exports are `anchorNative()` and `getGroupsForUser()`. Internal `throw_ioexception()` formats Windows error messages. Static `emptyGroups` caches a global empty Java string array for error fallback. The file calls `GetLocalGroupsForUser()` and frees returned buffers with `NetApiBufferFree()`.

## Control Flow
`getGroupsForUser()` lazily creates `emptyGroups`, obtains the Java user string as UTF-16, calls the Windows helper to get local groups, allocates a Java string array sized to `ngroups`, iterates `LOCALGROUP_USERS_INFO_0` entries into Java strings, then releases buffers. On non-success return codes it throws an IOException and returns `emptyGroups`.

## State and Persistence
`emptyGroups` is a process-wide global reference. Group result buffers are per-call and freed before return.

## Dependencies and Integration Points
It depends on Windows APIs, Hadoop `winutils.h`, JNI, and the same Java `JniBasedUnixGroupsMapping` class used by Unix.

## Risks and Edge Cases
`FormatMessageA` is called with `buffer` rather than `&buffer` while using `FORMAT_MESSAGE_ALLOCATE_BUFFER`, so error message allocation may not work as intended. Returning `emptyGroups` after throwing an exception can be confusing to callers if they clear exceptions. Local references for group strings are not deleted inside the loop.

## Test Signals
Tests should cover users with zero/multiple local groups, invalid users, Windows error formatting, repeated calls reusing `emptyGroups`, and memory cleanup of NetAPI buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/JniBasedUnixGroupsMappingWin.c -->
