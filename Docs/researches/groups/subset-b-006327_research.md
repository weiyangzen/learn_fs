<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/checkstack.pl -->
# sources/distributed-fs/ceph-client/scripts/checkstack.pl

## Purpose
`checkstack.pl` analyzes `objdump -d` output and reports functions whose static stack growth exceeds a configurable threshold. It is a kernel build/debugging helper used after compiling objects or `vmlinux`, with optional architecture and minimum-stack arguments.

## Important APIs, Types, and Functions
The script is procedural Perl. Its main data structures are regex variables `$re` for fixed stack deltas, `$dre` for dynamic deltas, `$funcre` for objdump function headers, and `@stack` for report lines. Architecture dispatch selects instruction regexes for arm, arm64, x86, mips, powerpc, s390, sparc, riscv, loongarch, and others. `arm_push_handling()` estimates ARM frame-pointer push size. `sort_lines()` orders findings by descending byte count and then function name.

## Control Flow and State
Startup resolves `$arch` from argv or `uname -m`, sets `$min_stack` to the numeric argument or 512, and installs architecture-specific patterns. The main loop streams stdin once, tracks the current object file, function, starting address, and accumulated stack size, and pushes an output row when a function boundary is reached and the previous total is above the threshold. State is in memory only and resets per function.

## Dependencies and Integration
It depends on Perl and GNU-style objdump text. It integrates with kernel workflows as `objdump -d vmlinux | scripts/checkstack.pl [arch] [min_stack]`.

## Risks and Test Signals
Correctness depends on instruction formatting and regex coverage for each architecture. Dynamic x86 stack reductions are accumulated but are architecture-limited. Test with representative objdump snippets for each supported architecture, threshold boundaries, file format lines, ARM push sequences, and sorting ties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/checkstack.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/checksyscalls.sh -->
# sources/distributed-fs/ceph-client/scripts/checksyscalls.sh

## Purpose
`checksyscalls.sh` checks whether the current architecture exposes required Linux syscall numbers relative to the i386 syscall table, while suppressing known legacy, ABI-specific, MMU-specific, and replacement syscall cases.

## Important APIs, Types, and Functions
`ignore_list()` emits a C preprocessor fragment containing many `__IGNORE_*` macros gated by kernel config and ABI macros. `syscall_list()` reads `arch/x86/entry/syscalls/syscall_32.tbl`, sorts syscall rows numerically, and emits `#warning syscall NAME not implemented` guarded by `!defined(__NR_NAME)` and `!defined(__IGNORE_NAME)`.

## Control Flow and State
The script enables `set -e`, builds the reference table path relative to the script, concatenates generated ignore and syscall check fragments, and pipes them to the compiler command supplied as argv with `-Wno-error -Wno-unused-macros -E -x c -`. It optionally appends dependencies to `$DEPFILE` for fixdep integration. It has no persistent state.

## Dependencies and Integration
It depends on POSIX shell, `grep`, `sort`, and a C preprocessor compatible with kernel headers. The caller supplies the compiler and options, normally through Kbuild.

## Risks and Test Signals
The reference is i386-specific, so the ignore list is part of the contract and can go stale as syscalls evolve. Shell word splitting intentionally expands the compiler command but makes quoting sensitive. Test by running through representative Kbuild compile commands for 32-bit, 64-bit, MMU, no-MMU, and `DEPFILE` modes and checking that only expected warnings appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/checksyscalls.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/checkversion.pl -->
# sources/distributed-fs/ceph-client/scripts/checkversion.pl

## Purpose
`checkversion.pl` enforces include hygiene for `<linux/version.h>`. It reports files that use version macros without including the header, and files that include the header without using any version macro.

## Important APIs, Types, and Functions
This is a single-pass Perl scanner over argv files. It skips generated UAPI version header paths. It tracks `$fInComment`, `$fInString`, `$fUseVersion`, and `$iLinuxVersion`. It recognizes quoted and angle-bracket includes and version uses including `LINUX_VERSION_CODE`, `KERNEL_VERSION`, and major, patchlevel, or sublevel macros.

## Control Flow and State
For each file, the script strips C comments and string literals using regex state across lines before looking for preprocessor includes and macro references. Once it sees both an include and a use it can stop scanning. It prints diagnostics after closing each file. State is per file only.

## Dependencies and Integration
It depends only on Perl and source file arguments, and is intended for kernel tree checks run by developers or build scripts.

## Risks and Test Signals
The lexer is deliberately lightweight and can be confused by unusual C syntax, preprocessor-generated tokens, raw strings in non-C files, or macros split across lines. Test with files containing block comments across lines, quoted macro names, both include styles, generated paths, and unused include cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/checkversion.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/clang-tools/gen_compile_commands.py -->
# sources/distributed-fs/ceph-client/scripts/clang-tools/gen_compile_commands.py

## Purpose
`gen_compile_commands.py` creates a `compile_commands.json` database for kernel sources by parsing Kbuild `.cmd` files generated during a build.

## Important APIs, Types, and Functions
Key constants are `_FILENAME_PATTERN`, `_LINE_PATTERN`, `_EXCLUDE_DIRS`, and default output/log settings. `parse_arguments()` handles output directory, output file, archive parser, and paths. `cmdfiles_in_dir()`, `to_cmdfile()`, `cmdfiles_for_a()`, and `cmdfiles_for_modorder()` discover command files. `process_line()` converts a matched `.cmd` line into a JSON entry with canonical `directory`, `file`, and `command` fields.

## Control Flow and State
`main()` parses arguments, sets logging, compiles `_LINE_PATTERN`, chooses a command-file iterator for each path, opens each `.cmd`, and appends entries whose source file exists. Output is sorted by file and written as JSON. All state is transient.

## Dependencies and Integration
It depends on Python 3, `json`, `subprocess`, `llvm-ar` or an alternate `--ar`, kernel `.cmd` files, `.mod` files, and `modules.order`. It intentionally excludes `.git`, Documentation, include, and tools.

## Risks and Test Signals
Parsing is tied to the Kbuild `.cmd` line format and only reads the first line of each `.cmd`. Archive handling yields object-relative `.cmd` names, so cwd and archive layout matter. Test with built-in `.a`, module `modules.order`, absolute and relative source paths, escaped `$(pound)`, missing sources, and excluded directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/clang-tools/gen_compile_commands.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/clang-tools/run-clang-tools.py -->
# sources/distributed-fs/ceph-client/scripts/clang-tools/run-clang-tools.py

## Purpose
`run-clang-tools.py` runs `clang-tidy` over every C/C++ entry in a compilation database, selecting either Linux kernel tidy checks or clang static analyzer checks.

## Important APIs, Types, and Functions
`parse_arguments()` accepts `clang-tidy` or `clang-analyzer`, the compilation database path, optional `-checks`, and optional `-header-filter`. `init()` shares a multiprocessing lock and parsed args with workers. `run_analysis()` builds the `clang-tidy` invocation, skips non-C/C++ files, runs in the entry directory, and serializes output through the lock.

## Control Flow and State
`main()` creates a multiprocessing pool, loads JSON from the database, and maps each entry to `run_analysis()`. Default checks are `linuxkernel-*` for tidy and `clang-analyzer-*` with one insecure API checker disabled for analyzer mode. There is no persistent state.

## Dependencies and Integration
It depends on Python 3, a valid `compile_commands.json`, multiprocessing, and `clang-tidy` in `PATH`. It is intended to consume the database produced by `gen_compile_commands.py`.

## Risks and Test Signals
The BrokenPipeError handler references `os` without importing it, so EPIPE cleanup can raise a secondary error. Analyzer mode still invokes `clang-tidy`; the mode only changes check names. Test with mixed `.c`, `.cpp`, and assembly entries, custom check lists, header filters, missing tools, malformed JSON, and piped output closed early.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/clang-tools/run-clang-tools.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/cleanfile -->
# sources/distributed-fs/ceph-client/scripts/cleanfile

## Purpose
`cleanfile` rewrites text files in place to remove trailing whitespace, normalize space-tab sequences to tab stops, drop blank lines at EOF, and report lines exceeding a configurable width.

## Important APIs, Types, and Functions
`clean_space_tabs()` converts runs of spaces before tabs into the minimal tab-aligned form while preserving visual alignment. `strwidth()` computes visual width with tabs expanding to 8 columns. Argument parsing accepts `-width` or `-w`; all other arguments are files.

## Control Flow and State
For each file, the script verifies it is a regular file, opens it read/write in binary mode, scans for NUL bytes to avoid binary input, then rereads line by line. It tracks input and output byte counts, buffers non-final blank lines, and only rewrites/truncates when output size differs. State is in process memory and the target file is the only persistence.

## Dependencies and Integration
It depends on Perl and `File::Basename`. It is a developer cleanup helper and is intentionally destructive.

## Risks and Test Signals
Files are rewritten in place and `.swp` protection is not used here, so interruption during write can damage the target. Unicode width is not semantically handled beyond Perl character iteration. Test with binary files, CRLF endings, trailing blank lines, tab alignment cases, unchanged files, and width reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/cleanfile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/cleanpatch -->
# sources/distributed-fs/ceph-client/scripts/cleanpatch

## Purpose
`cleanpatch` rewrites unified patch files in place, cleaning only added lines while preserving context and removed lines, and adjusts hunk headers when trailing added blank lines are removed.

## Important APIs, Types, and Functions
It shares `clean_space_tabs()` and `strwidth()` logic with `cleanfile`. The parser tracks hunk headers matching `@@ -start,count +start,count @@`, `$minus_lines`, `$plus_lines`, and `@hunk_lines`. Width warnings are emitted for added text lines only.

## Control Flow and State
For each regular, non-binary file, the script alternates between outside-hunk passthrough and inside-hunk processing. Added lines are cleaned, removed/context lines decrement hunk counters, malformed structure sets an error and prevents rewriting. At hunk end it removes trailing added blank lines and rewrites the plus-line count. Persistence is in-place file replacement through seek, print, and truncate.

## Dependencies and Integration
It depends on Perl and unified diff syntax. It is used as a developer patch cleanup tool before submission.

## Risks and Test Signals
Only strict hunk headers with explicit counts are accepted. It does not preserve malformed patches and can destructively modify valid but unusual diffs. Test clean added lines, unchanged context, trailing added blank removal, malformed hunks, zero-length hunks, binary detection, and width warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/cleanpatch -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/coccicheck -->
# sources/distributed-fs/ceph-client/scripts/coccicheck

## Purpose
`coccicheck` is the kernel wrapper around Coccinelle `spatch`, supporting whole-tree semantic patch runs and online single-file checking through Kbuild.

## Important APIs, Types, and Functions
Environment variables drive behavior: `SPATCH`, `V`, `SPFLAGS`, `LINUXINCLUDE`, `C`, `KBUILD_EXTMOD`, `MODE`, `J`, `COCCI`, `DEBUG_FILE`, `srcroot`, and `srctree`. `run_cmd_parmap()` uses spatch `--jobs` when supported. `run_cmd_old()` manually launches indexed spatch workers. `coccinelle()` checks per-rule `Options:` and `Requires:` headers, prints submission hints in verbose mode, and runs selected modes.

## Control Flow and State
The script locates `spatch`, computes include arguments, chooses online or offline options, determines concurrency, selects mode defaults, initializes debug output, and then either scans all matching `.cocci` files under `scripts/coccinelle` or runs the specified `COCCI`. It tracks worker PIDs for signal cleanup in old parallel mode. It persists only optional debug logs and generated patch/report output from spatch.

## Dependencies and Integration
It depends on Bash, Coccinelle, `lscpu`, `getconf`, `find`, `grep`, and Kbuild environment. It integrates directly with `make coccicheck` and `CHECK=scripts/coccicheck`.

## Risks and Test Signals
The script relies on shell word expansion for options and may mishandle spaces in paths. Debug file existence causes an immediate bail. Test online `C=1/2`, offline all-rule scan, single `COCCI`, `MODE=chain`, `SPFLAGS` overrides, old/new spatch job support, and signal cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/coccicheck -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/config -->
# sources/distributed-fs/ceph-client/scripts/config

## Purpose
`scripts/config` edits Linux `.config` files from the command line, enabling, disabling, modularizing, setting, undefining, querying, and refreshing symbols.

## Important APIs, Types, and Functions
`usage()` documents commands and options. `checkarg()` strips the configurable prefix, validates required arguments, and uppercases unless `--keep-case` is active. `txt_append()`, `txt_subst()`, and `txt_delete()` implement sed-backed edits via `$FN.swp`. `set_var()` replaces existing symbol lines or appends after an anchor. `undef_var()` removes both set and unset forms.

## Control Flow and State
Argument parsing first extracts `--file`, then replays the remaining command list. Commands mutate `$FN`, default `.config`, in sequence. `--state` prints `n`, `undef`, or the unquoted current value. `--refresh` runs `yes "" | make oldconfig KCONFIG_CONFIG=$FN`. Persistent state is the target config file.

## Dependencies and Integration
It depends on Bash, `sed`, `grep`, `tr`, `mv`, and optionally `make oldconfig`. `CONFIG_` can be overridden via environment for alternate prefixes.

## Risks and Test Signals
Regex anchors are interpolated into sed/grep, so unusual symbol names can be risky despite normal Kconfig naming. `$FN.swp` can collide and replacement is not atomic across filesystems. Test repeated commands, after-anchor insertion, string escaping, custom prefixes, keep-case mode, missing args, state output, and refresh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/container -->
# sources/distributed-fs/ceph-client/scripts/container

## Purpose
`container` runs a command in a Docker or Podman container with the current directory mounted at `/src`, providing a kernel-development container wrapper.

## Important APIs, Types, and Functions
`ContainerRuntime` is the abstract base with `is_present()`, `_do_run()`, `_do_abort()`, and `run()`. `CommonRuntime` implements shared `run` options: container name, `--rm`, current directory bind mount, working directory, env file, and interactive TTY. `DockerRuntime` adds `--user uid:gid`; `PodmanRuntime` adds `--userns keep-id`. `Runtimes` selects by name or first present runtime. `_get_logger()` creates a tagged logger.

## Control Flow and State
`main()` creates logging, resolves the runtime, and runs the requested image and command. Each invocation creates a UUID container name and aborts it on `KeyboardInterrupt`. No repo state is persisted.

## Dependencies and Integration
It depends on Python 3, Docker or Podman, and filesystem mount permissions. It is documented as a kernel container build helper.

## Risks and Test Signals
The current working directory is mounted read/write into the container, so commands can modify the source tree. UID/GID args are strings from argparse and are passed through directly. Test runtime auto-selection, missing runtime, Docker and Podman option sets, env-file mode, shell TTY mode, interrupt cleanup, and command exit propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/container -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/crypto/gen-fips-testvecs.py -->
# sources/distributed-fs/ceph-client/scripts/crypto/gen-fips-testvecs.py

## Purpose
`gen-fips-testvecs.py` generates a C header body for FIPS self-test vectors covering fixed test data/key material, HMAC digests, SHA3-256, and AES-CMAC.

## Important APIs, Types, and Functions
The constants are `fips_test_data` and `fips_test_key`. `print_static_u8_array_definition()` emits `static const u8 ... __initconst __maybe_unused` arrays in 8-byte rows. The script uses `hmac.new()`, `hashlib.sha3_256()`, `cryptography.hazmat.primitives.ciphers.algorithms.AES`, and `cryptography.hazmat.primitives.cmac.CMAC`.

## Control Flow and State
Execution is top-level: print SPDX and generated comments, include `<linux/fips.h>`, emit data/key arrays, compute HMAC for sha1, sha256, and sha512, compute SHA3-256, then compute AES-CMAC. Output goes to stdout; no input args or persistent state are used.

## Dependencies and Integration
It depends on Python 3 and the `cryptography` package. Generated output is intended for `lib/crypto/fips.h` or similar kernel generated headers.

## Risks and Test Signals
The AES key length is 16 bytes, so the vector is AES-128 despite the generic variable name. Reproducibility depends on Python library implementations. Test by regenerating and diffing expected header output, checking byte formatting, import failure behavior, and comparing vectors with independent crypto tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/crypto/gen-fips-testvecs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/crypto/gen-hash-testvecs.py -->
# sources/distributed-fs/ceph-client/scripts/crypto/gen-hash-testvecs.py

## Purpose
`gen-hash-testvecs.py` emits deterministic C test vectors for hashlib algorithms and kernel-specific hash/MAC primitives including AES-CMAC, GHASH, NH, Poly1305, POLYVAL, SHA3/SHAKE, and HMAC variants.

## Important APIs, Types, and Functions
`rand_bytes()` is a deterministic LCG used to reconstruct input data in kernel tests. Classes `AesCmac`, `Poly1305`, `Ghash`, and `Polyval` provide hash-like `update()` and `digest()` APIs. `hash_init()`, `compute_hash()`, and print helpers drive generic generation. Specialized generators include `gen_unkeyed_testvecs()`, `gen_hmac_testvecs()`, `gen_additional_sha3_testvecs()`, `gen_additional_blake2_testvecs()`, `gen_nh_testvecs()`, and all-ones stress cases for Poly1305, GHASH, and POLYVAL.

## Control Flow and State
The script requires exactly one algorithm argument, prints generated-file headers, dispatches by algorithm name, and writes C arrays/structs to stdout. State is local to each generated digest and deterministic from constants.

## Dependencies and Integration
It depends on Python 3, `hashlib`, `hmac`, and `cryptography` for AES-CMAC. It is integrated with kernel crypto test vector generation.

## Risks and Test Signals
Specialized algorithms are straightforward reference implementations, not optimized or hardened. Partial-block handling is intended only for final blocks. A formatting issue exists in `print_static_u8_array_definition()`: it prints `static const u8 {name} = {`, so callers include array dimensions in `name`. Test every dispatch path, reproducible diffs, boundary lengths in `DATA_LENS`, unsupported algorithms, and independent vector verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/crypto/gen-hash-testvecs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/decode_stacktrace.sh -->
# sources/distributed-fs/ceph-client/scripts/decode_stacktrace.sh

## Purpose
`decode_stacktrace.sh` annotates Linux stack traces with source file and line information using `vmlinux`, module debug info, `nm`, and `addr2line`; it can also decode inline `Code:` lines through `decodecode`.

## Important APIs, Types, and Functions
Key functions are `find_module()`, `parse_symbol()`, `debuginfod_get_vmlinux()`, `decode_code()`, and `handle_line()`. It supports `-r <release>` lookup, `-R` return-address mode, module build IDs, optional debuginfod, Rust demangling via `llvm-cxxfilt` or `c++filt`, and tool prefix/suffix selection through `LLVM` and `CROSS_COMPILE`.

## Control Flow and State
Argument parsing resolves `vmlinux`, base path, module path, and release. If Bash associative arrays are available, symbol and module lookups are cached. The stdin loop strips CR, detects stack-symbol lines, `Code:` lines, and debuginfod version lines, then prints transformed or original lines. `parse_symbol()` resolves module/object, finds symbol base address via `nm`, adjusts return addresses unless `-R`, calls `addr2line -i`, strips base path, demangles Rust names, and rewrites the symbol token.

## Dependencies and Integration
It depends on Bash, GNU binutils or LLVM tools, `gdb` for release extraction, `find`, `sed`, optional debuginfod, and the sibling `decodecode` script.

## Risks and Test Signals
Stack trace tokenization is format-sensitive. Module paths with spaces are not robust. Missing debug info yields warnings and passthrough symbols. Test vmlinux-only traces, module traces, build-id debuginfod, inline frames, Rust symbols, `-R`, auto base path, and `Code:` continuation lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/decode_stacktrace.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/decodecode -->
# sources/distributed-fs/ceph-client/scripts/decodecode

## Purpose
`decodecode` disassembles the `Code:` byte dump found in Linux oops reports and marks the trapping instruction.

## Important APIs, Types, and Functions
`cleanup()` removes temp files, `die()` exits with an error, `disas()` assembles and objdumps generated assembly, `get_substr_opcode_bytes_num()` matches opcode bytes against objdump lines, and `get_faultlinenum()` maps the marker location to a disassembly line. Environment variables include `AFLAGS`, `PC`, `ARCH`, and `CROSS_COMPILE`.

## Control Flow and State
The script reads stdin, captures the first `Code:` line and hex continuation lines, infers opcode width, maps host uname to common kernel `ARCH` values, and writes temporary assembly containing `.byte`, `.2byte`, `.4byte`, or `.inst` data. If the dump contains `<...>` or `(...)` markers, it disassembles all code and the suffix beginning at the faulting instruction. Temporary files are removed via trap.

## Dependencies and Integration
It depends on Bash, `mktemp`, `expr`, assembler, objdump, strip, grep, sed, and optional cross-compile tools. `decode_stacktrace.sh` delegates `Code:` lines to it.

## Risks and Test Signals
Width inference assumes the first space-delimited token determines instruction unit size. Architecture-specific objdump flags are limited. Shell parsing of byte dumps is permissive but not a full parser. Test x86 byte dumps, ARM Thumb and ARM64 4-byte instructions, RISC-V byte order matching, `PC` adjusted VMA, no marker, no `Code:` line, and cleanup on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/decodecode -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/depmod.sh -->
# sources/distributed-fs/ceph-client/scripts/depmod.sh

## Purpose
`depmod.sh` is a thin wrapper used during `make modules_install` to run `depmod` with the correct kernel release and `System.map`, while gracefully skipping when prerequisites are absent.

## Important APIs, Types, and Functions
It accepts exactly one argument, `kernelrelease`. It reads environment variables `DEPMOD`, `objtree`, and `INSTALL_MOD_PATH`. It builds `depmod` arguments `-ae -F ${objtree}/System.map`, optionally adding `-b $INSTALL_MOD_PATH`.

## Control Flow and State
The script validates argv count, defaults `DEPMOD=depmod`, checks for readable `${objtree}/System.map`, appends `/sbin` to `PATH`, checks command availability, then `exec`s depmod. It persists no state beyond depmod's normal module dependency outputs.

## Dependencies and Integration
It depends on POSIX shell, `command -v`, and kmod `depmod`. It is invoked by Kbuild modules installation.

## Risks and Test Signals
The `command -v` test uses unquoted command substitution, so unusual `DEPMOD` values are fragile. Missing `System.map` or `depmod` is a warning, not failure. Test missing args, missing `System.map`, custom `DEPMOD`, `INSTALL_MOD_PATH`, and successful exec argument ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/depmod.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dev-needs.sh -->
# sources/distributed-fs/ceph-client/scripts/dev-needs.sh

## Purpose
`dev-needs.sh` runs on a booted target and traces device probe dependencies from `/sys/devices` paths, reporting suppliers and parent devices in formats useful for humans, Graphviz, or `tsort`.

## Important APIs, Types, and Functions
Output detail functions include `detail_compat()`, `detail_module()`, `detail_driver()`, `detail_fwnode()`, `detail_graphviz()`, `detail_tsort()`, and `detail_device()`. `add_suppliers()` follows `supplier:*` device links unless disabled, ignoring `sync_state_only` proxy links. `add_parent()` walks to the nearest parent with a driver. `already_seen()` prevents duplicate traversal. `dev_to_detail()` renders sorted unique output.

## Control Flow and State
Flags select detail mode and dependency filters. `CONSUMERS` acts as a breadth-first queue, while `OUT_LIST` stores consumer/supplier pairs. Each consumer is resolved with `realpath`, optionally skipped if it lacks a driver, expanded through suppliers and parent, or marked as root. Output is sorted and deduplicated. State is runtime-only.

## Dependencies and Integration
It depends on Bash arrays, `realpath`, sysfs layout under `/sys/devices`, `sort`, `uniq`, `cut`, and optionally toybox behavior for target devices.

## Risks and Test Signals
Paths are mostly unquoted, so sysfs names with unusual characters would be fragile. The driver filter intentionally skips class-like links by default and can omit useful dependencies. Test modes `-c/-d/-m/-f/-g/-t`, no-driver allowance, excluded parents/devlinks, cycles via sync-state links, and multiple input devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dev-needs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/diffconfig -->
# sources/distributed-fs/ceph-client/scripts/diffconfig

## Purpose
`diffconfig` compares two Linux `.config` files and prints sorted semantic configuration changes instead of raw line diffs.

## Important APIs, Types, and Functions
`readconfig()` parses `CONFIG_FOO=value` and `# CONFIG_FOO is not set` into dictionaries without the `CONFIG_` prefix, mapping unset symbols to `n`. `print_config()` emits normal or merge-style output. `show_diff()` handles options, default filenames, comparison, and sorting.

## Control Flow and State
The script accepts `-h`, `-m`, zero config paths, or two config paths. With no paths it compares `.config.old` to `.config`, prefixed by `$KBUILD_OUTPUT` when present. It computes removed, changed, and added keys and prints them in sorted order. State is in memory only.

## Dependencies and Integration
It depends on Python 3 and config file syntax. It is a kernel developer utility for reviewing configuration deltas.

## Risks and Test Signals
Parsing assumes every non-comment config line that starts with `CONFIG_` contains `=` and every unset line ends with ` is not set`. It mutates dictionaries during iteration in a way that is safe for the currently used loops over one dict while deleting from another or after collecting keys, but should be regression-tested. Test normal and merge output, default files, `KBUILD_OUTPUT`, strings with `=`, removed-only, added-only, and broken file errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/diffconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/Makefile -->
# sources/distributed-fs/ceph-client/scripts/dtc/Makefile

## Purpose
This Makefile wires the device tree compiler host tools into the Linux build, producing `dtc` when `CONFIG_DTC` or `CHECK_DTBS` requires it and `fdtoverlay` when `CONFIG_DTC` is enabled.

## Important APIs, Types, and Functions
It defines `hostprogs-always-*` entries, `dtc-objs`, `libfdt-objs`, `libfdt`, and `fdtoverlay-objs`. `HOST_EXTRACFLAGS` adds the userspace libfdt include path and defines `NO_YAML`. Generated lexer/parser object flags add the source tree include path. The lexer object explicitly depends on the parser-generated header.

## Control Flow and State
There is no runtime control flow. Kbuild expands object lists and host flags to build generated and static C sources into host utilities.

## Dependencies and Integration
It depends on Kbuild host program rules, flex/bison outputs, libfdt sources under `scripts/dtc/libfdt`, and the Linux config variables controlling DTC.

## Risks and Test Signals
Object lists must stay synchronized with source files and `.gitignore`. `NO_YAML` removes YAML output support from this kernel build. Test host builds with `CONFIG_DTC=y`, `CHECK_DTBS=y`, generated lexer/parser ordering, and fdtoverlay link coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/checks.c -->
# sources/distributed-fs/ceph-client/scripts/dtc/checks.c

## Purpose
`checks.c` is the validation and fixup engine for DTC live trees. It reports structural, semantic, style, bus, phandle, interrupt, GPIO, and graph binding issues and performs reference fixups before output.

## Important APIs, Types, and Functions
`struct check` describes a named check, callback, data pointer, warning/error enablement, status, and prerequisites. Macros `WARNING`, `ERROR`, and `CHECK` declare checks. `check_msg()`, `FAIL`, and `FAIL_PROP` format diagnostics. `run_check()` enforces prerequisites and walks the tree through `check_nodes_props()`. Public APIs are `parse_checks_option()` and `process_checks()`.

## Control Flow and State
`process_checks()` iterates `check_table`, running enabled checks. Each check caches status as `UNCHECKED`, `PREREQ`, `PASSED`, or `FAILED`, and `inprogress` guards recursion. Some checks mutate the tree: `name_properties` removes redundant `name`, phandle and path reference checks patch property data, `omit_unused_nodes` deletes nodes, and bus checks set `node->bus`. Warning/error state is mutable through `-W` and `-E` options.

## Dependencies and Integration
It depends on DTC live-tree helpers from `livetree.c`, data/marker APIs, source positions, libfdt endian helpers, and global CLI flags such as `quiet` and `generate_symbols`.

## Risks and Test Signals
Checks have ordering dependencies and some mutate state used by later checks. Overlay/plugin behavior intentionally suppresses or defers some reference failures. Test duplicate names/labels, explicit and generated phandles, plugin unresolved references, bus-specific reg formats, interrupt maps, GPIO cell checks, graph endpoints, `-Wno-*`, `-E*`, `-f`, and quiet levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/checks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/data.c -->
# sources/distributed-fs/ceph-client/scripts/dtc/data.c

## Purpose
`data.c` implements DTC's growable binary data buffers and marker lists used for property values, references, labels, typed arrays, strings, reserves, and inserted fixups.

## Important APIs, Types, and Functions
Public functions include `data_free()`, `data_grow_for()`, `data_copy_mem()`, `data_copy_escape_string()`, `data_copy_file()`, `data_append_data()`, `data_insert_at_marker()`, `data_merge()`, integer append helpers, `data_add_marker()`, `data_is_one_string()`, `data_insert_data()`, and `alloc_marker()`. It uses `struct data` and `struct marker` from `dtc.h`.

## Control Flow and State
Data buffers are immutable-by-value at the API surface but contain owned heap pointers. Append and insert operations return updated structs after reallocating and adjusting markers. `data_merge()` appends `d2` bytes to `d1`, splices `d2` markers into `d1`, offsets them by `d1.len`, clears `d2.markers`, and frees `d2.val`. `data_copy_file()` grows in chunks until EOF or max length.

## Dependencies and Integration
It depends on `xmalloc`, `xrealloc`, `xstrdup`, `die`, `get_escape_char`, and libfdt endian conversion helpers. Parser, tree source, flattree, and checks code all depend on these buffers.

## Risks and Test Signals
Ownership transfer in `data_merge()` and marker copying in `data_insert_data()` are subtle. `data_grow_for()` doubles from `xlen` and assumes arithmetic does not overflow except where explicitly checked in file reads. Test append/merge marker offsets, escaped strings, max-length file reads, integer endian output, alignment, insertion at markers, and free-after-merge behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/dt-extract-compatibles -->
# sources/distributed-fs/ceph-client/scripts/dtc/dt-extract-compatibles

## Purpose
`dt-extract-compatibles` extracts device-tree compatible strings from C source files or directories by scanning common OF match tables, OF declaration macros, and compatible-lookup helper calls.

## Important APIs, Types, and Functions
`parse_of_declare_macros()`, `parse_of_device_id()`, `parse_of_match_table()`, and `parse_of_functions()` implement regex extraction. `parse_compatibles()` applies normal or driver-match filtering. `parse_compatibles_to_ignore()` collects non-driver OF declarations to suppress. `glob_without_symlinks()` and `files_to_parse()` discover `.c` files.

## Control Flow and State
Argparse accepts files/directories, `--with-filename`, and `--driver-match`. In driver-match mode it first builds an ignore list from all inputs, then parses each file and prints either one compatible per line or filename-prefixed summaries. State is transient lists.

## Dependencies and Integration
It depends on Python 3, regexes, filesystem walking, and Linux OF coding conventions. It is used by device tree binding and driver coverage workflows.

## Risks and Test Signals
The scanner removes newlines and uses regexes rather than a C parser, so macros, comments, nested braces, generated strings, and multiline constructs can be missed or misread. Directory pruning mutates `dirs` during iteration. Test OF tables with and without `of_match_ptr`, declaration macros, helper calls, driver-match filtering, hidden directories, and malformed source snippets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/dt-extract-compatibles -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/dt_to_config -->
# sources/distributed-fs/ceph-client/scripts/dtc/dt_to_config

## Purpose
`dt_to_config` maps compatible strings found in one or more device trees to likely driver source files and Kconfig symbols, helping developers derive kernel config requirements from hardware descriptions.

## Important APIs, Types, and Functions
Global hashes cache driver-to-config, compatible-to-driver, driver counts, and existing config values. White and hard-coded lists cover known compatibles and drivers. `print_flags()` computes report flags for multiple compatibles, drivers, configs, disabled nodes, hard-coded entries, and config mismatches. `scan_makefile()` heuristically finds Makefile/Kbuild config symbols for a driver. `find_kconfig()`, `handle_compatible()`, `read_dts()`, and `read_config_file()` drive analysis.

## Control Flow and State
Command-line parsing supports config input, config-friendly output, include/exclude flag filters, suspect filtering, whitelists, blacklists, list display, and short names. For each input tree, `read_dts()` runs `scripts/dtc/dtx_diff` to normalize to DTS, tracks node paths, `status`, and `compatible`, and calls `handle_compatible()`. Compatible handling skips the root, honors whitelists/caches, runs `git grep` for C files containing the compatible string, resolves configs through caches or Makefile scans, and prints report rows. Persistent state is only output; caches are per run.

## Dependencies and Integration
It depends on Perl, Getopt::Long, `git grep`, kernel source tree layout, `scripts/dtc/dtx_diff`, Kbuild Makefiles/Kbuild files, and optionally a `.config`.

## Risks and Test Signals
The script is explicitly heuristic. It can miss drivers that do not quote compatibles in `.c`, misinterpret clever Makefiles, and produce false positives from unrelated strings. Many variables are global, and regex filters are built from user-supplied flags. Test with DTS, DTB, and `/proc/device-tree` inputs, config-file modes, whitelist modes, disabled nodes, multiple compatible strings, multiple drivers, hard-coded config mappings, and missing tree-root execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/dt_to_config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/dtc-lexer.l -->
# sources/distributed-fs/ceph-client/scripts/dtc/dtc-lexer.l

## Purpose
`dtc-lexer.l` is the flex lexer for DTS source input. It tokenizes DTS syntax, handles include files and line directives, tracks source positions, and passes typed semantic values to the Bison parser.

## Important APIs, Types, and Functions
Start states include `BYTESTRING`, `PROPNODENAME`, and `V1`. Tokens include strings, labels, references, literals, character literals, bytes, directives, delete/omit keywords, operators, and property/node names. `push_input_file()`, `pop_input_file()`, and `lexical_error()` integrate with `srcfile` and `srcpos`.

## Control Flow and State
`YY_USER_ACTION` updates `yylloc` on every token. `/include/ "file"` pushes a new input buffer. EOF pops include buffers until the root ends. Line directives update source position. Strings and character literals use `data_copy_escape_string()`. The lexer switches to `BYTESTRING` after `[`, to `PROPNODENAME` after `{`, `;`, and delete/omit directives, and to `V1` after `/dts-v1/`. Lexical errors set `treesource_error`.

## Dependencies and Integration
It depends on flex, `dtc-parser.tab.h`, `dtc.h`, `srcpos.h`, srcfile helpers, and parser globals.

## Risks and Test Signals
Lexer state transitions are grammar-coupled. The comment notes buffer behavior assumes no `yyless()` or `yyunput()`. Path/reference regexes are permissive but not full path parsers. Test nested includes, line directives with escaped filenames, literals with suffixes, bad identifiers after `/dts-v1/`, byte strings, labels in property data, delete directives, and lexical errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/dtc-lexer.l -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/dtc-parser.y -->
# sources/distributed-fs/ceph-client/scripts/dtc/dtc-parser.y

## Purpose
`dtc-parser.y` is the Bison grammar for DTS files. It builds live tree structures, memory reservations, property data blobs, labels, references, overlays, delete markers, omit markers, included binary data, and integer expressions.

## Important APIs, Types, and Functions
The grammar uses a `%union` carrying property/node names, label refs, bytes, `struct data`, array metadata, properties, nodes, reserve entries, integers, and DTS flags. It calls live-tree builders such as `build_dt_info()`, `build_reserve_entry()`, `build_property()`, `build_node()`, `merge_nodes()`, `add_orphan_node()`, `delete_node()`, and data helpers. `is_ref_relative()` rejects label-relative plugin references.

## Control Flow and State
The root production builds `parser_output` from headers, reserves, and the device tree. Device-tree productions support root definitions, repeated root merges, label/path overlays, orphan plugin fragments, node deletion, and omit-if-no-ref. Property productions build empty, scalar, array, bytestring, path-reference, and incbin data. Integer expressions implement C-like precedence with divide-by-zero errors. Errors set `treesource_error`.

## Dependencies and Integration
It depends on Bison, lexer tokens, `srcpos`, `srcfile_relative_open()`, live-tree APIs, and data buffer APIs.

## Risks and Test Signals
The grammar uses `$<flags>-1` to inspect earlier header/plugin state, which is powerful but fragile. Incbin reads external files relative to source. Test plugin orphan handling, label/path references, relative reference rejection, delete nodes/properties, array bit widths, truncation warnings, expression precedence, incbin offsets/lengths, and property-before-subnode enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/dtc-parser.y -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/dtc.c -->
# sources/distributed-fs/ceph-client/scripts/dtc/dtc.c

## Purpose
`dtc.c` is the main entry point for the device tree compiler host tool. It parses CLI options, detects input/output formats, reads a device tree, validates and mutates it, then emits DTS, DTB, ASM, YAML when enabled, or null output.

## Important APIs, Types, and Functions
Global option state includes `quiet`, reserve/pad/min/align sizes, `phandle_format`, symbol/fixup flags, alias generation, and annotation level. Helpers are `is_power_of_2()`, `fill_fullpaths()`, `guess_type_by_name()`, and `guess_input_format()`. `main()` coordinates parser functions, checks, symbol/fixup generation, sorting, and output functions.

## Control Flow and State
CLI parsing uses `util_getopt_long()` and the local option tables. Defaults are inferred from filenames and blob magic. Dependency-file output writes escaped output targets. The selected reader is `dt_from_source()`, `dt_from_fs()`, or `dt_from_blob()`. After fullpath filling, plugin inputs enable fixups by default. The pipeline runs checks, optional aliases/symbols/fixups/local fixups, optional sort, output open, and selected writer.

## Dependencies and Integration
It depends on DTC subsystems for source parsing, flattened tree parsing/writing, filesystem tree reading, checks, source position dependencies, util option helpers, and libfdt.

## Risks and Test Signals
Many options set global state consumed by other modules. `-v` calls `util_version()` without an explicit break, relying on that function to exit. Input guessing can misclassify unreadable files by fallback. Test all input/output formats, dependency files, plugin default fixups, annotation restrictions, align power-of-two rejection, min/pad mutual exclusion, sorting, quiet/force behavior, and stdout output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/dtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/dtc.h -->
# sources/distributed-fs/ceph-client/scripts/dtc/dtc.h

## Purpose
`dtc.h` is the central public header for the DTC implementation. It declares command-line globals, endian helpers, data buffers, marker types, live tree structures, reserve and root tree metadata, and cross-module APIs.

## Important APIs, Types, and Functions
Core types are `cell_t`, `enum markertype`, `struct marker`, `struct data`, `struct label`, `struct property`, `struct node`, `struct reserve_info`, and `struct dt_info`. It defines traversal macros for labels, properties, children, and markers, helpers like `phandle_is_valid()`, `dtb_ld16/32/64()`, `strends()`, and `ALIGN()`, and declarations for data, live-tree, check, flattree, source, YAML, and filesystem operations.

## Control Flow and State
The header itself has no control flow. It exposes the shared state model: live tree nodes contain parent/child/sibling links, properties, labels, bus classification, phandles, address/size cell metadata, source positions, delete/omit/reference flags, and full paths populated after parsing.

## Dependencies and Integration
It depends on standard C headers, `libfdt_env.h`, `fdt.h`, and `util.h`. Almost every DTC C file includes it, making it the integration contract between parser, checks, tree manipulation, and output writers.

## Risks and Test Signals
Changes to struct layout or marker semantics affect the full compiler. Deleted nodes/properties remain in lists and are filtered by traversal macros, so callers must use the right iterator. Test by compiling all DTC objects, exercising parser/check/output round trips, and verifying phandle, marker, deletion, and source-position behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/dtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/dtx_diff -->
# sources/distributed-fs/ceph-client/scripts/dtc/dtx_diff

## Purpose
`dtx_diff` normalizes DTS, DTB, or `/proc/device-tree` style inputs to sorted DTS and either prints one decompiled tree or diffs two normalized trees.

## Important APIs, Types, and Functions
`usage()` documents modes. `compile_to_dts()` detects directory, binary FDT magic, or DTS source and invokes `dtc` with the right input format. It preprocesses DTS with `cpp` using kernel DT include flags. The main body parses flags for color, full unified diff, source tree, git root, annotation, and sorting.

## Control Flow and State
After parsing args, the script locates a preferred kernel-built `scripts/dtc/dtc`, falling back to `dtc` in `PATH` with detailed build hints. It builds `cpp_flags` and a `DTC` command string. With two inputs it runs `diff` over process substitutions of normalized output; with one input it prints normalized DTS. It persists no files except subprocess temp state.

## Dependencies and Integration
It depends on Bash, `cpp`, `dtc`, `hexdump`, `diff`, `git`, `which`, and kernel source include-prefixes. `dt_to_config` uses it as a normalizer.

## Risks and Test Signals
The script relies on `ARCH` for include paths and can include the wrong local file when diffing trees from different directories. Command strings and paths are not robustly quoted. Test source, blob, and fs inputs; two-way diffs; `-S` and `-s`; `KBUILD_OUTPUT`; color fallback; annotation; unsorted mode; missing dtc; and bad `ARCH`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/dtx_diff -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/fdtget.c -->
# sources/distributed-fs/ceph-client/scripts/dtc/fdtget.c

## Purpose
`fdtget.c` implements the `fdtget` host utility for reading property values, listing properties, or listing subnodes from a flattened device tree blob.

## Important APIs, Types, and Functions
`enum display_mode` selects value, properties, or subnodes. `struct display_info` stores type, cell size, mode, and default value. `show_data()` formats string lists or integer data using selected or guessed size. `list_properties()` and `list_subnodes()` enumerate libfdt structures. `show_data_for_item()` dispatches by mode. `do_fdtget()` reads the blob and processes node/property argument groups.

## Control Flow and State
`main()` parses `-t`, `-p`, `-l`, `-d`, and `-h`, validates filename and argument grouping, then calls `do_fdtget()`. The blob is loaded with `utilfdt_read()`. For each node path, missing nodes or properties either print the default value or produce libfdt diagnostics. State is local to the loaded blob and display options.

## Dependencies and Integration
It depends on libfdt, `util.h` helpers including `utilfdt_read()`, `utilfdt_decode_type()`, `util_is_printable_string()`, and `USAGE_TYPE_MSG`. It is built as part of DTC host tools.

## Risks and Test Signals
`show_data()` casts unaligned byte pointers to `uint32_t *` for 4-byte reads, which can matter on strict-alignment hosts. Listing subnodes manually walks tags with a fixed `MAX_LEVEL` of 32. Test string, byte, 16-bit, 32-bit, signed/unsigned/hex formatting, defaults, missing paths, property and subnode list modes, deep trees, and malformed blobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/dtc/fdtget.c -->
