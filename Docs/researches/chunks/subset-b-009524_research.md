# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/configure lines 1-9179

## Purpose

This chunk is the first 9,179 lines of a GNU Autoconf 2.65 generated `configure` script for the e2fsprogs library tree embedded under `xfstests-bld`. Its job is to normalize the shell environment, parse user configure options, discover the source/build/host environment, probe the C compiler and platform features, select e2fsprogs library/program build modes, and populate `confdefs.h`, `config.log`, cache variables, and substitution variables that later `config.status` uses to generate build files.

The chunk starts at script bootstrap and ends inside the gettext/NLS setup after assigning `INTLLIBS="$LIBINTL"`. The actual `config.status` generation and later e2fsprogs-specific checks continue after this chunk.

## High-Level Structure

- Lines 1-535: Autoconf/M4sh bootstrap. The script establishes POSIX-ish shell behavior, finds a better shell when required, sanitizes environment variables, defines portable helpers, determines `as_me`, initializes echo/link/mkdir/test helpers, and opens descriptors used for status output.
- Lines 538-826: package and configure metadata. It initializes package identity, default includes, output substitution variables, file substitution variables, supported `--enable`/`--with` options, and precious environment variables.
- Lines 829-1564: command-line parser and help/version handling. It accepts GNU directory options, build/host/target aliases, e2fsprogs feature switches, package switches, `VAR=VALUE` assignments, and source directory resolution.
- Lines 1570-2244: reusable C probe functions. These helpers compile, link, preprocess, run, and check headers/types/functions/members/declarations for later cached tests.
- Lines 2245-2587: `config.log`, site/cache loading, and cache consistency checks. It records platform details, command-line arguments, output variables, file substitutions, and validates that precious variables did not change across cached runs.
- Lines 2591-4288: main body initialization, e2fsprogs version extraction, canonical build/host resolution, C compiler selection, C compiler sanity, GNU C and C89 detection, and C preprocessor discovery.
- Lines 4295-4556: core text/tool/header probes. It finds usable `grep`/`egrep`, checks ANSI headers and default system headers, and determines whether Linux headers are available.
- Lines 4567-5557: e2fsprogs build-policy options. It sets compiler flags, library extensions, root prefix behavior, maintainer/symlink/verbose flags, htree/compression/debug options, shared/profile/checker library modes, private/external uuid and blkid selection, optional programs, TLS, uuidd, and library makefile path variables.
- Lines 5559-6004: package identity override for gettext tooling plus make/install/NLS tool discovery. It sets `PACKAGE=e2fsprogs`, then `VERSION=0.14.1` for gettext macro compatibility, probes make/install helpers, initializes `MKINSTALLDIRS`, and searches gettext tools (`msgfmt`, `gmsgfmt`, `xgettext`, `msgmerge`).
- Lines 6007-7545: archive/runtime/compiler portability probes. It finds `ranlib`, checks `-lcposix`, C keywords/types, integer/printf/alloca/mmap/glibc behavior, inttypes/stdint details, computes `SIZE_MAX` if needed, locates linker `ld`, detects GNU ld, and runs `config.rpath`.
- Lines 7554-9179: libiconv and gettext library resolution. It honors `--with-libiconv-prefix`, resolves iconv library/include/rpath flags, checks `iconv()` and its declaration, probes locale/code-set support and bison, evaluates NLS/gettext choices, searches libc or external `libintl`, falls back to included gettext when needed, and sets NLS-related substitution variables.

## Important Functions and Probe APIs

- `as_fn_unset`, `as_fn_set_status`, `as_fn_exit`, `as_fn_mkdir_p`, `as_fn_append`, `as_fn_arith`, `as_fn_error`: Autoconf shell support functions used throughout the script for portable cleanup, error handling, arithmetic, appending, directory creation, and exits.
- `ac_fn_c_try_compile`, `ac_fn_c_try_link`, `ac_fn_c_try_cpp`, `ac_fn_c_try_run`: central test runners. They create `conftest.*`, execute compiler/preprocessor/link/run commands, write diagnostics into `config.log` on fd 5, clean temporary artifacts, and return success via shell status.
- `ac_fn_c_check_header_mongrel` and `ac_fn_c_check_header_compile`: header checks. The "mongrel" variant compares compiler and preprocessor results and warns when they disagree.
- `ac_fn_c_check_type`, `ac_fn_c_check_func`, `ac_fn_c_compute_int`, `ac_fn_c_check_member`, `ac_fn_c_check_decl`: generic type/function/integer/member/declaration checks. Later code uses these to define `HAVE_*`, replacement type macros, and cache variables.

These are generated shell functions rather than project-authored APIs, but they define the execution model for all subsequent platform detection.

## Important Variables and Build Surface

- `ac_subst_vars` and `ac_subst_files` are the contract with generated make/config files. This chunk registers variables such as `LIBUUID`, `LIBBLKID`, `DEBUGFS_CMT`, `FSCK_PROG`, `USE_NLS`, `LIBINTL`, `LIBICONV`, `E2FSPROGS_VERSION`, `root_prefix`, `MAKEFILE_ELF`, and `PUBLIC_CONFIG_HEADER`.
- `ac_user_opts` defines the accepted public configure switches. e2fsprogs-specific switches include `--enable-elf-shlibs`, `--enable-bsd-shlibs`, `--enable-profile`, `--enable-checker`, `--enable-libuuid`, `--enable-libblkid`, `--enable-debugfs`, `--enable-resizer`, `--enable-fsck`, `--enable-tls`, `--enable-uuidd`, and `--enable-nls`.
- `confdefs.h` accumulates compile-time defines such as `STDC_HEADERS`, `HAVE_*` headers/functions, `ENABLE_HTREE`, `CONFIG_TESTIO_DEBUG`, `CONFIG_BUILD_FINDFS`, `TLS`, `USE_UUIDD`, `HAVE_ICONV`, `ENABLE_NLS`, `HAVE_GETTEXT`, and `HAVE_DCGETTEXT`.
- `config.log` is the persistent diagnostic log for configure probes. It captures platform info, PATH entries, compiler stderr, failed programs, cached values, output variables, file substitutions, and `confdefs.h`.
- `config.cache` is optional and defaults to disabled (`/dev/null`). When enabled, the script validates precious variables (`CC`, `CFLAGS`, `LDFLAGS`, `LIBS`, `CPPFLAGS`, `CPP`, `PKG_CONFIG`, aliases) against prior cached values.

## Control Flow

1. Bootstrap normalizes shell behavior, echo behavior, path separators, stdin/stdout descriptors, and temporary-file cleanup.
2. Argument parsing maps supported options into shell variables and records unknown options for warnings or fatal errors depending on `--enable-option-checking`.
3. Source discovery locates `version.h` as `ac_unique_file`; failure to find it aborts configure.
4. `config.log` is opened and a trap is installed so exits and interrupts write cache/output summaries and remove `conftest*`, `confdefs*`, and configured cleanup files.
5. The main script extracts `E2FSPROGS_VERSION` and release date from `version.h`, canonicalizes build and host triplets via `config.guess`/`config.sub`, and sets `build_cpu/vendor/os` and `host_cpu/vendor/os`.
6. Compiler discovery chooses prefixed tools first for cross builds, then `gcc`, `cc`, and `cl.exe`, rejecting unusable compilers and warning when unprefixed tools are used during cross-compilation.
7. Compile/link/preprocess sanity checks establish `EXEEXT`, `OBJEXT`, `GCC`, default `CFLAGS`, C89 mode, and `CPP`.
8. System header and tool checks define the baseline compilation environment and decide whether bundled Linux headers must be included.
9. e2fsprogs feature switches set comment variables, library names, makefile fragment paths, and compile-time defines that control which libraries/programs get built.
10. gettext/libiconv support probes resolve host tools, library paths, rpath flags, and fallback paths for included gettext.

## State and Persistence Behavior

- Persistent generated outputs in this chunk are `config.log`, `confdefs.h`, optional `config.cache`, temporary `conftest.*` files, and temporary helper files such as `conftest.make`, `conftest.mmap`, and `conftest.txt`.
- The script mutates many shell globals (`LIBS`, `CPPFLAGS`, `LDFLAGS`, `CC`, `CFLAGS`, `LIBINTL`, `LIBICONV`) during probes, generally saving/restoring when a probe should not leak flags. Link checks temporarily prepend candidate libraries.
- Cache variables named `ac_cv_*`, `gt_cv_*`, `am_cv_*`, `jm_ac_cv_*`, and `bh_cv_*` persist probe results when caching is enabled. These cached answers can bypass later compile/run checks.
- `confdefs.h` is append-only within the configure run. Once a feature is detected or enabled, this chunk appends the relevant `#define`.
- Comment variables like `ELF_CMT`, `BSDLIB_CMT`, `PROFILE_CMT`, `CHECKER_CMT`, `DEBUGFS_CMT`, `UUID_CMT`, `BLKID_CMT`, and `UUIDD_CMT` are build-file gates; empty means enabled and `#` means commented out.

## Dependencies and Integration Points

- Requires standard shell tools and Autoconf auxiliary scripts: `config/install-sh` or equivalent, `config/config.guess`, `config/config.sub`, and later `config/config.rpath`.
- Reads `${srcdir}/version.h` for e2fsprogs version/date metadata.
- Integrates with C toolchain and linker discovery through `CC`, `CPP`, `LD`, `RANLIB`, `CFLAGS`, `CPPFLAGS`, `LDFLAGS`, and `LIBS`.
- Uses `pkg-config` when the user disables private `libuuid` or `libblkid`; it requires at least pkg-config 0.9.0 and uses `pkg-config --libs`/`--static --libs`.
- Resolves shared library fragments under `${srcdir}/lib/Makefile.elf-lib`, `Makefile.solaris-lib`, `Makefile.bsd-lib`, `Makefile.darwin-lib`, `Makefile.profile`, `Makefile.checker`, and `Makefile.library`.
- NLS integration depends on gettext tools (`msgfmt`, `gmsgfmt`, `xgettext`, `msgmerge`), optional bison, iconv/libiconv, libintl/gettext, locale headers, and `po`/`intl` build directories.

## Risks and Edge Cases

- This is generated code; direct manual edits are fragile because regeneration from `configure.ac` and macro inputs can overwrite changes.
- Cross-compilation can force guesses or conservative failures for run-time tests (`mmap`, stack direction, POSIX printf, divide-by-zero signal behavior). Cached answers may be needed for unusual targets.
- `VERSION` is deliberately reset from `E2FSPROGS_VERSION` to `0.14.1` before gettext macros emit `PACKAGE`/`VERSION` defines. This is surprising and may confuse consumers expecting package version consistency.
- Disabling private `libuuid`/`libblkid` requires working `pkg-config` and linkable external libraries; otherwise configure aborts.
- `--with-diet-libc` rewrites `CC` to `diet cc -nostdinc` and disables TLS by default, which can interact badly with later compiler and header checks.
- The linker/rpath logic sources `.la` files and executes `config.rpath` output. It assumes these build-tree/support files are trusted.
- `USE_NLS=yes` can still become `no` if neither preinstalled nor included gettext is usable. Conversely, included gettext changes `LIBINTL` to `${top_builddir}/intl/libintl.a` and removes `-lintl` from `LIBS`.
- Header checks intentionally warn and proceed when preprocessor and compiler disagree; downstream code may compile with the compiler result even when preprocessing looked broken.

## Test Signals

- Successful configure output includes version/date messages, build/host triplets, compiler/preprocessor results, feature enable/disable messages, and NLS/gettext source messages.
- `config.log` is the primary debugging artifact for failed probes; failed C programs are printed there with `| ` prefixes.
- Key positive signals include generated defines in `confdefs.h`: `STDC_HEADERS`, `ENABLE_HTREE`, `CONFIG_TESTIO_DEBUG`, `CONFIG_BUILD_FINDFS`, `USE_UUIDD`, `HAVE_ICONV`, `ENABLE_NLS`, `HAVE_GETTEXT`, and `HAVE_DCGETTEXT`.
- Key negative/abort signals include missing `version.h`, missing auxiliary scripts, no acceptable C compiler, failing C preprocessor sanity, missing external uuid/blkid when private libraries are disabled, no acceptable `ld`, and cache corruption from changed precious variables.
- Feature-specific assertions can be tested by running configure with switches such as `--disable-libuuid`, `--disable-libblkid`, `--enable-elf-shlibs`, `--enable-bsd-shlibs`, `--disable-nls`, `--with-libiconv-prefix=DIR`, and inspecting `config.log`, `confdefs.h`, and substituted `MCONFIG`/makefile values after the full script completes.
