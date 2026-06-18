# sources/compression/zstd/programs/Makefile

## Purpose
`programs/Makefile` builds the zstd command-line utilities from the libzstd sources and CLI sources. It provides default release builds, feature-detected builds with optional compression-format support, variant binaries with reduced capabilities, profile-guided optimization, manpage generation, dependency tracking, install/uninstall targets, and Windows resource handling.

## Important targets, variables, and rules
- Source aggregation imports `../lib/libzstd.mk` and derives `ZSTDLIB_COMMON_SRC`, `ZSTDLIB_COMPRESS_SRC`, `ZSTDLIB_DECOMPRESS_SRC`, `ZDICT_SRC`, `ZSTDLEGACY_SRC`, `ZSTDLIB_FULL_SRC`, local object lists, CLI source/object lists, and `ZSTD_ALL_SRC`/`ZSTD_ALL_OBJ`. Sources are sorted for reproducible builds.
- Platform variables define `EXT`, `RES64_FILE`, `RES32_FILE`, and `RES_FILE` for Windows executables and resources.
- Feature probes create temporary `have_pthread.c`, `have_zlib.c`, `have_lzma.c`, and `have_lz4.c` programs to decide `THREAD_CPP`/`THREAD_LD`, `ZLIBCPP`/`ZLIBLD`, `LZMACPP`/`LZMALD`, and `LZ4CPP`/`LZ4LD`.
- Main targets include `all`, `allVariants`, `zstd`, `zstd-release`, `zstd32`, `zstd-nolegacy`, `zstd-nomt`, `zstd-nogz`, `zstd-noxz`, `zstd-dll`, `zstd-pgo`, `zstd-small`, `zstd-frugal`, `zstd-decompress`, `zstd-compress`, `zstd-dictBuilder`, and `zstdmt`.
- Build caching is controlled by `SET_CACHE_DIRECTORY` and recursive `make`: when `BUILD_DIR` is unset, `zstd` reinvokes make with `BUILD_DIR=obj/$(HASH_DIR)` and a captured flag/source environment; when set, objects are built under that cache directory and then copied to the top-level `zstd` executable only if hash comparison shows the binary differs.
- Pattern rules generate `.d` dependency files with `-MMD -MP`, build `.c` and `.S` files into `$(BUILD_DIR)`, and include generated dependency files when present.
- Maintenance targets include `clean`, `man`, `clean-man`, `preview-man`, `generate_res`, `list`, `install`, and `uninstall`.

## Control flow and state behavior
The default goal is `zstd-release`, which disables backtrace flags and builds `zstd`. A normal `zstd` build first accumulates feature macros and link libraries, then either recursively selects a cache directory or links `$(BUILD_DIR)/zstd` from all objects. After linking, optional hash comparison avoids rewriting the top-level binary if content has not changed, reducing timestamp churn.

The feature-detection flow is side-effectful but short-lived: each probe writes a small C file in the programs directory, compiles it with relevant libraries, removes the executable if successful, echoes `1` or `0`, and removes the probe source. The resulting `HAVE_*` variables drive compile definitions, link flags, and diagnostic messages. Thread detection accepts either a successful pthread probe or Windows.

Variant targets modify `CPPFLAGS`, `CFLAGS`, `LDFLAGS`, source lists, or support macros before depending on a build rule. For example `zstd-small` and `zstd-frugal` compile a minimal source set with `ZSTD_NOBENCH`, `ZSTD_NODICT`, `ZSTD_NOTRACE`, and no legacy support; `zstd-compress` and `zstd-decompress` split compressor-only and decompressor-only source sets; `zstd-nolegacy` removes legacy format support; and `zstd-nomt`, `zstd-nogz`, and `zstd-noxz` override detected support variables before invoking the normal `zstd` target.

Install flow is guarded by an OS whitelist inherited through `INSTALL_OS_LIST`/`UNAME`. It builds `zstd-release` only if `zstd` is absent, creates binary and man directories, installs the binary, script wrappers, symlinks, and man pages, and provides a matching uninstall target.

## Dependencies and integration points
This Makefile depends on variables and source lists from `../lib/libzstd.mk`, compiler/linker variables such as `CC`, `FLAGS`, `CPPFLAGS`, `CFLAGS`, `LDFLAGS`, `LDLIBS`, utility variables such as `GREP`, `CP`, `RM`, `LN`, `HASH`, `HASH_DIR`, and environment/platform variables including `OS`, `UNAME`, `BACKTRACE`, `PROFILE_WITH`, and install paths. Optional external libraries are pthread, zlib, liblzma, and liblz4. Manpage generation depends on `ronn` and `sed`; Windows resource generation depends on `windres`.

The file integrates CLI sources in `programs/` with libzstd implementation sources in `lib/`. It also provides user-facing packaging hooks by installing `zstd`, `zstdcat`, `unzstd`, `zstdmt`, `zstdless`, `zstdgrep`, and manpages.

## Risks and edge cases
- Feature probes write temporary files in the source directory, so interrupted builds can leave probe artifacts. The recipe removes sources after each probe, but `clean` only lists `have_zlib` explicitly and relies on normal cleanup for other tmp/probe files.
- Recursive build caching depends on `HASH_DIR` and flag propagation. Missing or unstable hashing can cause unnecessary rewrites or stale-object confusion if source lists/flags are not represented in the cache key upstream.
- Optional-library detection uses compile/link probes at make-evaluation time. Cross-compilation, unusual sysroots, or compilers that cannot execute the probe assumptions may mis-detect capabilities.
- `zstd32` hardcodes `-m32`, which fails without a 32-bit toolchain.
- Some variant link recipes place flags and libraries differently from the main target; strict linkers may be sensitive to argument order.
- `clean` removes broad patterns such as `tmp*`, `result*`, `dictionary`, and `*.zst` in the programs directory, so users should not keep unrelated artifacts there.
- Install rules rely on symlink behavior and OS whitelist logic; Windows paths and packaging flows use different conventions.

## Test signals
Useful validation includes `make -C sources/compression/zstd/programs zstd-release`, `make allVariants`, targeted builds such as `zstd-small`, `zstd-compress`, `zstd-decompress`, `zstd-nomt`, and `zstd-nolegacy`, dependency-file rebuild checks after touching headers, optional-library detection runs with `HAVE_ZLIB=0`/`HAVE_LZMA=0`/`HAVE_LZ4=0`, `make clean`, `make man` where `ronn` is available, and smoke tests invoking the resulting CLI for compress/decompress round trips and `zstd -b` benchmark execution. Cross-platform signals include Windows resource builds and install/uninstall dry runs under supported Unix-like systems.
