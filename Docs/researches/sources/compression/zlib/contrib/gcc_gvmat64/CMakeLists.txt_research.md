# sources/compression/zlib/contrib/gcc_gvmat64/CMakeLists.txt

Purpose: integrates the AMD64 longest-match assembly object into the zlib CMake build.

Important APIs/types/functions: enables `ASM_MASM` for MSVC with CMake policy `CMP0194` on newer CMake, otherwise enables generic `ASM`; creates object library `zlib_gvmat64` from `gvmat64.S`; injects its object files into `zlib` and/or `zlibstatic`.

Control flow: language selection happens first based on compiler. The object library is always declared. Conditional `target_sources()` calls add `$<TARGET_OBJECTS:zlib_gvmat64>` only when shared or static zlib targets are enabled.

State and persistence: no runtime state. It mutates the CMake target graph.

Dependencies/integration: depends on parent build variables `ZLIB_BUILD_SHARED`, `ZLIB_BUILD_STATIC`, and target names `zlib`/`zlibstatic`. It assumes `gvmat64.S` can be assembled for the selected platform.

Risks: this file does not itself check CPU architecture or structure-offset compatibility. Enabling the object on an unsupported ABI can break build or runtime compression. MSVC assembly handling for `.S` may depend on generator and CMake version.

Test signals: build success and zlib compression tests are the primary signals; there is no local unit test for this CMake fragment.
