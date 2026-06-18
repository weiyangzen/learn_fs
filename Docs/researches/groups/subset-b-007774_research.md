# Research report: subset-b-007774

Grouped research for the requested OpenAFS config, crypto, directory, demand-attach server, demand-attach volserver, and AIX export sources. Each source section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.x86_darwin_190.h -->
# sources/distributed-fs/openafs/src/config/param.x86_darwin_190.h

This platform parameter header selects OpenAFS build behavior for x86/amd64 Darwin 19. It has separate kernel and `UKERNEL` userspace halves and defines the common Darwin lineage macros from `AFS_DARWIN70_ENV` through `AFS_DARWIN190_ENV`, 64-bit client and I/O behavior, `AFS_NAMEI_ENV`, syscall number 230, endian selection, and vnode/uio compatibility aliases.

Important API surface is preprocessor state, not functions. Kernel builds map AFS names such as `afsio_iov`, `AFS_KALLOC`, `v_count`, `v_vfsp`, and `direct` onto Darwin kernel structures, enable `RXK_UPCALL_ENV`, `RXK_TIMEDSLEEP_ENV`, `AFS_USERSPACE_IP_ADDR`, and `AFS_SOCKPROXY_ENV`, and set `NEED_IOCTL32`. Userspace builds define `AFS_USERSPACE_ENV`/`AFS_USR_DARWIN*_ENV` and matching `SYS_NAME`/`SYS_NAME_ID` for ppc, i386, and amd64.

There is no runtime control flow or persistence; state is compile-time ABI selection. Integration is broad: nearly every OpenAFS source that includes `afs/param.h` depends on these macros to select OS, pointer width, vnode, syscall, and network behavior. Risks are macro drift and architecture naming mistakes; the userspace i386 block includes `sys_x64_darwin_*` spellings where surrounding files use `sys_x86_darwin_*`, so consumers must be checked. Test signals are successful libafs and userspace builds on Darwin 19 for i386/amd64 paths, plus compile coverage for 32-bit ioctl compatibility and sockproxy/upcall features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.x86_darwin_190.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.x86_darwin_80.h -->
# sources/distributed-fs/openafs/src/config/param.x86_darwin_80.h

This header configures OpenAFS for Darwin 8 on ppc and i386. The kernel half defines `AFS_ENV`, `AFS_64BIT_CLIENT`, `AFS_64BIT_IOPS_ENV`, `AFS_VFSINCL_ENV`, Darwin 70/80 markers, `AFS_NAMEI_ENV`, syscall number 230, `DARWIN_REFBASE 3`, and RX listener/timed sleep behavior. The userspace half defines `AFS_USERSPACE_ENV`, `AFS_USR_DARWIN70_ENV`, `AFS_USR_DARWIN80_ENV`, `DARWIN_REFBASE 0`, and compatibility aliases for uio/vattr/directory handling.

The file's API is compile-time constants and OS structure aliases. `SYS_NAME`/`SYS_NAME_ID` select either `ppc_darwin_80` or `x86_darwin_80`, and endian macros select big-endian ppc or little-endian x86. Kernel-only mappings provide `AFS_KALLOC`, `AFS_KFREE`, vnode and mount field aliases, and `BIND_8_COMPAT`.

There is no runtime state. The persistent effect is ABI selection embedded into all compiled objects. Integration points are `afs_sysnames.h`, Darwin kernel headers through `KERNEL`, and all code paths guarded by `AFS_DARWIN80_ENV` or `AFS_USR_DARWIN80_ENV`. Main risks are fossilized OS assumptions, old 32-bit-only architecture handling, duplicated `AFS_UIOSYS` macros, and structure alias mismatch with newer headers. Test signals are successful Darwin 8 kernel module and userspace compiles and smoke tests for pioctl/syscall, RX listener, vnode cache, and directory operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.x86_darwin_80.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.x86_darwin_90.h -->
# sources/distributed-fs/openafs/src/config/param.x86_darwin_90.h

This platform header targets Darwin 9 on ppc and x86/x86_64 style builds. It extends the Darwin 8 configuration with `AFS_DARWIN90_ENV`, `AFS_CACHE_VNODE_PATH`, and `AFS_NEW_BKG`. Kernel builds define 64-bit client/I/O behavior, `AFS_NAMEI_ENV`, RX listener and timed sleep support, and Darwin kernel structure aliases.

Its important interfaces are preprocessor macros: architecture selectors `AFS_PPC_ENV`/`AFS_X86_ENV`, system names `ppc_darwin_90` and `x86_darwin_90`, endian macros, uio aliases, allocation wrappers, and `VATTR_NULL usr_vattr_null` in userspace. It includes `afs_sysnames.h` and defines `AFS_HAVE_FFS`.

Control flow is compile-time conditional branching between kernel and `UKERNEL`, then architecture branches. No runtime persistence exists. The file integrates with Darwin 9 kernel/user builds, OpenAFS syscall/pioctl code, vnode and uio consumers, and code that gates behavior on `AFS_CACHE_VNODE_PATH`. Risks include treating `__x86_64__` as `x86_darwin_90` instead of an amd64 sysname, legacy `AFS_VFS34` comments indicating unclear VFS assumptions, and duplicated macro definitions. Test signals are compile success under both `KERNEL` and `UKERNEL`, plus vnode path cache and RX listener/timed sleep regression coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.x86_darwin_90.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/permit_xprt.h -->
# sources/distributed-fs/openafs/src/config/permit_xprt.h

This tiny compatibility header unconditionally enables old export-permission macros. It defines `xprt_CoerceLevel`, makes `xprt_CryptOK(x)` always return `1`, and defines `AFS_HIDE`.

There are no functions, control flow, or persistent data. Its API is intentionally macro-only and is included by code that expects transport/export-layer authorization toggles to exist. The security-relevant behavior is that any caller using `xprt_CryptOK` receives success regardless of the argument.

Dependencies are only the C preprocessor. Integration points are legacy OpenAFS export/transport consumers that need these symbols to compile. The main risk is semantic: a macro named `CryptOK` returning true can hide missing encryption enforcement if used outside the historical context. Test signals are compile coverage of modules that include it and targeted audits of all `xprt_CryptOK` uses to confirm the macro is not relied on as a real policy decision.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/permit_xprt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/ranlib -->
# sources/distributed-fs/openafs/src/config/ranlib

This shell wrapper replaces `ranlib` on platforms where the operation is intentionally ignored. It prints a diagnostic of the form `ranlib <arg> ignored` and exits with the shell's default success status unless `echo` fails.

There are no APIs beyond the executable script interface. It has no state or persistence. Integration is through Makefiles that set `RANLIB` to this script when archive indexing is unnecessary or unsupported.

Risks are limited but real: build logs can show success even if a platform actually needs archive symbol indexing. Test signals are successful static library linkage on the affected platform and no unresolved symbols caused by missing archive indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/ranlib -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/shlib-build.in -->
# sources/distributed-fs/openafs/src/config/shlib-build.in

This autoconf-substituted shell script builds shared libraries without using libtool. It parses `-d <srcdir>`, `-f <filename>`, `-l <library>`, `-M <major>`, `-m <minor>`, `-i`, `-p`, then `--` followed by linker arguments. It computes the output filename and SONAME, derives export/version-map flags, prints the linker invocation, and executes `@SHLIB_LINKER@`.

Control flow is platform-specific by `@AFS_SYSNAME@`: AIX converts `.map` globals to `.exp` and uses `-bE`; Solaris uses map files and optional `= EXTERN` rewriting under `-i`; Linux passes `--version-script` and `-h`; HP-UX uses `.hp` export control; Darwin builds `_`-prefixed exported symbol lists and may add `-undefined dynamic_lookup`; unknown platforms just link.

State and persistence are generated shared objects and temporary export/map files in the build directory. Dependencies include `awk`, `sed`, platform linkers, generated map files, and autoconf substitutions. Integration points are library Makefiles using `SHLIB_BUILD`. Risks include fragile shell precedence in validation, unsanitized generated files, platform linker flag drift, and silent ABI exposure changes when map files are missing. Test signals are shared-library build/install tests on each supported OS, SONAME/symlink verification, and exported-symbol diffs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/shlib-build.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/shlib-install.in -->
# sources/distributed-fs/openafs/src/config/shlib-install.in

This companion script installs shared libraries and creates conventional unversioned and major-version symlinks. It parses `-d <dest>`, `-l <library>`, optional `-M <major>`, and `-m <minor>`, computes the built filename from `@SHLIB_SUFFIX@`, and runs `@INSTALL_DATA@` plus `ln -s -f`.

Control flow is platform-specific: AIX installs a `.shared` file, HP-UX installs either unversioned or major-only names, and the default path installs the full `lib.suffix.major.minor` and symlinks both `lib.suffix` and `lib.suffix.major` to it. The script persists files and symlinks under the destination tree.

Dependencies are autoconf substitutions, `INSTALL_DATA`, `ln`, and the calling Makefile having already built the expected filename. Integration is with the custom shared library build pipeline. Risks include missing quoting in one install line, platform symlink conventions that do not include minor versions, and no rpath handling. Test signals are package staging checks that all expected library names resolve and that repeated installs update symlinks idempotently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/shlib-install.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/stds.h -->
# sources/distributed-fs/openafs/src/config/stds.h

This installed portability header defines OpenAFS fixed-width types, integer helpers, annotation macros, formatting macros, and shared wire/disk structures. It intentionally avoids requiring `afsconfig.h` before inclusion and instead includes `afs/param.h` and `sys/types.h`.

Important types include `afs_int16/32/64`, `afs_uint16/32/64`, `afs_size_t`, `afs_offs_t`, `afs_foff_t`, `afs_fsize_t`, `afs_hyper_t`, `b64_string_t`, `afsUUID`, and `afs_time64`. Important macros cover 64-bit arithmetic (`FillInt64`, `SplitInt64`, `RoundInt64ToInt32`), hyper arithmetic (`hcmp`, `hadd32`, `hshlft`), network-byte-order aliases, printf format strings, `static_inline` portability, pointer/integer casts, compiler attributes, fallthrough, struct initializer compatibility, and `AFS_RXGK_*` feature gates.

There is no runtime control flow or persistence; all behavior is compile-time type and macro selection. Dependencies include platform macros from `param.h`, optional compiler feature macros, and networking headers for hton/ntoh users. Integration is repository-wide because these types are used on the wire and on disk. Risks include macro side effects, assumptions about 32-bit `int`, lossy pointer casts under non-64-bit pointer environments, and old compiler branches. Test signals are ABI layout checks, format-string warning-free builds, and cross-platform serialization tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/stds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/touch.c -->
# sources/distributed-fs/openafs/src/config/touch.c

This Windows build utility updates timestamps for files matching a wildcard. `main` calls `_findfirst`/`_findnext`, skips entries whose attributes are not normal files, opens each file read/write binary, seeks to end, writes one null byte, truncates back to the original length with `_chsize`, and closes.

Important functions are `usage` and `main`; the only important constant is `ATTRIBUTE_MASK`, which masks read-only, hidden, system, and directory bits so later Windows attribute bits do not affect the normal-file test. State changes are filesystem timestamp/metadata updates; file contents are intended to remain unchanged.

Dependencies are Windows headers and MSVCRT `_finddata_t`, `_open`, `_lseek`, `_write`, `_chsize`, and `_close`. Integration is Windows make/build rules that need a portable `touch` equivalent. Risks include no open-error checking after `_open`, working only on the current directory component returned by `_findfirst`, and skipping read-only/generated files. Test signals are Windows build rules that depend on timestamp refresh and content-preservation checks for wildcard matches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/touch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/util_cr.c -->
# sources/distributed-fs/openafs/src/config/util_cr.c

This Windows multi-tool supports historical OpenAFS build and installer tasks: CRLF conversion, version-template substitution, registry mutation, INI/profile updates, deletion, OS detection, current-directory derivation, environment-variable writes, and command spawning after `.et` normalization.

Important functions are `CheckVersion`, `Addkey`, `Subkey`, `doremove`, `gencurdir`, `isequal`, `SetSysEnv`, and `main`. `main` dispatches commands such as `_echo`, `_sysvar`, `_dir`, `_isequal`, `_del`, `_ver`, `_isOS`, `}` for product version placeholder substitution (`%1` through `%5`), `~` for file-presence assertion, `*` for registry add/delete, `@` for INI writes with `*DatE*`/`*TimE*`, `+` for adding CR before LF, `-` for stripping CR, and the default path that strips CR from an `.et` file before spawning another program.

State and persistence are extensive: registry keys/values, INI files, generated `home` temp file, environment broadcasts, deleted files, rewritten source/template files, and spawned child process effects. Dependencies are Win32 registry/profile/version APIs and MSVCRT file APIs. Risks are unchecked buffer copies into fixed arrays, destructive recursive delete behavior, mutation of `argv[2]` during version parsing, fragile `strtok` parsing, no robust error recovery, and deprecated OS version detection. Test signals are Windows installer/build scripts that invoke each command, plus isolated tests for CRLF idempotence, version parsing, registry string syntax, and recursive delete boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/util_cr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/uvenus.h -->
# sources/distributed-fs/openafs/src/config/uvenus.h

This file is not a usable header; it is a three-line notice stating that `uvenus.h` has been renamed to `venus.h` and that future changes should be made in `config/venus.h`.

There are no APIs, control flow, state, dependencies, or direct integration beyond acting as a migration marker for developers or stale include paths. The main risk is that a compiler including this file will see raw text, not comments, so it should not be on any active include path. Test signals are absence of source includes of `uvenus.h` and successful builds using `afs/venus.h` instead.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/uvenus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/venus.h -->
# sources/distributed-fs/openafs/src/config/venus.h

This installed header defines data structures used with Venus/cache-manager pioctls. It includes `afs/vioc.h` for ioctl command numbers and, outside `UKERNEL`, `netinet/in.h` for IPv4 server preference structures.

Important types include `spref`, `sprefrequest_33`, `sprefrequest`, `sprefinfo`, `setspref`, `gaginfo`, `rxparams`, `chservinfo`, `sbstruct`, and versioned `cm_initparams`. These structures carry server ranks, get/set server preference requests, cache-manager gag/log flags, RX tuning parameters, checkservers request state, store-behind settings, and cache manager initialization results. Constants include `DBservers`, `GAGUSER`, `GAGCONSOLE`, `logwritethruON`, and `CMI_VERSION`.

There is no runtime control flow; persistence occurs only through the pioctl consumers that serialize these structures to the cache manager. Dependencies are `vioc.h`, `afs/stds.h` types transitively, and network address types. Integration points are `fs`, `cmdebug`, cache-manager pioctl handlers, and any administrative tool using these structs. Risks are ABI compatibility, intentionally overrun flexible one-element arrays, bitfield layout in `cm_initparams`, and structure size expectations across 32/64-bit builds. Test signals are pioctl round trips for server preferences, RX params, gag flags, and init params.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/venus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/vioc.h -->
# sources/distributed-fs/openafs/src/config/vioc.h

This header centralizes Venus ioctl and pioctl numeric command constants. It includes `afs/vice.h` unless `_VICEIOCTL` is already available, then defines legacy IBM-managed `VIOC*` commands, coordinated central registry `C` commands, and OpenAFS-specific `O` commands.

Important constants include file-descriptor ioctls `VIOCCLOSEWAIT`, `VIOCABORT`, `VIOCIGETCELL`; pioctls for ACLs, tokens, volume state, flushing, checks, prefetch, PAG, cache size, new cells, sysname, NFS export, server/client preferences, RX stats, encryption settings, OSD extensions, and VCX status; coordinated commands like `VIOC_NEWALIAS`, `VIOC_GETTOK2`, `VIOC_NEWUUID`, `VIOC_GETPAG`, `VIOC_FLUSHALL`; and OpenAFS commands `VIOC_NFS_NUKE_CREDS` and `VIOC_SETBYPASS_THRESH`.

There is no runtime state; the ABI is the persisted contract. Integration is with userspace tools, `pioctl`, cache manager dispatch tables, and kernel/user boundary marshalling. Risks are number collisions, accidental use of reserved site/private ranges in distributed software, and mismatched command definitions between clients and kernel modules. Test signals are compile-time inclusion by `venus.h`/`kopenafs.h` and runtime pioctl dispatch tests for commands whose structures are defined elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/vioc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/Makefile.in -->
# sources/distributed-fs/openafs/src/crypto/hcrypto/Makefile.in

This Makefile builds OpenAFS' trimmed Heimdal hcrypto library. It includes config/lwp make fragments, defines libtool versioning, object lists for AES, Camellia, DES, EVP, HMAC, hashes, random, RC2/RC4, UI, and validation sources, and installs selected hcrypto headers into `TOP_INCDIR`.

Control flow is make target selection: `all-internal`, `all-lwp`, and `buildtools` install headers and build shared/static/LWP archives; `install` and `dest` stage `libafshcrypto.a` and optional shared libraries; explicit object rules compile sources from `external/heimdal/hcrypto` because implicit rules cannot find them. State is generated archives, libtool objects, installed headers, and optional test binary `test_cipher`.

Dependencies are Heimdal upstream sources, roken, libtool macros, OpenAFS make fragments, and `@hcrypto_all_target@`/`@hcrypto_install_target@` substitutions. Integration points are `rfc3961`, rxgk/rxkad crypto consumers, kernel-adapted hcrypto builds, and buildtools. Risks include upstream source drift, object/header list mismatch, intentionally disabled warnings for selected sources, and shared/static target divergence. Test signals are successful `libafshcrypto` builds, header installation, `test_cipher`, and downstream RFC3961 link tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/config.h -->
# sources/distributed-fs/openafs/src/crypto/hcrypto/config.h

This userspace hcrypto config shim adapts Heimdal code to OpenAFS. It includes `afsconfig.h`, `afs/param.h`, optional `stdint.h`, normalizes `inline` for older compilers, renames several hcrypto symbols to `_oafs_h_*`, and defines `RETSIGTYPE`/`SIGRETURN`.

The important API is preprocessor behavior: compiler compatibility for `inline`, namespace isolation for Camellia and ENGINE functions, and signal-return compatibility expected by Heimdal-derived files. There is no runtime control flow or persistence.

Dependencies are OpenAFS platform config and compiler feature macros. Integration is all userspace hcrypto compilation units that include `<config.h>`. Risks are incomplete symbol renaming causing clashes with system OpenSSL/Heimdal, and compiler-specific `inline` substitutions changing optimization or linkage. Test signals are warning-free builds on NT, HPUX, AIX, SGI, NetBSD, and normal Unix, plus link tests with external crypto libraries present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/engine.c -->
# sources/distributed-fs/openafs/src/crypto/hcrypto/engine.c

This file provides stub ENGINE support for hcrypto. OpenAFS does not build hcrypto public-key/ENGINE functionality, so `ENGINE_finish` and `ENGINE_up_ref` return `-1`, and `ENGINE_get_RAND` returns `NULL`.

The API is exactly those three functions declared in `engine.h`. Control flow is trivial and stateless. Dependencies are `config.h`, local `engine.h`, and `stdlib.h`; `engine.h` pulls in `hcrypto/rand.h` for `RAND_METHOD`.

Integration is with upstream hcrypto code that references ENGINE APIs but where OpenAFS wants linkability without real engine support. Risks arise if a caller starts treating ENGINE as supported; failures are deterministic but may be unchecked by upstream code. Test signals are link success and functional tests confirming default RAND paths do not require an ENGINE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/engine.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/engine.h -->
# sources/distributed-fs/openafs/src/crypto/hcrypto/engine.h

This header defines the minimal ENGINE type and prototypes required by the OpenAFS hcrypto build. It forward-declares `struct hc_engine` as `ENGINE`, includes `hcrypto/rand.h`, and declares `ENGINE_finish`, `ENGINE_up_ref`, and `ENGINE_get_RAND`.

There is no runtime state in the header. Integration is with `engine.c` stubs and Heimdal-derived hcrypto source expecting an ENGINE API. The risk is API incompleteness if future hcrypto code begins using more ENGINE functions or struct internals. Test signals are compile/link coverage of all hcrypto sources using this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/engine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/getarg.h -->
# sources/distributed-fs/openafs/src/crypto/hcrypto/getarg.h

This header disables Heimdal getarg functionality while preserving enough API shape for code to compile. It defines `struct getargs` with long/short names, option type enum, value pointer, help, and arg-help fields, then provides inline no-op `getarg`, `arg_printusage`, and `rk_print_version`.

Control flow is trivial: `getarg` always returns 0 and the usage/version functions return immediately. There is no persistent state. Integration is with Heimdal test or utility code that includes getarg but is not expected to parse command-line options in OpenAFS builds.

The main risk is behavioral surprise if a program built in this tree expects actual option parsing; options will be silently accepted but ignored. Test signals are compile coverage and ensuring no installed/user-facing OpenAFS tool relies on these stubs for argument handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/getarg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/heim_threads.h -->
# sources/distributed-fs/openafs/src/crypto/hcrypto/heim_threads.h

This userspace hcrypto threading shim maps Heimdal mutex macros to pthread mutexes under `AFS_PTHREAD_ENV`, and to no-op integer locks otherwise. The no-op path is justified by comments that the PRNG code does not yield or use the LWP IO manager, so it cannot be preempted under the LWP model.

The API consists of `HEIMDAL_MUTEX`, `HEIMDAL_MUTEX_INITIALIZER`, and init/lock/unlock/destroy macros. There is no independent state beyond mutex objects in users. Dependencies are pthreads when enabled and OpenAFS threading model assumptions when not.

Integration is with hcrypto random and global-state code. Risks are concurrency assumptions: if hcrypto gains yielding or I/O behavior in non-pthread builds, the no-op locks become unsafe. Test signals are pthread race tests for PRNG access, LWP builds, and review of hcrypto call paths for blocking/yielding changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/heim_threads.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/alloc.c -->
# sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/alloc.c

This kernel adapter implements libc-style allocation routines for hcrypto using OpenAFS kernel allocation primitives. `_afscrypto_calloc` allocates `num * len` bytes via `afs_osi_Alloc` and zeroes them if non-null; `_afscrypto_malloc` wraps `afs_osi_Alloc`; `_afscrypto_free` calls `afs_osi_Free(ptr, 0)`; `_afscrypto_strdup` duplicates with the remapped `malloc`; `_afscrypto_realloc` is a deliberately narrow workaround.

State is kernel heap memory. The realloc behavior is especially important: `realloc(NULL, len)` allocates space for 20 items via `calloc(20, len)`, while reallocating an existing pointer returns it unchanged. This matches known hcrypto call sites that shrink buffers or derive keys.

Dependencies are `kernel/config.h` macro remapping, `afs_osi_Alloc`, `afs_osi_Free`, and string functions. Integration is kernel hcrypto and RFC3961 builds. Risks include integer overflow in `num * len`, freeing without original size, and the hard-coded 20-key realloc assumption. Test signals are kernel crypto encrypt/decrypt/key-derivation tests and memory instrumentation for leaks or overwrite under derived-key workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/assert.h -->
# sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/assert.h

This file is intentionally blank. It satisfies include paths for code that expects an `assert.h` in the kernel hcrypto shim directory while assertions are instead handled in `kernel/config.h` by redefining `assert` to `osi_Assert`.

There are no APIs, state, control flow, or direct dependencies. Integration is include-path compatibility. The risk is only confusion: including this file alone does not provide `assert`. Test signals are successful kernel hcrypto builds and no compilation unit depending on declarations from this blank file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/assert.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/config.h -->
# sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/config.h

This kernel hcrypto config shim makes userspace Heimdal hcrypto sources build inside OpenAFS kernel code. It includes OpenAFS config, standard, sysinclude, afs include, and prototype headers; maps `assert` to `osi_Assert`; removes conflicting kernel macros like `current` and `u`; normalizes `inline`; and remaps libc allocation/string/random/process APIs to kernel-safe substitutes.

Important APIs are macro remaps for `calloc`, `malloc`, `free`, `strdup`, `realloc`, `strcasecmp`, `getpid`, `abort`, `open`, `read`, `close`, `rk_cloexec`, and optionally `gettimeofday`. It declares `osi_readRandom`, provides `_afscrypto_getpid` returning 1, `_afscrypto_abort` panicking, and stubs unsupported file operations. For Solaris and arm64 Linux kernel builds, it remaps `double` to `void *` to avoid floating-point ABI use.

There is no persistence except through functions it redirects to. Integration is every kernel hcrypto source compiled with this config. Risks are broad macro side effects, disabled entropy sources, stubbed file I/O, artificial PID entropy, and replacing `double` in function signatures. Test signals are kernel module builds on Linux, Solaris, AIX, HPUX, SGI, and runtime crypto/RNG tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/evp-algs.c -->
# sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/evp-algs.c

This file provides a deliberately small EVP provider for kernel hcrypto. It implements AES-128-CBC, AES-256-CBC, and SHA1, and returns `NULL` for many unsupported digest and cipher algorithms.

Important functions are `aes_init`, `aes_do_cipher`, `EVP_hckernel_aes_128_cbc`, `EVP_hckernel_aes_256_cbc`, `EVP_hckernel_sha1`, unsupported stubs such as `EVP_hckernel_sha256`, `EVP_hckernel_rc4`, `EVP_hckernel_des_cbc`, and `hcrypto_validate`. `aes_init` sets an AES encrypt/decrypt key based on `ctx->encrypt`; `aes_do_cipher` uses CFB8 if the flag is set, otherwise CBC, updating `ctx->iv`.

State is per-`EVP_CIPHER_CTX` cipher data and IV mutation; provider descriptors are static const. Dependencies are kernel `config.h`, hcrypto EVP/AES/SHA headers. Integration is RFC3961 kernel algorithm selection, primarily AES CTS/HMAC-SHA1 paths. Risks are unsupported algorithms causing NULL dereference if callers do not check, no AES-192 or CFB8 provider despite code support in `aes_do_cipher`, and reliance on hcrypto struct layouts. Test signals are AES128/AES256 Kerberos crypto vectors and SHA1 checksum vectors in kernel mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/evp-algs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/evp-hcrypto.h -->
# sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/evp-hcrypto.h

This kernel header declares the trimmed hcrypto EVP provider and names it with `HCRYPTO_DEF_PROVIDER hckernel`. It exposes AES-128-CBC, AES-256-CBC, and SHA1 as supported functions, and declares stubs for SHA2, MD*, RC2/RC4, DES, AES-192/CFB8, and Camellia.

There is no runtime control flow or persistence. Integration is with upstream hcrypto provider dispatch that constructs function names using `HCRYPTO_DEF_PROVIDER` and with `evp-algs.c`. Risks are header/implementation drift and callers assuming all declared algorithms are implemented. Test signals are compile/link coverage and runtime checks that unsupported algorithms are rejected cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/evp-hcrypto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/heim_threads.h -->
# sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/heim_threads.h

This kernel threading shim maps Heimdal mutex macros to OpenAFS kernel mutexes. `HEIMDAL_MUTEX` is `afs_kmutex_t *`, initialized to the global `hckernel_mutex`, and lock operations expand to `MUTEX_INIT`, `MUTEX_ENTER`, `MUTEX_EXIT`, and `MUTEX_DESTROY`.

It also disables userspace random methods by defining `NO_RAND_UNIX_METHOD` and `NO_RAND_EGD_METHOD`. State is the external global mutex declared in `rand.c` and initialized by `init_hckernel_mutex`.

Dependencies are `rx_kmutex.h` and OpenAFS kernel synchronization primitives. Integration is hcrypto PRNG/global state in kernel builds. Risks include all Heimdal mutex users sharing one global mutex and the initializer macro's trailing semicolon style. Test signals are kernel crypto concurrency tests and successful initialization from `osi_Init` before first hcrypto use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/heim_threads.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/krb5-types.h -->
# sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/krb5-types.h

This file is empty. It satisfies an include expected by hcrypto or Heimdal-derived kernel code, while the actual minimal Kerberos types are supplied by `src/crypto/rfc3961/rfc3961.h` and `krb5_locl.h`.

There are no APIs, state, or dependencies. Integration is include-path compatibility. The main risk is accidental reliance on it for type definitions; test signals are compile coverage ensuring required Kerberos types come from the RFC3961 headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/krb5-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/rand-timer.c -->
# sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/rand-timer.c

This file provides a stub timer-based RAND method so Heimdal's Fortuna code can link in kernel space. All method callbacks either do nothing, return success without filling data, or report not-ready status.

Important symbols are static callbacks `timer_seed`, `timer_bytes`, `timer_cleanup`, `timer_add`, `timer_pseudorand`, `timer_status`, the `hc_rand_timer_method` descriptor, and `RAND_timer_method`. There is no useful entropy state and no persistence.

Dependencies are hcrypto `RAND_METHOD` and `AFS_STRUCT_INIT`. Integration is link compatibility for `rand-fortuna.c`; actual randomness should come from `rand.c` and `osi_readRandom` or Fortuna seeded elsewhere. Risks are severe if this method is ever used as a real random source because `bytes` returns success without populating output. Test signals are audits that no production path selects `RAND_timer_method` for output and kernel RNG tests that exercise `RAND_bytes` instead.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/rand-timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/rand.c -->
# sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/rand.c

This file implements the kernel-facing hcrypto RAND interface. It defines global `afs_kmutex_t hckernel_mutex`, initializes it in `init_hckernel_mutex`, optionally uses Heimdal Fortuna on AIX/DragonFlyBSD/HPUX/SGI, and otherwise reads random bytes through `osi_readRandom`.

Important functions are `RAND_seed`, which seeds Fortuna only under `USE_FORTUNA`, and `RAND_bytes`, which returns failure for zero-size requests, delegates to Fortuna when enabled, or calls `osi_readRandom` and returns success when that read succeeds. State is the mutex and, on selected platforms, Fortuna internal PRNG state.

Dependencies are kernel hcrypto headers, `heim_threads.h`, `osi_readRandom`, and platform macros. Integration is Kerberos/RFC3961 key generation and kernel crypto. Risks include interpreting `osi_readRandom` return semantics correctly, no explicit locking around `RAND_bytes` in this file, and platform divergence between Fortuna and direct kernel RNG. Test signals are kernel RNG availability tests, seeded Fortuna behavior on listed platforms, and encryption key generation tests under low-entropy boot conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/rand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/roken.h -->
# sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/roken.h

This kernel-only roken stub exposes just enough of Heimdal's roken API for kernel hcrypto. It requires `KERNEL`, strips roken export annotations, defines `HAVE_STRLCPY`/`HAVE_STRLCAT` defaults with platform exceptions, aliases missing functions to `rk_strlcpy`/`rk_strlcat`, and declares `ct_memcmp`.

There is no runtime state in the header. Dependencies are kernel platform macros and any compiled roken replacement functions. Integration is hcrypto and RFC3961 kernel code using roken string and constant-time comparison helpers. Risks are mismatch between userspace autoconf availability and kernel availability, especially Linux without `strlcpy` and AIX without both functions. Test signals are kernel builds on exception platforms and crypto checksum tests that rely on `ct_memcmp`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/roken.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/stdio.h -->
# sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/stdio.h

This file is intentionally blank. It exists to satisfy include paths for userspace-derived code that includes `stdio.h` while compiling in kernel mode, where real stdio is unavailable or inappropriate.

There are no APIs, state, or control flow. Integration is include-path masking for kernel hcrypto. Risks are compile or behavior failures if code expects `FILE`, `printf`, or other stdio declarations. Test signals are successful kernel hcrypto builds and review that no kernel-compiled hcrypto source actually uses stdio APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/stdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/stdlib.h -->
# sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/stdlib.h

This file is intentionally blank and acts as a kernel include shim for code that includes `stdlib.h`. Actual allocation and abort behavior is supplied by macro remapping in `kernel/config.h`.

There are no APIs or state here. Integration is include-path compatibility for kernel hcrypto. Risks appear if a kernel-compiled source expects standard library declarations not provided by `config.h`. Test signals are compile coverage and no implicit declaration warnings for allocation or abort calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/stdlib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/string.h -->
# sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/string.h

This file is intentionally blank and serves as a kernel include shim for `string.h`. Required string functions are expected from OpenAFS kernel include sets and roken stubs, not from this file.

There are no APIs, state, or control flow. Integration is include-path compatibility for hcrypto kernel builds. Risks are missing prototypes or platform-specific string availability differences. Test signals are warning-free kernel builds and runtime tests for code paths using `memcpy`, `memset`, `strlen`, and `strcasecmp`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/krb5-types.h -->
# sources/distributed-fs/openafs/src/crypto/hcrypto/krb5-types.h

This Windows-specific compatibility header supplies C99-style integer typedefs when building under `AFS_NT40_ENV`. It maps `int8_t`, `int16_t`, `int32_t`, `int64_t`, unsigned variants, and BSD-style `u_int*_t` aliases to Microsoft `__int*` types.

There is no runtime control flow or persistence. Dependencies are `AFS_NT40_ENV` and MSVC type support. Integration is hcrypto/Heimdal code that expects fixed-width types before full stdint availability. Risks are duplicate typedefs if modern Windows builds include `stdint.h` first, and differences in signedness/width assumptions. Test signals are Windows hcrypto compile coverage and ABI checks for fixed-width crypto structs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/hcrypto/krb5-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/rfc3961/Makefile.in -->
# sources/distributed-fs/openafs/src/crypto/rfc3961/Makefile.in

This Makefile builds OpenAFS' selected Heimdal Kerberos RFC3961 crypto library. It installs `rfc3961.h`, compiles local shims `context.c` and `copy.c`, then compiles selected upstream Heimdal `krb5` crypto/data/keyblock/n-fold/store files into shared, PIC, and LWP/static archives.

Control flow is make target driven: `all` builds the installed header, shared `liboafs_rfc3961.la`, PIC archive, and `libafsrfc3961.a`; `install`/`dest` stage the static library; explicit rules compile upstream sources through `LTLWP_CCRULE`. State is generated archives, libtool objects, and installed headers.

Dependencies include hcrypto, roken, upstream Heimdal krb5 sources, OpenAFS make fragments, and warning-workaround CFLAGS for selected sources. Integration points are rxgk/security code and any Kerberos crypto consumer that uses the OpenAFS-renamed RFC3961 API. Risks include incomplete upstream source selection, algorithm lists diverging from header-advertised enctypes, and static/shared symbol conflicts. Test signals are Kerberos RFC3961 known-answer vectors and downstream link tests against hcrypto.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/rfc3961/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/rfc3961/context.c -->
# sources/distributed-fs/openafs/src/crypto/rfc3961/context.c

This file provides no-op Kerberos context and error-reporting functions required by selected Heimdal crypto code. `krb5_init_context` returns success without storing a context, `krb5_free_context` does nothing, `krb5_set_error_message` ignores formatted errors, and `krb5_abortx` returns 0.

There is no state, persistence, or meaningful control flow. Dependencies are `krb5_locl.h`, which renames these symbols for OpenAFS. Integration is RFC3961 crypto code that accepts a `krb5_context` parameter but does not need a real Kerberos library context in OpenAFS.

Risks are diagnostics and error semantics: callers get numeric errors only and no localized text; a real abort path is suppressed. Test signals are crypto operations that pass NULL/no-op contexts and verify errors are returned numerically without dereferencing context data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/rfc3961/context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/rfc3961/copy.c -->
# sources/distributed-fs/openafs/src/crypto/rfc3961/copy.c

This file supplies a few copy/free helpers from Heimdal without importing a larger dependency file. `der_copy_octet_string` allocates and copies `krb5_data`; `copy_EncryptionKey` zeroes the destination, copies keytype, and copies keyvalue; `free_Checksum` frees the checksum data.

State is heap allocation owned by the caller and freed through `krb5_data_free`. Dependencies are `krb5_locl.h`, `malloc`, `memcpy`, `memset`, `ENOMEM`, and RFC3961 data/keyblock types. Integration is upstream crypto functions that expect ASN.1 copy helpers.

Risks include zero-length allocation behavior, no cleanup of partially initialized structures beyond simple cases, and dependence on the active malloc macro in kernel builds. Test signals are keyblock copy/free tests, zero-length data tests, and failure-path tests for allocation returning NULL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/rfc3961/copy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/rfc3961/kernel/algs.c -->
# sources/distributed-fs/openafs/src/crypto/rfc3961/kernel/algs.c

This kernel-specific file limits RFC3961 algorithms to the minimal set needed in kernel space. It exports `_krb5_checksum_types` with SHA1 and AES128/AES256 HMAC-SHA1 checksum types, and `_krb5_etypes` with AES256-CTS-HMAC-SHA1 and AES128-CTS-HMAC-SHA1 encryption types. It also computes `_krb5_num_checksums` and `_krb5_num_etypes`.

There is no dynamic control flow or persistence; state is static global algorithm tables consumed by Heimdal crypto lookup routines. Dependencies are `krb5_locl.h` and upstream symbols for the selected checksum/encryption implementations.

Integration is kernel RFC3961 dispatch. Risks are unsupported enctypes/checksums being unavailable in kernel even if public headers list them, and table order affecting default/preferred algorithm selection. Test signals are kernel tests for AES128/AES256 enctypes and clean rejection of DES/ARCFOUR/MD5 paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/rfc3961/kernel/algs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/rfc3961/kernel/random.c -->
# sources/distributed-fs/openafs/src/crypto/rfc3961/kernel/random.c

This kernel adapter implements `krb5_generate_random_block` by calling `osi_readRandom(buf, len)`. It ignores any return value, matching a void Kerberos random-block API.

State is only the caller-provided output buffer. Dependencies are OpenAFS kernel includes and `rfc3961.h`. Integration is upstream RFC3961 key generation and confounder generation in kernel mode.

Risks are lack of error reporting from `osi_readRandom`; if the kernel RNG fails or returns short data, callers cannot know from this wrapper. Test signals are kernel random-block tests using instrumentation around `osi_readRandom` and crypto known-answer tests that do not require deterministic randomness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/rfc3961/kernel/random.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/rfc3961/krb5_locl.h -->
# sources/distributed-fs/openafs/src/crypto/rfc3961/krb5_locl.h

This private shim header turns selected Heimdal `krb5` crypto sources into a standalone OpenAFS RFC3961 library. It selects kernel or userspace includes, pulls hcrypto headers, imports `rfc3961.h`, configures Heimdal mutex macros, disables unused crypto families and random-file methods, defines missing Kerberos types/constants/errors, and renames many Heimdal symbols to `_oafs_h_*` to avoid clashes with external Kerberos libraries.

Important types include `EncryptedData`, `krb5_salttype`, `krb5_keytype` aliased to `krb5_enctype`, `krb5_salt`, and `krb5_crypto_iov`. Important macros include `HEIMDAL_SMALLER`, `HEIM_CRYPTO_NO_TRIPLE_DES`, `HEIM_CRYPTO_NO_ARCFOUR`, `HEIM_CRYPTO_NO_PK`, key usage values, Kerberos error constants, `ALLOC`, and symbol-renaming for crypto, data, keyblock, checksum, and n-fold functions. It also declares local prototypes used across upstream source files and kernel-only stubs for ARCFOUR and DES3 routines.

There is no runtime persistence, but it defines the ABI and link namespace for the library. Dependencies are hcrypto, roken, OpenAFS threading, and upstream `crypto.h`. Risks include macro breadth, incomplete symbol renaming, disabling algorithms while public enums still exist, and no-op mutexes under LWP assumptions. Test signals are full RFC3961 vector coverage, link tests alongside system Kerberos, and kernel/userspace builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/rfc3961/krb5_locl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/rfc3961/rfc3961.h -->
# sources/distributed-fs/openafs/src/crypto/rfc3961/rfc3961.h

This public header defines OpenAFS' RFC3961 crypto API, built from selected Heimdal Kerberos crypto pieces. It provides minimal Kerberos-compatible data, keyblock, checksum, enctype, and crypto handle types, then renames public functions to `oafs_h_*` symbols to avoid collisions.

Important types are `krb5_error_code`, `krb5_key_usage`, opaque `krb5_context` and `krb5_crypto`, `afs_heim_octet_string`/`krb5_data`, `krb5_keyblock`, `Checksum`, `krb5_cksumtype`, and `krb5_enctype`. Important functions include context init/free, enctype validation and key size queries, crypto init/destroy, encrypt/decrypt, data allocation/free, keyblock copy/free/init/zero/get-enctype, PRF/fx_cf2/random-to-key/random-block/overhead, and checksum create/verify/size/get-type.

There is no implementation state in the header; it defines ABI and enum values used on the wire. Dependencies are C size types and consumers including hcrypto-backed implementations. Risks include exposing enum values for unsupported algorithms, ABI compatibility across builds with `RFC3961_NO_ENUMS` or `RFC3961_NO_CKSUM`, and ownership expectations for allocated `krb5_data`/keyblocks. Test signals are API compile tests, encrypt/decrypt and checksum known-answer vectors for AES128/AES256, and symbol-prefix checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/crypto/rfc3961/rfc3961.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/dir/Makefile.in -->
# sources/distributed-fs/openafs/src/dir/Makefile.in

This Makefile builds and installs the OpenAFS directory package library. It compiles `buffer.o`, `dir.o`, `salvage.o`, and component version into `libdir.a`, installs `dir.h`, and runs the `test` subdirectory build.

Control flow is standard make: `all` builds library, depinstall, and tests; `depinstall` stages `dir.h`; `install` and `dest` install the library under AFS lib directories and the header under include directories; `clean` removes objects, archives, core files, and generated version files. State is the archive and installed header.

Dependencies are config make fragments, LWP settings, archive tools, and the three source files. Integration points are fileserver, volserver, salvager, and test programs that manipulate AFS directory pages. Risks are library consumers depending on external buffer I/O callbacks not visible in this Makefile, and tests only being built rather than necessarily run. Test signals are successful `libdir.a` build, `dir/test/dtest`, and downstream server links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/dir/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/dir/buffer.c -->
# sources/distributed-fs/openafs/src/dir/buffer.c

This file implements a fixed-size 2 KiB page buffer cache for AFS directory objects. Buffers are keyed by an opaque `dir_file_t` stored in an embedded fid byte array plus page number, hashed into 32 chains, protected by a global `afs_bufferLock` and per-buffer locks, and evicted by least-recently-used access time.

Important APIs are `DInit`, `DReadWithErrno`, `DRead`, `DNew`, `DRelease`, `DVOffset`, `DZap`, `DFlushVolume`, `DFlushEntry`, `DFlush`, and `DStat`; internal helpers are `bufferDir`, `FixupBucket`, and `newslot`. External integration callbacks are `FidZero`, `FidEq`, `ReallyRead`, `ReallyWrite`, `FidZap`, `FidVolEq`, and `FidCpy`.

Control flow on read first searches the hash chain, moves found buffers to the front, and increments lockers. Misses call `newslot`, which chooses an unlocked LRU buffer, writes it if dirty, zaps/copies the fid, zeros stale data, assigns the new page, and hashes it. Persistence occurs when dirty buffers are written by eviction or flush APIs. Risks include fatal `Die` on all buffers locked or write failure, access time wrap, fid layout assumptions in `pHash`, and correctness under concurrent lock transitions. Test signals are dtest operations, flush error propagation, and stress tests with small buffer counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/dir/buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/dir/dir.c -->
# sources/distributed-fs/openafs/src/dir/dir.c

This file implements the AFS on-disk directory format: 2 KiB pages, 64 32-byte directory blobs per page, page/free bitmaps, header allocation map, and 128 hash chains mapping names to fids.

Important public APIs are `afs_dir_NameBlobs`, `afs_dir_Create`, `afs_dir_Length`, `afs_dir_Delete`, `afs_dir_MakeDir`, `afs_dir_Lookup`, `afs_dir_LookupOffset`, `afs_dir_EnumerateDir`, `afs_dir_IsEmpty`, `afs_dir_GetBlobWithErrno`, `afs_dir_GetBlob`, `afs_dir_GetVerifiedBlob`, `afs_dir_DirHash`, `afs_dir_InverseLookup`, and `afs_dir_ChangeFid`. Internal helpers are `FindBlobs`, `AddPage`, `FreeBlobs`, `GetBlobWithLimit`, `FindItem`, and `FindFid`.

Control flow for create checks for duplicates, finds contiguous free blobs, writes a `DirEntry`, and links it into the hash table. Delete unlinks from a hash chain, clears the entry plus extension blobs, and updates free maps. Lookup and enumeration walk hash chains with loop bounds and verified blob reads. `MakeDir` formats page 0 and creates `.` and `..`. State persists in directory pages through `DNew`, `DRead`, and dirty `DRelease`. Risks include on-disk ABI fragility, bitmap/hash corruption, name termination validation, and caller ownership of locked buffers. Test signals are dtest create/delete/list/check/salvage workflows and salvager validation against corrupted directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/dir/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/dir/dir.h -->
# sources/distributed-fs/openafs/src/dir/dir.h

This header defines the AFS directory on-disk structures and public directory/buffer APIs. Constants define page size (`AFS_PAGESIZE` 2048), hash buckets (`NHASHENT` 128), old/new page limits (`MAXPAGES` 128, `BIGMAXPAGES` 1023), entries per page (`EPP` 64), and header-reserved entries (`DHE` 12).

Important types are `MKFid`, `PageHeader`, `DirBuffer`, `DirHeader`, `DirEntryFlex`, `DirEntry`, `DirXEntry`, `DirPage0`, `DirPage1`, and `dir_file_t` (kernel `struct dcache *`, userspace `struct DirHandle *`). It declares all `afs_dir_*` operations, buffer operations `DInit`/`DRead`/`DNew`/`DRelease`/flush/stat helpers, and userspace salvage `DirOK`/`DirSalvage`.

There is no runtime state in the header, but its layout is persistent on disk. Dependencies include `afs_int32`, `AFS_NORETURN`, and optional `HAVE_FLEXIBLE_ARRAY`. Integration is with directory library sources, fileserver, volserver, salvager, and tests. Risks are structure packing/layout changes, `DHE` needing coordinated changes in `MakeDir` and salvager, and flexible-array compatibility. Test signals are ABI/layout checks and round-trip directory operations across old/new directory formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/dir/dir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/dir/salvage.c -->
# sources/distributed-fs/openafs/src/dir/salvage.c

This file validates and repairs AFS directory files. `DirOK` determines whether a directory is definitely corrupt, and `DirSalvage` builds a fresh directory containing recoverable entries from a suspect source.

Important functions are internal `ComputeUsedPages`, public `DirOK`, and public `DirSalvage`. `DirOK` reads page 0, checks magic tags, allocation map ranges and contiguity, used page count, page freebitmap counts, hash-chain bounds, entry flags, null/too-long names, correct hash buckets, `.` at entry 13, `..` at entry 14, loop limits, and consistency between computed and stored freebitmaps. It distinguishes logical corruption from physical I/O errors through `DReadWithErrno`/`afs_dir_GetBlobWithErrno`, logging and dying for uncertain physical failures.

`DirSalvage` creates a target directory with supplied self/parent fids, reads source hash chains within valid page bounds, skips `.`/`..`, and recreates other entries until a chain becomes unrecoverable. State is persistent directory pages in the target and reads from the source. Dependencies are `dir.h`, `AFSNAMEMAX`, `Log`, `Die`, and directory APIs. Risks include best-effort salvage losing entries after chain damage, duplicate name handling, and relying on name termination. Test signals are dtest `-c` and `-s`, plus fuzzed/corrupted directory images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/dir/salvage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/dir/test/Makefile.in -->
# sources/distributed-fs/openafs/src/dir/test/Makefile.in

This Makefile builds the directory test utility `dtest`. It includes config and LWP make fragments, links `dtest.o` with `libdir.a`, `liblwp.a`, `libopr.a`, roken, and platform libraries, and defines minimal `all`, `install`, and `clean` targets.

There is no runtime state in the Makefile; build state is `dtest` and object files. Integration is the parent `src/dir` test target. Risks are that `install` only depends on `dtest` and does not stage it anywhere, and the test is built but not automatically run. Test signal is successful compilation/linking of `dtest`, which verifies the userspace callback surface required by `buffer.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/dir/test/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/dir/test/dtest.c -->
# sources/distributed-fs/openafs/src/dir/test/dtest.c

This userspace CLI exercises the directory package against flat files. Commands list (`-l`), check (`-c`), salvage (`-s`), create/fill (`-f`), delete (`-d`), lookup (`-r`), and add (`-a`) directory entries.

Important functions are command wrappers `LookupDir`, `AddEntry`, `ListDir`, `CheckDir`, `SalvageDir`, `DelTest`, `CRTest`; file helpers `OpenDir`/`CreateDir`; buffer backend callbacks `ReallyRead`, `ReallyWrite`, `FidZap`, `FidZero`, `FidEq`, `FidVolEq`, `FidCpy`; and diagnostic `Die`/`Log`. `main` initializes the directory buffer cache with 600 buffers and dispatches by the first option character.

State and persistence are test directory files opened with POSIX `open`, read/written in 2048-byte pages. `fidCounter` and `Uniq` provide simple unique ids in-process. Dependencies are `afs/dir.h`, `opr_abort`, file I/O, and varargs logging. Risks include simplistic fid equality by unique handle, no fsync, limited argument validation, and salvage continuing after failed dot lookups. Test signals are the command modes themselves and regression scripts that create, mutate, check, and salvage directory images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/dir/test/dtest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/dviced/Makefile.in -->
# sources/distributed-fs/openafs/src/dviced/Makefile.in

This Makefile builds the demand-attach fileserver `dafileserver` and `state_analyzer`. It reuses sources from `viced`, `vlserver`, `dir`, `vol`, and `fsint`, compiling with `-DRXDEBUG`, `-DFSSYNC_BUILD_SERVER`, `-DSALVSYNC_BUILD_CLIENT`, and `-DAFS_DEMAND_ATTACH_FS`.

Control flow is make target driven: explicit rules compile each borrowed object from its source directory; `dafileserver` statically links viced, directory, volume, fsint, and support libraries; `state_analyzer` links state analyzer and utility/opr libs; install/dest stage binaries into server libexec/sbin or destination tree. State is generated objects and binaries.

Dependencies include many OpenAFS libraries, hcrypto, roken, pthread/thread libs, and AIX import flags when needed. Integration is the demand-attach file server build variant and shares the directory package from this work item. Risks include object duplication across source directories, compile flags needing to match the source modules' expectations, and static link ordering. Test signals are successful `dafileserver` link, state analyzer link, demand-attach fileserver startup, volume attach/detach, fssync/salvsync interactions, and directory operations through fileserver RPCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/dviced/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/dvolser/Makefile.in -->
# sources/distributed-fs/openafs/src/dvolser/Makefile.in

This Makefile builds the demand-attach volume server `davolserver`. It compiles selected `volser`, `dir`, and `vol` sources with `-DRXDEBUG`, `-DFSSYNC_BUILD_CLIENT`, and `-DAFS_DEMAND_ATTACH_FS`, then statically links them with command, ACL, RX, rxstat, rxkad, LWP compatibility, util, opr, usd, hcrypto, roken, and platform libraries.

State is generated objects and the `davolserver` binary. Control flow is explicit make rules for each borrowed source, followed by install/dest staging to server libexec or destination server bin directories. Integration is with demand-attach volume operations, volume salvage/sync clients, and the directory package.

Risks include shared-source compile flag drift, static link ordering, and demand-attach-specific behavior depending on fssync/salvsync client definitions. Test signals are successful link, volume create/delete/dump/restore/move operations, vol_split coverage, and directory salvage operations under davolserver paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/dvolser/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/export/Makefile.in -->
# sources/distributed-fs/openafs/src/export/Makefile.in

This AIX-focused Makefile builds and installs the OpenAFS EXPORT kernel extension, export lists, and loader/configuration helpers. It generates 32-bit and 64-bit export files from AIX-version-specific `.exp` inputs, compiles `export.c`/`symtab.c` variants, links `export.ext` and `.nonfs` extensions, and builds `cfgexport`/`cfgafs` helper binaries.

Control flow is heavily conditional on `SYS_NAME`, `AIX32`, and `AIX64`. AIX 4/5/6/7 branches choose compile flags such as `__XCOFF64__`, `AFS_64BIT_KERNEL`, `AFS_AIX51_ENV`, and kernel options. Install/dest targets stage kernel modules, config helpers, and export maps to kernel and client/server destination trees. State includes generated export maps, kernel extension objects, helpers, and installed files.

Dependencies are AIX `ld`, XCOFF, kernel export/import files, OpenAFS make fragments, and `extras.exp`. Integration is AIX kernel module loading and symbol import for OpenAFS. Risks are platform-specific fragility, duplicated targets, stale AIX export lists, and 32/64-bit divergence. Test signals are AIX builds for enabled widths, load/unload of `export.ext`, and successful OpenAFS kernel extension import of missing symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/export/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/export/cfgafs.c -->
# sources/distributed-fs/openafs/src/export/cfgafs.c

This AIX userspace helper loads, initializes, terminates, and unloads the AFS kernel extension. It accepts `-a mod_file` to add and `-d mod_file` to delete, uses `sysconfig(SYS_KLOAD)`, `sysconfig(SYS_CFGKMOD)`, `SYS_KULOAD`, and persists the loaded module id in `<mod_file>.kmid`.

Important control flow: add loads the module, initializes it with `CFG_INIT`, writes the kmid file, and on init failure unloads. Delete reads and unlinks the kmid file, sends `CFG_TERM`, then unloads. On load failure it queries loader messages and execs AIX `execerror`. AIX32 installs a full-dump SIGSEGV handler for better core dumps.

Dependencies are AIX sysconfig/ldr/device APIs, `AFS_component_version_number.c`, and platform path selection for `execerror`. Integration is installation scripts and kernel extension lifecycle. Risks include fixed 256-byte path buffer, stale or missing kmid files, add and delete not being mutually exclusive if both options are supplied, and partial cleanup on failures. Test signals are add/delete cycles on AIX and kmid file lifecycle checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/export/cfgafs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/export/cfgexport.c -->
# sources/distributed-fs/openafs/src/export/cfgexport.c

This AIX userspace helper loads/configures the EXPORT kernel extension and passes it a translated kernel symbol table. It accepts `-a mod_file`, `-d mod_file`, optional `-s symbols` defaulting to `/unix`, and debug `-Z`. It persists kmid in `<mod_file>.kmid`.

Important functions are `get_syms`, `xlate_xtok`, `find_suffix`, `xsym_compar`, `dump_xsym`, `dump_ksym`, `error`, and `sys_error`. `get_syms` reads the XCOFF header, symbol table, and string table, filters external/hidden external symbols without strange names, skips aux entries, sorts symbols, uniquifies them, translates to EXPORT `sym_t` records, and fills `struct k_conf`. `xlate_xtok` builds a compact string table using suffix sharing, with 64-bit and 32-bit XCOFF handling. `main` loads the kernel module and passes `k_conf` through `SYS_CFGKMOD`.

State is allocated symbol/string tables, loaded module state, and kmid file persistence. Dependencies are AIX XCOFF, sysconfig, ldr, `export.h`, and `sym.h`. Risks include fixed `SYMBUFSIZE` behavior in 64-bit code, unchecked integer sizes, path buffer overflow, old-style varargs declarations, and symbol-table parsing fragility. Test signals are debug dumps, load/configure/unload cycles, and symbol lookup success from the kernel extension.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/export/cfgexport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/export/export.c -->
# sources/distributed-fs/openafs/src/export/export.c

This AIX kernel extension stores a kernel symbol table and exposes import helpers for kernel functions and variables missing from the normal exports list. Its entry point `export` handles `CFG_INIT` by calling `config` and `CFG_TERM` by calling `export_cleanup` under `kernel_lock`.

Important functions are `config`, `export_cleanup`, `import_kfunc`, `import_kvar`, optional `osetgroups`, and `okioctl`/`okioctl32`. `config` copies in a `struct k_conf`, validates symbol table size and 1 MiB total bound, allocates kernel memory, copies symbol and string tables from userspace, and rewrites string offsets to pointers. `import_kfunc` looks up `g_toc`/`ktoc` and the requested function, constructs an AIX function descriptor, and writes it through the caller's function pointer. `import_kvar` scans a caller TOC for a surrogate variable pointer and replaces it with the real kernel variable address under interrupt disable.

State is global `toc_syms`, `toc_nsyms`, `toc_strs`, `toc_size`, and cached `myg_toc`. Dependencies are AIX kernel APIs, `sym_lookup`, and cfgexport-provided tables. Risks are kernel-memory corruption from bad symbol data, TOC scanning without explicit bound, global state lifetime, and platform ABI assumptions. Test signals are module load/unload, importing known functions/variables, and OpenAFS kernel extension startup on AIX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/export/export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/export/export.h -->
# sources/distributed-fs/openafs/src/export/export.h

This header defines the userspace-to-kernel configuration contract and import descriptors for the AIX EXPORT extension. `struct k_conf` carries symbol count, symbol table size, string table size, and userspace addresses for both tables. `struct k_func` describes a function import destination and reserves a function descriptor. `struct k_var` describes a variable import surrogate and symbol name.

There is no runtime control flow. State is represented by these structures as passed through `SYS_CFGKMOD` or consumed by `import_kfunc`/`import_kvar`. Dependencies are AIX integer and address types such as `u_int`, `u_int64`, and `caddr_t`, plus `__XCOFF64__`/`AFS_64BIT_KERNEL` for descriptor width.

Integration is between `cfgexport.c`, `export.c`, and AIX OpenAFS kernel modules needing missing symbols. Risks are ABI mismatch between 32-bit and 64-bit builds, pointer-size assumptions, and caller responsibility for valid storage. Test signals are successful cfgexport-to-export configuration and import descriptors resolving real kernel symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/export/export.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/export/sym.h -->
# sources/distributed-fs/openafs/src/export/sym.h

This header defines the simplified symbol-table format used by the AIX EXPORT extension. `struct toc_syment` abstracts the relevant XCOFF symbol value and name/offset fields for 32-bit and 64-bit formats, with macros normalizing access to `n_name`, `n_nptr`, `n_zeroes`, and `n_offset`. It typedefs `sym_t` and declares global `toc_syms`, `toc_nsyms`, and `sym_lookup`.

There is no runtime control flow in the header, but its layout is shared persistent in-memory state between `cfgexport` translation and kernel `export` lookup. Dependencies are XCOFF width macros. Integration is `cfgexport.c`, `export.c`, and `symtab.c`.

Risks are layout drift between userspace-constructed tables and kernel interpretation, especially under `__XCOFF64__`, and macro differences hiding name-storage cases. Test signals are symbol lookup by name and address in both 32-bit and 64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/export/sym.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/export/symtab.c -->
# sources/distributed-fs/openafs/src/export/symtab.c

This file implements symbol lookup over the EXPORT extension's translated symbol table. `sym_lookup` searches by name when provided or by nearest address otherwise. Name lookup first tries the name exactly, then with `.` and `_` prefixes. Address lookup returns the symbol with the greatest value not exceeding the requested address.

Important helpers are `search`, `symsrch`, and `sym_flex`. `symsrch` prefers exact matches but accepts prefix matches. `sym_flex` copies a symbol into static storage and normalizes its name pointer into a static buffer, hiding 32-bit short-name versus string-table storage differences.

State is global `toc_syms`/`toc_nsyms` from `export.c` and static return buffers in `sym_flex`; it is not reentrant. Dependencies are string functions and `sym.h`. Integration is `import_kfunc`, `import_kvar`, and any debug/address resolution inside the AIX export module. Risks include prefix-match ambiguity, static buffer overwrite on nested/concurrent calls, truncation to 47/8 characters, and address search using `unsigned`. Test signals are lookup tests for exact, dotted, underscored, short-name, string-table, and address-nearest cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/export/symtab.c -->
