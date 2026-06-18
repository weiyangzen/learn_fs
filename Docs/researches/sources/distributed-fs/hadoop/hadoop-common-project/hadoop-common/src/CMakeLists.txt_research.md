# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/CMakeLists.txt

Purpose: CMake build script for Hadoop Common native code and native tests. It configures JNI, probes compression/crypto/native acceleration libraries, generates `config.h`, builds the dual `hadoop` shared library, sets RPATH behavior, and creates the CRC32 test binary. The source was read as a complete 259-line file.

Important APIs/functions: CMake entry points include `cmake_minimum_required`, `include(HadoopCommon)`, `include(HadoopJNI)`, `find_package(ZLIB REQUIRED)`, `find_package(BZip2 QUIET)`, `find_library` for ISA-L, PMDK, and OpenSSL/libcrypto, `check_c_source_compiles` for `EVP_aes_256_ctr`, `check_function_exists`, `check_library_exists`, `configure_file`, `hadoop_add_dual_library`, `hadoop_target_link_dual_libraries`, `hadoop_dual_output_directory`, `set_target_properties`, and `add_executable` for native tests.

Control flow: the script requires `GENERATED_JAVAH`, initializes JNI, then probes zlib as mandatory and bzip2, ISA-L, PMDK, and OpenSSL as optional unless their `REQUIRE_*` variables demand failure. It selects a hardware CRC32 source for x86, aarch64, or RISC-V, checks platform APIs such as `sync_file_range` and `posix_fadvise`, configures include paths, emits `config.h`, builds `libhadoop` from native IO, compression, crypto, domain socket, security, and CRC sources, then links `dl` and JVM libraries where needed.

State and persistence: build outputs live in the CMake/Maven target tree, including generated `config.h`, `libhadoop.so` or platform equivalent, `target/usr/local/lib`, and `test_bulk_crc32`. No runtime persistence is owned by CMake, but compile-time feature state is persisted into `config.h`.

Dependencies and integration: integrates with Maven's `cmake-compile` goal, generated JNI headers, Hadoop native C sources, zlib, optional bzip2, ISA-L, PMDK, OpenSSL, `dl`, JVM libraries, and `src/config.h.cmake`. Java native loaders use the configured library names and feature macros at runtime.

Risks: optional dependencies can produce different native feature sets across machines. Required-library flags intentionally fail the build, so CI matrices must set them consistently. OpenSSL detection depends on a compile probe for `EVP_aes_256_ctr`. RPATH uses `$ORIGIN` only for Linux/SunOS and may need extra RPATH for nonstandard deployments. A typo-like variable name `BULK_CRC_ARCH_SOURCE_FIlE` is internally consistent but easy to misuse in future edits.

Test signals: CMake configure output for found/missing native libraries, Maven `-Pnative` build, `test_bulk_crc32`, optional `erasure_code_test`, NativeLibraryChecker behavior, and Java tests that exercise native compression, native IO, domain sockets, and crypto loading.
