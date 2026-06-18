# sources/compression/zlib/contrib/crc32vx/CMakeLists.txt

Purpose: CMake feature probe and target integration for IBM s390x vector-accelerated CRC-32.

Important APIs/settings: uses `CHECK_C_SOURCE_COMPILES`, `ZLIB_WITH_CRC32VX`, `HAS_S390X_SUPPORT`, `HAS_S390X_VX_SUPPORT`, `HAS_Z13_S390X_VX_SUPPORT`, `VGFMAFLAG`, `target_sources`, `target_compile_definitions`, and `set_source_files_properties`.

Control flow: first verifies `__s390x__`, then checks vector intrinsics with `-fzvector` for Clang or `-mzarch` otherwise. If the first check fails, retries with `-march=z13`. On success, adds `crc32_vx.c` and header to shared/static zlib targets, defines `HAVE_S390X_VX=1`, and applies compile options to the source.

State and persistence: modifies CMake target source lists, compile definitions, and source compile options.

Dependencies and integration: included via contrib feature dispatch. Requires root zlib targets to already exist, compiler support for `<vecintrin.h>`, and s390x vector facility.

Risks: compile definitions are added PUBLIC, so consumers see `HAVE_S390X_VX=1`; that may be intentional for headers but broadens ABI/compile surface. `list(APPEND VGFMAFLAG "-march=z13")` makes a CMake list, which may need correct expansion as compile options.

Test signals: contrib CI enables `ZLIB_WITH_CRC32VX`; actual vector compilation is only meaningful on s390x-capable toolchains.
