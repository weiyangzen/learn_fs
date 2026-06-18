# Research: subset-b-006329

This grouped report covers the requested files under `sources/distributed-fs/ceph-client/scripts`. Each file section is delimited for deterministic split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/srcpos.c -->
# sources/distributed-fs/ceph-client/scripts/dtc/srcpos.c

Purpose: Implements dtc source-file stack management, include search paths, dependency-file emission, parser source location tracking, and formatted source-position diagnostics. It is the runtime backing for the `srcpos.h` parser location type.

Important APIs/functions: `srcfile_relative_open()` opens stdin or searches current source directory plus added include paths. `srcfile_push()` and `srcfile_pop()` maintain nested include state with `MAX_SRCFILE_DEPTH`. `srcfile_add_search_path()` appends include directories. `srcpos_update()` advances line/column counters for lexer text. `srcpos_copy()`, `srcpos_extend()`, and `srcpos_free()` manage location chains. `srcpos_string()`, `srcpos_string_first()`, `srcpos_string_last()`, `srcpos_error()`, and `srcpos_verror()` format diagnostics and annotations. `srcpos_set_line()` supports preprocessor line directives.

Control flow: parsing starts with `srcfile_push()`, which opens the file, records dirname, initializes line/column, links the previous file state, and seeds the initial path for shorter annotations. The lexer calls `srcpos_update()` for consumed text. Includes push another `srcfile_state`; popping restores the previous file. Diagnostics walk `srcpos` chains and shorten filenames relative to the initial source where possible.

State/persistence: Uses process-global `depfile`, `current_srcfile`, include search list, include depth, initial source path, and `initial_cpp`. `srcfile_pop()` intentionally leaks `srcfile_state` structures because parser location records may still reference them. Dependency output appends escaped paths to `depfile`.

Dependencies/integration: Depends on dtc allocation/error helpers from `util.h`, parser globals from generated lexer/parser, libc file I/O, and DTC global annotation settings through callers. It supplies `YYLTYPE` state consumed by the parser and annotation output in `treesource.c`.

Risks: Global mutable state is not reentrant. Closing stdin in `srcfile_pop()` can surprise embedding contexts when input is `-`. `shorten_to_initial_path()` assumes `initial_path` has been set before comment formatting. Location lifetime relies on intentional leaks. Include recursion is bounded but include path nodes are also never freed.

Test signals: Exercise nested includes, dependency-file output with paths containing spaces, stdin input, preprocessor line changes, multi-line tokens, annotation levels, and include-depth failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/srcpos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/srcpos.h -->
# sources/distributed-fs/ceph-client/scripts/dtc/srcpos.h

Purpose: Declares dtc source file and source position structures plus parser-location helpers.

Important APIs/types: `struct srcfile_state` stores `FILE *`, full name, directory, line/column, and previous include frame. `struct srcpos` stores first/last line and column, source file pointer, and optional chained positions. `YYLTYPE` aliases `struct srcpos`. `YYLLOC_DEFAULT` merges parser rule locations. The header exports source-file stack, include search, source position formatting, error reporting, and line reset functions.

Control flow: Generated Bison parser uses `YYLLOC_DEFAULT` to form a current location from child rule locations, setting `next` to `NULL`. Lexer/parser code calls exported functions implemented in `srcpos.c`.

State/persistence: Exposes global `depfile` and `current_srcfile`, so parser and lexer code directly share source state. `srcpos` objects may reference copied or leaked `srcfile_state` records.

Dependencies/integration: Includes `util.h` for attributes and allocation/error helpers. Integrated with dtc parser grammar, lexer, and tree annotation output.

Risks: The public globals make state coupling implicit. The `YYLLOC_DEFAULT` macro sets `file` from the last RHS symbol for non-empty rules, which can matter for mixed include-origin constructs. Header users must free strings returned by formatting functions.

Test signals: Parser location tests should verify empty and non-empty grammar rule locations, chained positions, and correct file attribution across includes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/srcpos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/treesource.c -->
# sources/distributed-fs/ceph-client/scripts/dtc/treesource.c

Purpose: Converts DTS source text into `dt_info` by invoking the dtc parser, and serializes a device tree back to DTS source form.

Important APIs/functions: `dt_from_source()` initializes parser globals, pushes the source file, assigns `yyin` and `yylloc.file`, runs `yyparse()`, and returns `parser_output`. `dt_to_source()` emits `/dts-v1/`, optional `/plugin/`, reserve entries, and recursively writes the node tree. `property_add_marker()` and `add_phandle_marker()` enrich property values with type, label, and phandle markers used for formatting.

Control flow: Serialization calls `write_tree_source_node()` recursively. Properties go through `write_propval()`, which ensures type markers exist with `guess_type_markers()`, then emits strings, byte arrays, integer cells, phandle references, labels, delimiters, and optional source annotations. Marker insertion preserves ordering invariants so formatting can walk a single marker list.

State/persistence: Uses global `parser_output` and `treesource_error` for parser communication. It reads global `annotate` and `quiet` settings. It mutates property marker lists when guessing types and adding phandle markers.

Dependencies/integration: Depends on dtc core tree structures, marker macros, libfdt byte-load helpers, source-position formatting, parser globals, and node lookup by phandle. It is one output backend selected by dtc front-end code.

Risks: Guessing value types can change property marker state and may not preserve an exact original textual representation. `add_phandle_marker()` only handles 4-byte cells and warns for missing referenced nodes. Formatting assumes marker invariants and valid type marker lengths. Parser globals are not reentrant.

Test signals: Round-trip DTS to source for strings, string lists, bytes, 16/32/64-bit cells, labels, memreserve labels, plugin flag, phandle labels and absolute paths, annotations, and malformed phandle offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/treesource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/update-dtc-source.sh -->
# sources/distributed-fs/ceph-client/scripts/dtc/update-dtc-source.sh

Purpose: Maintainer script for importing an upstream dtc snapshot into the Linux tree copy under `scripts/dtc`.

Important APIs/commands: `get_last_dtc_version()` derives the last imported upstream tag from git log. The script builds and checks upstream dtc, copies selected dtc, libfdt, and fdtoverlay files, rewrites libfdt includes from angle brackets to quoted local includes, stages files, and creates an editable signed-off git commit.

Control flow: Starts in the Linux tree, computes sibling `../dtc` and local `scripts/dtc` paths, captures the previous import, runs `make clean` and `make check` in upstream, copies manifest files into the kernel copy, applies `sed` include fixups, assembles a commit message with `git describe` and upstream log, and invokes `git commit -e -v -s`.

State/persistence: Mutates the working tree and git index, then creates a commit. It relies on current directory and adjacent upstream checkout layout.

Dependencies/integration: Uses git, make, cp, sed, and shell. It integrates Linux's vendored dtc copy with upstream dtc/libfdt.

Risks: `set -e` stops on command failures, but comments note upstream `make check` historically may not fail for test failures. Paths are unquoted and assume no spaces. It does not build/test the copied kernel-tree dtc. The commit message needs manual editing.

Test signals: Run from a throwaway Linux worktree with an adjacent dtc checkout; verify copied file list, include rewrites, staged paths, commit message range, and failure behavior when upstream build or copy fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/update-dtc-source.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/util.c -->
# sources/distributed-fs/ceph-client/scripts/dtc/util.c

Purpose: Implements shared dtc utility functions for allocation-backed strings, path printing, device-tree blob file I/O, escape decoding, data formatting, type option decoding, version output, and standardized usage output.

Important APIs/functions: `fprint_path_escaped()`, `xstrdup()`, `xstrndup()`, `xasprintf()`, `xasprintf_append()`, `join_path()`, `util_is_printable_string()`, `get_escape_char()`, `utilfdt_read_err()`, `utilfdt_read()`, `utilfdt_write_err()`, `utilfdt_write()`, `utilfdt_decode_type()`, `utilfdt_print_data()`, `util_version()`, and `util_usage()`.

Control flow: File reads grow a buffer by doubling until `read()` returns zero; writes use `fdt_totalsize()` and loop until all bytes are written. Escape decoding dispatches C-style escapes, octal, and hex. `util_usage()` aligns long options before printing help and exits success or failure depending on `errmsg`.

State/persistence: No long-lived mutable module state. Functions allocate caller-owned buffers and write to stdin/stdout/stderr or named files. `util_version()` and `util_usage()` terminate the process.

Dependencies/integration: Depends on libc/POSIX, `libfdt.h`, `version_gen.h`, and declarations from `util.h`. Used broadly by dtc and libfdt command-line utilities.

Risks: `utilfdt_read_err()` stores the buffer capacity in `*len`, not the final bytes read, which callers must understand. It closes fd 0 when reading `-`. `xavsprintf_append()` returns `strlen(p)`, which can truncate conceptual length for embedded NUL text. `utilfdt_decode_type()` has documented TODOs for 8-byte and octal formats.

Test signals: Cover escaped characters, invalid `\x`, printable string lists, binary data formatting, stdin/stdout I/O, partial writes, invalid format strings, help alignment, and version output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/util.h -->
# sources/distributed-fs/ceph-client/scripts/dtc/util.h

Purpose: Public utility header for dtc support code, including compiler attributes, fatal error handling, allocation wrappers, string helpers, libfdt I/O helpers, option-parsing helpers, and usage macros.

Important APIs/types: Defines `PRINTF`, `NORETURN`, `ARRAY_SIZE`, stringification macros, inline `die()`, `xmalloc()`, and `xrealloc()`. Declares string, path, escape, FDT read/write, data print, version, and usage functions. Provides `USAGE_COMMON_*`, `usage(errmsg)`, `util_getopt_long()`, and `case_USAGE_COMMON_FLAGS` helpers.

Control flow: Header inlines allocation failure into process termination via `die()`. getopt helpers assume local variables named `argc`, `argv`, and `usage_*`.

State/persistence: No state, but `die()`, `util_version()`, and `util_usage()` exit the process. Allocation wrappers return heap memory that callers own.

Dependencies/integration: Includes standard headers and `getopt.h`. Used by dtc C files and libfdt utilities for consistent error handling and CLI behavior.

Risks: Macros assume naming conventions and can obscure control flow because common option cases do not `break` after exit-only calls. Allocation wrappers cannot represent recoverable allocation failure. `PRINTF` format selection has platform-specific behavior for MinGW.

Test signals: Compile under GCC and non-GCC-like compilers, exercise shared CLI common options, and verify format-attribute warnings on supported toolchains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/version_gen.h -->
# sources/distributed-fs/ceph-client/scripts/dtc/version_gen.h

Purpose: Generated-style header carrying the dtc version string compiled into utilities.

Important APIs/types: Defines `DTC_VERSION` as `"DTC 1.7.2-g53373d13"`.

Control flow: No executable logic. Included by `util.c` for `util_version()`.

State/persistence: Compile-time constant only.

Dependencies/integration: Part of the vendored dtc source update flow; should match the imported upstream dtc snapshot.

Risks: If stale, `dtc -v` style output misreports the imported version. Since it is one line, merge conflicts or missed updates are easy to overlook.

Test signals: Build dtc tools and check version output against the intended upstream commit/tag.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/version_gen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/yamltree.c -->
# sources/distributed-fs/ceph-client/scripts/dtc/yamltree.c

Purpose: Emits a dtc `dt_info` tree as YAML using libyaml events.

Important APIs/functions: `dt_to_yaml()` sets up the YAML emitter and writes a stream/document containing the root tree. `yaml_tree()` recursively emits node mappings. `yaml_propval()` writes property name/value pairs. `yaml_propval_int()` emits typed integer sequences tagged `!u8`, `!u16`, `!u32`, or `!u64`, marking phandles as `!phandle`. `yaml_propval_string()` emits ASCII strings.

Control flow: `dt_to_yaml()` emits stream/document/sequence delimiters, calls `yaml_tree()`, then closes and deletes the emitter. Each node emits properties first, then child nodes keyed by name. Property values require markers; boolean properties emit YAML `true`, other properties emit a flow sequence of typed chunks.

State/persistence: No persistent module state other than `yaml_error_name`. It writes to the supplied `FILE *` and aborts with `die()` on emitter failures or invalid assumptions.

Dependencies/integration: Depends on libyaml, dtc tree and marker structures, `srcpos.h` indirectly through dtc structures, and byte-load helpers. It is an output backend selected by dtc front-end code.

Risks: Dies if a non-empty property has no markers. `yaml_propval_string()` asserts all bytes are 7-bit ASCII and NUL terminated. YAML output depends on marker correctness and does not represent deleted nodes.

Test signals: Emit YAML for boolean properties, strings, integer widths, phandles, nested nodes, deleted nodes, and non-ASCII or markerless values to validate expected failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/yamltree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dummy-tools/dummy-plugin-dir/include/plugin-version.h -->
# sources/distributed-fs/ceph-client/scripts/dummy-tools/dummy-plugin-dir/include/plugin-version.h

Purpose: Empty placeholder header used by dummy compiler tooling so Kconfig checks for GCC plugin header availability can succeed.

Important APIs/types: None; the file has zero lines.

Control flow: No logic. Its existence is the behavior.

State/persistence: None.

Dependencies/integration: Returned indirectly by `scripts/dummy-tools/gcc -print-file-name=plugin`, which points at `dummy-plugin-dir`; Kconfig tests for `include/plugin-version.h`.

Risks: If removed or relocated, `HAVE_GCC_PLUGINS`/`GCC_PLUGINS` visibility tests under dummy tools may fail. Because it is empty, it cannot support actual plugin compilation.

Test signals: `make CROSS_COMPILE=scripts/dummy-tools/ oldconfig` should see the path as existing for plugin capability probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dummy-tools/dummy-plugin-dir/include/plugin-version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dummy-tools/gcc -->
# sources/distributed-fs/ceph-client/scripts/dummy-tools/gcc

Purpose: Dummy compiler shim that makes Kconfig compiler feature probes succeed when preparing broad kernel configurations without a real target toolchain.

Important APIs/functions: Shell function `arg_contain()` tests whether an option is present. Special cases implement `--version`, `-E` preprocessing for GCC version macros, `-Wa,--version`, `-S` probes for stack protector and PowerPC checks, `-print-file-name=plugin`, and inverted failure for `-D__SIZEOF_INT128__=0`.

Control flow: The script checks recognized probe patterns in order and emits minimal expected output or exits with expected status. Most unrecognized invocations fall through to exit status 0 with no output.

State/persistence: Stateless. It reads stdin for preprocessing and emits probe-specific text to stdout/stderr.

Dependencies/integration: Used as `CROSS_COMPILE=scripts/dummy-tools/`, so kernel build checks invoke this as a compiler. Integrates with scripts such as `cc-version.sh`, Kconfig `cc-option`, GCC plugin path probing, assembler version probing, and arch capability scripts.

Risks: It intentionally lies about feature support and must not be used for real compilation. Probe-specific output can become stale as Kbuild checks evolve. `readlink -f` may vary on non-GNU hosts.

Test signals: Run representative Kbuild probes for version, preprocessing macros, assembler version, stack protector, PowerPC profile/patchable entry, plugin path, and int128 negative check.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dummy-tools/gcc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dummy-tools/ld -->
# sources/distributed-fs/ceph-client/scripts/dummy-tools/ld

Purpose: Dummy linker shim that succeeds for Kconfig/build capability probes and reports a GNU-like version when asked.

Important APIs/functions: `arg_contain()` scans arguments. `--version` or `-v` prints `GNU ld (scripts/dummy-tools/ld) 2.50`.

Control flow: Handles version probes, otherwise exits successfully with no output.

State/persistence: Stateless.

Dependencies/integration: Used through `CROSS_COMPILE=scripts/dummy-tools/` for linker feature/version tests.

Risks: It does not link anything, so any workflow that proceeds to real build actions with dummy tools will produce false success or missing outputs.

Test signals: Verify `scripts/dummy-tools/ld --version`, `-v`, and arbitrary unsupported options all exit as Kconfig expects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dummy-tools/ld -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dummy-tools/nm -->
# sources/distributed-fs/ceph-client/scripts/dummy-tools/nm

Purpose: Dummy `nm` shim for build/Kconfig probes.

Important APIs/functions: Same `arg_contain()` pattern as dummy `ld`; version probes print `GNU nm (scripts/dummy-tools/nm) 2.50`.

Control flow: Emits GNU-like version only for `--version` or `-v`; all other invocations succeed silently.

State/persistence: Stateless.

Dependencies/integration: Part of the dummy cross-toolchain prefix used to expose broad configuration options.

Risks: Produces no symbol table output, so it only suits probes that inspect exit status or version.

Test signals: Version and silent-success probe invocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dummy-tools/nm -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dummy-tools/objcopy -->
# sources/distributed-fs/ceph-client/scripts/dummy-tools/objcopy

Purpose: Dummy `objcopy` shim for build/Kconfig probes.

Important APIs/functions: Uses `arg_contain()` and emits `GNU objcopy (scripts/dummy-tools/objcopy) 2.50` for version probes.

Control flow: Handles `--version`/`-v`; otherwise exits success without transforming files.

State/persistence: Stateless and does not create output files.

Dependencies/integration: Used by dummy cross-toolchain mode for capability discovery.

Risks: Any real build step requiring output files will fail later or consume stale files because this script does nothing.

Test signals: Version output and behavior when passed typical `objcopy` arguments by Kbuild probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dummy-tools/objcopy -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dummy-tools/pahole -->
# sources/distributed-fs/ceph-client/scripts/dummy-tools/pahole

Purpose: Dummy `pahole` version reporter for Kconfig/BTF capability probes.

Important APIs/functions: Prints `v99.99`.

Control flow: Always prints the version string and exits with shell success.

State/persistence: Stateless.

Dependencies/integration: Lets configuration probes believe a sufficiently new `pahole` exists.

Risks: It cannot generate BTF data. Real build use will not produce expected artifacts.

Test signals: Invoke with or without version-like arguments and verify Kconfig version parsing sees a high version.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dummy-tools/pahole -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dummy-tools/python3 -->
# sources/distributed-fs/ceph-client/scripts/dummy-tools/python3

Purpose: Dummy `python3` executable for probes that only need command success.

Important APIs/functions: Runs `true`.

Control flow: Ignores all arguments and exits success.

State/persistence: Stateless.

Dependencies/integration: Part of dummy tooling used by configuration generation.

Risks: Does not execute Python. Any script expecting output, file creation, or validation will silently get no behavior.

Test signals: Probe commands that check only for Python availability should pass; commands that require generated files should be excluded from dummy-tool workflows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dummy-tools/python3 -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/elf-parse.c -->
# sources/distributed-fs/ceph-client/scripts/elf-parse.c

Purpose: Maps an ELF file read/write and initializes a global endian/class dispatch table for generic ELF header, section, symbol, and relocation accessors.

Important APIs/functions: `elf_map()` maps and validates a file, initializes `elf_parser`, and returns the mapping. `elf_unmap()` unmaps it. `elf_map_machine()` returns `e_machine`. `elf_map_long_size()` returns 4 or 8 from ELF class. Internal `map_file()` uses `open`, `fstat`, and shared writable `mmap`; `elf_parse()` validates magic/version/type and assigns accessor callbacks.

Control flow: `elf_map()` calls `map_file()`, then `elf_parse()`. `elf_parse()` first sets endian read/write functions from `EI_DATA`, validates ELF magic/current version, verifies allowed type bitmask, then selects ELF32 or ELF64 field accessor functions and checks header and section header sizes.

State/persistence: Global `struct elf_funcs elf_parser` is overwritten for each mapped file. Mappings are `MAP_SHARED` and writable, so relocation writes through accessors can persist to the file.

Dependencies/integration: Paired with `elf-parse.h`; used by kernel scripts that need endian/class-neutral ELF access. Depends on POSIX mmap/stat/open and `<elf.h>`.

Risks: Not reentrant for multiple simultaneous ELF files with different class/endian because the parser dispatch table is global. `map_file()` returns `MAP_FAILED` rather than `NULL` if mmap fails after printing, which callers treat as non-null unless parsing fails; this is a notable edge risk. Minimal bounds checking trusts header offsets and sizes after initial validation.

Test signals: Map valid/invalid ELF32 and ELF64, little and big endian, disallowed type masks, non-regular files, corrupt header sizes, and mmap failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/elf-parse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/elf-parse.h -->
# sources/distributed-fs/ceph-client/scripts/elf-parse.h

Purpose: Provides endian- and class-neutral ELF accessor types and inline functions backed by the global `elf_parser` dispatch table.

Important APIs/types: Defines union wrappers `Elf_Ehdr`, `Elf_Shdr`, `Elf_Sym`, and `Elf_Rela`; declares `struct elf_funcs` function pointers; exports `elf_map()`, `elf_unmap()`, `elf_map_machine()`, and `elf_map_long_size()`. Inline accessors cover ELF header section fields, section header fields, symbol fields, relocation fields and writes, and endian read/write helpers.

Control flow: After `elf_map()` initializes `elf_parser`, callers use generic helpers such as `ehdr_shoff()`, `shdr_size()`, `sym_value()`, and `rela_write_addend()` without branching on class or endian.

State/persistence: All inline generic accessors depend on process-global `elf_parser`; using them before successful `elf_map()` or after mapping a second file with different attributes is unsafe.

Dependencies/integration: Includes `<elf.h>` and kernel tools byte-shift helpers. Integrated with `elf-parse.c` and scripts manipulating ELF relocation/symbol data.

Risks: The header defines `SHDR_WORD` twice identically, which is harmless but brittle. Several accessors cast relocation field addresses to unaligned integer pointers and rely on byte-shift helpers. `compare_extable` is in the dispatch struct but not initialized in this file.

Test signals: Compile users with both 32/64-bit ELF files, verify all accessors match readelf output, and test relocation addend writes on endian variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/elf-parse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/extract-fwblobs -->
# sources/distributed-fs/ceph-client/scripts/extract-fwblobs

Purpose: Extracts built-in firmware blobs from a non-stripped `vmlinux`.

Important APIs/commands: Uses `readelf -SW` to find `.rodata` address and file offset, `readelf -sW` plus awk to pair firmware start/end symbols, shell arithmetic to compute file offsets and sizes, and `dd` with byte skip to write each firmware file.

Control flow: Validates one argument, derives `.rodata` mapping, builds entries from symbol stream when `fw_end` is seen after a start symbol, strips `_fw_` prefix and `_bin` suffix from symbol names, computes offset/size, and writes `./${FW_NAME}`.

State/persistence: Writes extracted firmware files into the current directory. No temp files.

Dependencies/integration: Depends on bash, readelf, awk, dd, and Linux built-in firmware symbol naming conventions.

Risks: Assumes firmware symbols appear in start/end order in readelf output. Filename derivation trusts symbol names. It does not check `.rodata` discovery or duplicate names robustly. Firmware output can overwrite existing files.

Test signals: Run on a known non-stripped vmlinux with built-in firmware and compare extracted bytes/sizes; test missing argument, stripped image, no firmware symbols, and existing output names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/extract-fwblobs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/extract-ikconfig -->
# sources/distributed-fs/ceph-client/scripts/extract-ikconfig

Purpose: Extracts embedded `.config` data from a kernel image built with `CONFIG_IKCONFIG`.

Important APIs/functions: `dump_config()` locates the `IKCFG_ST` gzip signature and pipes from that offset through `zcat`. `try_decompress()` scans for compression magic, decompresses candidate streams into a temp file, and retries `dump_config()`.

Control flow: Validates exactly one non-empty image argument, creates `/tmp/ikconfig$$.*` temp files with a cleanup trap, first tries direct extraction, then tries gzip, xz, bzip2, lzma, lzop, lz4, and zstd container signatures. On success it prints config and exits 0; otherwise prints a failure message and exits 1.

State/persistence: Uses predictable `/tmp/ikconfig$$.1` and `.2` temp files removed on exit. Writes config to stdout.

Dependencies/integration: Shell, `tr`, `grep -abo`, `tail`, `zcat`, and optional decompressor commands. Used by developers/debug scripts to recover kernel configs.

Risks: Predictable temp filenames can collide in unusual same-PID namespace scenarios. Missing decompressors are silently skipped via redirected errors. Magic scanning can false-positive and repeatedly invoke decompressors. It assumes gzip-wrapped config format.

Test signals: Test uncompressed object/image, each supported compressed wrapper, missing config, invalid args, and images with multiple compression magic candidates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/extract-ikconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/extract-module-sig.pl -->
# sources/distributed-fs/ceph-client/scripts/extract-module-sig.pl

Purpose: Extracts selected portions of an appended Linux kernel module signature.

Important APIs/functions: Reads an entire module, validates the magic string `~Module signature appended~\n`, unpacks the 12-byte descriptor with `unpack("CCCCCxxxN", ...)`, slices signer name, key id, signature/PKCS#7 message, unsigned module, and full signature trailer. Options are `-0`, `-a`, `-d`, `-n`, `-k`, and `-s`.

Control flow: Validates two arguments, reads the module in binary mode, checks minimum length, finds the magic at EOF, backs up over descriptor and variable-length name/key/signature regions, prints diagnostics to stderr, and writes the requested binary or textual part to stdout.

State/persistence: No persistent state. Reads whole input into memory and writes requested output to stdout.

Dependencies/integration: Perl core only. Integrated with module signing diagnostics and tooling.

Risks: Unknown option values fall through without explicit error after parsing, producing no output. Entire module read can be large. It trusts descriptor lengths after one aggregate bounds check.

Test signals: Signed module fixtures for each output part, unsigned/too-short module, PKCS#7 id type warnings for name/key, unsupported id type, and malformed descriptor lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/extract-module-sig.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/extract-sys-certs.pl -->
# sources/distributed-fs/ceph-client/scripts/extract-sys-certs.pl

Purpose: Extracts the built-in system certificate list from `vmlinux` into a keyring file.

Important APIs/functions: Parses `objdump -h` section rows into VMA/file-offset metadata, parses `nm` or optional System.map symbols, locates `__cert_list_start` and `system_certificate_list_size`, reads the list size from the image, validates section containment, then copies the certificate bytes to the output file.

Control flow: Validates either `<vmlinux> <keyring>` or `-s <System.map> <vmlinux> <keyring>`, builds section and symbol tables, falls back to System.map if `nm` has no symbols, verifies required symbols, finds the containing section, computes file offsets with `Math::BigInt`, reads bytes, and writes the keyring file.

State/persistence: Writes the output keyring file. Uses in-memory section and symbol tables.

Dependencies/integration: Perl, `Math::BigInt`, `Fcntl`, `objdump`, `nm`, and optionally System.map. Used in certificate extraction workflows where vmlinux contains key material.

Risks: Parses human-readable binutils output with regexes. Size is read as native unsigned long via `unpack 'L!'`, so cross-width/cross-endian assumptions matter. Output file is overwritten. Diagnostic messages go to stdout and stderr mixed through `die`.

Test signals: vmlinux with symbols, extract-vmlinux output plus System.map fallback, missing symbols, cert spanning a section boundary, 32/64-bit host width behavior, and short read/write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/extract-sys-certs.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/extract-vmlinux -->
# sources/distributed-fs/ceph-client/scripts/extract-vmlinux

Purpose: Extracts an uncompressed `vmlinux` image from a compressed kernel image or emits an already uncompressed image.

Important APIs/functions: `check_vmlinux()` accepts files identified by `file` as Linux boot executables or by successful `readelf -h`. `try_decompress()` scans for compression magic, tails from candidate offsets through a decompressor into a temp file, then checks the result.

Control flow: Validates one image argument, creates a temp file with `mktemp`, tries gzip, xz, bzip2, lzma, lzop, lz4, and zstd offsets, then checks the original file. On success it cats the uncompressed image to stdout and reports method/offset to stderr; otherwise prints failure and exits nonzero by falling off shell end after echo.

State/persistence: Uses one temp file removed by trap. Writes binary image to stdout.

Dependencies/integration: Shell, `file`, `readelf`, `tr`, `grep`, `tail`, and optional decompressors. Used for debugging and certificate/config extraction.

Risks: Magic scanning can false-positive. Missing decompressors are hidden by redirected errors. Binary output and stderr status must be redirected correctly by callers. It only validates enough to identify an ELF/kernel image.

Test signals: Known compressed formats, already uncompressed vmlinux, invalid image, missing decompressor, and images with multiple embedded compression streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/extract-vmlinux -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/extract_xc3028.pl -->
# sources/distributed-fs/ceph-client/scripts/extract_xc3028.pl

Purpose: Extracts XC2028/XC3028 firmware blobs from specific Windows driver files and writes Linux firmware files `xc3028-v24.fw` and/or `xc3028-v27.fw`.

Important APIs/functions: `verify()` checks driver md5 hashes. `get_hunk()` reads exact byte ranges. `write_le16()`, `write_le32()`, and `write_le64()` emit little-endian metadata. `write_hunk()` copies raw bytes. `write_hunk_fix_endian()` copies firmware bytecode while swapping two-byte length words and payloads. `main_firmware_24()` and `main_firmware_27()` encode hard-coded descriptor tables and source offsets. `extract_firmware()` chooses available source drivers and invokes generation.

Control flow: If `UDXTTM6000.sys` exists, verifies the v2.4 hash, opens it, writes a padded firmware name, version 516, descriptor count 77, and many descriptors. If `hcw85bda.sys` exists, verifies the v2.7 hash, writes version 519 and 80 descriptors. Each descriptor writes type, id, optional IF frequency, size, and byte range payload. The script prints `Firmwares generated.` at the end even if no source file was present.

State/persistence: Reads fixed source filenames from the current directory. Writes firmware output files in the current directory. Uses global Perl filehandles `INFILE` and `OUTFILE` and global debug flag.

Dependencies/integration: Perl, `md5sum`, exact vendor driver file versions, and Linux firmware loader expectations for descriptor format.

Risks: The descriptor table is hard-coded and fragile; offset or size mistakes corrupt firmware. `use strict` is commented out, increasing typo risk. It relies on external `md5sum` via shell command string. It does not fail when neither source file exists. Output files are overwritten.

Test signals: Hash verification against known driver files, generated firmware md5/size comparison with known-good outputs, no-source behavior, short read failure, and descriptor count consistency with emitted descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/extract_xc3028.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/faddr2line -->
# sources/distributed-fs/ceph-client/scripts/faddr2line

Purpose: Resolves kernel stack dump `function+offset[/size]` entries to source lines, handling KASLR-style function-relative addresses and inline call chains better than direct `addr2line`.

Important APIs/functions: `run_readelf()` captures ELF header, section headers, and symbols. `check_vmlinux()` detects EXEC/DYN vmlinux. `init_addr2line()` starts a persistent `addr2line` coprocess for vmlinux. `run_addr2line()` queries either the coprocess or one-shot section-specific addr2line. `find_dir_prefix()` strips source-tree prefixes using `start_kernel`. `__faddr2line()` matches symbols, computes kallsyms-like symbol sizes, validates offsets/user sizes, and prints source or `--list` context.

Control flow: Parses optional `--list`, validates tools and debug info, reads ELF metadata, initializes addr2line, then processes each func+offset argument. For duplicate symbol names it prints all size-compatible matches. If no match prints warnings on a second pass.

State/persistence: Uses many shell globals (`ELF_*`, `ADDR2LINE_OUT`, `IS_VMLINUX`, `DIR_PREFIX`, `DONE`, `FIRST`). A coprocess remains active during script execution for vmlinux.

Dependencies/integration: Bash, readelf/addr2line from CROSS_COMPILE or LLVM selection, awk, grep, sed, sort, mktemp, and source files for `--list`. Used for kernel debugging.

Risks: Parses readelf text and symbol fields positionally. `--list` evaluates source paths from debug info and can fail if files are absent. Long-running coprocess handling relies on sentinel output variants from GNU/LLVM addr2line. Symbol size approximation depends on sorted section symbols and skips mapping symbols heuristically.

Test signals: vmlinux and module/object inputs, GNU and LLVM tools, duplicate symbol names with and without size, inlined functions, absent debug info, `--list`, KASLR-like function offsets, and invalid argument formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/faddr2line -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/file-size.sh -->
# sources/distributed-fs/ceph-client/scripts/file-size.sh

Purpose: Prints the byte size of a file using `ls -dn` field parsing.

Important APIs/functions: Runs `set -- $(ls -dn "$1")` and prints `$5`.

Control flow: One positional file argument is passed to `ls`; shell fields are reassigned to ls output tokens; fifth field is printed.

State/persistence: Stateless and read-only.

Dependencies/integration: POSIX shell and `ls`. Used where a simple file size helper is needed in build scripts.

Risks: Parses `ls` output, which is less robust than `stat`; unusual implementations or locale/format changes can break it. Missing argument or nonexistent file behavior is delegated to `ls`.

Test signals: Regular files, symlinks, missing file, names with spaces, and host variants where `ls -dn` output differs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/file-size.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gcc-plugins/Kconfig -->
# sources/distributed-fs/ceph-client/scripts/gcc-plugins/Kconfig

Purpose: Defines kernel configuration switches for GCC plugin support and the latent entropy plugin.

Important APIs/options: `HAVE_GCC_PLUGINS` is selected by supported architectures. `GCC_PLUGINS` depends on architecture support, GCC compiler selection, and existence of GCC plugin headers from `$(CC) -print-file-name=plugin`. `GCC_PLUGIN_LATENT_ENTROPY` enables entropy instrumentation.

Control flow: Kconfig exposes the menu only when dependencies pass; latent entropy appears under `if GCC_PLUGINS`.

State/persistence: Affects generated `.config` and therefore build flags/plugin selection.

Dependencies/integration: Depends on Kconfig shell success checks, compiler identity, and plugin header paths. References documentation under `Documentation/kbuild/gcc-plugins.rst`.

Risks: Header existence probe can be fooled by dummy tools or broken GCC plugin installs. Only latent entropy is present in this snippet, while other plugin files may be selected elsewhere or in different tree versions.

Test signals: Kconfig with real GCC plugin headers, Clang/CC_IS_GCC false, unsupported architecture, dummy tools, and latent entropy selection visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gcc-plugins/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gcc-plugins/Makefile -->
# sources/distributed-fs/ceph-client/scripts/gcc-plugins/Makefile

Purpose: Builds GCC plugin shared objects and generated support headers for kernel GCC plugin infrastructure.

Important APIs/rules: Generates `randomize_layout_seed.h` from `scripts/basic/randstruct.seed` with private warning comments. Computes `GCC_PLUGINS_DIR` from `$(CC) -print-file-name=plugin`. Defines `plugin_cxxflags`, `plugin_ldflags`, single-file and multi-file plugin rules, object rules, and touches `include/generated/gcc-plugins.h` after plugin build.

Control flow: `always-y += $(GCC_PLUGIN)` drives selected plugin targets. Single-file plugins compile directly from `.c` to `.so` with `HOSTCXX`; multi-file plugins compile objects then link. Dependency files are generated through `if_changed_dep`.

State/persistence: Produces plugin `.so`, `.o`, generated seed header, dependency files, and generated `gcc-plugins.h`. The seed header embeds the randstruct seed and must remain private.

Dependencies/integration: Kbuild, host C++ compiler, GCC plugin include dir, kernel compiler-version header, selected `GCC_PLUGIN` variables, and `randstruct.seed`.

Risks: Seed exposure weakens randstruct layout secrecy. Host compiler/GCC plugin header version mismatch can break builds. Treating `.c` as host C++ plugin code requires GCC-plugin-compatible source style.

Test signals: Build single and multi-object plugins, seed regeneration when seed changes, out-of-tree object paths, dependency tracking, and clean-files behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gcc-plugins/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gcc-plugins/gcc-common.h -->
# sources/distributed-fs/ceph-client/scripts/gcc-plugins/gcc-common.h

Purpose: Central compatibility and convenience header for Linux GCC plugins across GCC internal API versions.

Important APIs/types: Includes a broad set of GCC internal headers. Defines visibility/unused macros, declaration/type name helpers, `build_const_char_string()`, `add_type_attr()`, `PASS_INFO`, compatibility no-op macros for old APIs, cgraph/varpool wrappers, gimple type aliases and casts, IPA reference wrappers, RTL helper aliases, and version-specific verification macro mappings.

Control flow: Plugin source includes this header before using GCC internals. Helpers adapt to the GCC version selected by `BUILDING_GCC_VERSION` and expose stable names used by plugin implementations.

State/persistence: No runtime state, but functions mutate GCC tree attributes, symbol tables, and pass structures in the current compiler process.

Dependencies/integration: Requires GCC plugin development headers and kernel-provided compiler-version definitions. Used by latent entropy, randstruct, stackleak, and generated pass headers.

Risks: GCC internal APIs are unstable; this header must track version changes closely. `add_type_attr()` mutates canonical/main variants and can affect type identity. Some macros intentionally stub old API functions, which can hide semantic differences.

Test signals: Compile all plugins across supported GCC versions, exercise type attribute propagation, cgraph edge rebuilds, IPA wrappers, and GIMPLE casts under checking-enabled GCC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gcc-plugins/gcc-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gcc-plugins/gcc-generate-gimple-pass.h -->
# sources/distributed-fs/ceph-client/scripts/gcc-plugins/gcc-generate-gimple-pass.h

Purpose: Macro generator for boilerplate GIMPLE optimization passes in GCC plugins.

Important APIs/types: Requires `PASS_NAME`; optionally consumes `NO_GATE`, `NO_EXECUTE`, `PROPERTIES_*`, and `TODO_FLAGS_*`. Emits pass data, a `gimple_opt_pass` subclass, optional `gate()` and `execute()` methods calling `PASS_NAME_gate()` and `PASS_NAME_execute()`, `clone()`, and `make_PASS_NAME_pass()`.

Control flow: Included after a plugin defines callbacks and macros. The generated factory is used in `register_pass_info`.

State/persistence: No state by itself. Generated passes operate in GCC's pass manager and use global `g`.

Dependencies/integration: Depends on GCC plugin headers via `gcc-common.h`. Included by latent entropy, stackleak, and randstruct-related passes.

Risks: The file comments mention GCC 4.5-6, but current code is C++ pass-manager style; compatibility assumptions must be tested with supported compiler range. Macro cleanup is critical because the header may be included multiple times.

Test signals: Compile generated passes with gate/execute present and omitted, custom properties/todos, multiple inclusions in one translation unit, and pass registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gcc-plugins/gcc-generate-gimple-pass.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gcc-plugins/gcc-generate-ipa-pass.h -->
# sources/distributed-fs/ceph-client/scripts/gcc-plugins/gcc-generate-ipa-pass.h

Purpose: Macro generator for IPA optimization pass boilerplate.

Important APIs/types: Requires `PASS_NAME`; optionally consumes `NO_GENERATE_SUMMARY`, `NO_READ_SUMMARY`, `NO_WRITE_SUMMARY`, `NO_READ_OPTIMIZATION_SUMMARY`, `NO_WRITE_OPTIMIZATION_SUMMARY`, `NO_STMT_FIXUP`, `NO_FUNCTION_TRANSFORM`, `NO_VARIABLE_TRANSFORM`, `NO_GATE`, `NO_EXECUTE`, `PROPERTIES_*`, `TODO_FLAGS_*`, and `FUNCTION_TRANSFORM_TODO_FLAGS_START`. Emits an `ipa_opt_pass_d` subclass and `make_PASS_NAME_pass()`.

Control flow: The generated constructor wires summary, optimization-summary, statement-fixup, function-transform, and variable-transform callbacks into GCC's IPA pass manager.

State/persistence: No independent state; generated pass instances are managed by GCC.

Dependencies/integration: Relies on GCC IPA pass APIs exposed by `gcc-common.h`.

Risks: The visible code places `clone()` inside the `#ifndef NO_GATE` block, so defining `NO_GATE` can affect clone method generation unexpectedly. IPA constructor signatures are particularly sensitive to GCC version changes.

Test signals: Compile IPA passes with different omitted callbacks, with and without gates, and under LTO-oriented builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gcc-plugins/gcc-generate-ipa-pass.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gcc-plugins/gcc-generate-rtl-pass.h -->
# sources/distributed-fs/ceph-client/scripts/gcc-plugins/gcc-generate-rtl-pass.h

Purpose: Macro generator for RTL optimization pass boilerplate.

Important APIs/types: Requires `PASS_NAME`; supports `NO_GATE`, `NO_EXECUTE`, `PROPERTIES_*`, and `TODO_FLAGS_*`. Emits RTL pass data, an `rtl_opt_pass` subclass, optional callbacks, clone, and `make_PASS_NAME_pass()`.

Control flow: Included by plugins after defining the pass callbacks and registration metadata. The generated factory is registered with GCC's pass manager.

State/persistence: No independent state; generated passes mutate GCC RTL for the current function when executed.

Dependencies/integration: Depends on GCC RTL pass APIs from `gcc-common.h`; used by `stackleak_cleanup`.

Risks: RTL pass placement is sensitive because late passes have final frame information but limited ability to insert high-level calls. Macro-generator compatibility must be maintained with GCC internals.

Test signals: Compile and run a generated RTL pass with gate and execute callbacks, verify pass position registration, and inspect RTL dumps for expected transformations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gcc-plugins/gcc-generate-rtl-pass.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gcc-plugins/gcc-generate-simple_ipa-pass.h -->
# sources/distributed-fs/ceph-client/scripts/gcc-plugins/gcc-generate-simple_ipa-pass.h

Purpose: Macro generator for simple IPA pass boilerplate where only gate/execute style callbacks are needed.

Important APIs/types: Requires `PASS_NAME`; supports `NO_GATE`, `NO_EXECUTE`, `PROPERTIES_*`, and `TODO_FLAGS_*`. Emits simple IPA pass metadata, class/factory, and macro cleanup.

Control flow: Intended for inclusion after defining callbacks; generated pass is registered through GCC's pass manager.

State/persistence: No independent state.

Dependencies/integration: Uses GCC pass APIs from `gcc-common.h`.

Risks: Same macro-inclusion risks as the other generators: leaked macros, missing callback names, or GCC API drift break builds. Simple IPA passes still run at whole-program points where side effects can be broad.

Test signals: Compile a minimal simple IPA plugin, exercise no-gate/no-execute variants, and verify pass-manager registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gcc-plugins/gcc-generate-simple_ipa-pass.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gcc-plugins/latent_entropy_plugin.c -->
# sources/distributed-fs/ceph-client/scripts/gcc-plugins/latent_entropy_plugin.c

Purpose: GCC plugin that implements `__attribute__((latent_entropy))` for kernel functions and variables, adding pseudo-random initialization and instrumentation to feed the kernel's global `latent_entropy`.

Important APIs/functions: Attribute handler validates functions/static variables and initializes integer, integer array, or integer-field struct variables with random constants. `get_random_const()` uses deterministic `-frandom-seed` when present, else `/dev/urandom`. The GIMPLE pass uses `latent_entropy_gate()`, `latent_entropy_execute()`, `init_local_entropy()`, `perturb_local_entropy()`, and `perturb_latent_entropy()`. `latent_entropy_start_unit()` declares external volatile `unsigned long latent_entropy`. `plugin_init()` registers attributes, GGC roots, start-unit callback, and pass info.

Control flow: For marked variables, random initializers are assigned during attribute handling. For marked functions, the pass skips noreturn-like functions, creates a local entropy variable, initializes it with frame address and global entropy, perturbs it in each basic block with rotating add/xor/rotate operations, and writes it back to the global entropy before returns or tail calls.

State/persistence: Maintains GCC GC root `latent_entropy_decl`, deterministic seed, random buffer, index, and `/dev/urandom` fd in the compiler process. It mutates GCC GIMPLE and variable initializers.

Dependencies/integration: Requires GCC plugin internals, `gcc-common.h`, generated GIMPLE pass header, kernel symbol `latent_entropy`, and plugin args such as `disable`.

Risks: Random initializer output is build-environment dependent unless a deterministic seed is supplied. `/dev/urandom` failure asserts. Instrumentation depends on CFG shape, tail-call handling, and SSA updates. Attribute misuse produces compile errors. Not cryptographic entropy, as documented.

Test signals: Compile marked variables of allowed/disallowed types, marked functions with branches and tail calls, noreturn functions, deterministic seed builds for reproducibility, disabled plugin, and runtime presence of global `latent_entropy`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gcc-plugins/latent_entropy_plugin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gcc-plugins/randomize_layout_plugin.c -->
# sources/distributed-fs/ceph-client/scripts/gcc-plugins/randomize_layout_plugin.c

Purpose: GCC plugin that randomizes selected kernel `struct` field layouts and warns about casts that can violate randomized type boundaries.

Important APIs/functions: Attribute handlers support `randomize_layout`, `no_randomize_layout`, `randomize_considered`, and `randomize_performed`. PRNG functions `raninit()`/`ranval()` seed from `randomize_layout_seed.h` plus struct name hash. `relayout_struct()` shuffles fields, preserves trailing flexible arrays, applies attributes, and relayouts the type. `randomize_type()`, `finish_type()`, and `randomize_layout_finish_decl()` hook type/declaration finalization. `find_bad_casts_execute()`, `check_global_variables()`, and helpers detect suspicious pointer casts/initializers.

Control flow: On type finish, eligible structs explicitly marked or consisting purely of function pointers are shuffled unless opted out, already considered, UAPI, or special-cased. Declaration finish resets and relayouts variables of randomized types, including flexible-array initializer sizing. An inserted GIMPLE pass after SSA scans local assignments for casts involving randomized record pointers and reports mismatches.

State/persistence: Global `performance_mode` and `shuffle_seed[4]`. Mutates GCC type field chains, type attributes, declaration layout fields, and emits diagnostics.

Dependencies/integration: Requires generated private seed header, GCC plugin internals, GIMPLE pass generator, and kernel annotations. Kbuild generates `randomize_layout_seed.h`.

Risks: Field-chain mutation can break code relying on positional initialization; plugin enforces `designated_init` to reduce this. Seed exposure reveals layouts. Performance mode has a comment noting group shuffle is currently a no-op. Cast detection is heuristic and must avoid false positives such as `container_of` and `IS_ERR` patterns.

Test signals: Marked/unmarked/no-randomize structs, pure ops structs, flexible arrays, UAPI path rejection, deterministic seed reproducibility, bad cast diagnostics, global/local constructor checks, and performance mode behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gcc-plugins/randomize_layout_plugin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gcc-plugins/stackleak_plugin.c -->
# sources/distributed-fs/ceph-client/scripts/gcc-plugins/stackleak_plugin.c

Purpose: GCC plugin that tracks deepest kernel stack usage by inserting calls to `__sanitizer_cov_stack_depth()` after dynamic stack allocation and in functions with sufficiently large final stack frames.

Important APIs/functions: `stackleak_start_unit()` declares the tracking function. `stackleak_instrument_execute()` inserts GIMPLE calls or asm calls after `alloca()` and at function entry. `add_stack_tracking_gcall()` updates cgraph edges; `add_stack_tracking_gasm()` uses x86 `current_stack_pointer` and asm when `no_caller_saved_registers` is available. `stackleak_cleanup_execute()` removes unnecessary instrumentation in late RTL for functions without alloca and below `track-min-size`. Gate and plugin init functions parse `track-min-size`, `arch`, `disable`, and `verbose`.

Control flow: An early GIMPLE pass instruments broadly before tree-to-RTL expansion. Later, an RTL pass runs when frame size is known, keeps instrumentation for `cfun->calls_alloca` or large frames, and deletes inserted calls/asm otherwise. Section gating skips init, noinstr, entry, head, and related sections.

State/persistence: Global plugin arguments, x86 flag, verbose/disable flags, and GGC-rooted `track_function_decl`. It mutates GIMPLE, cgraph, and RTL in the compiler process.

Dependencies/integration: GCC plugin internals, generated GIMPLE and RTL pass headers, architecture-provided `current_stack_pointer` for optimized x86 asm path, kernel runtime implementation of `__sanitizer_cov_stack_depth()`.

Risks: Two-pass design is sensitive to pass order. Incorrect removal can leave overhead or remove needed tracking. x86 asm path depends on attributes and symbol availability. Leaf inline/paravirt special cases avoid ABI clobber issues but may need updates.

Test signals: Functions with alloca, large/small static frames, leaf inline special cases, paravirt functions, excluded sections, x86 asm path, non-x86 gcall path, disabled/verbose args, and RTL dumps proving cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gcc-plugins/stackleak_plugin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/Makefile -->
# sources/distributed-fs/ceph-client/scripts/gdb/Makefile

Purpose: Top-level Kbuild makefile for GDB helper scripts.

Important APIs/rules: `subdir-y := linux` includes the `linux` helper package subdirectory in the build traversal.

Control flow: Kbuild descends into `scripts/gdb/linux`.

State/persistence: No direct outputs.

Dependencies/integration: Kbuild subdirectory mechanism.

Risks: If omitted, generated constants and out-of-tree symlinks for the GDB helpers would not be handled.

Test signals: Kernel build should descend into `scripts/gdb/linux` and produce expected helper artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/Makefile -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/Makefile

Purpose: Builds/generated support for the Linux GDB Python helper package.

Important APIs/rules: In out-of-tree builds, creates symlinks for Python files from source to object directory. Generates `constants.py` from `constants.py.in` by preprocessing it as C, then deleting the C-header prelude through the marker. Cleans Python bytecode files.

Control flow: `always-y` includes symlinks when `building_out_of_srctree` and always includes `constants.py`. The generation rule uses `$(CPP) -E -x c -P $(c_flags)` then `sed -i`.

State/persistence: Produces symlinked helper files and generated `constants.py` in the object tree.

Dependencies/integration: Kbuild, CPP, sed, kernel include paths/config macros, and the Python helper package.

Risks: Generated constants depend on current kernel configuration and headers. Marker deletion must match `constants.py.in`. Out-of-tree symlink behavior depends on path correctness.

Test signals: In-tree and out-of-tree builds, changed config constants, absence of stale bytecode, and import of generated `linux.constants` in GDB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/__init__.py -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/__init__.py

Purpose: Package initializer for the Linux GDB Python helpers.

Important APIs/types: None; contains only a comment noting no initialization work.

Control flow: Importing `linux` performs no side effects from this file.

State/persistence: None.

Dependencies/integration: Allows helper modules to be imported as `linux.<module>`.

Risks: No direct risk; initialization is intentionally left to individual modules.

Test signals: `import linux` should succeed when the package path is configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/bpf.py -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/bpf.py

Purpose: Provides GDB-side helpers for BPF kernel debugging, including tracking BPF ksyms/programs and generating temporary debug objects for JITed BPF code.

Important APIs/classes: `list_ksyms()`, `list_progs()`, `get_ksym_name()`, `KsymMonitor`, `ProgMonitor`, breakpoint classes for add/remove events, `btf_str_by_offset()`, `LInfoIter`, and `generate_debug_obj()`.

Control flow: Feature availability is gated by generated constants for BPF, BPF JIT, and BPF syscall support. Monitors set internal breakpoints on BPF add/remove functions and notify callbacks for initial and dynamic objects. `generate_debug_obj()` reads JITed code bytes, writes a temporary assembly file with `.byte` directives and `.loc` records from BPF line info, invokes `as`, and returns a temporary object file.

State/persistence: Monitors hold breakpoints until `delete()`. Temporary `.s` and `.o` files are created; returned object remains open via `NamedTemporaryFile`. GDB cached types are module globals.

Dependencies/integration: GDB Python API, generated `linux.constants`, Linux helper modules `lists`, `radixtree`, `utils`, BPF kernel data structures, BTF line info, JSON escaping, tempfile, subprocess, and host assembler `as`.

Risks: Kernel struct layout changes can break field access. Missing assembler returns `None`. Temporary debug object lifetime is tied to the returned file object. Breakpoint symbols must exist and match expected argument names.

Test signals: Kernels with/without BPF JIT/syscall, existing and newly loaded BPF programs, subprogram enumeration, BTF line-info mapping, missing `as`, and breakpoint cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/bpf.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/clk.py -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/clk.py

Purpose: Adds GDB commands/functions for inspecting Linux common clock framework state.

Important APIs/classes: `clk_core_for_each_child()` walks clock child hlists. `LxClkSummary` command prints a tree similar to debugfs `clk_summary`. `LxClkCoreLookup` function returns a `struct clk_core` by name.

Control flow: `lx-clk-summary` checks for `clk_root_list`, prints headers, then recursively emits root and orphan clock subtrees with enable/prepare/protect counts, rate, and `(c)` marker for cached rates. `$lx_clk_core_lookup(name)` recursively searches root and orphan lists.

State/persistence: Registers one GDB command and one GDB convenience function at import. No persistent cache beyond `CachedType`.

Dependencies/integration: GDB Python API, `linux.utils`, `linux.lists`, generated `constants.LX_CLK_GET_RATE_NOCACHE`, and kernel `struct clk_core` lists.

Risks: Requires CONFIG_COMMON_CLK-era symbols and struct fields. Output rate may be cached/stale by design. Recursive traversal assumes valid list topology.

Test signals: Kernels with registered clocks, no clocks, orphan clocks, cached-rate flags, and lookup of existing/missing clock names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/clk.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/config.py -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/config.py

Purpose: Adds a GDB command to dump the kernel's embedded compressed configuration.

Important APIs/classes: `LxConfigDump` command registered as `lx-configdump`.

Control flow: Command accepts an optional filename defaulting to `config.txt`, evaluates `&kernel_config_data` and `&kernel_config_data_end`, reads that memory from the inferior, decompresses gzip data with `zlib.decompress(..., 16)`, writes the result in binary mode, and reports the filename.

State/persistence: Writes the requested output file on the host running GDB. No module cache.

Dependencies/integration: GDB Python API, `zlib`, `linux.utils.read_memoryview`, and kernel symbols from CONFIG_IKCONFIG.

Risks: Fails if `CONFIG_IKCONFIG` is disabled or symbols are unavailable. User-provided filename is used directly. Decompression assumes gzip-wrapped config data.

Test signals: Kernels with and without IKCONFIG, default and explicit filenames, corrupt config data, and remote inferior memory reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/config.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/constants.py.in -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/constants.py.in

Purpose: Template for generating `linux.constants` Python values from kernel C headers and configuration.

Important APIs/macros: C prelude includes relevant Linux headers, defines `STRING`, `XSTRING`, `LX_VALUE`, `LX_GDBPARSED`, and `LX_CONFIG`, then a marker separates Python output. After preprocessing, Python imports `gdb` and assigns constants such as config booleans, mount/superblock flags, IRQ flags, module section constants, radix/maple tree values, vmalloc flags, page-owner flags, slab flags, and CPU/config values.

Control flow: Kbuild preprocesses this file as C so macros and config checks expand, then strips everything through `<!-- end-c-headers -->`, leaving executable Python assignments.

State/persistence: Generated `constants.py` contains static Python assignments evaluated at import time, some using `gdb.parse_and_eval()`.

Dependencies/integration: Kernel headers, current `.config`, CPP, sed rule in `Makefile`, and GDB Python importers.

Risks: Any constant requiring `gdb.parse_and_eval()` depends on debug symbols and target context. Header or config macro changes can break preprocessing. Template line count in this tree ends at the KVM comment block, so downstream constants may be absent compared with newer kernels.

Test signals: Generate under multiple configs, import in GDB, verify representative constants match kernel headers, and test reduced-debug-info configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/constants.py.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/cpus.py -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/cpus.py

Purpose: Provides GDB helpers for per-CPU variables, CPU masks, and current task lookup.

Important APIs/classes: `get_current_cpu()`, `per_cpu()`, `cpu_list()`, `each_online_cpu()`, `each_present_cpu()`, `each_possible_cpu()`, `each_active_cpu()`, `LxCpus`, GDB functions `$lx_per_cpu`, `$lx_per_cpu_ptr`, `get_current_task()`, and `$lx_current`.

Control flow: Current CPU is derived from QEMU thread number or KGDB active counter. `per_cpu()` adds the architecture per-CPU offset to a variable pointer, with sparc and !SMP cases handled. CPU mask iteration caches `.bits` arrays until stop/new_objfile events invalidate the cache. Current task lookup handles x86/UML, aarch64 using `SP_EL0`, and riscv `tp`/`sscratch`.

State/persistence: `cpu_mask` cache stores GDB values and connects invalidation handlers after first use. Commands/functions are registered at import.

Dependencies/integration: GDB Python API, `linux.tasks`, `linux.utils`, kernel per-CPU symbols, CPU masks, and architecture registers.

Risks: Current CPU/task support is limited by gdbserver type and architecture. CPU mask cache must be invalidated on target changes. `MAX_CPUS` is defined but not enforced in `cpu_list()`. aarch64 rejects user-mode context.

Test signals: QEMU and KGDB sessions, SMP and !SMP, x86/UML/aarch64/riscv current task, CPU hotplug mask changes, and per-CPU variable dereference.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/cpus.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/device.py -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/device.py

Purpose: Adds GDB commands/functions for traversing Linux driver-core buses, classes, devices, and child device trees.

Important APIs/classes: `dev_name()`, `for_each_bus()`, `for_each_class()`, `get_bus_by_name()`, `get_class_by_name()`, `klist_for_each()`, `bus_for_each_device()`, `class_for_each_device()`, `device_for_each_child()`, commands `lx-device-list-bus`, `lx-device-list-class`, `lx-device-list-tree`, and functions `$lx_device_find_by_bus_name`, `$lx_device_find_by_class_name`.

Control flow: Bus/class iteration walks global `bus_kset` and `class_kset` kobject lists, converts containers to `subsys_private`, then traverses klist device nodes. Commands list all buses/classes or a named one; tree command validates a `struct device *` expression and recursively prints children. Finder functions return the first matching device by name.

State/persistence: Registers commands/functions at import. Uses cached GDB types.

Dependencies/integration: GDB Python API, `linux.utils.container_of`, `linux.lists.list_for_each_entry`, and driver-core struct layouts.

Risks: Strongly tied to kernel internals such as `struct subsys_private` and `struct device_private`. Invalid pointers or corrupted lists can make traversal fail. Finder functions return `None` silently when not found.

Test signals: List all buses/classes, query known bus/class and device names, recursive child tree traversal, invalid pointer argument, and kernels with changed driver-core layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/device.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/dmesg.py -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/dmesg.py

Purpose: Adds `lx-dmesg`, a GDB command that prints the kernel printk ring buffer from target memory.

Important APIs/classes: `LxDmesg` command. Cached types for `struct printk_info`, `struct prb_data_blk_lpos`, `struct prb_desc`, `struct prb_desc_ring`, `struct prb_data_ring`, and `struct printk_ringbuffer`.

Control flow: The command locates the static `prb` symbol in `printk.c`, reads ring metadata, computes descriptor/data ring sizes and addresses from type field offsets, reads tail/head ids, iterates committed/finalized descriptors, handles data-less and wrapping records, decodes UTF-8 text with replacement, and prints timestamped lines.

State/persistence: Registers command at import. Reads target memory but does not modify it.

Dependencies/integration: GDB Python API, `linux.utils` memory and integer readers, printk ringbuffer layout and symbols.

Risks: Very sensitive to printk ringbuffer internal layout and symbol names. Concurrent target logging can race with memory reads. Wrapped/truncated records are approximated. Python 2 compatibility path remains for unicode output.

Test signals: Ring buffers with committed/finalized/noncommitted records, wrapped text data, data-less records, UTF-8 replacement, live target mutation, and kernels with changed printk internals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/dmesg.py -->
