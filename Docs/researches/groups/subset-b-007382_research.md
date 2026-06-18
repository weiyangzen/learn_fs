# subset-b-007382 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/JniBasedUnixGroupsNetgroupMapping.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/JniBasedUnixGroupsNetgroupMapping.c

## Purpose
`JniBasedUnixGroupsNetgroupMapping.c` implements the native JNI method behind `JniBasedUnixGroupsNetgroupMapping.getUsersForNetgroupJNI`. It resolves a Unix netgroup name into the users listed by the platform netgroup database and returns them to Java as a `String[]`.

## Important APIs, types, and functions
The only exported JNI symbol is `Java_org_apache_hadoop_security_JniBasedUnixGroupsNetgroupMapping_getUsersForNetgroupJNI`. Internally it uses a small `UserList` singly linked list to stage user names before the final Java array is allocated. Platform APIs are `setnetgrent`, `getnetgrent`, and `endnetgrent`; JNI APIs include `GetStringUTFChars`, `NewObjectArray`, `FindClass`, `NewStringUTF`, and `SetObjectArrayElement`. Exceptions are raised through Hadoop's `THROW` macro from `org_apache_hadoop.h`.

## Control flow
The method converts the Java netgroup name into a UTF-8 C string, opens netgroup iteration, walks every `(host,user,domain)` tuple, copies non-null user entries into the linked list, allocates a Java `String` array sized to the collected count, and fills it from the list. A single `END` cleanup path releases the Java string, calls `endnetgrent` if lookup was started, frees all list nodes, and either returns the array or throws the selected Java exception.

## State and persistence
All state is per-call native heap and libc netgroup iterator state. There is no persistent Hadoop state. The returned array order is reverse iteration order because new list nodes are pushed at the head.

## Dependencies and integration points
This file integrates Java group mapping with OS netgroup sources such as `/etc/netgroup`, NIS, or LDAP as exposed by libc. It is compiled into the Hadoop native library and called by `JniBasedUnixGroupsNetgroupMapping` and its fallback wrapper when native code is available.

## Risks and test signals
Risks include platform differences in `setnetgrent` return values, Linux treating an unknown netgroup as an `IOException`, unchecked `malloc` failures for list nodes and strings, duplicate user entries, and reverse-order results. Test signals include unknown netgroup behavior on Linux and BSD/macOS, netgroups with null user fields, large member lists, OOM/fault injection around JNI string allocation, and fallback behavior when the native library is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/JniBasedUnixGroupsNetgroupMapping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/hadoop_group_info.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/hadoop_group_info.c

## Purpose
`hadoop_group_info.c` provides a reusable C context for looking up Unix group records by gid with `getgrgid_r`. It wraps buffer management, retry behavior, and platform error normalization for Hadoop native security code.

## Important APIs, types, and functions
Public functions are `hadoop_group_info_alloc`, `hadoop_group_info_free`, and `hadoop_group_info_fetch`. `hadoop_group_info_clear` resets the embedded `struct group`, and `getgrgid_error_translate` maps platform-specific lookup failures to a narrower Hadoop-facing errno set. The allocation starts with an 8 KiB group buffer and can grow to 2 MiB.

## Control flow
Allocation creates the context and its initial scratch buffer. Fetch clears stale pointers, calls `getgrgid_r`, and loops on `EINTR`. On `ERANGE`, it doubles the buffer up to the maximum before retrying. Success requires both a zero return code and a non-null `struct group *`; a zero return with null group means not found. Other errors are translated so unknown groups become `ENOENT` while resource and I/O failures are preserved.

## State and persistence
The context owns one dynamically sized lookup buffer plus the embedded `struct group` whose string/member pointers point into that buffer. Data remains valid until the next fetch or free. No state is persisted outside the process.

## Dependencies and integration points
It depends on POSIX group database APIs and is used by native user/group mapping code that needs stable group names after discovering gids. The helper isolates libc buffer sizing quirks from JNI-facing code.

## Risks and test signals
Risks include very large group member lists exceeding the 2 MiB cap, callers retaining `struct group` pointers after the context is reused or freed, and platform-specific `getgrgid_r` error behavior. Test signals include nonexistent gids, gids with large membership lists, injected `ERANGE` growth, `EINTR` retry, and resource failures returning `ENOMEM`, `EMFILE`, `ENFILE`, or `EIO`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/hadoop_group_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/hadoop_group_info.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/hadoop_group_info.h

## Purpose
`hadoop_group_info.h` declares the native group lookup context used by Hadoop's Unix security helpers. It exposes a small lifecycle and fetch API around `struct group` without exposing libc buffer-management details to callers.

## Important APIs, types, and functions
The central type is `struct hadoop_group_info`, containing `buf_sz`, an embedded `struct group`, and the backing `char *buf`. Declared functions are `hadoop_group_info_alloc`, `hadoop_group_info_free`, and `hadoop_group_info_fetch(struct hadoop_group_info *, gid_t)`.

## Control flow
Callers allocate one context, call `hadoop_group_info_fetch` for each gid to refresh the embedded group record, read `ginfo->group` on success, and free the context when finished. Each fetch overwrites previous lookup results.

## State and persistence
The header defines runtime-only state. `struct group` member pointers are valid only while the context and its current buffer remain alive. There is no persistent storage or global cache contract.

## Dependencies and integration points
The header depends on `<grp.h>` for `struct group` and `<unistd.h>` for `size_t`. It is included by `hadoop_group_info.c` and native security components that need gid-to-group-name translation.

## Risks and test signals
Risks are API misuse: dereferencing stale group pointers after a later fetch, freeing a context twice, or assuming fetch never reallocates. Test signals are compile coverage from all native security users plus lookup tests covering successful gid lookup, unknown gid, and large group records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/hadoop_group_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/hadoop_user_info.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/hadoop_user_info.c

## Purpose
`hadoop_user_info.c` provides a reusable native context for resolving Unix user records and supplementary groups. It is the lower-level implementation behind JNI group mapping code that needs `passwd` fields, gids, and deterministic placement of the user's primary gid.

## Important APIs, types, and functions
Public functions are `hadoop_user_info_alloc`, `hadoop_user_info_free`, `hadoop_user_info_fetch`, and `hadoop_user_info_getgroups`. Helpers include `hadoop_user_info_clear`, `getpwnam_error_translate`, and `put_primary_gid_first`. Constants define an initial supplementary-gid array of 32 entries and a maximum passwd buffer size of 32 KiB.

## Control flow
Allocation sizes the passwd scratch buffer from `_SC_GETPW_R_SIZE_MAX`, with a 1 KiB floor. `hadoop_user_info_fetch` clears any previous result, calls `getpwnam_r`, retries `EINTR`, doubles the scratch buffer on `ERANGE`, and returns success only if libc supplies a non-null `struct passwd *`. `hadoop_user_info_getgroups` requires a valid fetched user, allocates or grows a gid array, calls `getgrouplist`, accounts for Linux versus FreeBSD return-code semantics, retries after resizing if necessary, and swaps the primary gid to index zero.

## State and persistence
The context owns a passwd buffer, an embedded `struct passwd`, and a dynamically allocated gid array. Lookup results persist until the next fetch, getgroups call, clear, or free. There is no disk persistence or global cache.

## Dependencies and integration points
It depends on POSIX passwd/group APIs and feeds Hadoop's JNI-based group mapping implementation. Java-facing code can use it to map usernames to group names by resolving a user, enumerating gids, then using `hadoop_group_info` for gid names.

## Risks and test signals
Risks include platform-specific `getgrouplist` return values, NSS backends that return zero or inconsistent group counts, primary gid missing from supplementary results, and callers keeping pointers after context reuse. Test signals include users with only primary group, users with more than 32 groups, unknown users, NSS failures, `ERANGE` passwd-buffer growth, and cross-platform Linux/BSD behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/hadoop_user_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/hadoop_user_info.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/hadoop_user_info.h

## Purpose
`hadoop_user_info.h` declares Hadoop's native Unix user lookup context and its public API. It lets JNI security code share one contract for fetching passwd data and supplementary groups.

## Important APIs, types, and functions
`struct hadoop_user_info` contains `buf_sz`, embedded `struct passwd pwd`, scratch `buf`, supplementary `gid_t *gids`, `num_gids`, and `gids_size`. The API declares allocation/free, `hadoop_user_info_fetch(struct hadoop_user_info *, const char *)`, and `hadoop_user_info_getgroups`.

## Control flow
The intended sequence is allocate, fetch a username, call getgroups if group membership is needed, read `pwd` and `gids`, and free. Every fetch clears previous user and group membership state.

## State and persistence
All state is caller-owned runtime memory. `pwd` string pointers point into `buf`; `gids` is owned by the context and may be reallocated. No information is persisted outside the native process.

## Dependencies and integration points
The header depends on `<pwd.h>` and `<unistd.h>`. It is paired with `hadoop_group_info.h` for user-to-group-name resolution in Hadoop's native group mapping implementation.

## Risks and test signals
Risks include stale pointer use after fetch/free, assuming `gids` ordering beyond the primary-gid-first guarantee, and passing an unfetched context to `hadoop_user_info_getgroups`. Test signals are native builds across Unix platforms and user/group lookup tests with unknown users and high group counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/hadoop_user_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/NativeCodeLoader.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/NativeCodeLoader.c

## Purpose
`NativeCodeLoader.c` implements small JNI probes used by Java to discover which optional native features were compiled into the Hadoop native library and where the loaded native library resides.

## Important APIs, types, and functions
Exported JNI methods are `buildSupportsSnappy`, `buildSupportsOpenssl`, `buildSupportsIsal`, and `getLibraryName`. The feature probes return `JNI_TRUE` only when build-time macros `HADOOP_SNAPPY_LIBRARY`, `HADOOP_OPENSSL_LIBRARY`, or `HADOOP_ISAL_LIBRARY` are present. `getLibraryName` uses `dladdr` on Unix and `GetLibraryName` on Windows.

## Control flow
Each support method is compile-time branching only. `getLibraryName` asks the runtime loader for the module that contains the JNI function pointer and returns the path as a Java string, or `"Unavailable"` if the platform lookup fails.

## State and persistence
There is no mutable state. Results reflect compile-time options and the current process's loaded native module path.

## Dependencies and integration points
The file integrates Java `NativeCodeLoader` with native build configuration, optional compression/crypto/erasure-code libraries, `dladdr`, and Windows winutils helpers. Java code uses these methods to gate native accelerators and diagnostics.

## Risks and test signals
Risks include mismatches between build macros and actually loadable optional libraries, platform-specific path encoding, and missing return path if an unsupported platform macro set is used. Test signals include native builds with each optional feature on/off, Unix and Windows `getLibraryName` calls, and Java fallback behavior when support probes return false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/NativeCodeLoader.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/NativeCrc32.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/NativeCrc32.c

## Purpose
`NativeCrc32.c` is the JNI bridge between Java `NativeCrc32`/`DataChecksum` and the native `bulk_crc` engine. It computes or verifies chunked CRC32 and CRC32C checksums for direct `ByteBuffer`s and Java byte arrays.

## Important APIs, types, and functions
The primary exported method is `nativeComputeChunkedSums`; wrappers include `nativeVerifyChunkedSums` and `nativeComputeChunkedSumsByteArray`. Helpers are `convert_java_crc_type` and `throw_checksum_exception`, which constructs `org.apache.hadoop.fs.ChecksumException`. The code accepts Hadoop checksum constants and maps them to `CRC32_ZLIB_POLYNOMIAL` or `CRC32C_POLYNOMIAL`.

## Control flow
For direct buffers, the method validates non-null buffers, direct-address availability, nonnegative offsets/lengths, and positive `bytes_per_checksum`; then it casts checksum storage to `uint32_t *` and calls `bulk_crc` either in compute or verify mode. For byte arrays, it uses `GetPrimitiveArrayCritical` in bounded iterations of about 1 MiB of data to avoid long critical sections. Verification failures are translated into `ChecksumException` with filename, absolute data position, expected CRC, and observed CRC.

## State and persistence
The JNI layer has no persistent state. It mutates the supplied checksum buffer or array in compute mode and reads it in verify mode. Byte-array critical sections are released after every iteration.

## Dependencies and integration points
It depends on Hadoop-generated JNI headers, `bulk_crc32.h`, branch prediction macros, Java `NativeCrc32`, `DataChecksum`, and `ChecksumException`. It is the high-performance path used by checksum calculation and verification in Hadoop I/O.

## Risks and test signals
Risks include missing upper-bound validation for offsets against actual buffer/array length, unaligned `uint32_t *` checksum casts, JNI critical-section constraints, endian assumptions via `bulk_crc`, and assertion failures if `bulk_crc` returns an unexpected code. Test signals include direct and heap byte-array checksum tests, invalid checksum type, null/non-direct buffers, partial final chunks, intentional checksum mismatch position, and large arrays that require multiple critical-section iterations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/NativeCrc32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/bulk_crc32.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/bulk_crc32.c

## Purpose
`bulk_crc32.c` implements Hadoop's native chunked CRC engine. It can compute or verify sequential CRC values over fixed-size chunks using CRC32C or zlib CRC32, with software slicing-by-8 defaults and architecture-specific function-pointer overrides.

## Important APIs, types, and functions
The public API is `bulk_crc`. Global function pointers `pipelined_crc32c_func` and `pipelined_crc32_zlib_func` default to software helpers and may be overwritten by CPU-specific constructor code. Important helpers include `store_or_verify`, `crc_val`, `crc32c_sb8`, `crc32_zlib_sb8`, `pipelined_crc32c_sb8`, and `pipelined_crc32_zlib_sb8`. Lookup-table dependencies are `crc32c_tables.h` and `crc32_zlib_polynomial_tables.h`.

## Control flow
`bulk_crc` determines whether it is computing or verifying from whether `error_info` is null, selects the polynomial implementation, processes complete chunks three at a time through the pipelined function, handles one or two remaining full chunks, then handles a smaller final chunk. Each raw CRC starts at `0xffffffff`, is finalized by bitwise inversion, converted with `ntohl`, and stored or compared. On mismatch, it fills `crc32_error_t` with got/expected values and a pointer to the failing data chunk.

## State and persistence
Only the two global function pointers are process state. They start as portable software implementations and may be changed during library load by architecture files. The caller owns data and checksum storage.

## Dependencies and integration points
This file is called by `NativeCrc32.c` and native tests. CMake links the matching architecture source for x86, AArch64, or RISC-V so constructors can replace the default implementation when CPU support is detected.

## Risks and test signals
Risks include unaligned 32-bit loads in slicing-by-8 code, endian conversion compatibility with Java checksum layout, function-pointer initialization races at load time, invalid checksum type handling, and relying on callers to size `sums` correctly. Test signals include `test_bulk_crc32`, Java `DataChecksum` tests, CRC32 and CRC32C vectors, one-byte chunks, final remainders, mismatch reporting, and architecture-specific accelerator parity against software.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/bulk_crc32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/bulk_crc32.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/bulk_crc32.h

## Purpose
`bulk_crc32.h` defines the public C contract for Hadoop's native bulk CRC implementation. It standardizes checksum type constants, verification return codes, error reporting, and the `bulk_crc` function signature.

## Important APIs, types, and functions
Constants are `CRC32C_POLYNOMIAL`, `CRC32_ZLIB_POLYNOMIAL`, `CHECKSUMS_VALID`, `INVALID_CHECKSUM_DETECTED`, and `INVALID_CHECKSUM_TYPE`. `crc32_error_t` reports `got_crc`, `expected_crc`, and `bad_data`. `bulk_crc` computes or verifies checksums over `data_len` bytes in `bytes_per_checksum` chunks.

## Control flow
Callers pass `error_info == NULL` for compute mode, where `sums` is written. They pass non-null `error_info` for verification mode, where `sums` is read and mismatch details are filled before returning `INVALID_CHECKSUM_DETECTED`.

## State and persistence
The header declares no global state. It defines how callers share data buffers, checksum buffers, and error metadata with the implementation.

## Dependencies and integration points
The header depends on `<stdint.h>` and, on Unix, `<unistd.h>` for `size_t`. It is included by JNI checksum code, portable CRC implementation, architecture accelerators, and native tests.

## Risks and test signals
Risks include callers providing insufficient checksum storage, zero or negative chunk sizes before validation, and interpreting compute-mode error codes as verification codes. Test signals are build coverage across Unix/Windows and consumers verifying both compute and verify modes for both polynomial constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/bulk_crc32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/bulk_crc32_aarch64.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/bulk_crc32_aarch64.c

## Purpose
`bulk_crc32_aarch64.c` provides AArch64 hardware-accelerated implementations for Hadoop's bulk CRC engine. It replaces the portable slicing-by-8 functions when the CPU advertises CRC32 instructions.

## Important APIs, types, and functions
Static functions `pipelined_crc32c` and `pipelined_crc32_zlib` process one to three independent blocks with ARMv8 CRC instructions. Inline-assembly macros include `LDP`, `CRC32CX`, `CRC32CW`, `CRC32CH`, `CRC32CB`, and zlib-polynomial variants `CRC32ZX`, `CRC32ZW`, `CRC32ZH`, `CRC32ZB`. The constructor `init_cpu_support_flag` checks `getauxval(AT_HWCAP)` and `HWCAP_CRC32`.

## Control flow
The pipelined functions receive initial CRC values and a contiguous data region containing one, two, or three blocks. They use a switch on `num_blocks`, process most data with 128-bit pair loads and 64-bit CRC operations, then consume remaining 8-, 4-, 2-, and 1-byte tails. On library load, if hardware support is present, the file assigns `pipelined_crc32c_func` and `pipelined_crc32_zlib_func` to these accelerated functions.

## State and persistence
The only state mutation is updating the global function pointers declared in `bulk_crc32.c`. No per-call state persists beyond output CRC values.

## Dependencies and integration points
It depends on AArch64 assembler support, Linux auxiliary-vector hardware capabilities, `bulk_crc32.h`, and branch prediction macros. CMake selects this file for AArch64 native builds.

## Risks and test signals
Risks include assembler compatibility, unaligned loads in tail handling, incorrect `HWCAP_CRC32` definitions on non-Linux platforms, and any mismatch between ARM CRC instructions and Hadoop's expected polynomial/endian layout. Test signals include disassembly/performance checks noted in comments, `test_bulk_crc32` on CRC-capable and non-capable AArch64 CPUs, odd chunk sizes, and parity against software fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/bulk_crc32_aarch64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/bulk_crc32_riscv.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/bulk_crc32_riscv.c

## Purpose
`bulk_crc32_riscv.c` adds a RISC-V 64-bit zlib CRC32 accelerator using the Zbc carry-less multiply extension. It only accelerates the zlib polynomial path; CRC32C remains on the default implementation.

## Important APIs, types, and functions
Key helpers are `rv_clmul`, `rv_clmulh`, `rv_crc32_zlib_bitwise`, `rv_crc32_zlib_clmul`, and `pipelined_crc32_zlib`. Constants such as `RV_CRC32_CONST_R3`, `RV_CRC32_CONST_R4`, `RV_CRC32_CONST_R5`, and `RV_CRC32_POLY_TRUE_LE_FULL` drive folding and reduction. The constructor `init_cpu_support_flag` parses `/proc/cpuinfo` for `zbc` before assigning `pipelined_crc32_zlib_func`.

## Control flow
The accelerated CRC handles small buffers with a bitwise fallback, aligns the input to a 16-byte boundary, seeds two 64-bit lanes with the initial CRC, folds 16-byte blocks with `clmul` and `clmulh`, performs final reduction to a 32-bit CRC, and processes any remaining bytes bitwise. The pipelined wrapper calls that routine for one, two, or three chunks.

## State and persistence
The only persistent process state is the optional replacement of `pipelined_crc32_zlib_func`. Per-call state is local CRC lanes and pointers.

## Dependencies and integration points
It depends on a RISC-V 64-bit compiler that accepts inline `.option arch, +zbc`, `/proc/cpuinfo` availability, `bulk_crc32.h`, and the shared `bulk_crc32.c` function-pointer hooks. CMake selects this source on RISC-V builds.

## Risks and test signals
Risks include fragile feature detection by substring search, Linux-specific `/proc/cpuinfo` dependency, strict-aliasing/alignment concerns around 64-bit loads, absence of CRC32C acceleration, and correctness of polynomial constants. Test signals include software parity for varied lengths and alignments, systems with and without `zbc`, cross-checking zlib CRC vectors, and performance tests that confirm the constructor actually selects the accelerator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/bulk_crc32_riscv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/bulk_crc32_x86.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/bulk_crc32_x86.c

## Purpose
`bulk_crc32_x86.c` provides an x86 SSE4.2 hardware implementation for the CRC32C path in Hadoop's bulk CRC engine. It avoids requiring a global `-msse4.2` compiler flag by using inline assembly and runtime CPU detection.

## Important APIs, types, and functions
Important helpers include `cpuid`, inline `_mm_crc32_u64`, `_mm_crc32_u32`, `_mm_crc32_u16`, `_mm_crc32_u8` shims, and the 64-bit or 32-bit `pipelined_crc32c` implementation selected at compile time. The constructor checks `CPUID_FEATURES` bit `SSE42_FEATURE_BIT` and assigns `pipelined_crc32c_func` when available.

## Control flow
At load time, CPUID determines whether SSE4.2 CRC instructions are supported. During CRC calculation, the pipelined function processes one to three chunks in lockstep, using `crc32q` on 64-bit builds or `crc32l` on 32-bit builds for full machine words, then byte-level CRC instructions for the remainder.

## State and persistence
State is limited to the global `pipelined_crc32c_func` pointer in `bulk_crc32.c`. The implementation does not accelerate zlib CRC32 on x86.

## Dependencies and integration points
It depends on GCC-style inline x86 assembly, CPUID, `bulk_crc32.h`, and branch prediction macros. It is linked for x86 native builds and consumed through the shared `bulk_crc` dispatch.

## Risks and test signals
Risks include inline assembly constraints, PIC handling on 32-bit EBX, unaligned machine-word loads, only accelerating CRC32C, and CPU feature detection in virtualized environments. Test signals include 32-bit and 64-bit builds, CPUs with and without SSE4.2, `test_bulk_crc32` for many chunk sizes, and parity against the portable slicing-by-8 implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/bulk_crc32_x86.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/crc32_zlib_polynomial_tables.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/crc32_zlib_polynomial_tables.h

## Purpose
`crc32_zlib_polynomial_tables.h` contains the precomputed slicing-by-8 lookup tables for Hadoop's software CRC32 implementation using the zlib polynomial. It is data-only support for `bulk_crc32.c`.

## Important APIs, types, and functions
The file defines static table arrays named in the `CRC32_T8_*` family. Each table contains 256 32-bit constants for one slicing lane. There are no functions or exported symbols beyond header-scope table definitions.

## Control flow
There is no control flow in the header. `crc32_zlib_sb8` indexes these tables for eight-byte chunks and tail bytes to update the running CRC.

## State and persistence
The tables are immutable compiled data. They persist in the process image and are shared by all calls to the software zlib CRC path.

## Dependencies and integration points
The header is included directly by `bulk_crc32.c`. It must remain consistent with the reflected zlib CRC32 polynomial and the lookup order expected by the slicing-by-8 implementation.

## Risks and test signals
Risks are accidental table corruption, wrong table ordering, duplicate definitions if included in multiple translation units, and endian/layout mismatch with the algorithm. Test signals include known zlib CRC32 vectors, `test_bulk_crc32`, Java `DataChecksum` parity, and accelerator fallback comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/crc32_zlib_polynomial_tables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/crc32c_tables.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/crc32c_tables.h

## Purpose
`crc32c_tables.h` contains the precomputed slicing-by-8 lookup tables for the software CRC32C implementation. It supplies Castagnoli-polynomial data used when no hardware CRC32C accelerator is selected.

## Important APIs, types, and functions
The header defines static `CRC32C_T8_*` lookup-table arrays. Each table has 256 32-bit entries used by `crc32c_sb8` in `bulk_crc32.c`. It does not declare functions or mutable objects.

## Control flow
There is no executable control flow. The software CRC32C loop indexes these tables for the lower and higher words of each eight-byte slice and for final tail bytes.

## State and persistence
The table data is immutable compiled state loaded with the native library. It is safe for concurrent reads and has no lifecycle.

## Dependencies and integration points
It is included by `bulk_crc32.c` and indirectly backs `NativeCrc32` when CRC32C computation falls back to software. Hardware x86 and AArch64 code should match this table-based result exactly.

## Risks and test signals
Risks include generated-table errors, mismatch with the Castagnoli polynomial expected by Hadoop's `CHECKSUM_CRC32C`, and silent corruption because the table is trusted by every software computation. Test signals include CRC32C known-answer tests, cross-checks against Java implementations, `test_bulk_crc32`, and hardware/software parity on supported CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/crc32c_tables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/gcc_optimizations.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/gcc_optimizations.h

## Purpose
`gcc_optimizations.h` centralizes branch prediction macros for native Hadoop code. It lets performance-sensitive C code annotate likely and unlikely branches when compiled by GCC-compatible compilers.

## Important APIs, types, and functions
The header defines `likely(x)` and `unlikely(x)`. Under `__GNUC__`, they expand to `__builtin_expect`; otherwise they evaluate to the expression unchanged.

## Control flow
There is no runtime control flow. The macros influence compiler branch layout and prediction hints at compile time.

## State and persistence
The header has no state. It only affects generated code in translation units that include it.

## Dependencies and integration points
It is included by checksum JNI and CRC implementation files where hot loops and validation branches benefit from predictable layout. `org_apache_hadoop.h` separately defines fallback branch macros for broader native code.

## Risks and test signals
Risks are macro name collisions, double evaluation if passed expressions with side effects, and portability to non-GCC compilers. Test signals are native builds with GCC/Clang and non-GNU toolchains plus warning-free compilation of CRC code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/gcc_optimizations.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/yarn/server/nodemanager/windows_secure_container_executor.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/yarn/server/nodemanager/windows_secure_container_executor.c

## Purpose
`windows_secure_container_executor.c` implements the JNI bridge between YARN's `WindowsSecureContainerExecutor.Native` Java classes and privileged Windows `winutils` RPC operations. It creates tasks as users, performs elevated filesystem operations, and wraps Windows process handles in Java process-stub objects.

## Important APIs, types, and functions
Initialization functions are `initWsceNative`, `winutils_process_stub_init`, `winutils_process_stub_deinit`, and `winutils_process_stub_create`. Exported JNI operations include `createTaskAsUser0`, elevated kill/chown/mkdir/chmod/copy/create/delete methods, and process-stub methods `destroy`, `waitFor`, `resume`, `exitValue`, `dispose`, and `getFileDescriptorFromHandle`. Cached JNI state includes global class `wps_class`, constructor ID, and field IDs for process/thread handles and disposed state.

## Control flow
Initialization finds the nested `WinutilsProcessStub` class, stores a global reference, resolves fields and constructor, and cleans up on failure. Windows-only native methods convert Java UTF-16 strings to `LPCWSTR`, call `RpcCall_Winutils*` helpers, throw `IOException` via `throw_ioe` on nonzero Win32 status, and release all strings in a `done` block. Task creation receives process/thread/std stream handles, constructs a Java stub, and terminates/closes handles if Java object creation fails. Stub methods directly operate on cached handles.

## State and persistence
The file has process-global JNI metadata and per-process Windows handles stored in Java objects. It does not persist state, but it controls live OS processes and handle ownership. `dispose` marks Java stubs as disposed after closing process and thread handles.

## Dependencies and integration points
It depends on JNI, Windows APIs, `winutils.h`, `file_descriptor.h`, and YARN's Windows secure container executor classes. Unix builds expose the symbols but throw unsupported `IOException`s for platform-specific operations.

## Risks and test signals
Risks include global initialization races if `initWsceNative` is not called as intended, handle leaks for std stream handles after stub creation, double-close or use-after-dispose patterns, broad `TerminateProcess` behavior, and security-sensitive trust in winutils RPC authorization. Test signals include Windows container launch/kill lifecycle tests, elevated filesystem operation tests, Java finalization/dispose paths, failure injection for RPC calls and object construction, and Unix tests confirming unsupported-operation exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/yarn/server/nodemanager/windows_secure_container_executor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/yarn/server/nodemanager/windows_secure_container_executor.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/yarn/server/nodemanager/windows_secure_container_executor.h

## Purpose
`windows_secure_container_executor.h` declares the JNI support API for creating and managing YARN's Windows winutils process-stub objects.

## Important APIs, types, and functions
It defines `WINUTILS_PROCESS_STUB_CLASS` as the nested Java class name and declares `winutils_process_stub_init`, `winutils_process_stub_deinit`, and `winutils_process_stub_create`. The create function accepts process, thread, and standard stream handles as `jlong`s.

## Control flow
Callers initialize cached JNI metadata, create Java stub objects from native Windows handles, and deinitialize global refs on failure or shutdown. The header itself is declarative.

## State and persistence
The header declares functions that manage process-global JNI state in the `.c` file. No state is defined directly in the header.

## Dependencies and integration points
It requires JNI types and is included by `windows_secure_container_executor.c`. It couples native code to the exact Java nested class binary name.

## Risks and test signals
Risks include class-name drift if Java nested classes are renamed, signature mismatches for the constructor, and handle type truncation on unusual platforms. Test signals include Windows native build, `initWsceNative` lookup success, and Java integration tests that instantiate the native process stub.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/yarn/server/nodemanager/windows_secure_container_executor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org_apache_hadoop.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org_apache_hadoop.h

## Purpose
`org_apache_hadoop.h` is a shared native compatibility header for Hadoop JNI code. It supplies exception macros, dynamic-symbol loading helpers, platform-specific type/configuration glue, branch prediction fallbacks, class locking helpers, and retry-on-EINTR behavior.

## Important APIs, types, and functions
Key macros are `THROW`, `PASS_EXCEPTIONS`, `PASS_EXCEPTIONS_GOTO`, `PASS_EXCEPTIONS_RET`, `LOCK_CLASS`, `UNLOCK_CLASS`, and `RETRY_ON_EINTR`. Unix code gets `LOAD_DYNAMIC_SYMBOL` around `dlopen`/`dlsym`; Windows code defines Unicode settings, Windows headers, `do_dlsym`, and a Windows-specific `LOAD_DYNAMIC_SYMBOL`. `terror` creates formatted errors from `errno`.

## Control flow
Most constructs are macros that short-circuit on Java exceptions or retry interrupted syscalls. `LOAD_DYNAMIC_SYMBOL` attempts symbol resolution and throws Java exceptions on failure. `LOCK_CLASS` and `UNLOCK_CLASS` enter/exit Java monitor locks and propagate exceptions.

## State and persistence
The header has no own persistent state. It governs control-flow conventions and error propagation in many native translation units.

## Dependencies and integration points
It includes JNI and Hadoop config headers, and platform headers for Unix dynamic loading or Windows APIs. It is included by native security, checksum, loader, and YARN Windows executor code.

## Risks and test signals
Risks include macro side effects, inconsistent exception class names, monitor leaks if `UNLOCK_CLASS` is skipped, Windows macro substitutions such as `snprintf`, and divergence between this header's branch macros and `gcc_optimizations.h`. Test signals include native compilation on Unix and Windows, dynamic library load failure tests, JNI exception propagation tests, and EINTR retry coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org_apache_hadoop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/test/org/apache/hadoop/io/erasurecode/erasure_code_test.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/test/org/apache/hadoop/io/erasurecode/erasure_code_test.c

## Purpose
`erasure_code_test.c` is a native smoke and correctness test for Hadoop's ISA-L erasure coding bridge. It demonstrates encoder/decoder use and verifies that combinations of up to three missing data/parity units can be reconstructed.

## Important APIs, types, and functions
The test calls `build_support_erasurecode`, `load_erasurecode_lib`, `initEncoder`, `encode`, `initDecoder`, `decode`, and `dumpDecoder`. It uses `IsalEncoder`, `IsalDecoder`, data/parity unit arrays, and ISA-L headers such as `erasure_code.h`, `gf_util.h`, and `erasure_coder.h`.

## Control flow
The test skips successfully if native erasure coding is not compiled in. Otherwise it loads ISA-L, allocates six data units and three parity units of 1024 bytes, fills data with deterministic pseudo-random bytes, encodes parity, builds an `allUnits` array, and exhaustively iterates triples of erased indexes. For one, two, or three distinct erased units it nulls the inputs, decodes into output buffers, compares reconstructed bytes to backups, restores pointers, and fails on any mismatch.

## State and persistence
All state is heap memory local to the process. The test does not persist outputs. It intentionally leaks some allocations at process exit, which is acceptable for a short test binary but not a reusable library pattern.

## Dependencies and integration points
It depends on Hadoop's native ISA-L loader/wrapper and the external ISA-L erasure coding library. It is built and run by the native test configuration when ISA-L support is present.

## Risks and test signals
Risks include insufficient allocation failure checks, no cleanup, fixed coding parameters, and only deterministic random data. Passing the test signals basic encode/decode correctness for RS(6,3) with chunk size 1024 and up to three erasures, plus successful dynamic loading of the erasure coding library.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/test/org/apache/hadoop/io/erasurecode/erasure_code_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/test/org/apache/hadoop/util/test_bulk_crc32.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/test/org/apache/hadoop/util/test_bulk_crc32.c

## Purpose
`test_bulk_crc32.c` is the native unit and timing test for `bulk_crc`. It verifies that compute mode followed by verify mode succeeds for multiple CRC algorithms, data lengths, and bytes-per-checksum settings, then prints simple timing results.

## Important APIs, types, and functions
The test uses `bulk_crc`, `CRC32C_POLYNOMIAL`, `CRC32_ZLIB_POLYNOMIAL`, and `crc32_error_t`. Helpers are `testBulkVerifyCrc`, `timeBulkCrc`, and `EXPECT_ZERO`.

## Control flow
Each verification test allocates deterministic byte data, allocates enough checksum entries, computes checksums, verifies the same data, and frees memory. `main` covers 4096-byte buffers, 256-byte buffers with one-byte chunks, tiny one/two/seventeen-byte cases, and both CRC types where specified. It then runs two high-iteration timing loops over 16 KiB data with 512-byte chunks.

## State and persistence
The test owns temporary heap buffers and writes timing output to stdout/stderr. No state persists after process exit.

## Dependencies and integration points
It links against `bulk_crc32.c` and the selected architecture-specific CRC implementation in the native CMake test target. It validates both software and hardware-dispatched paths depending on host CPU support.

## Risks and test signals
Risks include no negative mismatch test, no malloc failure checks, and performance loops that can be long on slow machines. Passing output is a strong smoke signal for compute/verify consistency across chunk sizes and both polynomial constants, but it does not prove known-vector correctness independently of compute mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/test/org/apache/hadoop/util/test_bulk_crc32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/FSProtos.proto -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/FSProtos.proto

## Purpose
`FSProtos.proto` defines stable private protobuf records for common filesystem metadata. It encodes permissions, file status fields, and local filesystem path handles used by Hadoop common filesystem APIs.

## Important APIs, types, and functions
Messages are `FsPermissionProto`, `FileStatusProto`, and `LocalFileSystemPathHandleProto`. `FileStatusProto` defines `FileType` values `FT_DIR`, `FT_FILE`, `FT_SYMLINK` and `Flags` bits for ACL, encryption, erasure coding, and snapshots. Fields cover path, length, permission, owner, group, times, symlink target, replication, block size, encryption data, erasure-coding data, and flags.

## Control flow
This is a schema file. Serialization is handled by generated Java classes; Java converters populate optional metadata fields from `FileStatus`-like objects and consumers inspect presence/defaults during deserialization.

## State and persistence
The schema defines wire and serialized state. Optional fields allow sparse metadata. Field numbers are stable and comments reserve compatibility with HDFS status field IDs even though cross-serialization is not promised.

## Dependencies and integration points
It generates `org.apache.hadoop.fs.FSProtos` and integrates with `FileStatus`, `PBHelper`, and `LocalFileSystemPathHandle`. It is part of Hadoop's private stable protobuf surface.

## Risks and test signals
Risks include changing required fields or field numbers, misinterpreting unset optional fields as defaults, and incompatibility if encryption or EC opaque bytes change format. Test signals include protobuf compatibility tests, `FileStatus` round-trips, local path-handle serialization tests, and clients reading older messages without newer optional fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/FSProtos.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/GenericRefreshProtocol.proto -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/GenericRefreshProtocol.proto

## Purpose
`GenericRefreshProtocol.proto` defines the protobuf RPC contract for Hadoop's generic refresh mechanism, where callers request a named subsystem refresh and receive handler-specific statuses.

## Important APIs, types, and functions
Messages are `GenericRefreshRequestProto` with optional `identifier` and repeated `args`, `GenericRefreshResponseProto` with optional `exitStatus`, `userMessage`, and `senderName`, and `GenericRefreshResponseCollectionProto` with repeated responses. The service `GenericRefreshProtocolService` exposes `refresh`.

## Control flow
RPC clients serialize an identifier and arguments, the server dispatches to matching refresh handlers, and the response collection returns zero or more status records. The proto itself is declarative; generated service stubs implement call dispatch.

## State and persistence
There is no persistent state in the schema. It captures one refresh request and response set. Exit status and messages are optional, so callers must handle missing fields.

## Dependencies and integration points
It generates `org.apache.hadoop.ipc.proto.GenericRefreshProtocolProtos` and integrates with Hadoop IPC, admin CLIs, and refresh handler registries.

## Risks and test signals
Risks include ambiguous identifiers, handlers returning inconsistent exit statuses, and client assumptions about a single response. Test signals include client/server translator tests, refresh commands with no handlers and multiple handlers, argument preservation, and compatibility with older clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/GenericRefreshProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/GetUserMappingsProtocol.proto -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/GetUserMappingsProtocol.proto

## Purpose
`GetUserMappingsProtocol.proto` defines the protobuf RPC used by Hadoop tools to ask a daemon which groups are mapped to a given user.

## Important APIs, types, and functions
`GetGroupsForUserRequestProto` has required `user`. `GetGroupsForUserResponseProto` has repeated `groups`. `GetUserMappingsProtocolService` exposes `getGroupsForUser`.

## Control flow
A client sends a username, the server resolves group membership through its configured group mapping provider, and the response returns zero or more group names. The proto service is implemented by generated blocking stubs and Hadoop protocol translators.

## State and persistence
The wire state is one username and a repeated group list. The schema itself does not cache mappings; caching behavior lives in the server-side group mapping implementation.

## Dependencies and integration points
It generates `org.apache.hadoop.tools.proto.GetUserMappingsProtocolProtos` and integrates with `GetUserMappingsProtocol`, security group mapping providers, and admin/debugging tools.

## Risks and test signals
Risks include required-field compatibility, server-side identity canonicalization, empty group results, and exposure of group membership to unauthorized callers. Test signals include protocol translator tests, unknown user behavior, users with many groups, and authorization checks around group-mapping endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/GetUserMappingsProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/HAServiceProtocol.proto -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/HAServiceProtocol.proto

## Purpose
`HAServiceProtocol.proto` defines Hadoop's protobuf RPC contract for high-availability service control and health/status checks. It is used by HA admin tooling and failover controllers.

## Important APIs, types, and functions
Enums are `HAServiceStateProto` (`INITIALIZING`, `ACTIVE`, `STANDBY`, `OBSERVER`) and `HARequestSource` (`REQUEST_BY_USER`, forced user request, and `REQUEST_BY_ZKFC`). Messages include `HAStateChangeRequestInfoProto`, health monitor request/response, transition request/response pairs for active, standby, and observer, and `GetServiceStatusResponseProto` with state, readiness, and not-ready reason. The service exposes `monitorHealth`, `transitionToActive`, `transitionToStandby`, `transitionToObserver`, and `getServiceStatus`.

## Control flow
Clients issue health checks, status requests, or state transition requests carrying request-source metadata. Servers enforce HA semantics and return empty responses for successful transitions or status metadata for queries. Generated protobuf service stubs carry this contract over Hadoop IPC.

## State and persistence
The schema represents transient control-plane calls. Actual HA state is persisted or coordinated by the HA implementation, not by the proto. Required fields make transition request source and status state mandatory on the wire.

## Dependencies and integration points
It generates `org.apache.hadoop.ha.proto.HAServiceProtocolProtos` and integrates with `HAServiceProtocol`, `HAAdmin`, health monitors, and ZK failover controller code.

## Risks and test signals
Risks include changing enum values, missing observer support in older clients, incorrect handling of forced requests, and readiness fields being absent. Test signals include HA protocol translator tests, mixed-version clients, transitions from user and ZKFC sources, observer transition coverage, and health-monitor failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/HAServiceProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/IpcConnectionContext.proto -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/IpcConnectionContext.proto

## Purpose
`IpcConnectionContext.proto` defines metadata sent when a Hadoop IPC connection is established. It communicates user identity and target protocol before individual RPC calls are processed.

## Important APIs, types, and functions
`UserInformationProto` has optional `effectiveUser` and `realUser`. `IpcConnectionContextProto` has optional `userInfo` and optional `protocol`; field 1 is reserved by omission from older context usage.

## Control flow
During IPC setup, clients serialize the connection context after authentication/handshake framing. Servers use the user information for UGI/proxy-user context and the protocol field to bind the connection to a target RPC protocol.

## State and persistence
The context is per connection. It is not persisted independently, but it influences all calls multiplexed over that connection.

## Dependencies and integration points
It generates `org.apache.hadoop.ipc.protobuf.IpcConnectionContextProtos` and integrates with Hadoop IPC client/server connection setup, security, and proxy-user handling.

## Risks and test signals
Risks include missing user fields under simple/authenticated modes, proxy-user confusion between effective and real user, protocol mismatches, and compatibility around omitted/unknown fields. Test signals include secure and insecure IPC connection tests, proxy user tests, mixed-version context parsing, and protocol mismatch failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/IpcConnectionContext.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/ProtobufRpcEngine.proto -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/ProtobufRpcEngine.proto

## Purpose
`ProtobufRpcEngine.proto` defines the request header for Hadoop's original protobuf RPC engine. It identifies the target method, declaring protocol, and client protocol version for each RPC request.

## Important APIs, types, and functions
The single message is `RequestHeaderProto` with required `methodName`, required `declaringClassProtocolName`, and required `clientProtocolVersion`. It is generated into `org.apache.hadoop.ipc.protobuf.ProtobufRpcEngineProtos`.

## Control flow
For every protobuf-engine RPC, the client sends this header before the serialized protobuf request body. The server uses method name and declaring protocol to resolve the Java method and protocol implementation, while client protocol version participates in compatibility checks. Response headers are handled by `RpcHeader.proto`.

## State and persistence
The header is per RPC call. Required fields make malformed or incomplete call headers fail protobuf initialization/parsing.

## Dependencies and integration points
It is consumed by `ProtobufRpcEngine`, `ProtobufRpcEngine2` compatibility paths, Hadoop IPC server dispatch, and generated Java under `src/main/proto2-generated`.

## Risks and test signals
Risks include method-name drift, wrong declaring protocol for meta-protocol calls, required-field incompatibility, and generated-code skew with the proto. Test signals include RPC engine unit tests, protocol metadata calls, mixed client/server protocol versions, and generated Java regeneration diffs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/ProtobufRpcEngine.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/ProtobufRpcEngine2.proto -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/ProtobufRpcEngine2.proto

## Purpose
`ProtobufRpcEngine2.proto` defines the same per-call request header shape for Hadoop's newer protobuf RPC engine namespace. It supports the `ProtobufRpcEngine2` implementation while preserving the established method/protocol/version contract.

## Important APIs, types, and functions
The single `RequestHeaderProto` message has required fields `methodName`, `declaringClassProtocolName`, and `clientProtocolVersion`. It generates `org.apache.hadoop.ipc.protobuf.ProtobufRpcEngine2Protos`.

## Control flow
Clients using `ProtobufRpcEngine2` prepend this header to each protobuf request body. Servers dispatch using the method name and declaring protocol and validate protocol version compatibility.

## State and persistence
The message is transient per call. Required fields prevent partially initialized headers from being built by generated Java code.

## Dependencies and integration points
It integrates with `ProtobufRpcEngine2`, Hadoop IPC request deserialization, protocol translators, and RPC client utility code that selects the newer engine.

## Risks and test signals
Risks include divergence from the original engine header, mismatch between generated and handwritten RPC code, and mixed-engine compatibility issues. Test signals include engine2 RPC tests, backward compatibility tests with original engine clients where supported, meta-protocol calls, and generated-source checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/ProtobufRpcEngine2.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/ProtocolInfo.proto -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/ProtocolInfo.proto

## Purpose
`ProtocolInfo.proto` defines Hadoop's RPC meta-protocol for querying protocol versions and method signatures. It lets clients determine server capabilities across RPC kinds.

## Important APIs, types, and functions
Messages include `GetProtocolVersionsRequestProto`, `ProtocolVersionProto`, `GetProtocolVersionsResponseProto`, `GetProtocolSignatureRequestProto`, `GetProtocolSignatureResponseProto`, and `ProtocolSignatureProto`. The service `ProtocolInfoService` exposes `getProtocolVersions` and `getProtocolSignature`.

## Control flow
Clients ask for versions supported by a protocol or for method signature hashes for a specific protocol/rpc-kind pair. Servers return repeated version records or per-version method hash lists. This can be invoked as a meta-protocol over an existing RPC connection.

## State and persistence
The schema represents server capability metadata at request time. Version lists and method hashes are not persisted by the proto, though implementations may cache reflection results.

## Dependencies and integration points
It generates `org.apache.hadoop.ipc.protobuf.ProtocolInfoProtos` and integrates with `ProtocolMetaInfoPB`, RPC compatibility negotiation, and protocol translator support checks.

## Risks and test signals
Risks include stale method hash calculations, wrong `rpcKind` strings, incomplete version lists, and incompatibility if required fields change. Test signals include `isMethodSupported` tests, mixed-version protocol negotiation, meta-protocol calls over regular service connections, and reflection/signature regression tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/ProtocolInfo.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/RefreshAuthorizationPolicyProtocol.proto -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/RefreshAuthorizationPolicyProtocol.proto

## Purpose
`RefreshAuthorizationPolicyProtocol.proto` defines the protobuf RPC used to ask a Hadoop daemon to reload service authorization policy.

## Important APIs, types, and functions
The schema has empty request/response messages `RefreshServiceAclRequestProto` and `RefreshServiceAclResponseProto`. `RefreshAuthorizationPolicyProtocolService` exposes `refreshServiceAcl`.

## Control flow
An admin client sends the empty request; the server reloads authorization policy from configuration and returns an empty response or an RPC exception on failure. Generated service stubs handle transport.

## State and persistence
The proto carries no payload. The state change is external: server-side in-memory authorization policy is refreshed from configured sources.

## Dependencies and integration points
It generates `org.apache.hadoop.security.proto.RefreshAuthorizationPolicyProtocolProtos` and integrates with Hadoop service ACL refresh commands and server-side authorization managers.

## Risks and test signals
Risks include unauthorized callers triggering policy reloads, empty responses hiding partial reload failures, and compatibility around service naming. Test signals include admin CLI tests, authorization enforcement before/after refresh, failure-to-read-config behavior, and RPC authorization tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/RefreshAuthorizationPolicyProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/RefreshCallQueueProtocol.proto -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/RefreshCallQueueProtocol.proto

## Purpose
`RefreshCallQueueProtocol.proto` defines the RPC for refreshing an IPC server's call queue configuration without restarting the daemon.

## Important APIs, types, and functions
The schema contains empty `RefreshCallQueueRequestProto` and `RefreshCallQueueResponseProto` messages. The service `RefreshCallQueueProtocolService` exposes `refreshCallQueue`.

## Control flow
An administrative client invokes `refreshCallQueue`; the server reloads queue settings and swaps or reconfigures the call queue as its implementation allows. Transport-level success returns an empty response; failures surface as RPC exceptions.

## State and persistence
The proto carries no payload. Runtime state changes in the target IPC server's call queue. Persistent settings live in configuration files outside the message.

## Dependencies and integration points
It generates `org.apache.hadoop.ipc.proto.RefreshCallQueueProtocolProtos` and integrates with IPC server administration and call queue manager code.

## Risks and test signals
Risks include changing queues while calls are in flight, losing fairness/priority settings, unauthorized refresh calls, and empty response ambiguity. Test signals include call queue refresh integration tests, active-load refresh tests, authorization checks, and invalid configuration handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/RefreshCallQueueProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/RefreshUserMappingsProtocol.proto -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/RefreshUserMappingsProtocol.proto

## Purpose
`RefreshUserMappingsProtocol.proto` defines RPCs for refreshing cached user-to-group mappings and superuser proxy group configuration in Hadoop daemons.

## Important APIs, types, and functions
Messages are empty request/response pairs for `RefreshUserToGroupsMappings` and `RefreshSuperUserGroupsConfiguration`. The service `RefreshUserMappingsProtocolService` exposes `refreshUserToGroupsMappings` and `refreshSuperUserGroupsConfiguration`.

## Control flow
Admin clients invoke the desired refresh method. The server invalidates or reloads its group mapping cache or proxy-user group configuration and returns an empty response on success. Errors are represented as RPC exceptions.

## State and persistence
The proto carries no data, but it triggers mutation of server-side security caches. Persistent definitions remain in external configuration or OS identity services.

## Dependencies and integration points
It generates `org.apache.hadoop.security.proto.RefreshUserMappingsProtocolProtos` and integrates with `RefreshUserMappingsProtocol`, client/server PB translators, `Groups`, and proxy-user authorization code.

## Risks and test signals
Risks include unauthorized cache invalidation, stale mappings if refresh silently fails, race conditions with concurrent authorization checks, and ambiguity from empty success responses. Test signals include cache refresh tests, proxy-user configuration reload tests, RPC authorization checks, and concurrent lookup behavior during refresh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/RefreshUserMappingsProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/RpcHeader.proto -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/RpcHeader.proto

## Purpose
`RpcHeader.proto` defines Hadoop IPC framing metadata for requests, responses, tracing, caller context, retry/state tracking, router federation state, authorization headers, and SASL negotiation.

## Important APIs, types, and functions
Top-level `RpcKindProto` enumerates writable, protocol-buffer, and protocol-buffer2 RPC kinds. Messages include `RPCTraceInfoProto`, `RPCCallerContextProto`, `RpcRequestHeaderProto`, `RpcResponseHeaderProto`, and `RpcSaslProto`. Request fields include call ID, client ID, retry count, trace info, caller context, state ID, router federated state, and authorization header. Response fields include call ID, status, IPC version, exception data, error detail enum, client ID, retry count, state ID, and router state. SASL state covers negotiate/initiate/challenge/response/wrap and advertised auth methods.

## Control flow
Every IPC request and response uses these headers around the engine-specific payload. During authentication, `RpcSaslProto` drives the SASL handshake. During normal calls, request headers identify operation and call correlation; response headers return status or exception metadata.

## State and persistence
Headers are per packet/call. They carry transient correlation, retry, auth, trace, and federation metadata. State IDs reflect server/global state but are not persisted by the proto itself.

## Dependencies and integration points
It generates `org.apache.hadoop.ipc.protobuf.RpcHeaderProtos` and is central to Hadoop IPC client/server, retry cache behavior, tracing, router federation, authorization, and SASL authentication.

## Risks and test signals
Risks include enum value compatibility, required call/client IDs, leakage of authorization headers, large error messages, mismatched retry counts, and SASL state-machine bugs. Test signals include IPC compatibility tests, SASL auth suites, retry-cache tests, tracing propagation, router federation tests, and mixed-version client/server calls with unknown optional fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/RpcHeader.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/Security.proto -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/Security.proto

## Purpose
`Security.proto` defines stable protobuf records for Hadoop tokens, credentials, and delegation-token RPC payloads. It is shared by security-sensitive protocols that need to serialize token identifiers, passwords, kinds, services, and credential collections.

## Important APIs, types, and functions
Messages include `TokenProto`, `CredentialsKVProto`, `CredentialsProto`, `GetDelegationTokenRequestProto`, `GetDelegationTokenResponseProto`, `RenewDelegationTokenRequestProto`, `RenewDelegationTokenResponseProto`, `CancelDelegationTokenRequestProto`, and `CancelDelegationTokenResponseProto`. `TokenProto` requires identifier, password, kind, and service. Credential entries bind an alias to either a token or secret bytes.

## Control flow
Services serialize tokens and credentials for transfer or persistence. Delegation-token protocols use request/response messages to issue, renew, or cancel tokens, with success responses containing a token, new expiry time, or void marker.

## State and persistence
The schema can carry persisted credential material and live delegation-token state. Sensitive fields include token passwords and secret bytes, so transport/storage protections are external but critical.

## Dependencies and integration points
It generates `org.apache.hadoop.security.proto.SecurityProtos` and integrates with Hadoop `Token`, `Credentials`, delegation token secret managers, and multiple filesystem/service protocols.

## Risks and test signals
Risks include secret leakage through logs, compatibility issues around required token fields, ambiguous `CredentialsKVProto` entries containing both token and secret, and unsigned expiry interpretation. Test signals include token/credential round-trip tests, delegation token issue/renew/cancel tests, secure transport tests, and backward compatibility checks for serialized credentials.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/Security.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/TraceAdmin.proto -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/TraceAdmin.proto

## Purpose
`TraceAdmin.proto` defines the protobuf RPC contract for administering Hadoop tracing span receivers. It supports listing, adding, and removing receivers at runtime.

## Important APIs, types, and functions
Messages include empty `ListSpanReceiversRequestProto`, `SpanReceiverListInfo` with required `id` and `className`, `ListSpanReceiversResponseProto`, `ConfigPair`, `AddSpanReceiverRequestProto` with class name and config pairs, `AddSpanReceiverResponseProto` with receiver id, `RemoveSpanReceiverRequestProto` with id, and empty `RemoveSpanReceiverResponseProto`. The service `TraceAdminService` exposes `listSpanReceivers`, `addSpanReceiver`, and `removeSpanReceiver`.

## Control flow
An admin client lists existing receivers, requests construction of a receiver class with config key/value pairs, or removes a receiver by id. Server-side tracing code performs class loading and registry updates.

## State and persistence
The proto captures one admin operation. Runtime receiver registry state changes on add/remove. Persistence of receiver configuration, if any, is outside this schema.

## Dependencies and integration points
It generates `org.apache.hadoop.tracing.TraceAdminPB` and integrates with Hadoop tracing admin CLI, tracing subsystem, and RPC protocol translators.

## Risks and test signals
Risks include unsafe class loading from user-supplied class names, leaking configuration values, id collisions, removing active receivers, and authorization gaps. Test signals include trace admin protocol tests, add/remove/list lifecycle tests, invalid class/config handling, and admin authorization checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/TraceAdmin.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/ZKFCProtocol.proto -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/ZKFCProtocol.proto

## Purpose
`ZKFCProtocol.proto` defines the protobuf RPC contract for controlling a ZooKeeper Failover Controller. It supports ceding active leadership for a duration and requesting graceful failover.

## Important APIs, types, and functions
`CedeActiveRequestProto` has required `millisToCede`. `CedeActiveResponseProto`, `GracefulFailoverRequestProto`, and `GracefulFailoverResponseProto` are empty. `ZKFCProtocolService` exposes `cedeActive` and `gracefulFailover`.

## Control flow
Clients ask a ZKFC to step back from active election for the specified milliseconds or to coordinate graceful failover. The server performs coordination with HA state and ZooKeeper; success returns empty responses while failures surface as RPC exceptions.

## State and persistence
The proto carries a transient command. Actual failover coordination state lives in ZKFC and ZooKeeper, not in the message.

## Dependencies and integration points
It generates `org.apache.hadoop.ha.proto.ZKFCProtocolProtos` and integrates with Hadoop HA failover controllers, HA admin tooling, and `HAServiceProtocol`.

## Risks and test signals
Risks include invalid or extreme cede durations, unauthorized failover commands, race conditions with automatic election, and compatibility around empty messages. Test signals include ZKFC protocol translator tests, graceful failover integration tests, cede-active timing tests, and authorization checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/ZKFCProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto2-generated/org/apache/hadoop/ipc/protobuf/ProtobufRpcEngineProtos.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto2-generated/org/apache/hadoop/ipc/protobuf/ProtobufRpcEngineProtos.java

## Purpose
`ProtobufRpcEngineProtos.java` is generated Java code for `ProtobufRpcEngine.proto`. It provides the runtime protobuf representation of the original Hadoop protobuf RPC request header.

## Important APIs, types, and functions
The outer class is `org.apache.hadoop.ipc.protobuf.ProtobufRpcEngineProtos`. The main generated type is `RequestHeaderProto`, an extendable protobuf message with required fields `methodName`, `declaringClassProtocolName`, and `clientProtocolVersion`. It includes `RequestHeaderProtoOrBuilder`, parser singleton `PARSER`, many `parseFrom`/`parseDelimitedFrom` overloads, `newBuilder`, `toBuilder`, `Builder`, descriptors, field accessor table, `registerAllExtensions`, and static `descriptorData`.

## Control flow
Parsing reads tags 1, 2, and 3 from a `CodedInputStream`, stores unknown fields, and preserves extensions. `isInitialized` fails until all three required fields and extensions are initialized. Builders set bit fields as required values are provided, build partial or fully initialized messages, merge unknown and extension fields, and throw on missing required fields when `build()` is used. Serialization writes set fields, extension data, and unknown fields in protobuf order.

## State and persistence
Instances are immutable protobuf messages after construction. Builders hold mutable field state and bit masks. Static descriptors and the default instance are process-wide generated metadata. Serialized messages are the wire/persistent representation used by Hadoop IPC.

## Dependencies and integration points
It depends on the Google protobuf Java runtime and is consumed by `ProtobufRpcEngine`, server-side request deserialization, and compatibility paths in `ProtobufRpcEngine2`. The source is excluded from some static-analysis/license checks as generated code.

## Risks and test signals
Risks include generated source becoming stale relative to `ProtobufRpcEngine.proto`, protobuf runtime version incompatibility, required-field parse failures for malformed clients, and manual edits being overwritten. Test signals include regenerating from the proto with no semantic diff, RPC engine request/response tests, malformed header parsing tests, and mixed-version protocol negotiation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto2-generated/org/apache/hadoop/ipc/protobuf/ProtobufRpcEngineProtos.java -->
