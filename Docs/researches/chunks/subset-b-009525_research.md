# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/configure lines 9180-12421

## Scope

This chunk is the final third of the generated GNU Autoconf `configure` script for the bundled `e2fsprogs-libs` copy under `xfstests-bld`. It begins after earlier compiler and option setup and covers build-tool discovery, header/type/function probes, platform-specific installation defaults, generated header creation, cache persistence, and `config.status` generation/execution.

The file is generated shell, not hand-written application logic. The important behavior is the sequence of probes and side effects that produce `confdefs.h`, `public_config.h`, `asm_types.h`, `MCONFIG`, Makefiles, pkg-config files, gettext files, and other configured build artifacts for the e2fsprogs libraries.

## Purpose

The chunk adapts the e2fsprogs library build to the local host and build environment. It answers questions that downstream C and Makefile code depend on:

- Which build utilities are available: `make`, GNU make, `ln`, `mv`, `cp`, `rm`, `chmod`, `awk`, `egrep`, `sed`, `perl`, `ldconfig`, `ar`, `ranlib`, `strip`, and `makeinfo`.
- Which compiler should build host-side helper tools when cross-compiling.
- Which C headers, types, struct members, declarations, functions, libraries, byte order, and integer sizes exist.
- Which platform defaults should apply for Linux, GNU/kFreeBSD-like systems, Cygwin, Solaris, and Darwin.
- Which generated files should be instantiated from templates by `config.status`.

For the larger `xfstests-bld` integration, this script is a bootstrap boundary: successful configuration determines whether the bundled e2fsprogs libraries can be built consistently for the intended test environment.

## Important APIs, Functions, And Variables

The "APIs" in this chunk are Autoconf shell conventions and generated helper functions:

- `ac_fn_c_check_header_mongrel`, `ac_fn_c_check_header_compile`, `ac_fn_c_check_func`, `ac_fn_c_check_member`, `ac_fn_c_check_type`, `ac_fn_c_check_decl`, `ac_fn_c_compute_int`, `ac_fn_c_try_compile`, `ac_fn_c_try_link`, and `ac_fn_c_try_run` are generated probe helpers defined earlier in the script. This chunk uses them heavily to compile, link, or run temporary C programs.
- `confdefs.h` is the accumulating preprocessor-definition file. This chunk appends `HAVE_*`, `SIZEOF_*`, `WORDS_BIGENDIAN`, `AC_APPLE_UNIVERSAL_BUILD`, `_INTL_REDIRECT_MACROS`, and related definitions.
- `config.log` receives probe status, command lines, warnings, and error context through file descriptor 5.
- `config.status` is generated near the end and becomes the durable re-instantiation script for configured files.
- `ac_cv_*` and package-specific `e2fsprogs_cv_*` variables cache probe results. Examples include `ac_cv_prog_make_*_set`, `ac_cv_path_LN`, `ac_cv_prog_AR`, `ac_cv_sizeof_long_long`, `ac_cv_c_bigendian`, `e2fsprogs_cv_struct_st_flags`, and `ac_cv_e2fsprogs_use_static`.
- Substitution variables set here include `SET_MAKE`, `ifGNUmake`, `ifNotGNUmake`, `LN`, `LN_S`, `MV`, `CP`, `RM`, `CHMOD`, `AWK`, `EGREP`, `SED`, `PERL`, `LDCONFIG`, `AR`, `RANLIB`, `STRIP`, `MAKEINFO`, `BUILD_CC`, `ASM_TYPES_HEADER`, `PUBLIC_CONFIG_HEADER`, `SOCKET_LIB`, `SEM_INIT_LIB`, `UNI_DIFF_OPTS`, `LINUX_CMT`, `CYGWIN_CMT`, `UNIX_CMT`, `root_prefix`, root installation directories, `LDFLAG_STATIC`, `SS_DIR`, `ET_DIR`, `DO_TEST_SUITE`, `INTL_FLAGS`, `BUILD_CFLAGS`, and `BUILD_LDFLAGS`.

The generated `config.status` script defines its own portable shell helpers, including `as_fn_error`, `as_fn_set_status`, `as_fn_exit`, `as_fn_unset`, `as_fn_append`, `as_fn_arith`, and `as_fn_mkdir_p`. These are used to parse `config.status` arguments, create directories, substitute `@VAR@` placeholders, and instantiate files.

## Control Flow

The chunk proceeds in a mostly linear Autoconf sequence:

1. It checks whether `${MAKE-make}` sets `$(MAKE)` and sets `SET_MAKE` only when recursive make invocations need an explicit assignment.
2. It searches for GNU make by trying `$MAKE`, `make`, `gmake`, and `gnumake`, then exposes makefile comment variables `ifGNUmake` and `ifNotGNUmake`.
3. It discovers standard file and text-processing tools, using user-provided environment overrides when present and falling back to safe defaults such as `ln`, `mv`, `cp`, `rm`, `:`, or `sed`.
4. It detects archiving and binary tools with cross-prefix preference. For `AR`, `RANLIB`, and `STRIP`, it first tries `${ac_tool_prefix}<tool>` and then unprefixed tools, warning if cross-compiling with an unprefixed fallback.
5. It configures documentation generation through `MAKEINFO`, replacing a missing tool with an echo-and-true command so info docs are skipped instead of failing the whole build.
6. It chooses `BUILD_CC`. Native builds reuse `CC`; cross builds search for a native `gcc` or `cc`.
7. It probes a large set of system headers, then specialized headers requiring prerequisite includes, such as `sys/disk.h`, `sys/mount.h`, and `net/if.h`.
8. It probes functions, declarations, members, and sizes: `vprintf`/`_doprnt`, `struct dirent.d_reclen`, `ssize_t`, `llseek`, `lseek64`, `sizeof(short/int/long/long long)`, and byte order.
9. It runs `$ac_aux_dir/parse-types.sh` with `BUILD_CC` and `CPP` to generate assembly-visible type information, then writes `public_config.h` with the public `HAVE_SYS_TYPES_H` and `WORDS_BIGENDIAN` subset needed by `ext2fs.h`.
10. It probes additional C portability features: `inttypes.h`, `intptr_t`, `struct stat.st_flags`, `UF_IMMUTABLE`, `struct sockaddr.sa_len`, optional `blkid_probe_all`, a broad function list, `-lsocket`, `optreset`, and `sem_init` in libc, `-lpthread`, `-lrt`, or `-lposix4`.
11. It computes host-specific makefile comments and install defaults. Linux-like hosts get `HAVE_EXT2_IOCTLS`, usually default `root_prefix=""`, and default `prefix="/usr"` with `/usr/share/man`; Cygwin flips `UNIX_CMT`; Solaris disables static-linking even if the linker accepts `-static`; Darwin defines `_INTL_REDIRECT_MACROS`.
12. It derives static-link flags, source directory paths for `lib/ss` and `lib/et`, test-suite enablement, intl include flags, and native build flags.
13. It creates required build directories and builds `outlist` by checking whether each source-side template directory exists. The resulting list is appended to `ac_config_files`.
14. It writes `confcache`, updates the configured cache file if writable and changed, computes `DEFS` from `confdefs.h`, expands `LIBOBJS`/`LTLIBOBJS`, and emits the full `config.status` script.
15. Unless `--no-create` was requested, it closes/reopens logging around executing `$SHELL ./config.status`, then warns about unrecognized configure options and makes `util/gen-tarball` executable if generated.

## State And Persistence Behavior

This chunk has many filesystem side effects:

- Temporary C sources, objects, executables, makefiles, awk scripts, and cache fragments are created as `conftest*`, `conf$$*`, or under a temporary `./confXXXXXX` directory and usually removed after each probe.
- `confdefs.h` is appended throughout and later transformed into the `DEFS` substitution string.
- `asm_types.h` is generated indirectly by `parse-types.sh`, and `ASM_TYPES_HEADER=./asm_types.h` is exported for substitutions.
- `public_config.h` is rewritten with only public header-relevant defines for `HAVE_SYS_TYPES_H` and `WORDS_BIGENDIAN`.
- `lib`, `include`, `include/linux`, and `include/asm` directories are created if absent.
- The configure cache file is updated from `confcache` when writable and different.
- `config.status` is created, made executable, and later run to instantiate configured files from `*.in` templates.
- `config.status` writes configured files atomically through a temporary output and `mv`, and it creates output directories as needed.
- Gettext-related `default-1` commands create `POTFILES` and specialized `po/Makefile` content from `POTFILES.in`, `LINGUAS`, and `Makevars` when those inputs exist.

No long-lived application state or daemon state is involved. Persistence is build-tree state: generated headers, makefiles, pkg-config files, caches, and logs.

## Dependencies And Integration Points

The chunk depends on a POSIX-like shell environment plus common build tools. It integrates with:

- The C compiler and linker through compile, link, and run probes.
- Host and target toolchains through `CC`, `BUILD_CC`, `ac_tool_prefix`, `AR`, `RANLIB`, and `STRIP`.
- Shell utilities including `grep`, `egrep` or `$GREP -E`, `sed`, `awk`, `diff`, `mkdir`, `chmod`, `ln`, `cp`, `mv`, `rm`, and optionally `perl`, `ldconfig`, and `makeinfo`.
- e2fsprogs auxiliary script `$ac_aux_dir/parse-types.sh`.
- Optional system libraries: `libblkid`, `libsocket`, `libpthread`, `librt`, and `libposix4`.
- Template-driven build files such as `MCONFIG`, top-level and subdirectory `Makefile`s, library type headers, pkg-config files for `ss`, `uuid`, `com_err`, `e2p`, `blkid`, and `ext2fs`, `e2fsprogs.spec`, `util/subst.conf`, `util/gen-tarball`, and gettext inputs.
- Public e2fsprogs headers, especially `lib/ext2fs/ext2_types.h`, `lib/uuid/uuid_types.h`, `lib/blkid/blkid_types.h`, and `public_config.h`.

This chunk also bridges configure-time results into later make execution. Makefile conditionals consume comment variables such as `LINUX_CMT`, `CYGWIN_CMT`, `UNIX_CMT`, `ifGNUmake`, and `ifNotGNUmake`, while C sources consume `HAVE_*` and `SIZEOF_*` definitions.

## Risks And Edge Cases

- Generated-script fragility: edits to this file can be overwritten by rerunning Autoconf and may diverge from `configure.ac` intent.
- Cross-compilation ambiguity: probes that need execution are avoided or guessed in some cases, but incorrect cached values for byte order, sizes, or declarations can produce incompatible headers.
- Tool fallback masking: missing `makeinfo`, `ranlib`, `strip`, `chmod`, or `ldconfig` may become `:` or an echo command. That keeps configuration moving but can hide incomplete packaging or install behavior.
- Cache poisoning: stale `ac_cv_*` or `e2fsprogs_cv_*` values can bypass real probes and generate incorrect `confdefs.h` and Makefiles.
- Host-specific defaults affect installation paths. Linux-like defaulting of `prefix=/usr`, `root_prefix=""`, and `mandir=/usr/share/man` can surprise callers expecting Autoconf's usual `/usr/local` default.
- The `BLKID_CMT` guard means blkid probing only happens when that earlier variable requests it; consumers must understand whether bundled or system blkid is selected outside this chunk.
- Static-link detection mutates `LDFLAGS` during the probe and then restores it. A failed restoration or hostile environment variable would affect later link tests.
- `sem_init` search order chooses the first successful provider among libc, `-lpthread`, `-lrt`, and `-lposix4`; platform linker behavior can make the selected `SEM_INIT_LIB` important for all downstream targets.
- The generated `config.status` substitution machinery relies on `awk`, delimiter selection, and sed escaping. Values with newlines are explicitly stripped from cache output, so unusual environment values may not round-trip.
- The `net/if.h` prerequisite block tests `#if HAVE_SYS_SOCKET` rather than the more common `HAVE_SYS_SOCKET_H`; if that macro is not defined elsewhere, the compile probe may omit `sys/socket.h` on platforms that require it.

## Test Signals

Useful validation signals for this chunk are configure and build outcomes rather than unit tests:

- Running the generated `configure` script should complete without `as_fn_error`, create `config.status`, update `config.log`, and instantiate the expected `outlist` files.
- `config.log` should show successful or intentionally negative results for required probes, especially C type sizes, endianness, `BUILD_CC`, `sem_init`, static linking, and tool discovery.
- Generated files should exist and be non-empty after configuration: `MCONFIG`, relevant `Makefile`s, `public_config.h`, `asm_types.h`, library type headers, and pkg-config files for enabled libraries.
- A subsequent `make` or package build under `xfstests-bld` exercises whether tool substitutions, root install directories, static flags, gettext outputs, and library dependencies are coherent.
- Cross-build test signals should include checking that host tools are built with `BUILD_CC`, target objects use `CC`, and cached endian/size values match the target ABI.
- On Linux hosts, `confdefs.h` or generated config headers should contain `HAVE_EXT2_IOCTLS`, and install substitutions should reflect `/usr` plus the root-prefix split expected by e2fsprogs.
