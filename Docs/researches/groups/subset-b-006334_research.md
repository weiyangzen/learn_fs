# subset-b-006334 Kernel Scripts and Module Postprocessing Research

This grouped report covers the assigned Ceph-client mirror of Linux kernel helper scripts for livepatch builds, FIT image generation, diagnostic annotation, packaging, module metadata generation, and module postprocessing. Each section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/livepatch/klp-build -->
# sources/distributed-fs/ceph-client/scripts/livepatch/klp-build

## Purpose

`klp-build` builds a livepatch kernel module from one or more patch files. It validates livepatch-capable kernel configuration, builds original and patched kernels with function/data sections and objtool checksums, diffs changed objects with `objtool klp diff`, and links the resulting objects into a normal loadable module.

## Important APIs, Types, and Functions

The script is Bash 4.4+ and uses functions as its API: `process_args()`, `validate_config()`, `set_kernelversion()`, patch parsers, `apply_patch()`/`revert_patch()`, `fix_patches()`, `build_kernel()`, `find_objects()`, object copy/diff helpers, `diff_checksums()`, and `build_patch_module()`. Global state includes `PATCHES`, `APPLIED_PATCHES`, `STASHED_FILES`, temp subdirectories, `NAME`, `OUTFILE`, `REPLACE`, `SHORT_CIRCUIT`, `JOBS`, and debug/verbosity flags.

## Control Flow

The main path processes arguments, initializes temp state, validates patches, builds a clean original tree, copies original `.o` files for `vmlinux.o` and modules, fixes patch line numbers with `fix-patch-lines` and `recountdiff`, applies patches, builds the patched tree, copies changed objects, diffs them through objtool, optionally identifies first changed instructions, and builds a final module under `klp-tmp/kmod`. Short-circuit mode resumes at selected stages when a preserved temp tree exists.

## State and Persistence Behavior

Persistent effects are intentionally bounded but invasive during execution: it applies and reverts source patches, temporarily modifies `scripts/setlocalversion`, runs kernel builds, creates `klp-tmp`, writes logs and copied object trees, and emits the final `.ko`. Cleanup traps revert patches, restore stashed files, and remove temp state unless `--keep-tmp`, debug, or short-circuit behavior requests preservation.

## Dependencies and Integration Points

It integrates with top-level Kbuild, `.config`, `scripts/livepatch/init.c`, `tools/objtool/objtool`, GNU `patch`, `gawk`, `find`, `objcopy`, `recountdiff` from patchutils, and `fix-patch-lines`. It depends on `CONFIG_LIVEPATCH`, `CONFIG_KLP_BUILD`, compatible objtool support, and unsupported-patch filters for `lib/*` and assembly.

## Risks and Edge Cases

The script mutates a live source tree and relies on trap cleanup, so interrupted or externally modified runs can leave patched files or temp output. It rejects some unsupported inputs but cannot prove semantic livepatch safety. Timestamp-based changed-object discovery is backed by `cmp`, but stale objects and unusual out-of-tree layouts are explicitly unsupported. Missing objtool, bad `.cmd` data, modpost warnings, BTF corruption, or kernel config plugins can fail late.

## Test Signals

Good signals are dry-run patch validation, clean original and patched build logs, non-empty diff objects, successful `objtool klp post-link`, a final loadable `.ko`, and `--show-first-changed` output for known function edits. Regression tests should cover fuzzed patches, multiple patches, `--no-replace`, short-circuit resume, unsupported paths, missing config flags, and cleanup after failed builds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/livepatch/klp-build -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/macro_checker.py -->
# sources/distributed-fs/ceph-client/scripts/macro_checker.py

## Purpose

`macro_checker.py` scans C and header files for function-like macros whose formal parameters are not referenced in the replacement text. It is a lightweight style/bug finder meant to catch stale macro arguments while avoiding common false positives.

## Important APIs, Types, and Functions

The script exposes command-line arguments `path` and `--verbose`. `check_macro()` parses one full macro definition, compares arguments to the macro body, prints diagnostics, and records names with at least one observed correct definition. `macro_strip()` removes simple comment/whitespace forms. `file_check_macro()` handles `.c` and `.h` files, including backslash continuations and conditional-compilation depth. `dir_check_macro()` recurses into directories.

## Control Flow

`main()` decides whether the target is a file or directory. Each file is first scanned in report-suppressed mode to populate `correct_macros`, then scanned in reporting mode. Non-verbose mode skips `.c` macros inside any conditional block and `.h` macros outside the usual outer include-guard depth. Verbose mode checks conditional macros too.

## State and Persistence Behavior

The only retained state is the process-global `correct_macros` list and parsed `args`. The script writes diagnostics to stdout and does not modify source files.

## Dependencies and Integration Points

It depends only on Python standard modules `argparse`, `os`, and `re`. It integrates as a developer/CI lint helper rather than a Kbuild build product.

## Risks and Edge Cases

Parsing is regex-based and does not fully understand C preprocessing, nested parentheses, stringification, token pasting, comments, or identifiers appearing inside strings. Substring matching can mistake `a` as used inside another token. Directory order affects `correct_macros`, and the error message has a typo for nonexistent paths.

## Test Signals

Tests should include single-line and multiline macros, variadic macros, empty `do {} while (0)`/`0`/`1` macros, include guards, conditional definitions, duplicate macro names with correct and incorrect variants, and macro arguments that appear only as token substrings.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/macro_checker.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/make_fit.py -->
# sources/distributed-fs/ceph-client/scripts/make_fit.py

## Purpose

`make_fit.py` builds a U-Boot-compatible FIT image containing a kernel, optional ramdisk, and many DTBs. It can compress image payloads, deduplicate DTBs, decompose composite DTBs created by `fdtoverlay`, and optionally convert embedded data into external FIT data.

## Important APIs, Types, and Functions

Important functions are `parse_args()`, `setup_fit()`, `write_kernel()`, `write_ramdisk()`, `finish_fit()`, `compress_data()`, `compress_dtb()`, `output_dtb()`, `process_dtb()`, `_process_dtbs()`, `build_fit()`, and `run_make_fit()`. `COMP_TOOLS` maps compression names to file extensions and command fallback lists. It uses `libfdt.FdtSw` for writing and `libfdt.FdtRo` for reading DTB model/compatible metadata.

## Control Flow

The main path parses FIT metadata, writes the root and `/images`, compresses and embeds the kernel, embeds an uncompressed ramdisk if supplied, processes DTBs, writes `/configurations`, packs the FDT, writes the output file, and optionally runs `mkimage -E -F` to externalize payload data. DTB processing first reads root properties, optionally uses the `.dtb.cmd` file to split composite DTBs into base/overlay inputs, compresses unique DTB files in parallel, and emits each unique file once.

## State and Persistence Behavior

The script persists only the requested FIT output file. During compression it creates temporary files and multiprocessing worker state. The FIT contains a generation timestamp, payload bytes or external data metadata, per-DTB nodes, and configurations referencing one or more `fdt-*` nodes.

## Dependencies and Integration Points

It depends on Python `libfdt`, external compression commands such as `gzip`, `zstd`, `xz`, `lz4`, and optional `mkimage`. It integrates with kernel DTB build output, particularly `.cmd` files containing `scripts/dtc/fdtoverlay` commands, and with bootloaders that understand FIT.

## Risks and Edge Cases

Compression uses `subprocess.call()` but does not inspect non-zero exit status if the tool exists, so failed compressors can produce empty or bad payloads. Composite DTB decomposition assumes command-line structure around `-i`. Missing root `model` or `compatible`, missing `.cmd` files, duplicate basenames, huge payloads, absent compression tools, and external FIT conversion failures are important edges.

## Test Signals

Useful tests build FITs with no compression and each supported compressor, verify DTB deduplication and composite decomposition, run `dumpimage`/`fdtdump` on the output, check external FIT totalsize reporting, and assert failures for missing kernel, bad DTB, missing compressor, malformed `.cmd`, and absent `mkimage`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/make_fit.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/makelst -->
# sources/distributed-fs/ceph-client/scripts/makelst

## Purpose

`makelst` creates mixed source/assembly listings with relocation addresses adjusted against `System.map`. It is intended for Makefile rules that compile a `.c` file with debug info and pipe objdump output into a `.lst` artifact.

## Important APIs, Types, and Functions

The only helper is `field()`, a shell function that returns a numbered whitespace field after shifting. The script expects three positional arguments: object file, `System.map`, and objdump binary.

## Control Flow

It asks objdump for symbols in the object, selects the first text function, extracts its symbol name and object VMA, finds the same symbol in `System.map`, computes the address delta, and runs objdump with `-r --source --adjust-vma=<delta>`. If no readable `System.map` is present, it warns and defaults adjustment to zero.

## State and Persistence Behavior

There is no persistent state. Output is written to stdout and diagnostics to stderr.

## Dependencies and Integration Points

It depends on POSIX shell, `grep`, arithmetic expansion, `printf`, and the provided objdump. It integrates with optional Kbuild listing targets that know the object and `System.map` paths.

## Risks and Edge Cases

Symbol matching is simple text grep and can pick ambiguous names. Missing or mismatched `System.map`, object files without `.text` functions, non-GNU objdump output, and very large address deltas can degrade listings. The script does not quote all command substitutions robustly around unusual symbol data.

## Test Signals

Test with an object whose first text function appears in `System.map`, a missing map, no text symbols, and cross-objdump output. Validate that adjusted addresses match the linked kernel addresses and relocations remain visible.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/makelst -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/markup_oops.pl -->
# sources/distributed-fs/ceph-client/scripts/markup_oops.pl

## Purpose

`markup_oops.pl` reads an x86 kernel oops from stdin, finds the faulting instruction in `vmlinux` or a module, disassembles nearby code, and annotates the output with known register values from the oops.

## Important APIs, Types, and Functions

Options are `--cross-compile`, `--module`, and `--help`. `parse_x86_regs()` extracts 32-bit and 64-bit register dumps. `reg_name()` normalizes some 64-bit register names to 32-bit aliases. `process_x86_regs()` marks read and clobbered registers while walking backward from the fault. `InRange()` tests address proximity with `Math::BigInt`.

## Control Flow

The script parses stdin for EIP/RIP target address, function name, function offset, module name, and registers. If the fault is in a module, it locates the module file through `modinfo` unless explicitly provided and computes an `--adjust-vma` offset by disassembling the module. It then runs objdump around the target address, keeps lines within roughly 4 KiB, finds the center line, computes print bounds, walks backward to annotate registers, and prints a marked instruction window.

## State and Persistence Behavior

State is in Perl scalars, `%regs`, and temporary arrays of disassembly lines. It has no persistent writes.

## Dependencies and Integration Points

It depends on Perl, `Getopt::Long`, `Math::BigInt`, objdump via `CROSS_COMPILE`, `modinfo`, a matching `vmlinux` or `.ko`, and oops formats generated by x86 kernels.

## Risks and Edge Cases

The parser is x86-centric and regex-sensitive; newer oops formats, KASLR offsets, inline frames, ORC output, compressed/debug-split modules, or unavailable module files can prevent matching. Register annotation is heuristic and does not fully model instruction semantics, memory writes, aliases, or flags.

## Test Signals

Use known oops snippets for 32-bit, 64-bit, vmlinux, and module faults; verify that the faulting line is marked and address adjustment is correct. Negative tests should cover missing target, absent module file, and unsupported oops formats.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/markup_oops.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/min-tool-version.sh -->
# sources/distributed-fs/ceph-client/scripts/min-tool-version.sh

## Purpose

`min-tool-version.sh` prints the minimum supported version for a named kernel build tool. It centralizes version floors consumed by build checks and documentation.

## Important APIs, Types, and Functions

The command accepts exactly one tool name. Supported names are `binutils`, `gcc`, `llvm`, `rustc`, and `bindgen`. The GCC floor is special-cased for `ARCH=parisc64`, and the LLVM floor is special-cased for `SRCARCH=loongarch`.

## Control Flow

After argument-count validation, a `case` statement echoes the tool-specific version or fails with an unknown-tool error.

## State and Persistence Behavior

The script is read-only. Output is the version string on stdout; errors go to stderr with a non-zero exit.

## Dependencies and Integration Points

It depends only on POSIX shell and environment variables set by Kbuild. It integrates with compiler/toolchain version checks and must stay synchronized with `Documentation/process/changes.rst`.

## Risks and Edge Cases

The values are policy, not detection. Drift between this script, docs, and actual compiler feature use can reject valid setups or accept broken ones. Architecture environment variables must be set correctly for special cases.

## Test Signals

Run for every known tool, for `ARCH=parisc64`, for `SRCARCH=loongarch`, and for an unknown tool. Build tests with exactly-minimum and just-below-minimum toolchains validate the floors.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/min-tool-version.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/misc-check -->
# sources/distributed-fs/ceph-client/scripts/misc-check

## Purpose

`misc-check` runs extra repository hygiene checks controlled by `KBUILD_EXTRA_WARN`. It catches tracked files ignored by git and mismatches between `EXPORT_SYMBOL()` use and direct inclusion of `<linux/export.h>`.

## Important APIs, Types, and Functions

`check_tracked_ignored_files()` reports tracked files that match ignore rules. `check_missing_include_linux_export_h()` finds C/header providers using export macros without including `<linux/export.h>`. `check_unnecessary_include_linux_export_h()` warns about `.c` files including the header without exporting symbols.

## Control Flow

The script exits on shell errors. If `KBUILD_EXTRA_WARN` contains `1`, it runs the git-ignore check. If it contains `2`, it runs both export-header checks. Git grep pipelines use `xargs -r` and write warnings to stderr.

## State and Persistence Behavior

It is read-only and emits warnings only. It uses `${srctree:-.}` to choose the source root.

## Dependencies and Integration Points

It depends on git, sed, xargs, grep-compatible regexes, and a git worktree. It integrates with Kbuild warning levels and source include-hygiene cleanup.

## Risks and Edge Cases

The checks require git metadata and intentionally exclude `tools/`. Regex detection can miss multiline or macro-wrapped exports and can warn on unusual generated files. It warns but does not fix ordering or include placement.

## Test Signals

Test with temporary tracked ignored files, source files with and without export macros, direct and indirect export-header use, and `KBUILD_EXTRA_WARN` combinations `0`, `1`, `2`, and `12`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/misc-check -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mkcompile_h -->
# sources/distributed-fs/ceph-client/scripts/mkcompile_h

## Purpose

`mkcompile_h` generates compile identity macros for kernel build metadata: target machine, build user, build host, and compiler/linker string.

## Important APIs, Types, and Functions

It accepts `UTS_MACHINE`, `CC_VERSION`, and `LD` as positional arguments. It honors `KBUILD_BUILD_USER` and `KBUILD_BUILD_HOST`; otherwise it derives them from `whoami` and `uname -n`. Linker identity comes from `$LD -v`.

## Control Flow

The script chooses user/host strings, escapes backslashes in the user, normalizes the first linker version line by removing compatibility parentheticals/trailing whitespace, and prints a small C header fragment with four `#define`s.

## State and Persistence Behavior

It writes only to stdout. Kbuild decides whether generated output replaces a header.

## Dependencies and Integration Points

It depends on shell, `whoami`, `uname`, `head`, `sed`, and a linker executable. It integrates with generated kernel compile metadata included in version reporting.

## Risks and Edge Cases

User/host strings can contain quotes or other characters not escaped here. Linker version formatting is tool-dependent. Reproducible builds must set `KBUILD_BUILD_USER` and `KBUILD_BUILD_HOST` to stable values.

## Test Signals

Run with explicit build user/host, unset environment, linker strings with compatibility text, and unusual usernames. Verify produced C string literals compile.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mkcompile_h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mksysmap -->
# sources/distributed-fs/ceph-client/scripts/mksysmap

## Purpose

`mksysmap` is a sed filter that removes symbols unsuitable for `System.map` and kallsyms from sorted `nm -n` output.

## Important APIs, Types, and Functions

The file is itself a sed script. Rules delete local absolute/debug/undefined/local-weak symbols, local-label prefixes such as `$` and `.L`, and architecture-specific private namespaces such as arm64 EFI, PIE, and non-VHE KVM local symbols.

## Control Flow

Input lines are streamed through ordered sed delete patterns. Lines not matching any ignored symbol type or prefix pass through unchanged.

## State and Persistence Behavior

It is stateless and writes filtered symbols to stdout.

## Dependencies and Integration Points

It depends on sed and the symbol format produced by `nm -n`. It integrates with kernel `System.map` generation, kallsyms, module-init tools, and debugging tools.

## Risks and Edge Cases

Filtering is string-pattern based. New compiler-generated local symbol names or architecture namespaces can leak into `System.map` until a rule is added, while overly broad patterns can hide useful symbols. Format drift in `nm` output would break matching.

## Test Signals

Feed synthetic `nm` rows for ignored types, local labels, architecture prefixes, and normal exported/text/data symbols. Compare `System.map` content across architectures after compiler upgrades.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mksysmap -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mkuboot.sh -->
# sources/distributed-fs/ceph-client/scripts/mkuboot.sh

## Purpose

`mkuboot.sh` invokes U-Boot `mkimage` when the tool is available. It is a thin availability/check wrapper used by architecture image rules that already assemble the correct `mkimage` arguments.

## Important APIs, Types, and Functions

The script has no internal functions. It chooses `${CROSS_COMPILE}mkimage` first, then falls back to host `mkimage`, and forwards all original arguments with `"$@"`.

## Control Flow

It searches `PATH` with `type -path`. If no tool is found it prints a warning-style error and exits non-zero; otherwise it executes the selected `mkimage` with the caller-provided argument vector.

## State and Persistence Behavior

The only persistent effect is whatever output file the forwarded `mkimage` invocation creates.

## Dependencies and Integration Points

It depends on U-Boot `mkimage`, optional `CROSS_COMPILE`, and Kbuild-provided command arguments. It integrates with architecture boot-image targets.

## Risks and Edge Cases

Wrong load/entry addresses, compression labels, architecture strings, or stale input images produce boot failures that the wrapper cannot detect because it only forwards arguments. Missing `mkimage` causes the image target to fail.

## Test Signals

Build a known image, inspect it with `mkimage -l`, and boot it under the target firmware or emulator. Negative tests should cover missing host and cross `mkimage`, missing input, and invalid forwarded parameters.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mkuboot.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/Makefile -->
# sources/distributed-fs/ceph-client/scripts/mod/Makefile

## Purpose

`scripts/mod/Makefile` defines host-side build products for module postprocessing: `modpost`, `mk_elfconfig`, `empty.o`, generated `elfconfig.h`, and generated `devicetable-offsets.h`.

## Important APIs, Types, and Functions

Key variables are `hostprogs-always-y`, `always-y`, `modpost-objs`, `devicetable-offsets-file`, and `targets`. Explicit dependencies force `modpost.o`, `file2alias.o`, `sumversion.o`, and `symsearch.o` to include generated ELF configuration, while `file2alias.o` also depends on device-table offsets.

## Control Flow

Kbuild first builds `empty.o` without LTO flags, runs `mk_elfconfig` over it to produce target ELF-class/endian configuration, assembles `devicetable-offsets.s`, filters it through `filechk offsets` to produce the offsets header, and then builds host `modpost` from its object list.

## State and Persistence Behavior

Persistent generated files are under the build object directory: `elfconfig.h`, `devicetable-offsets.h`, `devicetable-offsets.s`, `empty.o`, `mk_elfconfig`, and `modpost`.

## Dependencies and Integration Points

It depends on Kbuild host-program rules, `filechk`, generated-offset conventions, and the target compiler output for `empty.o`. It integrates directly with module builds and `vmlinux` export generation.

## Risks and Edge Cases

Stale generated headers can cause host tools to parse target ELF or device tables incorrectly. LTO must be removed from `empty.o` so ELF probing remains stable. Adding new device-table structures requires synchronized changes in `devicetable-offsets.c` and `file2alias.c`.

## Test Signals

Build host tools for 32-bit and 64-bit targets, big and little endian, with and without LTO. Verify regenerated headers change when target ABI or mod device-table layouts change.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/devicetable-offsets.c -->
# sources/distributed-fs/ceph-client/scripts/mod/devicetable-offsets.c

## Purpose

`devicetable-offsets.c` emits C-structure sizes and field offsets for all `struct *_device_id` tables consumed by `file2alias.c`. It lets a host tool decode target-built module data without assuming host ABI layout.

## Important APIs, Types, and Functions

Macros `DEVID()` and `DEVID_FIELD()` wrap `DEFINE()` from `linux/kbuild.h`. `main()` enumerates each supported device-id type and the fields needed to build module alias strings.

## Control Flow

Kbuild compiles the file to assembly, where `DEFINE()` markers are then extracted by `filechk offsets` into `devicetable-offsets.h`. There is no runtime behavior beyond returning from `main()`.

## State and Persistence Behavior

The generated header persists size and offset constants such as `SIZE_usb_device_id` and `OFF_usb_device_id_idVendor`.

## Dependencies and Integration Points

It depends on `linux/mod_devicetable.h` and the generated-offset mechanism. It must stay in lockstep with `file2alias.c` and any kernel structures referenced by `MODULE_DEVICE_TABLE()`.

## Risks and Edge Cases

Missing a field causes aliases to be incomplete or decoded at the wrong offset. Adding a new device table requires a size entry here and a handler in `file2alias.c`. Cross-endian and packed layout issues are only safe if offsets match target compilation.

## Test Signals

Regenerate offsets after changing `mod_devicetable.h`, build modules for multiple architectures, and compare produced `MODULE_ALIAS()` strings for USB, PCI, OF, ACPI, and newer bus tables.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/devicetable-offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/empty.c -->
# sources/distributed-fs/ceph-client/scripts/mod/empty.c

## Purpose

`empty.c` is an intentionally empty translation unit used to produce `empty.o` for target ELF probing.

## Important APIs, Types, and Functions

It defines no functions or data.

## Control Flow

Kbuild compiles it, then `mk_elfconfig` reads the resulting object to infer target ELF class and endianness.

## State and Persistence Behavior

The only persisted artifact is `empty.o` in the object tree.

## Dependencies and Integration Points

It integrates with `scripts/mod/Makefile` and `mk_elfconfig.c`. LTO flags are removed for this object to keep the probe object simple.

## Risks and Edge Cases

If the compiler emits unusual or non-ELF output due to flags, `mk_elfconfig` may fail. The file itself has no logic risk.

## Test Signals

Build `empty.o` for each target class/endian combination and verify `elfconfig.h` reports the expected `KERNEL_ELFCLASS` and `KERNEL_ELFDATA`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/empty.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/file2alias.c -->
# sources/distributed-fs/ceph-client/scripts/mod/file2alias.c

## Purpose

`file2alias.c` converts `MODULE_DEVICE_TABLE()` ELF symbols into generated `MODULE_ALIAS()` metadata. It decodes target-compiled device-id arrays for many buses and appends alias strings to the module record used by `modpost`.

## Important APIs, Types, and Functions

The public entry point is `handle_moddevtable()`. Core helpers include `module_alias_printf()`, `do_table()`, `sym_is()`, `add_uuid()`, `add_guid()`, and many `do_*_entry()` handlers for USB, OF, HID, PCI, ACPI, PNP, input, virtio, vmbus, I2C, SPI, DMI, platform, AMBA, CPU, Type-C, MHI, auxiliary, CDX, and other buses. `struct devtable` maps device-table names to target sizes and handler callbacks.

## Control Flow

For each ELF symbol, `handle_moddevtable()` filters for section-relative object symbols named `__mod_device_table__kmod_<modname>__<type>__<name>`. It obtains symbol data from the ELF image or zero-fills NOBITS data, finds the matching `devtable` entry, checks array size and NULL terminator, and invokes the bus-specific entry formatter for each element except the terminator. Handlers read fields through generated offsets and `get_unaligned_native()`, construct modalias syntax, and deduplicate aliases.

## State and Persistence Behavior

State is appended to `mod->aliases` as dynamically allocated `struct module_alias` entries. Built-in aliases may carry a builtin module name later emitted by `modpost`; loadable modules become `MODULE_ALIAS()` lines in generated `.mod.c`.

## Dependencies and Integration Points

It depends on target ELF definitions from `elfconfig.h`, offsets from `devicetable-offsets.h`, `linux/mod_devicetable.h`, `modpost.h`, list helpers, and `xalloc`. It is linked into host `modpost` and feeds module autoloading through depmod/modalias consumers.

## Risks and Edge Cases

The file is sensitive to device-table layout, target endianness, unaligned access, alias grammar, and terminator validation. A missing or wrong handler breaks device autoloading. Fixed-size alias buffers and string formatting require careful bounds assumptions. Composite match rules such as USB BCD ranges and input bitmaps are easy to regress.

## Test Signals

Compile test modules with every `MODULE_DEVICE_TABLE()` family and compare generated aliases against expected modalias strings. Test malformed arrays, missing terminators, NOBITS all-zero tables, duplicate aliases, cross-endian builds, and new bus table additions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/file2alias.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/mk_elfconfig.c -->
# sources/distributed-fs/ceph-client/scripts/mod/mk_elfconfig.c

## Purpose

`mk_elfconfig.c` reads an ELF object from stdin and emits preprocessor defines describing the target ELF class and data encoding for host-side module tools.

## Important APIs, Types, and Functions

Its `main()` reads `Elf32_Ehdr`, verifies the ELF magic, checks `EI_CLASS` for `ELFCLASS32` or `ELFCLASS64`, and checks `EI_DATA` for little or big endian.

## Control Flow

The program consumes the header, prints `#define KERNEL_ELFCLASS ...` and `#define KERNEL_ELFDATA ...`, and exits with failure for non-ELF or unknown class/data values.

## State and Persistence Behavior

It has no persistent state itself; Kbuild redirects stdout into `elfconfig.h`.

## Dependencies and Integration Points

It depends on host `<elf.h>` and standard I/O. It integrates with the `empty.o` target object generated by Kbuild and with all `scripts/mod` C files that include `elfconfig.h`.

## Risks and Edge Cases

The probe assumes the first bytes on stdin are an ELF header. Truncated or LTO-wrapper objects can fail. Host `<elf.h>` constants must be available and compatible.

## Test Signals

Feed known 32-bit, 64-bit, little-endian, big-endian, invalid, and truncated ELF headers; verify define output and failure status.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/mk_elfconfig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/modpost.c -->
# sources/distributed-fs/ceph-client/scripts/mod/modpost.c

## Purpose

`modpost.c` is the main host-side postprocessor for kernel object metadata. It reads relocatable ELF objects and symbol-version dumps, collects exports and unresolved symbols, checks licenses, namespaces, section mismatches, and module metadata, then writes generated `.mod.c`, `.vmlinux.export.c`, `Module.symvers`, and namespace dependency files.

## Important APIs, Types, and Functions

Key APIs include `read_symbols()`, `parse_elf()`, `handle_symbol()`, `handle_moddevtable()`, `check_sec_ref()`, `extract_crcs_for_object()`, `mod_set_crcs()`, `check_exports()`, `write_mod_c_file()`, `write_vmlinux_export_c_file()`, `read_dump()`, `write_dump()`, `write_namespace_deps_files()`, and `main()`. Core state is held in `struct module`, internal `struct symbol`, the global `modules` list, `symbol_hashtable`, and option flags for module support, modversions, trimming, external modules, warning policy, and endianness.

## Control Flow

`main()` parses options, detects host endian, reads optional symbol dumps, reads object paths from arguments or `-T`, and processes each object. ELF parsing mmaps the object, normalizes endianness, finds sections, symbol tables, `.modinfo`, `.export_symbol`, `.no_trim_symbol`, and initializes nearest-symbol search. Symbol handling records undefined references, exports, init/cleanup presence, module aliases, and metadata. Later passes check section references, license/GPL export use, namespace imports, dependencies, symbol CRCs, module-name length, and generated C output.

## State and Persistence Behavior

In-memory state persists per run across all modules so dependencies can be resolved globally. Persistent outputs include `<module>.mod.c`, `.vmlinux.export.c`, `Module.symvers`-style dumps, and missing namespace dependency files. `write_if_changed()` avoids touching generated files when content is identical.

## Dependencies and Integration Points

It depends on host ELF headers, Kbuild-generated `.mod` and `.*.cmd` files, genksyms `#SYMVER` lines, `license.h`, `file2alias.c`, `sumversion.c`, `symsearch.c`, and kernel list/hash/xalloc helpers. It is central to `make modules`, external module builds, module autoloading, modversion CRCs, namespace enforcement, and section-mismatch diagnostics.

## Risks and Edge Cases

ELF parsing is security-sensitive because malformed object bounds, extended section indices, cross-endian data, and relocation addends are handled manually. Policy flags change warnings into errors. Missing `Module.symvers`, stale `.cmd` files, long symbol names, GPL-only imports by non-GPL modules, namespace drift, and architecture-specific relocation encodings can cause subtle build failures.

## Test Signals

Use `allmodconfig`, `allyesconfig`, external module builds, modversions basic and extended modes, namespace import tests, GPL-only export tests, section-mismatch fixtures, missing-symbol warning/error modes, cross-endian targets, and malformed object tests. Generated `.mod.c` and `Module.symvers` should be stable under no-op rebuilds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/modpost.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/modpost.h -->
# sources/distributed-fs/ceph-client/scripts/mod/modpost.h

## Purpose

`modpost.h` defines the shared host-tool ABI for `modpost`, `file2alias`, `sumversion`, and `symsearch`. It abstracts target ELF class/endian handling, unaligned reads, module records, ELF metadata, buffers, aliases, and logging.

## Important APIs, Types, and Functions

Important macros are target-selecting `Elf_*` typedef aliases, `TO_NATIVE()`, `get_unaligned_native()`, `ARRAY_SIZE()`, and `strstarts()`. Important types are `struct buffer`, `struct module_alias`, `struct module`, and `struct elf_info`. Declared functions include `buf_printf()`, `buf_write()`, `symsearch_init()`, `symsearch_find_nearest()`, `handle_moddevtable()`, `get_src_version()`, `read_text_file()`, `get_line()`, `sym_get_data()`, and `modpost_log()`.

## Control Flow

The header has inline helpers for section-index normalization and symbol-name validity. It maps ELF32 or ELF64 types at compile time based on generated `elfconfig.h`, while runtime globals choose endian conversion.

## State and Persistence Behavior

It declares external `target_is_big_endian` and `host_is_big_endian` and structures that own in-memory module lists, alias lists, no-trim symbol data, and parsed ELF pointers. It does not persist files itself.

## Dependencies and Integration Points

It depends on `elfconfig.h`, Linux host helper headers, and `module_symbol.h`. It is included by all module postprocessing translation units.

## Risks and Edge Cases

Type abstraction must match the target object, not the host. Incorrect endian or class configuration corrupts parsing. `get_secindex()` must handle large section tables and reserved ranges consistently. Consumers must free buffers and symsearch state.

## Test Signals

Build `modpost` for ELF32/ELF64 and big/little-endian targets, test more-than-64k sections, mapping symbols, unaligned fields, and error/warn/fatal formatting.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/modpost.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/sumversion.c -->
# sources/distributed-fs/ceph-client/scripts/mod/sumversion.c

## Purpose

`sumversion.c` computes module source-version hashes for `MODULE_INFO(srcversion, ...)`. It hashes relevant source files and dependency lists using an in-file MD4 implementation.

## Important APIs, Types, and Functions

The public function is `get_src_version()`. Internal MD4 helpers include `md4_init()`, `md4_update()`, `md4_transform()`, and `md4_final_ascii()`. Source parsing helpers include `parse_file()`, `parse_source_files()`, `parse_string()`, `parse_comment()`, and `is_static_library()`.

## Control Flow

Given a module name, the code reads the module's `.mod` file to find object/source inputs, skips static libraries as needed, parses source file content while normalizing comments and strings, updates the MD4 context, and writes an ASCII digest into the provided buffer.

## State and Persistence Behavior

State is local to the MD4 context and temporary file buffers. The result persists only when `modpost` emits it into generated `.mod.c`.

## Dependencies and Integration Points

It depends on `modpost.h`, `read_text_file()`, `get_line()`, Kbuild `.mod` files, and source file availability. It integrates with `CONFIG_MODULE_SRCVERSION_ALL` and module `version` metadata behavior in `modpost.c`.

## Risks and Edge Cases

The hash is build metadata, not cryptographic integrity. Missing `.mod` or source files, generated sources, static libraries, and parser approximations for C syntax can affect reproducibility. MD4 implementation and endian conversion must remain stable for existing version semantics.

## Test Signals

Compare srcversion output before and after source edits, comments, string changes, generated file changes, missing files, and static library references. Verify deterministic results across host endianness.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/sumversion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/symsearch.c -->
# sources/distributed-fs/ceph-client/scripts/mod/symsearch.c

## Purpose

`symsearch.c` builds sorted per-section symbol lookup tables so `modpost` can find nearest symbols for relocation/section-mismatch diagnostics.

## Important APIs, Types, and Functions

Internal types are `struct syminfo` and `struct symsearch`. `syminfo_compare()`, `symbol_count()`, `symsearch_populate()`, and `symsearch_fixup()` build the tables. Public functions are `symsearch_init()`, `symsearch_finish()`, and `symsearch_find_nearest()`.

## Control Flow

Initialization counts valid named symbols, allocates table storage, records symbol pointers with section indexes and values, sorts them, and fixes duplicate/ordering details for nearest lookup. Lookup searches for the closest symbol in the requested section, optionally allowing negative distances and enforcing a minimum distance bound. Finish frees the allocated state.

## State and Persistence Behavior

The lookup table is attached to `struct elf_info` for the lifetime of one parsed object and freed in `parse_elf_finish()`. No files are written.

## Dependencies and Integration Points

It depends on `modpost.h`, target ELF symbol tables, valid-name filtering, and qsort/bsearch-style ordering. It is used by section mismatch reporting in `modpost.c`.

## Risks and Edge Cases

Nearest-symbol diagnostics can be misleading for stripped, compiler-generated, duplicate-address, or section-boundary symbols. Large objects consume memory proportional to symbol count. Incorrect section-index normalization breaks lookups.

## Test Signals

Test relocations near named symbols, duplicate addresses, missing names, mapping symbols, section boundaries, negative-distance behavior, and large symbol tables.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/symsearch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/module-common.c -->
# sources/distributed-fs/ceph-client/scripts/module-common.c

## Purpose

`module-common.c` provides common module metadata source included in the module link process, primarily vermagic information.

## Important APIs, Types, and Functions

It defines `INCLUDE_VERMAGIC` and includes `linux/module.h` and related module metadata headers. The file relies on header-side macros rather than defining functions.

## Control Flow

Compilation expands module metadata definitions needed by Kbuild for module objects.

## State and Persistence Behavior

The persisted effect is object-file metadata included in module builds.

## Dependencies and Integration Points

It depends on kernel module headers, generated compile/config metadata, and Kbuild module linking. It integrates with module version compatibility checks.

## Risks and Edge Cases

Incorrect header inclusion or config-dependent macro changes can alter vermagic and make modules unloadable on the intended kernel. The file is small but sits in a sensitive build path.

## Test Signals

Build modules across config/compiler changes and inspect `modinfo vermagic`. Confirm expected rejection or acceptance by `insmod` on matching and mismatching kernels.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/module-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/module.lds.S -->
# sources/distributed-fs/ceph-client/scripts/module.lds.S

## Purpose

`module.lds.S` is the linker script fragment for kernel modules. It arranges module-specific sections, metadata, init/exit areas, alternatives, unwind/orc data, BTF, and architecture-provided sections into a layout expected by the loader.

## Important APIs, Types, and Functions

The file uses linker-script `SECTIONS` syntax and C preprocessor conditionals/macros from kernel linker headers. Important section families include `.text`, `.init`, `.exit`, `.modinfo`, `__versions`, `__patchable_function_entries`, `.orc_*`, `.BTF`, and architecture hook sections.

## Control Flow

The linker consumes the script during module final link. Section patterns collect input sections, preserve required metadata with `KEEP()` where needed, and discard or align sections according to kernel module expectations.

## State and Persistence Behavior

The script persists no state itself, but controls the section layout of every `.ko` linked with it.

## Dependencies and Integration Points

It depends on GNU ld/LLD linker-script compatibility, module loader expectations, modpost-generated sections, objtool ORC data, BTF generation, livepatch metadata, and architecture linker fragments.

## Risks and Edge Cases

Dropping required sections can break module loading, unwinding, tracing, BTF, alternatives, or symbol versioning. Linker differences and new instrumentation sections require careful updates. Alignment and `KEEP()` placement affect garbage collection.

## Test Signals

Build and load modules with modversions, ORC unwind, BTF, ftrace, livepatch, alternatives, and multiple architectures using ld.bfd and LLD. Inspect `readelf -S` and module loader diagnostics.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/module.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/modules-check.sh -->
# sources/distributed-fs/ceph-client/scripts/modules-check.sh

## Purpose

`modules-check.sh` validates module install/order metadata for duplicate module names that would collide after installation.

## Important APIs, Types, and Functions

The script operates on module list files such as `modules.order`, converting object paths to `.ko` names and checking basenames.

## Control Flow

It reads module paths, normalizes them, sorts or groups by basename, and reports duplicate module names as errors.

## State and Persistence Behavior

It is read-only and exits non-zero when duplicates are found.

## Dependencies and Integration Points

It depends on POSIX shell and core text utilities. It integrates with Kbuild module checks before packaging or installation.

## Risks and Edge Cases

Only name-level collisions are detected; semantic conflicts or aliases are outside scope. Generated or externally supplied module lists must be current. Path normalization must match install naming.

## Test Signals

Feed module lists with unique modules, same basename in different directories, empty lists, and paths already ending in `.ko`. Confirm duplicate diagnostics and exit status.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/modules-check.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/nsdeps -->
# sources/distributed-fs/ceph-client/scripts/nsdeps

## Purpose

`nsdeps` applies missing namespace import hints generated by `modpost` by using Coccinelle to insert `MODULE_IMPORT_NS()` statements into module source files.

## Important APIs, Types, and Functions

The script reads `modules.nsdeps`, resolves each `<module>.ko:` record to source files through the module's `.mod` file, and uses `spatch` with `scripts/coccinelle/misc/add_namespace.cocci`. It requires Coccinelle `spatch` version 1.0.4 or newer.

## Control Flow

It locates `spatch`, checks its version, then reads each `modules.nsdeps` line. For every namespace it runs the Coccinelle semantic patch in-place and then sorts all `MODULE_IMPORT_NS` lines in each touched source file by rebuilding the file around the import block.

## State and Persistence Behavior

Unlike most build checks, this script intentionally mutates source files by adding and sorting `MODULE_IMPORT_NS()` declarations. Its input is generated build state from modpost.

## Dependencies and Integration Points

It depends on shell, Coccinelle `spatch`, `sed`, `grep`, `sort`, `diff`, `wc`, module `.mod` files, `modules.nsdeps`, and source files with module metadata. It integrates with `make nsdeps` and modpost namespace enforcement.

## Risks and Edge Cases

Automatic insertion can touch all `.c` files listed in a multi-object module and disturb formatting around import blocks. Stale `.mod`/namespace data can add unnecessary imports. Missing `srcroot`, `srctree`, or compatible `spatch` breaks the run.

## Test Signals

Create modules with missing namespace imports, existing imports, multiple source files, generated modules, and absent `.mod` files. Confirm idempotence, sorted imports, and successful rebuild without namespace warnings.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/nsdeps -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/objdiff -->
# sources/distributed-fs/ceph-client/scripts/objdiff

## Purpose

`objdiff` compares the generated assembly of a single object between two source trees or build outputs. It helps diagnose compiler/codegen changes at object granularity.

## Important APIs, Types, and Functions

Functions are `usage()`, `get_output_dir()`, `do_objdump()`, `dorecord()`, `dodiff()`, and `doclean()`. Actions include recording objdump output, diffing current output against a saved baseline, and cleaning generated files.

## Control Flow

The script parses an action and object path, determines output paths, runs objdump with a stable set of disassembly/source options, stores baseline output for `record`, produces a unified diff for `diff`, or removes saved output for `clean`.

## State and Persistence Behavior

It persists objdump text under an output directory derived from the object path. Diff action reads that baseline and writes diff output to stdout.

## Dependencies and Integration Points

It depends on shell, objdump, diff, mkdir/rm, and Kbuild object paths. It is a developer diagnostic helper rather than a production build step.

## Risks and Edge Cases

Objdump output includes paths, addresses, debug/source context, and tool-version formatting that can create noisy diffs. Missing debug info or stripped objects reduce usefulness. Cross-toolchain comparisons require the right objdump.

## Test Signals

Record and diff an unchanged object, a changed object, a missing object, and a cross-compiled object. Confirm clean removes only its own generated baseline.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/objdiff -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/objdump-func -->
# sources/distributed-fs/ceph-client/scripts/objdump-func

## Purpose

`objdump-func` prints the disassembly for one named function from an object or binary, making targeted inspection easier than browsing full objdump output.

## Important APIs, Types, and Functions

It accepts an object file and function name, uses objdump disassembly output, and filters from the matching function label until the next function label.

## Control Flow

The script validates arguments, invokes objdump, searches for a line like `<function>:`, prints subsequent lines, and stops when another symbol label is reached.

## State and Persistence Behavior

It is read-only and writes filtered disassembly to stdout.

## Dependencies and Integration Points

It depends on shell, objdump, and awk/sed-style filtering. It integrates with developer debugging and codegen review.

## Risks and Edge Cases

Inlined functions, local symbol suffixes, duplicate names, stripped objects, or objdump syntax changes can cause no match or wrong range. It does not understand source-level scopes.

## Test Signals

Run against objects with global functions, static functions with suffixes, missing names, and stripped binaries. Compare range boundaries with full objdump output.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/objdump-func -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/orc_hash.sh -->
# sources/distributed-fs/ceph-client/scripts/orc_hash.sh

## Purpose

`orc_hash.sh` computes a preprocessor byte list hash from ORC unwind ABI definitions. It is intended to hash the parts of headers that define `ORC_REG_*`, `ORC_TYPE_*`, and `struct orc_entry`.

## Important APIs, Types, and Functions

The script is a stdin-to-stdout shell pipeline. It prints `#define ORC_HASH `, extracts matching lines with awk, hashes them with `sha1sum`, and formats each digest byte as `0xNN,`.

## Control Flow

It streams input through awk. The awk program prints ORC register/type defines and the complete `struct orc_entry` block, then the shell pipeline hashes and byte-formats that text.

## State and Persistence Behavior

It does not write persistent state; callers include or compare the emitted define text.

## Dependencies and Integration Points

It depends on shell, awk, `sha1sum`, `cut`, and `sed`. It integrates with ORC unwind format change detection in kernel builds.

## Risks and Edge Cases

Hash stability depends on the input being the expected header/preprocessor text. Renaming defines, changing struct formatting, or using a platform without compatible `sha1sum`/sed behavior can change or break output.

## Test Signals

Hash unchanged ORC header text, then change an ORC register define, type define, and `struct orc_entry` field to confirm digest changes. Verify non-ORC input changes are ignored.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/orc_hash.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/PKGBUILD -->
# sources/distributed-fs/ceph-client/scripts/package/PKGBUILD

## Purpose

`PKGBUILD` packages a built kernel for Arch Linux-style package management, producing the main kernel package and optional headers, API headers, and debug packages.

## Important APIs, Types, and Functions

Package functions include `_prologue()`, `build()`, `_package()`, `_package-headers()`, `_package-api-headers()`, and debug-package handling. Variables derive `pkgbase`, `pkgname`, `pkgver`, `pkgrel`, `arch`, dependencies, and extra package selection from Kbuild and pacman environment variables.

## Control Flow

`build()` invokes Kbuild with fixed `KERNELRELEASE` and build revision. The main package installs the kernel image, pkgbase marker, modules, and optional DTBs. The headers package calls `install-extmod-build`, adds `System.map` and `.config`, and creates `/usr/src` links. API headers run `headers_install`; debug packaging extracts debug info and build-id links.

## State and Persistence Behavior

It writes into makepkg's `pkgdir` package roots, installing files under `/usr/lib/modules`, `/usr/src`, `/usr/include`, boot/module debug paths, and package metadata.

## Dependencies and Integration Points

It depends on makepkg, Kbuild, `install-extmod-build`, `modules_install`, `dtbs_install`, `headers_install`, objcopy/readelf for debug packaging, and Arch packaging conventions.

## Risks and Edge Cases

MAKEFLAGS must be restored from Kbuild to avoid makepkg overrides. Package split behavior depends on config and environment variables. Stale images or missing DTB directories can produce incomplete packages. Debug extraction assumes module paths and build IDs are valid.

## Test Signals

Run `make pacman-pkg` variants with and without modules, DTBs, extra packages, and debug package enabled. Inspect package contents, symlinks, module dependency generation, and installability with pacman.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/PKGBUILD -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/builddeb -->
# sources/distributed-fs/ceph-client/scripts/package/builddeb

## Purpose

`builddeb` installs built kernel artifacts into Debian package staging directories for image, headers, libc headers, and debug packages.

## Important APIs, Types, and Functions

Helpers include `is_enabled()`, `if_enabled_echo()`, image-install logic, maintainer-script generation, `install_linux_image_dbg()`, `install_kernel_headers()`, and `install_libc_headers()`. It uses package name dispatch at the end.

## Control Flow

For image packages it installs modules, image files, config/System.map, DTBs, and maintainer scripts that run hook directories. Debug packages parse `modules.order`, extract debug info with objcopy, create build-id links, and install `vmlinux` symlinks. Header packages call `install-extmod-build`; libc headers call `headers_install` and move asm headers into the Debian multiarch include path.

## State and Persistence Behavior

It writes into `debian/<package>` staging roots, creates maintainer scripts under `DEBIAN`, package file trees under `/boot`, `/lib/modules`, `/usr/src`, `/usr/include`, and `/usr/lib/debug`.

## Dependencies and Integration Points

It depends on Kbuild variables, Debian packaging layout, `modules.order`, `READELF`, `OBJCOPY`, `run-parts`, `dpkg-architecture`-derived variables, and `install-extmod-build`.

## Risks and Edge Cases

Module debug extraction assumes uncompressed accessible `.ko` files and build IDs. Cross-compiles need correct `DEB_HOST_GNU_TYPE`. Hook scripts are generated dynamically and must be shell-safe. Missing modules or images can produce incomplete packages.

## Test Signals

Build Debian packages for image, debug, headers, and libc headers; inspect maintainer scripts, build-id links, module trees, DTBs, and multiarch header placement. Test no-modules and cross-compile configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/builddeb -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/buildtar -->
# sources/distributed-fs/ceph-client/scripts/package/buildtar

## Purpose

`buildtar` stages a built kernel into a directory suitable for tarball packaging, including modules, core boot artifacts, optional DTBs, and architecture-specific images.

## Important APIs, Types, and Functions

It accepts a temporary directory argument and relies on `ARCH`, `SRCARCH`, `KERNELRELEASE`, `KBUILD_IMAGE`, `objtree`, `srctree`, and `KCONFIG_CONFIG`.

## Control Flow

The script recreates the temp directory, optionally installs DTBs when OF early flattree support and an architecture DTB directory exist, runs `modules_install`, copies `System.map`, `.config`, and `vmlinux`, and then selects the boot image path through an architecture `case`.

## State and Persistence Behavior

It deletes and recreates the staging directory, writing files under `boot/`, `boot/dtbs/<release>`, and the module install tree.

## Dependencies and Integration Points

It depends on Kbuild install targets, module installation, architecture boot image conventions, and tar packaging callers.

## Risks and Edge Cases

The file notes stale-image risk for MIPS and arm64 when the first matching file is copied. Architecture-specific image names vary, and missing `KBUILD_IMAGE` or modules can break packaging. It unconditionally recreates the staging directory.

## Test Signals

Run on common architectures, with and without DTBs/modules, and inspect tar contents. Specifically test MIPS/arm64 stale image scenarios and riscv image suffix handling.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/buildtar -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/debian/rules -->
# sources/distributed-fs/ceph-client/scripts/package/debian/rules

## Purpose

`debian/rules` is the Debian debhelper entry point for kernel packages generated by `mkdebian`. It delegates build and install phases back to Kbuild and `builddeb`.

## Important APIs, Types, and Functions

Targets include debhelper overrides for configure, build, auto-test, install, and binary behavior. It uses package names and Kbuild variables to decide which install logic runs.

## Control Flow

Debhelper invokes the rules file. Build targets call Kbuild for the kernel and modules, while install targets call `scripts/package/builddeb` for each binary package. Tests are typically disabled or no-op for packaging speed.

## State and Persistence Behavior

It writes through debhelper into `debian/<package>` staging directories and creates `.deb` packages through standard Debian tooling.

## Dependencies and Integration Points

It depends on `debhelper-compat`, generated `debian/control`, Kbuild, `builddeb`, and Debian package build environment variables.

## Risks and Edge Cases

Rules must preserve Kbuild's configured output tree and not trigger unwanted rebuilds. Cross-build environment variables and package build profiles can alter dependency and install paths.

## Test Signals

Run `dpkg-buildpackage` for binary-only and source builds, with and without headers/debug packages, and verify that debhelper calls the intended Kbuild/package steps.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/debian/rules -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/gen-diff-patch -->
# sources/distributed-fs/ceph-client/scripts/package/gen-diff-patch

## Purpose

`gen-diff-patch` writes `git diff HEAD` to a requested patch file for Debian source package generation, then warns if untracked files might make the source package incomplete.

## Important APIs, Types, and Functions

It accepts an output patch path, creates its parent directory, and runs `git -C "${srctree:-.}" diff HEAD`.

## Control Flow

The script writes local tracked differences into the requested patch file. If the patch is empty, or if there are no untracked files, it exits quietly. If both tracked diffs and untracked files are present, it prints a multi-line warning. `mkdebian` later prepends subject/author metadata and adds the patch to `debian/patches/series` only if it is non-empty.

## State and Persistence Behavior

It persists the generated patch file and does not modify source files.

## Dependencies and Integration Points

It depends on shell and git. It integrates with `mkdebian --need-source` and Debian `3.0 (quilt)` source packages.

## Risks and Edge Cases

Only tracked diffs are captured; needed untracked files are not included and only trigger a warning. Uncommitted local changes become part of source packaging, so reproducibility depends on a clean or intentionally staged tree. Binary changes may not serialize usefully.

## Test Signals

Run with a clean tree, a modified tracked source file, tracked plus untracked files, and binary diffs. Verify warning behavior, non-empty behavior, and quilt applicability.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/gen-diff-patch -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/install-extmod-build -->
# sources/distributed-fs/ceph-client/scripts/package/install-extmod-build

## Purpose

`install-extmod-build` installs the subset of a kernel build tree required to build external modules against packaged headers.

## Important APIs, Types, and Functions

The script accepts an installation directory and copies/synchronizes Makefiles, generated headers, scripts, tools needed by external module builds, `Module.symvers` when present, and architecture-specific include/build files.

## Control Flow

It prepares the destination, creates required directory structure, copies core Kbuild metadata and generated config headers, installs module build scripts, and prunes unnecessary files so the result is suitable for `/lib/modules/<release>/build` or distro header packages.

## State and Persistence Behavior

It writes into the destination directory supplied by packaging scripts. It does not modify the source tree.

## Dependencies and Integration Points

It depends on rsync/cp/find-style tools, Kbuild output layout, generated headers, `scripts/mod/modpost`, and packaging callers such as Arch `PKGBUILD` and Debian `builddeb`.

## Risks and Edge Cases

Omitting generated files breaks external module builds; copying too much bloats header packages. Cross-compile and separate output-tree layouts require source and object paths to be handled carefully. Stale build output can leak into packages.

## Test Signals

Install headers, then build simple and modversioned external modules against the result. Test in-tree and `O=` builds, cross-compiles, missing `Module.symvers`, and clean package-content checks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/install-extmod-build -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/mkdebian -->
# sources/distributed-fs/ceph-client/scripts/package/mkdebian

## Purpose

`mkdebian` generates a Debian packaging directory for the current kernel build. It creates control metadata, changelog, rules, source-package patches, and package stanzas for image, headers, libc headers, and optional debug packages.

## Important APIs, Types, and Functions

Helpers are `is_enabled()`, `if_enabled_echo()`, `set_debarch()`, and `gen_source()`. Important variables include maintainer identity, package version, source name, image package name, Debian architecture, host GNU tuple, distribution, and build profiles.

## Control Flow

The script removes and recreates `debian/`, derives maintainer and package version, optionally creates source package metadata and quilt patches, maps `UTS_MACHINE` and config flags to a Debian architecture, detects the changelog distribution, writes `debian/arch`, `changelog`, `control`, rules, and support files. It uses package profiles and config flags to include or omit package variants.

## State and Persistence Behavior

It persistently replaces the `debian/` directory and may write patches under `debian/patches`. Source generation includes `.config` and local diffs as quilt patches.

## Dependencies and Integration Points

It depends on shell, dpkg tools, `lsb_release`, Kbuild config/output files, `scripts/setlocalversion`, `scripts/build-version`, `gen-diff-patch`, and Debian package conventions.

## Risks and Edge Cases

Architecture mapping can fall back to host architecture, which is risky for unsupported targets. Replacing `debian/` discards local packaging edits. Maintainer identity and distribution are environment-sensitive. Source patches depend on current uncommitted tree state.

## Test Signals

Run for multiple architectures, `ARCH=um`, source and binary package modes, custom `KDEB_*` variables, no `lsb_release`, and unsupported architecture fallback. Validate `dpkg-buildpackage` succeeds from generated metadata.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/mkdebian -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/mkspec -->
# sources/distributed-fs/ceph-client/scripts/package/mkspec

## Purpose

`mkspec` generates an RPM spec file for packaging the current kernel build.

## Important APIs, Types, and Functions

It derives package name, version, release, architecture, dependencies, config flags, and install script sections from Kbuild environment and kernel release metadata.

## Control Flow

The script prints a complete spec to stdout. The spec defines build requirements, package descriptions, `%prep`, `%build`, `%install`, file lists, and optional subpackages such as headers/devel/debug depending on configuration and environment.

## State and Persistence Behavior

The script itself is read-only; callers redirect stdout to a `.spec` file consumed by rpmbuild.

## Dependencies and Integration Points

It depends on shell, rpm macro conventions, Kbuild build/install targets, and distro package expectations. It integrates with `make rpm-pkg` or related package targets.

## Risks and Edge Cases

Spec generation must match current RPM macro behavior and kernel install paths. Architecture naming, debug package handling, and module/header package splits can vary by distro. Environment-sensitive version strings affect reproducibility.

## Test Signals

Generate and build RPMs with and without modules, headers, debug info, and cross-architecture settings. Inspect file lists, dependency metadata, and install/remove script behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/mkspec -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/pahole-version.sh -->
# sources/distributed-fs/ceph-client/scripts/pahole-version.sh

## Purpose

`pahole-version.sh` prints the numeric version of a `pahole` executable for BTF capability checks, using the kernel's compact three-digit style such as `119` for v1.19.

## Important APIs, Types, and Functions

It accepts the pahole command and any wrapper arguments as `"$@"`, checks that the resolved command is executable, and parses `--version` output with sed.

## Control Flow

If the command is not executable it prints `0` and exits with status 1. Otherwise it runs `"$@" --version` and converts a leading `v<major>.<minor>` pattern to `<major><minor>`.

## State and Persistence Behavior

It is read-only and writes only stdout/stderr.

## Dependencies and Integration Points

It depends on shell and `pahole` from dwarves. It integrates with Kbuild BTF generation gates.

## Risks and Edge Cases

Different pahole version formats can break parsing. The compact format can be ambiguous for multi-digit components, so callers must compare it the same way Kbuild expects. Incorrect version detection can enable unsupported BTF features.

## Test Signals

Run against several dwarves versions, missing executables, and wrapper output. Verify Kbuild BTF feature gates for versions below and above required thresholds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/pahole-version.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/parse-maintainers.pl -->
# sources/distributed-fs/ceph-client/scripts/parse-maintainers.pl

## Purpose

`parse-maintainers.pl` extracts, sorts, and filters information from the kernel `MAINTAINERS` file. It supports category and pattern-oriented output for tooling that needs maintainership metadata.

## Important APIs, Types, and Functions

Options select input/output behavior. Functions include `usage()`, `by_category()`, `by_pattern()`, `trim()`, `alpha_output()`, and `file_input()`. The parser stores section/category lines and file pattern lines in arrays/hashes for sorted output.

## Control Flow

The script parses arguments, reads `MAINTAINERS` or stdin, tracks section headers and tagged lines, normalizes whitespace, then emits records sorted alphabetically by category or by pattern depending on mode.

## State and Persistence Behavior

State is in memory during one run. Output goes to stdout and no files are modified.

## Dependencies and Integration Points

It depends on Perl and the format conventions of the Linux `MAINTAINERS` file. It integrates with scripts and reports that need maintainer/file-pattern indexes.

## Risks and Edge Cases

The parser is tied to MAINTAINERS tag syntax. Multiline continuations, unusual section names, malformed entries, and new tag types can produce incomplete output. Sorting may lose original contextual ordering that reviewers expect.

## Test Signals

Test representative MAINTAINERS entries with multiple `M:`, `L:`, `F:`, `X:`, `N:`, malformed sections, empty sections, and category/pattern sorting modes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/parse-maintainers.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/patch-kernel -->
# sources/distributed-fs/ceph-client/scripts/patch-kernel

## Purpose

`patch-kernel` incrementally applies kernel version patches from a patch directory to a source tree until a requested stop version or until no next patch is found. It is legacy release-management automation for patching kernel tarball trees.

## Important APIs, Types, and Functions

The script parses source directory, patch directory, stop version, and optional `-ac` patch series arguments. It reads top-level `Makefile` version variables and searches for patch files in multiple compression formats.

## Control Flow

It determines the current kernel version, decides the next patch level, locates the matching patch file, decompresses when needed, applies it with `patch -p1 -s` from the source tree, checks for `.rej` files, removes `.orig` files on success, updates version state, and repeats until the stop condition.

## State and Persistence Behavior

It persistently mutates the kernel source tree by applying patches and deleting backup files. Reject files remain on failure for manual inspection.

## Dependencies and Integration Points

It depends on shell, patch, decompression tools for gzip/bzip/bzip2/zip/compress/plaintext patches, find, and the kernel top-level Makefile version scheme.

## Risks and Edge Cases

It assumes historical version naming and patch layout. Applying patches to a dirty tree can mix local changes with release patches. Reject detection is post-hoc, and compressed patch selection can choose unexpected files. Modern git workflows generally supersede it.

## Test Signals

Run on disposable source trees for one-step, multi-step, exact stop version, already-at-target, missing patch, compressed patch, and reject scenarios. Verify version variables and absence/presence of `.rej`/`.orig` files.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/patch-kernel -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/profile2linkerlist.pl -->
# sources/distributed-fs/ceph-client/scripts/profile2linkerlist.pl

## Purpose

`profile2linkerlist.pl` converts sorted `readprofile` output into linker-script section patterns for hot function text sections.

## Important APIs, Types, and Functions

The script reads lines from stdin or file arguments, extracts a function name with a regex, and prints `*(.text.<function>)` unless the line contains `unknown` or `total`.

## Control Flow

It assumes the input has already been sorted, usually by `readprofile | sort -rn`. It processes each line independently and emits linker-consumable section patterns in input order.

## State and Persistence Behavior

It has no meaningful retained state beyond the current line. It writes only stdout.

## Dependencies and Integration Points

It depends on Perl and the expected profiler output format. It integrates with profile-guided kernel layout or linker-list experiments.

## Risks and Edge Cases

Unexpected profiler formats can produce empty or wrong function names because the regex result is not validated before printing. Duplicate symbols are not deduplicated. Stale profile data can produce ineffective ordering.

## Test Signals

Feed sorted readprofile samples with duplicates, `unknown`, `total`, malformed lines, and symbols absent from the final link. Compare emitted order with expected input order and linker acceptance.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/profile2linkerlist.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/prune-kernel -->
# sources/distributed-fs/ceph-client/scripts/prune-kernel

## Purpose

`prune-kernel` removes installed kernel boot and module artifacts for supplied kernel release strings, while preserving the running kernel and kernels owned by RPM packages.

## Important APIs, Types, and Functions

The script loops over command-line release names. For each release it checks `rpm -qf /lib/modules/<release>` and compares against `uname -r`.

## Control Flow

For removable releases it deletes `/boot/initramfs-<release>.img`, `/boot/System.map-<release>`, `/boot/vmlinuz-<release>`, `/boot/config-<release>`, and `/lib/modules/<release>`, then calls `new-kernel-pkg --remove` or `kernel-install remove` when available.

## State and Persistence Behavior

It intentionally mutates system boot/module locations by deleting files. There is no automatic restore.

## Dependencies and Integration Points

It depends on Bash, `rpm`, `uname`, `rm`, and optionally `new-kernel-pkg` or `kernel-install`. It is a local maintenance helper outside the normal Kbuild compile path.

## Risks and Edge Cases

Deletion is destructive and targets absolute system paths. It assumes RPM ownership is the right preservation signal and may be unsafe on non-RPM systems. It must not be run with release names the user still needs.

## Test Signals

Test on a disposable root or container with fake release names, RPM-owned module directories, the running kernel release, and optional `kernel-install` hooks. Verify only intended boot/module paths are removed.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/prune-kernel -->
