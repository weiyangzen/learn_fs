# Research Group subset-b-009534

Grouped research for `sources/test-tools/xfstests-bld/fstests-bld/popt` build-helper and hash implementation files. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/depcomp -->
# sources/test-tools/xfstests-bld/fstests-bld/popt/depcomp

## Purpose

`depcomp` is the Automake dependency-compilation wrapper vendored with the `popt` subtree inside xfstests-bld. It runs the compiler command supplied on its argv, collects compiler-generated dependency side effects, normalizes them into the dependency file named by `depfile`, and adds dummy header targets so generated make dependency includes do not fail after a header is deleted.

The source was read as a complete 630-line shell script. It is generated Autotools infrastructure rather than project-specific business logic, but it is on the critical build path for compiling the vendored `popt` library on many compilers and host platforms.

## Important APIs, Types, and Functions

The script's public interface is its command-line and environment contract:

- `depcomp [--help] [--version] PROGRAM [ARGS]` executes `PROGRAM ARGS`.
- Required environment variables are `depmode`, `source`, and `object`.
- Optional environment variables are `DEPDIR`, `depfile`, `tmpdepfile`, `libtool`, `MAKEDEPEND`, and compiler/tool variables inherited through `PROGRAM ARGS`.
- Generated defaults map an object such as `sub/bar.o` to `sub/.deps/bar.Po`; `tmpdepfile` is the same path with `.T*` suffix.

Supported `depmode` values include `gcc3`, `gcc`, `hp`, `sgi`, `aix`, `icc`, `hp2`, `tru64`, `dashmstdout`, `dashXmstdout`, `makedepend`, `cpp`, `msvisualcpp`, `msvcmsys`, and `none`. Compatibility aliases are normalized before the main `case`: `hp` becomes `gcc` with `gccflag=-M`, `dashXmstdout` becomes `dashmstdout` with `dashmflag=-xM`, and `msvcmsys` becomes `msvisualcpp` with a `sed`-based path converter instead of `cygpath`.

Important shell transformations are the `sed`, `tr`, `sort`, and `cygpath`/path-conversion pipelines that rewrite compiler-native dependency output into Makefile-compatible rules. There are no functions; each depmode stanza is a top-level branch.

## Control Flow

Startup handles empty command, `--help`, and `--version`, then validates that `depmode`, `source`, and `object` are set. It computes `depfile` and `tmpdepfile`, deletes any stale temporary dependency file, normalizes alias modes, and dispatches through the single large `case "$depmode"`.

The common control-flow shape is:

1. Invoke the compiler command with depmode-specific dependency flags or run it once before a second dependency-only pass.
2. Check the command status; on failure, remove temporary dependency files and exit with the compiler status.
3. Rewrite compiler-generated dependency output so the target is the configured `$object`.
4. Append dummy `header.h:` style rules for each dependency where the compiler mode can expose deleted-header failures.
5. Remove temporary files and exit successfully.

Fast GCC3 mode injects `-MT "$object" -MD -MP -MF "$tmpdepfile"` immediately before the `-c` argument, runs the compiler once, and renames the temporary file to the final dependency file. Older `gcc` mode uses `-Wp,-MD,...`, rewrites the target manually, and generates dummy targets. Vendor-specific modes locate compiler-specific side-effect files such as AIX `.u`, HP `foo.d`, Tru64 `.o.d`, or libtool `.libs` variants before rewriting them. `dashmstdout`, `cpp`, and `msvisualcpp` remove libtool wrappers and `-o $object` arguments, run preprocessing to stdout, and derive dependency lists from preprocessor line markers. `makedepend` strips unsupported compiler options and delegates to `${MAKEDEPEND-makedepend}`. `none` simply `exec`s the compiler command with no dependency tracking.

## State and Persistence Behavior

Persistent outputs are the final dependency file at `$depfile` and the object or compilation side effects produced by the compiler command. Transient files include `$tmpdepfile` and depmode-specific compiler byproducts such as `.u`, `.d`, `.o.d`, and `.libs/*` dependency files. The script removes temporary dependency files on successful paths and on most compiler failures.

The wrapper has no internal persistent state across invocations. Its behavior is entirely determined by environment variables, the compiler command, current working directory, filesystem layout, and tool availability. Because Makefile includes often read `*.Po`/`*.Plo` files incrementally, incomplete or stale dependency files can persist into later builds if a depmode branch fails after creating `$depfile`.

## Dependencies and Integration Points

`depcomp` integrates with Automake-generated make rules and Autoconf's dependency-mode selection. `depend.m4` expects some unreachable branch labels to exist textually, so placeholder cases such as `hp`, `dashXmstdout`, and `msvcmsys` must remain in the script even though pre-dispatch normalization prevents them from running.

The script depends on `/bin/sh`, `sed`, `tr`, `sort`, `rm`, `mv`, optional `cygpath`, optional `makedepend`, the selected compiler, and libtool argument conventions when `libtool=yes`. It is consumed by `Makefile.in`-generated compile rules for the `popt` subtree, where `$object`, `$source`, `$DEPDIR`, and `$depmode` are set by Automake.

## Risks and Edge Cases

The script is portable shell from 2009, so its quoting and text processing intentionally target old systems but still carry edge-case risk with unusual filenames. Dependency parsing is largely whitespace-oriented; paths with spaces, tabs, embedded newlines, colons, or backslashes can be misparsed, though the script has special handling for DOS drive-letter paths in some modes. Several branches rely on compiler output formats that may vary by version or vendor.

The `gcc` and aligned parser branches create dummy header rules to tolerate deleted headers, but correctness depends on the dependency list being parsed accurately. Some modes write `#dummy` if no compiler dependency file appears, which keeps Makefile includes from failing but can hide missing dependency tracking. The script deliberately removes and rewrites `$depfile`; interruption between those steps can leave a missing or partial dependency file. `none` mode bypasses tracking completely and can cause stale builds if used accidentally.

## Test Signals

Useful build signals include running `./configure` for the `popt` subtree and confirming the selected dependency mode, then compiling with `make V=1` to verify `depcomp` invocations create `.deps/*.Po` or `.Plo` files. Regression tests should cover default GCC/GCC3 flows, `libtool=yes` object names, dependency files for subdirectory objects, deleted-header rebuild behavior, missing compiler failure cleanup, `depmode=none`, and path conversion behavior on MSYS/Cygwin-style paths. A practical smoke test is to touch a header included by a `popt` C file and confirm the object rebuilds, then delete that header from the dependency file context and confirm make reports the real source failure rather than an include-file dependency parse error.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/depcomp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/install-sh -->
# sources/test-tools/xfstests-bld/fstests-bld/popt/install-sh

## Purpose

`install-sh` is a portable shell implementation of the BSD/X11 `install` utility. The vendored `popt` build uses it when a platform `install` program is absent or unsuitable, allowing generated make install rules to copy files, create directories, set modes, optionally set ownership/group, optionally strip binaries, and avoid replacing an unchanged destination when requested.

The source was read as a complete 520-line shell script. It is generated build infrastructure with direct filesystem side effects during `make install` and related Autotools workflows.

## Important APIs, Types, and Functions

The public interface is:

- `install-sh [OPTION]... [-T] SRCFILE DSTFILE`
- `install-sh [OPTION]... SRCFILES... DIRECTORY`
- `install-sh [OPTION]... -t DIRECTORY SRCFILES...`
- `install-sh [OPTION]... -d DIRECTORIES...`

Supported options are `--help`, `--version`, ignored `-c`, `-C` copy-on-change, `-d` directory creation, `-g GROUP`, `-m MODE`, `-o USER`, `-s`, `-t DIRECTORY`, `-T`, and `--` to end options. The script exposes command overrides through environment variables: `CHGRPPROG`, `CHMODPROG`, `CHOWNPROG`, `CMPPROG`, `CPPROG`, `MKDIRPROG`, `MVPROG`, `RMPROG`, `STRIPPROG`, and `DOITPROG` for dry-run style command echoing.

Important internal state variables include `mode`, `copy_on_change`, `dir_arg`, `dst_arg`, `no_target_directory`, `posix_mkdir`, `posix_glob`, `doit`, `doit_exec`, `cp_umask`, `mkdir_umask`, `dsttmp`, and `rmtmp`. There are no shell functions; behavior is organized by option parsing and a `for src` loop.

## Control Flow

The script initializes IFS, command defaults, desired file mode, and option state. It parses options, validates modes to reject whitespace and glob characters, extracts the destination argument when not using `-d` or `-t`, and exits successfully for empty `install-sh -d` calls because conditional directory variables in Makefiles can expand to nothing.

For each source or directory target, it protects leading-dash names with `./`, resolves whether the destination is a directory, computes `dstdir` with `dirname` or fallback `expr`/`sed`, and tests whether the destination directory already exists. If parent directories are missing, it first probes whether `mkdir -p` behaves safely for the current mode and umask. When that probe fails or a race occurs, it falls back to component-by-component directory creation while tolerating concurrent creators.

With `-d`, it creates/configures directories and then applies optional owner, group, and mode commands. For file installation, it sets a restrictive copy umask based on the requested mode and strip behavior, copies the source to `$dstdir/_inst.$$_`, applies owner/group/strip/chmod to the temp file, compares old and new metadata/content for `-C`, and either discards the unchanged temp or renames it into place. If the first `mv -f` fails, it removes or renames aside the existing destination and retries the move. Exit traps remove temporary files on signal or error paths.

## State and Persistence Behavior

Persistent effects are created directories, installed files, mode changes, ownership/group changes, stripped binaries, and replacement of previous destination files. Temporary files named `_inst.$$_` and `_rm.$$_` are created in the destination directory and removed by traps or explicit cleanup. `-C` preserves the previous destination file and its modification time when file type, owner, group, size metadata, and byte content match.

The script does not write configuration state. However, its filesystem changes persist outside the build tree when install prefixes point to system locations. `DOITPROG` changes execution from direct `exec` for some commands to command-printing or a caller-supplied wrapper, which is useful for dry runs but means state changes depend on the wrapper semantics.

## Dependencies and Integration Points

`install-sh` is integrated by Autoconf/Automake-generated make install rules. Its filename avoids `make` implicit-rule confusion with an `install` target. It depends on `/bin/sh`, `basename`, `dirname` when available, `expr`, `sed`, `ls`, `cmp`, `mkdir`, `cp`, `mv`, `rm`, `chmod`, optional `chown`, optional `chgrp`, and optional `strip`.

The script coordinates with generated `Makefile.in` variables such as `INSTALL`, `INSTALL_PROGRAM`, `INSTALL_DATA`, `MKDIR_P`, and install directories. It is especially relevant for old or non-GNU platforms where `mkdir -p`, `install -C`, or `install -T` behavior differs from modern GNU coreutils.

## Risks and Edge Cases

The implementation deliberately supports old shells and non-POSIX utilities, which makes path handling complex. It has protections for leading dashes and several fallback `dirname` cases, but many operations remain sensitive to unusual paths containing newlines, shell metacharacters, or aggressively nonstandard whitespace. Temporary filenames are based on `$$` in the destination directory; normal build use is low risk, but shared writable install directories can expose collision or symlink-style concerns.

Owner/group operations can fail without sufficient privilege. `strip` requires writable temporary files, so umask calculation is adjusted and can interact with unusual symbolic modes. The `-C` comparison parses `ls -dlL` output fields, which is inherently platform-sensitive. The fallback replacement path may unlink or move aside an old destination before the final move succeeds; a failure at that point can leave the target absent. Directory creation contains explicit concurrency handling, but races remain possible on unusual filesystems.

## Test Signals

Useful smoke tests include installing one data file to an explicit path, installing multiple sources into an existing directory, creating nested directories with `-d`, using `-T` against an existing directory and expecting failure, using `-C` twice and confirming the second run does not replace an identical file, and overriding `DOITPROG=echo` to inspect generated operations. Platform tests should cover requested modes `0644` and `0755`, owner/group behavior when permitted, strip behavior for binaries, concurrent directory creation, missing source and missing destination diagnostics, and paths with leading dashes or spaces to document current support limits.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/install-sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/lookup3.c -->
# sources/test-tools/xfstests-bld/fstests-bld/popt/lookup3.c

## Purpose

`lookup3.c` contains Bob Jenkins' public-domain lookup3 non-cryptographic hash implementation, adapted for conditional compilation in the vendored `popt` library. It can provide 32-bit hashes for word arrays, little-endian byte arrays, big-endian byte arrays, and paired 32-bit outputs. The introductory comments state that `jlu32l()` is the common byte-array hash, while `jlu32lpair()` returns two hashes for roughly the cost of one.

The source was read as a complete 969-line C file, including optional self-test code guarded by `_JLU3_SELFTEST`.

## Important APIs, Types, and Functions

The file includes `<stdint.h>` and relies on `size_t`; self-test builds also require standard library declarations for `time()` and `printf()` through the surrounding build configuration or compiler defaults.

Important macros and data objects are:

- `static const union _dbswap endian` detects host byte order at runtime-like compile-unit scope.
- `HASH_LITTLE_ENDIAN` and `HASH_BIG_ENDIAN` inspect the byte layout of `0x11223344`.
- `ROTL32(x, s)` performs 32-bit left rotation unless supplied externally.
- `_JLU3_INIT(h, _size)` seeds the internal state as `0xdeadbeef + size + h`.
- `_JLU3_MIX(a,b,c)` is the reversible 12-byte block mixer.
- `_JLU3_FINAL(a,b,c)` performs final avalanche-style mixing into `c`.

Public hash functions are conditionally emitted:

- `jlu32w(uint32_t h, const uint32_t *k, size_t size)` hashes an array of 32-bit words where `size` is a word count.
- `jlu32l(uint32_t h, const void *key, size_t size)` hashes a byte array using little-endian order where possible.
- `jlu32lpair(const void *key, size_t size, uint32_t *pc, uint32_t *pb)` returns two 32-bit hash values through output parameters seeded by the input values of `*pc` and `*pb`.
- `jlu32b(uint32_t h, const void *key, size_t size)` hashes byte arrays with big-endian-oriented ordering.

Defining `_JLU3_SELFTEST` automatically defines all four hash feature macros and compiles `driver1()`, `driver2()`, `driver3()`, `driver4()`, and `main()`.

## Control Flow

Each hash initializes three 32-bit accumulators `a`, `b`, and `c` from `_JLU3_INIT`; `jlu32lpair()` additionally adds the secondary seed `*pb` into `c`. Null input pointers short-circuit: `jlu32w()` and `jlu32l()` return the initialized `c`, `jlu32lpair()` stores initialized `c` and `b` through its outputs, while `jlu32b()` returns the original seed `h`.

For full blocks, the functions consume 12 bytes or three 32-bit words at a time, add them into `a`, `b`, and `c`, then call `_JLU3_MIX()`. Tail processing is branch-heavy and specialized:

- `jlu32w()` handles up to three remaining words and calls `_JLU3_FINAL()` when at least one word remains.
- `jlu32l()` and `jlu32lpair()` choose among aligned little-endian 32-bit reads, half-aligned little-endian 16-bit reads, or byte-by-byte assembly. The aligned non-`VALGRIND` tails intentionally read a full word and mask unused bytes for speed.
- `jlu32b()` chooses aligned big-endian 32-bit reads when possible, otherwise assembles bytes manually in big-endian order.

After non-empty tail handling, `_JLU3_FINAL()` is applied and `c` is returned as the primary hash. `jlu32lpair()` also returns `b` as the secondary hash. The self-test `main()` runs timing, avalanche, alignment/overread, and zero-length repeated-hash checks, then returns `1`.

## State and Persistence Behavior

The hash functions are deterministic and mostly pure: they read caller-provided memory and return values, with `jlu32lpair()` mutating only `*pc` and `*pb`. The only file-scope state is immutable endian-detection data. There is no allocation, file I/O, caching, or persistent state.

Self-test builds write diagnostics to stdout and use local stack buffers. They do not persist files or modify global state, but their `main()` changes the compilation unit from a library source into a standalone test program.

## Dependencies and Integration Points

The implementation integrates through preprocessor feature macros that select which symbols are compiled. In popt-derived trees, these functions are commonly used by popt's lookup/filter code; the surrounding build may rename symbols or define only the needed `_JLU3_*` feature macros to avoid exporting unused functions.

The code depends on C integer wraparound semantics for `uint32_t`, predictable byte widths for `uint8_t`/`uint16_t`/`uint32_t`, and host behavior for unaligned reads only when alignment checks permit the cast path. The `VALGRIND` macro switches tail code away from deliberate masked overreads so memory-checking builds can run cleanly.

## Risks and Edge Cases

The hash is explicitly not cryptographic. It should not be used for adversarial hash flooding protection, authentication, signatures, or any security boundary where collisions matter. The recommended use is hash table lookup or IDs where a random 32-bit or paired 64-bit collision rate is acceptable.

Endian and alignment paths are performance-sensitive and easy to break. The non-`VALGRIND` aligned tail code deliberately reads past the logical key length but masks unused bytes; this assumes the extra bytes live in the same accessible aligned word. It can still be reported by memory checkers and can be unsafe on unusual memory-mapped boundaries. Strict-aliasing and unaligned-access concerns are mitigated by alignment checks and byte fallbacks but remain important for compiler settings and non-mainstream architectures.

There is an apparent syntax defect in the `VALGRIND` branch of `jlu32l()` at the `case 12` line where `a+=k[0]` is missing a semicolon before `break`; this path only compiles when `VALGRIND` and `_JLU3_jlu32l` are defined. The self-test code uses `time_t` and `printf()` without visible includes in this file, so standalone self-test compilation may need additional includes or permissive compiler settings depending on the surrounding build.

## Test Signals

Core test signals are deterministic hash-vector checks for empty input, one-byte through twelve-byte tails, longer multi-block inputs, null pointer behavior, repeated seeding, and paired-hash output. Platform coverage should exercise little-endian aligned 32-bit reads, little-endian half-aligned reads, byte fallback paths, and big-endian behavior where available.

Memory-safety signals include running with `VALGRIND` defined under Valgrind or sanitizers, testing buffers positioned at the end of an allocation/page, and verifying no bytes beyond the logical key affect the result. Build signals include compiling each conditional API macro combination used by popt, compiling `_JLU3_SELFTEST`, and ensuring the self-test drivers report no avalanche or alignment errors. Integration tests should verify any popt data structure using `jlu32lpair()` remains stable across compiler optimization levels and target architectures.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/popt/lookup3.c -->
