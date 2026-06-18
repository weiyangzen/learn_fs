# sources/test-tools/xfstests-bld/fstests-bld/popt/configure lines 9376-17882

## Purpose

This chunk is the middle and largest generated section of the GNU Autoconf 2.63 `configure` script for `popt` 1.16. It continues the libtool setup that began in the previous chunk, finishes the host/linker/dynamic-loader model used to generate the `libtool` helper script, runs `popt` feature checks for large-file support, headers, functions, version-script support, gcov instrumentation, NLS/gettext, libiconv, and libintl, then starts writing the generated `config.status` script.

The range begins immediately after the hard-link lock probe and ends while emitting the `libtool` `CONFIG_COMMANDS` body into `config.status`, just after the generated libtool header and the `available_tags=""` assignment. The actual completion of the `libtool` command, gettext `po-directories` command, `config.status` execution, and recursive subdirectory handling are in the following chunk.

## High-Level Structure

- Lines 9376-9382: Completes the libtool compiler lock decision. If hard-link locking works while compiler `-c -o` support is missing, `need_locks=warn`; otherwise locking is disabled.
- Lines 9387-11398: Computes the libtool shared-library linker recipe for the active C compiler and host. It initializes archive/linking variables, splits GNU ld from non-GNU ld behavior, and fills host-specific commands for AIX, AmigaOS, BeOS, Cygwin/MinGW, Interix, Linux/GNU, NetBSD, Solaris, SCO/UnixWare, SunOS, Darwin, FreeBSD, HP-UX, IRIX, OSF, QNX, and other System V families.
- Lines 11400-11520: Detects dynamic linker characteristics and library hardcoding policy. It derives library naming rules, shared-library suffixes, runtime path environment variables, `finish_cmds`, system library search paths, whether `shlibpath` overrides embedded runpaths, and whether `libtool` must relink for installed paths.
- Lines 11530-12340: Probes `dlopen` support. Depending on host it checks `load_add_on`, `LoadLibrary`, `dlopen`, `dyld`, `shl_load`, `dld_link`, and candidate libraries such as `-ldl`, `-ldld`, and `-lsvld`; when possible it also tests whether a program can `dlopen` itself and whether that still works for static executables.
- Lines 12346-12452: Finalizes libtool library-mode toggles. It detects whether library stripping is possible, reports shared/static build enablement, applies AIX namespace restrictions, and appends `libtool` to `ac_config_commands`.
- Lines 12456-12862: Performs C and large-file portability checks. It checks whether `$CC` needs `-traditional`, whether large files require special compiler flags, `_FILE_OFFSET_BITS=64`, or `_LARGE_FILES=1`, and defines matching preprocessor macros in `confdefs.h`.
- Lines 12873-13325: Runs `popt` header and library capability checks. It finds the library containing `strerror`, decides whether prototypes are available, checks `in string.h`, checks headers including `float.h`, `fnmatch.h`, `glob.h`, `langinfo.h`, `libintl.h`, `mcheck.h`, and `unistd.h`, then sets the Automake conditional for linker version scripts.
- Lines 13326-13598: Handles `--enable-build-gcov`, `setreuid`, and function availability. It may append `-fprofile-arcs -ftest-coverage` to `CFLAGS`, falls back to `-lc -lucb` for `setreuid` on legacy systems, and defines `HAVE_*` macros for `getuid`, `geteuid`, `iconv`, `mtrace`, `__secure_getenv`, `setregid`, `stpcpy`, `strerror`, `vasprintf`, and `srandom`.
- Lines 13610-16056: Configures NLS/gettext/iconv. It honors `--enable-nls`, finds gettext tools (`msgfmt`, `gmsgfmt`, `xgettext`, `msgmerge`), schedules the `po-directories` command, discovers GNU ld/rpath behavior via `config.rpath`, resolves optional libiconv/libintl prefixes and dependencies, checks GNU gettext in libc or libintl, sets NLS macros and `INTLLIBS`, and verifies whether iconv links and works.
- Lines 16065-16117: Sets `popt` project substitutions and defines. It expands `POPT_SYSCONFDIR`, computes `POPT_PKGCONFIG_LIBS`, records `POPT_SOURCE_PATH`, registers an empty `subdirs` list, and declares generated files `Makefile`, `popt.pc`, `popt.spec`, and `test-poptrc`.
- Lines 16119-16258: Writes `confcache`, updates `config.cache` when writable and changed, normalizes `prefix`/`exec_prefix`, sets `DEFS=-DHAVE_CONFIG_H`, expands `LIBOBJS`/`LTLIBOBJS`, and validates Automake conditionals (`MAINTAINER_MODE`, `AMDEP`, `am__fastdepCC`, `HAVE_LD_VERSION_SCRIPT`).
- Lines 16260-17882: Begins generating `./config.status`. It emits the config.status M4sh prologue, option parser, configured file/header/command lists, cached substitutions, libtool delayed-quote support, awk/sed substitution machinery, config-header machinery, and the start of the `CONFIG_COMMANDS` dispatcher for `depfiles` and `libtool`.

## Important APIs, Variables, And Generated Contracts

- `archive_cmds`, `archive_expsym_cmds`, `module_cmds`, `module_expsym_cmds`, `old_archive_from_new_cmds`, and `old_archive_from_expsyms_cmds` are libtool command templates. They are shell snippets evaluated later by the generated `libtool` script to build shared archives, loadable modules, and old-style static archives.
- `runpath_var`, `shlibpath_var`, `shlibpath_overrides_runpath`, `hardcode_libdir_flag_spec`, `hardcode_libdir_separator`, `hardcode_direct`, `hardcode_minus_L`, `hardcode_shlibpath_var`, `hardcode_automatic`, `hardcode_into_libs`, and `hardcode_action` encode how runtime library paths are represented and whether libtool can avoid install-time relinking.
- `library_names_spec`, `soname_spec`, `libname_spec`, `shrext_cmds`, `version_type`, `need_lib_prefix`, and `need_version` define platform library naming/versioning rules. They are central to whether output files are `.so`, `.dylib`, `.dll`, `.sl`, `.a`, or platform-specific versioned names.
- `variables_saved_for_relink` captures environment variables to preserve in wrapper scripts and relink commands, commonly `PATH`, the shared-library path variable, `LD_RUN_PATH`, and GCC-specific `GCC_EXEC_PREFIX`, `COMPILER_PATH`, and `LIBRARY_PATH`.
- `enable_dlopen`, `enable_dlopen_self`, `enable_dlopen_self_static`, `lt_cv_dlopen`, and `lt_cv_dlopen_libs` describe dynamic-loading support and any extra libraries needed for it.
- `enable_shared`, `enable_static`, `enable_fast_install`, `can_build_shared`, `build_libtool_libs`, and `build_old_libs` are the final libtool mode switches exposed to generated Makefiles and the generated `libtool` script.
- `ac_cv_sys_file_offset_bits`, `ac_cv_sys_large_files`, and related checks drive `_FILE_OFFSET_BITS` and `_LARGE_FILES` definitions for large-file ABI compatibility.
- `HAVE_LD_VERSION_SCRIPT_TRUE` and `HAVE_LD_VERSION_SCRIPT_FALSE` are Automake conditional variables controlled by default host logic and `--enable-ld-version-script`.
- `USE_NLS`, `GETTEXT_MACRO_VERSION`, `MSGFMT`, `GMSGFMT`, `XGETTEXT`, `MSGMERGE`, `LIBINTL`, `LTLIBINTL`, `INCINTL`, `INTLLIBS`, `POSUB`, and `XGETTEXT_EXTRA_OPTIONS` form the gettext/NLS substitution contract for Makefiles and the `po` directory.
- `LIBICONV`, `LTLIBICONV`, `INCICONV`, `LIBICONV_PREFIX`, `LIBINTL_PREFIX`, `rpathdirs`, and `ltrpathdirs` are built by dependency-scanning loops that search additional prefixes, `LDFLAGS`, existing libtool archives, shared objects, static archives, and `.la` dependency lists.
- `POPT_SYSCONFDIR`, `POPT_PKGCONFIG_LIBS`, and `POPT_SOURCE_PATH` are `popt`-specific definitions/substitutions. They affect generated `config.h`, `popt.pc`, and build/test behavior.
- `CONFIG_STATUS`, `config_files`, `config_headers`, and `config_commands` define the second-stage generator. In this chunk `config.status` is created but not yet executed.

## Control Flow

1. The chunk first closes the compiler-lock decision from the previous chunk, then resets a large set of libtool linker variables to conservative defaults before host-specific decisions are made.
2. It branches on `with_gnu_ld`. GNU ld hosts share defaults such as `LD_RUN_PATH`, `-rpath`, `--export-dynamic`, and optional `--whole-archive`; non-GNU hosts use a larger native-linker matrix.
3. Each `host_os` branch mutates command templates and capabilities. Some branches only set flags; others compile or link `conftest` programs to inspect default library paths, GNU ld versioning, runpath behavior, or AIX import-file data.
4. After shared-library command selection, dynamic-linker detection maps the host to naming/versioning/search-path policy. If no dynamic linker is supported, `can_build_shared=no`.
5. Runtime path policy is reduced to `hardcode_action`: `relink`, `immediate`, or `unsupported`. This also adjusts `enable_fast_install` because relinking or inherited rpaths can make fast install impossible or needless.
6. Dynamic-loading checks run only when `enable_dlopen` is not already disabled. The script tries host-native mechanisms first, then common functions/libraries, and records whether self-dlopen works. Runtime tests are skipped or guessed under cross-compilation.
7. Libtool is then declared as a config command. Later `config.status` will use all accumulated libtool variables to build the actual `libtool` script from `ltmain.sh`.
8. The script switches to project and portability probes: compiler mode quirks, large-file ABI macros, library lookup for `strerror`, prototype/header checks, linker version-script conditional, gcov flags, `setreuid` fallback, and individual function checks.
9. NLS setup begins by honoring `--enable-nls`, locating gettext command-line tools, and scheduling `po-directories`. It then invokes `config.rpath` to get link-editor and rpath rules for gettext/libiconv discovery.
10. Library discovery for iconv and intl proceeds by iterative dependency expansion. For each logical library name it checks additional prefix directories, `-L` flags, `.so`/versioned shared libraries, static archives, and `.la` dependency metadata, accumulating link flags and rpath flags without duplicating entries.
11. GNU gettext is accepted if found in libc or in an external libintl that passes symbol/link tests; otherwise NLS is disabled unless included gettext support is requested elsewhere. The script defines `ENABLE_NLS`, `HAVE_GETTEXT`, and `HAVE_DCGETTEXT` only for accepted NLS configurations.
12. Iconv is checked twice in this chunk: once inside gettext support and once for the project-level iconv macro path. The first successful link may use libc iconv or `LIBICONV`; a runtime test rejects known-broken iconv implementations where execution is possible.
13. Project-specific substitutions are computed, cache output is prepared, Automake conditionals are validated, and `config.status` is generated as an executable shell script.
14. The emitted `config.status` parser can recheck the original configure invocation, accept `--file`, `--header`, and `--config` requests, prepare substitution awk scripts, materialize configured files and headers, and dispatch extra commands. The range stops inside the `libtool` command emission.

## State And Persistence Behavior

- `confdefs.h` remains the append-only store for C preprocessor results. This chunk adds macros such as `_FILE_OFFSET_BITS`, `_LARGE_FILES`, `HAVE_*` headers/functions, `ENABLE_NLS`, `HAVE_GETTEXT`, `HAVE_DCGETTEXT`, `HAVE_ICONV`, `POPT_SYSCONFDIR`, and `POPT_SOURCE_PATH` depending on probe results.
- `config.cache` may be updated through a temporary `confcache` file. Only `*_cv_*` variables are persisted, variables containing newlines are scrubbed, and `/dev/null` remains the default nonpersistent cache target unless caching was requested.
- `config.status` is created and made executable in this chunk. It persists the configured file/header/command lists, all substitution variables, and the delayed-quoted libtool configuration that later generates `libtool`.
- Temporary probe files include `conftest.$ac_ext`, object/executable outputs, `conftest.err`, `conftest.sh`, `conf$$.file`, `confcache`, and config.status temporary awk files. Most are removed immediately after each check.
- `LIBS`, `CPPFLAGS`, `LDFLAGS`, `prefix`, `exec_prefix`, and `libdir` are repeatedly saved, temporarily modified for link/rpath probes, and restored. Incorrect restoration would leak dependency flags into unrelated tests, so this pattern is important.
- The library-discovery loops maintain deduplication state in `names_already_handled`, `names_next_round`, `rpathdirs`, and `ltrpathdirs`. `.la` files can introduce additional dependency libraries, which are recursively queued.
- The generated `config.status` uses its own temporary directory and trap cleanup; if file/header creation fails, it reports errors and exits nonzero.

## Dependencies And Integration Points

- This chunk depends on the C compiler/linker state, libtool tool variables, and `host` triplets established earlier in the script.
- `ltmain.sh` is not consumed until the following chunk completes the `libtool` command, but this chunk begins embedding the generated libtool configuration that will be prepended before portions of `ltmain.sh`.
- `config.rpath` is executed to derive gettext/libiconv/libintl rpath and naming behavior. Missing or broken `config.rpath` would affect NLS and external library discovery.
- Gettext tooling integration expects usable `msgfmt`, `gmsgfmt`, `xgettext`, and `msgmerge`; absent tools degrade to `:` placeholders or reduced PO update capability.
- The `po-directories` command is registered here and completed in the next chunk. It integrates with `po/POTFILES.in`, optional `po/LINGUAS`, `po/Makevars`, and generated PO/GMO catalog lists.
- Output templates registered in this chunk are `Makefile`, `popt.pc`, `popt.spec`, and `test-poptrc`, plus `config.h` from the earlier header registration.
- Environment and configure options that materially alter this chunk include `--disable-shared`, `--disable-static`, `--disable-fast-install`, `--disable-libtool-lock`, `--enable-ld-version-script`, `--enable-build-gcov`, `--disable-nls`, `--disable-rpath`, `--with-libiconv-prefix`, `--with-libintl-prefix`, `CC`, `CFLAGS`, `CPPFLAGS`, `LDFLAGS`, `LIBS`, `LD`, and `LINGUAS`.

## Risks And Edge Cases

- The libtool host matrix is generated code and very sensitive to regeneration from different libtool/autoconf macro versions. Manual edits here are likely to diverge from `configure.ac` and `ltmain.sh`.
- Linker behavior detection can be brittle. Several branches rely on parsing `$LD -v`, `$LD --help`, `$CC -print-search-dirs`, `objdump -p`, `dump -H`, or `/etc/ld.so.conf`; format changes or restricted build environments can lead to wrong hardcoding or search-path decisions.
- Cross-compilation weakens runtime validation. Self-dlopen and iconv runtime tests may be guessed; a cross build can therefore accept a dynamic loading or iconv path that fails on target hardware.
- The generated rpath logic intentionally hardcodes paths in some cases. Incorrect `libdir`, `--disable-rpath`, `LD_RUN_PATH`, or `config.rpath` outputs can produce binaries that link at build time but fail after installation.
- External `.la` files can pull in stale absolute dependency paths. The recursive `dependency_libs` handling can propagate bad `-L`, `-R`, or archive references from installed libtool archives.
- `--enable-build-gcov` only appends coverage flags when `$CC --version` output contains `GCC`; compatible compilers with different branding may not receive instrumentation.
- The fallback `setreuid` logic appends `-lc -lucb` and sets `USEUCB=y` only when it detects `setreuid` in `libucb`. On systems where `libucb` changes other symbol resolution, this can affect link behavior globally through `LIBS`.
- `POPT_SOURCE_PATH` records the configure-time current working directory. Reproducible builds or relocatable build trees may need to account for this absolute path in generated config headers.
- `config.status` substitution uses sed and awk scripts with delimiter selection and line splitting. Very unusual substitution values containing newlines, delimiter collisions, or shell metacharacters can still stress this generated machinery.

## Test Signals

- Configure output should report the shared-library linker result, dynamic linker characteristics, hardcode action, dlopen/self-dlopen support, stripping support, whether libtool supports shared libraries, shared/static build decisions, large-file checks, header/function checks, NLS request, gettext tool paths, GNU gettext source, iconv status, and creation of `config.status`.
- `config.log` should contain the compile/link/run details for failed and successful `conftest` probes, including linker, dlopen, large-file, gettext, libintl, and iconv checks.
- `config.h` produced after the full script runs should reflect this chunk's macro decisions, especially large-file macros, `HAVE_*` headers/functions, `ENABLE_NLS`, `HAVE_GETTEXT`, `HAVE_DCGETTEXT`, `HAVE_ICONV`, `POPT_SYSCONFDIR`, and `POPT_SOURCE_PATH`.
- Generated `libtool` should contain the libtool configuration variables emitted from this chunk: archive commands, hardcode policy, dynamic linker model, library naming specs, `need_locks`, `pic_flag`, `wl`, `LD`, `NM`, `AR`, and rpath variables.
- Generated `popt.pc` should use `POPT_PKGCONFIG_LIBS`; on Linux/GNU hosts with standard `/usr/lib`, `/usr/lib64`, `/lib`, or `/lib64`, it should omit `-L${libdir}` and use `-lpopt`.
- Important failure signals include no acceptable linker, unsupported shared-library creation, broken C preprocessor/compiler checks in later generated outputs, missing input templates for `config.status`, config.status write failures, conditional validation errors for Automake variables, and gettext/iconv link failures when NLS is requested.
