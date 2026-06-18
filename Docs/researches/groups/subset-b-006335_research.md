# subset-b-006335 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/recordmcount.c -->
# sources/distributed-fs/ceph-client/scripts/recordmcount.c

Purpose: `recordmcount.c` is the compiled replacement for the older Perl `recordmcount` path. It rewrites relocatable kernel object files after compilation so ftrace can later find all call sites to `mcount`, `_mcount`, `__fentry__`, or architecture-specific alternates through a generated `__mcount_loc` section. It operates directly on ELF `ET_REL` objects and appends new section-string-table data, section headers, `__mcount_loc` contents, and relocation records.

Important APIs, types, and functions: the file-level state tracks the mapped object (`file_map`, `file_end`, `file_ptr`, `sb`), appended data (`file_append`, `file_append_size`), endian conversion callbacks (`w`, `w2`, `w8`), architecture hooks (`make_nop`, `is_fake_mcount32/64`, `Elf*_r_sym`, `Elf*_r_info`), symbol naming (`gpfx`, `altmcount`), and notrace warning behavior. `mmap_file()` maps or reads an object privately, `uwrite()` edits the in-memory image or append buffer, `write_file()` writes a replacement `*.rc` file and renames it into place, and `do_file()` validates ELF identity, selects architecture relocation types, and dispatches to `do32()` or `do64()` from `recordmcount.h`.

Control flow: `main()` parses `-w`, skips `kernel/trace/ftrace.o`, and processes each object independently. `do_file()` determines byte order and ELF class, configures x86, ARM, AArch64, MIPS, LoongArch, PPC, S390, SH, and SPARC relocation semantics, then calls the macro-generated implementation. The header code finds relocation sections that target executable traceable text sections, sifts mcount relocations into a new table, optionally NOPs calls in ignored sections, and appends the generated sections only if work was found.

State and persistence: edits are first made in private memory and an append buffer. On success, `write_file()` writes the original mapped bytes plus appended bytes to a temporary sibling and renames it over the original object. Per-file cleanup frees append buffers and unmaps or frees the file image. There is no lock; concurrent writers to the same object are explicitly outside the intended build model.

Dependencies and integration points: it depends on `<elf.h>`, POSIX mmap/stat/open/read/write/rename APIs, and `recordmcount.h` included twice. It is invoked by Kbuild during object compilation for dynamic ftrace. Its architecture-specific relocation constants must match kernel toolchains and architecture ABIs.

Risks: binary-format corruption is the main risk if section offsets, extended section counts, endian conversion, or relocation types are wrong. NOP conversion relies on exact instruction encodings for x86, ARM, Thumb, and arm64. `uwrite()` pointer arithmetic assumes GNU C-style `void *` arithmetic. LoongArch fake-mcount uses `ELF64_R_TYPE` in a 32-bit helper, which should be treated carefully. The file rewrites artifacts in place through rename, so interrupted writes can leave temporary `*.rc` files.

Test signals: useful validation is ftrace boot/selftests, successful module/vmlinux links, `readelf -S/-r` inspection for a single `__mcount_loc`, architecture build coverage, and targeted objects with mcount in traceable and ignored sections. Existing protection includes ELF magic/type/class checks and duplicate `__mcount_loc` detection in the generated header code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/recordmcount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/recordmcount.h -->
# sources/distributed-fs/ceph-client/scripts/recordmcount.h

Purpose: `recordmcount.h` is implementation code, not a conventional declaration header. `recordmcount.c` includes it twice, once for 32-bit ELF and once with `RECORD_MCOUNT_64`, to generate parallel `do32()` and `do64()` implementations for adding ftrace `__mcount_loc` metadata.

Important APIs, types, and functions: macro aliases map generic names such as `Elf_Ehdr`, `Elf_Shdr`, `Elf_Rel`, `append_func`, `sift_rel_mcount`, `nop_mcount`, `find_secsym_ndx`, `has_rel_mcount`, and `do_func` to 32-bit or 64-bit variants. `get_symindex()`, `get_shnum()`, `set_shnum()`, and `get_shstrndx()` handle extended ELF section numbering. `find_symtab()` locates symbol and extended-symbol-index tables. `append_func()` appends the new section-string table, rewritten section header table, `__mcount_loc`, and its relocation section. `get_mcountsym()`, `sift_rel_mcount()`, and `nop_mcount()` identify and transform mcount relocations.

Control flow: `do_func()` computes a conservative relocation-space bound, allocates mcount location and relocation arrays, scans all section headers, and distinguishes traceable executable text sections from ignored executable sections. Traceable sections require a non-weak local or global section symbol from `find_secsym_ndx()` so final link relocations remain valid. Ignored sections are optionally NOPed or warned. If any mcount locations were collected, `append_func()` writes all appended ELF structures and updates `e_shoff` and section count.

State and persistence: all persistent file mutation is done through callbacks and globals in `recordmcount.c`, especially `uwrite()`, endian conversion functions, `file_updated`, and architecture hooks. The header itself maintains per-specialization static hooks for fake mcount filtering and relocation info packing.

Dependencies and integration points: it depends on the global variables and helpers defined before inclusion in `recordmcount.c`, plus architecture overrides installed by `do_file()`. It integrates with the kernel linker's expectation that `__mcount_loc` points at relocatable call-site addresses and that ignored notrace sections do not leave active profiling calls.

Risks: macro-generated dual inclusion makes review and debugging harder because each static identifier expands differently. The code assumes valid, bounded ELF offsets after initial checks; malformed objects may still stress pointer arithmetic. The upper-bound allocation of `totrelsz` avoids dynamic growth but depends on correct section sizes. Extended section index logic is critical for large objects.

Test signals: compare 32-bit and 64-bit builds on supported architectures, inspect generated relocations with `readelf`, validate duplicate-section no-op behavior, and test objects with weak-only symbols, local section symbols, extended section indexes, REL and RELA relocations, and notrace text sections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/recordmcount.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/recordmcount.pl -->
# sources/distributed-fs/ceph-client/scripts/recordmcount.pl

Purpose: `recordmcount.pl` is the older Perl implementation of the ftrace mcount-table generator. It parses `nm` and `objdump` output, emits temporary assembly containing `__mcount_loc` entries, compiles that assembly, and links it back into the original object.

Important APIs, types, and functions: the script is driven by twelve positional arguments: architecture, endian, bit width, tool paths for objdump/objcopy/cc/ld/nm/rm/mv, module flag, and input object. Architecture blocks define `$local_regex`, `$weak_regex`, `$section_regex`, `$function_regex`, `$mcount_regex`, `$mcount_adjust`, `$alignment`, `$section_type`, and assembly data directive `$type`. `update_funcs()` writes pending offsets relative to a chosen reference function and records local symbols that must be globalized during the link.

Control flow: it skips `kernel/trace/ftrace.o`, normalizes x86 arch names, configures architecture-specific objdump and linker options, runs `nm` to collect local and weak symbols, then runs `objdump -hdr` to find executable sections, functions, and mcount call relocations. For each section, it selects a safe reference function, writes offset expressions to a temporary `.s`, compiles it, and either links it directly or first globalizes local reference symbols, links, then localizes them again.

State and persistence: the script mutates the input object by creating temporary files in the input object's directory: `.tmp_mc_*.s`, `.tmp_mc_*.o`, `.tmp_gl_*`, and `.tmp_mx_*`. Successful processing overwrites or moves the linked result back to the input path. It keeps transient hash state for local, weak, and converted symbols.

Dependencies and integration points: it depends on exact `nm` and `objdump` textual formats, assembler syntax, `objcopy` symbol transformations, and `ld -r`. It supports many architecture-specific patterns including x86, s390, sh, powerpc, arm, arm64, sparc64, mips, microblaze, riscv, and csky.

Risks: textual disassembly parsing is fragile across binutils versions and architectures. Backtick command invocations do not check every exit code directly. Temporary file names are predictable per object prefix. The duplicate `__mcount_loc` check exits with failure, unlike the C path's graceful already-done signal.

Test signals: run against representative objects for each supported architecture, compare `__mcount_loc` output against the C tool, verify local-symbol conversion round trips, and test duplicate processing. Link-time ftrace selftests and inspection of temp-free successful builds are the primary integration checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/recordmcount.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/relocs_check.sh -->
# sources/distributed-fs/ceph-client/scripts/relocs_check.sh

Purpose: `relocs_check.sh` produces a filtered list of suspicious dynamic relocations in `vmlinux` for architecture-specific relocation checkers. It removes relocations known to be legitimate due to unresolved weak symbols.

Important APIs, types, and functions: it accepts three positional arguments: objdump path, nm path, and vmlinux path. It builds `undef_weak_symbols` with `nm "$vmlinux" | awk '$1 ~ /w/ { print $2 }'`, then pipes `$objdump -R "$vmlinux"` through a relocation grep and an optional fixed-string word exclusion for weak symbols.

Control flow: the script has no option parsing. It computes weak undefined names first, then streams objdump relocation rows containing `R_`. If the weak-symbol set is non-empty, `grep -F -w -v` drops matching rows; otherwise the stream is passed through unchanged.

State and persistence: it is stateless and writes only to stdout/stderr through its child commands.

Dependencies and integration points: used by architecture relocation validation scripts after vmlinux link. It depends on GNU-style `objdump -R` and `nm` output and on `awk`, `grep`, and shell pipelines.

Risks: the weak-symbol awk pattern is broad and tied to nm column formatting. Filtering by symbol name can hide rows if names collide unexpectedly. The script does not `set -e`, so failures may be represented only through pipeline exit behavior in callers.

Test signals: feed a vmlinux with known weak unresolved symbols and known bad relocations, verify weak relocations are removed and bad relocations remain. Tool absence and empty weak-symbol cases should be exercised.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/relocs_check.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/remove-stale-files -->
# sources/distributed-fs/ceph-client/scripts/remove-stale-files

Purpose: `remove-stale-files` is a Kbuild startup cleanup script for generated files that were moved, renamed, or removed from the build but may still be present in developer trees after git updates or bisects.

Important APIs, types, and functions: it is a shell script with `set -e` and a small fixed list of `rm -f` commands. Current removals include the old `scripts/selinux/genheaders/genheaders`, top-level `*.spec`, and `lib/test_fortify.log`.

Control flow: it runs unconditionally and exits on unexpected command failure, though `rm -f` makes the intended cleanup idempotent.

State and persistence: it deletes stale files from the working tree. There is no record of what was removed and no user prompt.

Dependencies and integration points: Kbuild invokes this before building so stale generated artifacts do not mask source moves or create confusing untracked files.

Risks: every path added to this script must be known generated output; adding source-like paths would silently delete user files. Because it is intentionally temporary, stale entries should be removed after enough release cycles.

Test signals: run in clean and dirty trees with/without listed artifacts, verify idempotence and absence of build-visible stale files. Git status after cleanup is a practical signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/remove-stale-files -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/rust_is_available.sh -->
# sources/distributed-fs/ceph-client/scripts/rust_is_available.sh

Purpose: `rust_is_available.sh` validates that Kbuild has a usable Rust toolchain. It checks required environment variables, command availability, `rustc`, `bindgen`, and libclang versions, Clang/libclang consistency warnings, and the availability of Rust `core` source.

Important APIs, types, and functions: `get_canonical_version()` converts `x.y.z` into a comparable integer with extra major/minor room for Rust 1.100+. `print_docs_reference()` and `print_kbuild_explanation()` centralize diagnostics. The script uses `scripts/min-tool-version.sh` for minimum `rustc`, `bindgen`, and LLVM versions, `scripts/cc-version.sh` to identify Clang, and `rust_is_available_bindgen_libclang.h` to force bindgen to print libclang version.

Control flow: after `set -e`, an EXIT trap prints the Rust quick-start reference on failure or warning. It validates `RUSTC`, `BINDGEN`, and `CC` are set and executable, parses version output with sed, compares canonical versions, invokes bindgen on the probe header, warns if Clang and libclang versions differ, then checks `$RUST_LIB_SRC` or the rustc sysroot for `core/src/lib.rs`.

State and persistence: it writes diagnostics to stderr and produces no stdout on success. It does not modify files. `warning=1` preserves successful exit while still causing the docs reference to print.

Dependencies and integration points: called by Kbuild's `rustavailable` target and Rust build checks. It depends on POSIX shell, `sed`, `cut`, rustc, bindgen, a C compiler, libclang, and the in-tree helper scripts.

Risks: version parsing accepts only full numeric `x.y.z` prefixes and may reject unusual tool wrappers. The `CC` invocation is intentionally loose to handle ccache/multiple arguments, but shell word splitting is involved. Missing Rust source is a common packaging issue.

Test signals: `rust_is_available_test.py` provides extensive fake-tool coverage. Integration tests should include real GCC/Clang, mismatched Clang/libclang, version suffixes, missing executables, and sysroot/RUST_LIB_SRC failure cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/rust_is_available.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/rust_is_available_bindgen_libclang.h -->
# sources/distributed-fs/ceph-client/scripts/rust_is_available_bindgen_libclang.h

Purpose: this two-line C header is a bindgen probe used by `rust_is_available.sh` to discover the libclang version that bindgen loaded.

Important APIs, types, and functions: it contains only an SPDX header and `#pragma message("clang version " __clang_version__)`. The preprocessor expands `__clang_version__`, and bindgen forwards the compiler diagnostic to stderr.

Control flow: it is not executed directly. Bindgen parses it; successful parsing creates a warning/message containing `clang version x.y.z`, which the shell script extracts with sed.

State and persistence: no persistent state.

Dependencies and integration points: depends on clang/libclang supporting `__clang_version__` and pragma messages. It is tightly coupled to the sed pattern in `rust_is_available.sh` and the fake bindgen output in `rust_is_available_test.py`.

Risks: changes to bindgen diagnostic formatting or libclang pragma output could break version extraction. Non-Clang front ends would not provide the expected macro, but bindgen uses libclang by design.

Test signals: unit tests feed many realistic warning strings, including absolute paths, distro suffixes, and locale noise, and expect the same version extraction behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/rust_is_available_bindgen_libclang.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/rust_is_available_test.py -->
# sources/distributed-fs/ceph-client/scripts/rust_is_available_test.py

Purpose: `rust_is_available_test.py` is a unittest suite for `rust_is_available.sh`. It uses generated executable stubs to simulate rustc, bindgen, and clang behavior across success, warning, and failure cases.

Important APIs, types, and functions: `TestRustIsAvailable.Expected` models expected outcome classes. `generate_executable()`, `generate_clang()`, `generate_rustc()`, and `generate_bindgen()` create temporary executable scripts with controlled stdout/stderr/exit behavior. `setUpClass()` discovers default minimum versions through `scripts/min-tool-version.sh` and rust sysroot from real rustc. `run_script()` executes `scripts/rust_is_available.sh`, asserts stdout is empty, checks return code and docs-reference behavior, and returns decoded stderr.

Control flow: individual tests override environment entries to cover unset variables, missing/non-executable tools, unexpected version output, old versions, libclang failures, version mismatch warnings, missing core sources, supported version suffixes, and real-program smoke tests for GCC and Clang.

State and persistence: it creates a temporary directory for fake executables and one non-executable file. It does not write into the source tree.

Dependencies and integration points: depends on Python 3, unittest, executable permission support, the real helper scripts, and, for some tests, real `rustc`, `bindgen`, `gcc`, and `clang` in PATH. It is a test companion to the shell script and probe header.

Risks: the "real programs" test can fail in minimal build environments without bindgen or compilers. The generated stubs are Python scripts, so the test environment needs Python executable support. Because defaults are read from the current tree, min-version changes automatically affect expectations.

Test signals: the file is itself the main signal. Useful additions would include malformed `CC` values, libclang messages without file prefixes, and shell metacharacter safety around generated tool paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/rust_is_available_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/rustc-llvm-version.sh -->
# sources/distributed-fs/ceph-client/scripts/rustc-llvm-version.sh

Purpose: `rustc-llvm-version.sh` prints the LLVM version used by a rustc binary in a six-digit comparable integer form.

Important APIs, types, and functions: `get_canonical_version()` converts `x.y.z` to `10000*x + 100*y + z`. The script runs `"$@" --version --verbose`, greps the first `LLVM.*x.y.z` line, and canonicalizes the third shell word after `set -- $output`.

Control flow: if the command and grep succeed, it prints the canonical version. Otherwise it prints `0` and exits with status 1.

State and persistence: no persistent state; stdout is the version number.

Dependencies and integration points: used by Kbuild version checks or Makefile conditionals that need the Rust compiler's LLVM backend version. Depends on rustc verbose output format, grep, and POSIX shell.

Risks: output parsing assumes the LLVM version appears as the third whitespace-delimited token. Nonstandard rustc wrappers or localized output may produce `0`.

Test signals: test rustc wrappers with normal verbose output, missing rustc, and unexpected LLVM lines. Makefile consumers should treat `0` as unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/rustc-llvm-version.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/rustc-version.sh -->
# sources/distributed-fs/ceph-client/scripts/rustc-version.sh

Purpose: `rustc-version.sh` prints the Rust compiler version in a comparable integer form that can represent Rust versions past 1.99.

Important APIs, types, and functions: `get_canonical_version()` maps `x.y.z` to `100000*x + 100*y + z`. The main path runs `"$@" --version`, splits the output, and canonicalizes the second word, which is expected to be the numeric rustc version.

Control flow: successful version command prints the canonicalized version. Failure prints `0` and exits with status 1.

State and persistence: no persistent state.

Dependencies and integration points: Makefiles and shell checks can call it with a rustc command or wrapper. It uses POSIX shell arithmetic and expects rustc-like version output.

Risks: if a wrapper prints extra words before `rustc`, `$2` may not be the version. Suffixes are not explicitly stripped here, so callers should verify input format or rely on rustc's normal output.

Test signals: run with real rustc, wrapper failures, and version strings around 1.100.0 to verify canonical ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/rustc-version.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/rustdoc_test_builder.rs -->
# sources/distributed-fs/ceph-client/scripts/rustdoc_test_builder.rs

Purpose: `rustdoc_test_builder.rs` transforms a single rustdoc-generated doctest source from stdin into a saved test body under `rust/test/doctests/kernel/`. It works around rustdoc not exposing stable test metadata.

Important APIs, types, and functions: `main()` reads stdin into a `String`, extracts the inner doctest function name by searching for the generated `fn main() { ... fn NAME()` pattern, rewrites unqualified `Result` return signatures to `::core::result::Result`, rewrites generated `unwrap()` checks into kernel `assert!(is_ok())`, derives a compact name after `_rust_kernel_`, and writes the transformed body to `rust/test/doctests/kernel/{name}`.

Control flow: every step is direct and uses `unwrap()`/`expect()` for fail-fast behavior. The script assumes one rustdoc-generated inner function and a known naming convention.

State and persistence: it creates or replaces one file in `rust/test/doctests/kernel/` for each rustdoc test fed to it. It does not create the directory itself.

Dependencies and integration points: invoked by the Rust kernel doctest build flow after rustdoc generates test code. Its output is consumed by `rustdoc_test_gen.rs`.

Risks: rustdoc output format changes can break function-name extraction. String replacement is precise and may miss semantically equivalent generated code. Panics are acceptable in the build pipeline but produce abrupt errors.

Test signals: doctests with plain `()`, `Result`, multiple generated numbers, and names containing `_rust_kernel_`; verify output path, stable name generation, and assert rewrite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/rustdoc_test_builder.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/rustdoc_test_gen.rs -->
# sources/distributed-fs/ceph-client/scripts/rustdoc_test_gen.rs

Purpose: `rustdoc_test_gen.rs` aggregates saved rustdoc doctest bodies into generated Rust and C KUnit glue: `rust/doctests_kernel_generated.rs` and `rust/doctests_kernel_generated_kunit.c`.

Important APIs, types, and functions: `find_real_path()` reconstructs the source path represented by rustdoc's flattened file name by recursively trying underscore-as-path-separator combinations under `rust/kernel`. It panics on zero or multiple candidates. `main()` reads and sorts saved doctest files, groups tests by original file to assign stable per-file numbers, builds Rust extern test functions with KUnit-aware `assert!` and `assert_eq!` macro overrides, emits KTAP-style location diagnostics, and writes matching C `KUNIT_CASE` declarations.

Control flow: the script gets `srctree` from the environment, scans `rust/test/doctests/kernel`, sorts paths for deterministic output, parses each filename as `{file}_{line}_{number}`, resolves the real source path once per file, computes body line offsets for diagnostics, and appends generated code fragments before writing both output files.

State and persistence: it writes two generated files in `rust/`. It reads all saved doctest bodies and maintains only transient string buffers and path-candidate vectors.

Dependencies and integration points: depends on the builder output naming convention, `srctree`, KUnit C APIs, Rust kernel prelude, and `kernel::kunit_assert*` macros. It is part of the Rust documentation-test Kbuild path.

Risks: ambiguous underscore/path mappings cause a panic and require source renaming. Doctest failures from spawned threads may only log and not fail the owning KUnit test, as documented. Generated C/Rust must stay synchronized with KUnit and Rust kernel APIs.

Test signals: doctest suites with multiple tests per file, files/directories containing underscores, ambiguous candidates, and Result-returning bodies. Generated files should compile and report original locations accurately.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/rustdoc_test_gen.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/selinux/Makefile -->
# sources/distributed-fs/ceph-client/scripts/selinux/Makefile

Purpose: this Makefile declares the SELinux script subdirectory build relationship.

Important APIs, types, and functions: it contains `subdir-y := mdp`, telling Kbuild to descend into `scripts/selinux/mdp`.

Control flow: Kbuild interprets the assignment during host-tool build traversal; there is no executable logic in the file.

State and persistence: no runtime state. It affects build graph state by including the `mdp` host program directory.

Dependencies and integration points: integrates with the kernel Kbuild recursive make system and the `mdp/Makefile`.

Risks: removing or changing the subdir entry would stop building the dummy policy generator used by `install_policy.sh`.

Test signals: `make scripts` or a SELinux dummy policy build should descend into `scripts/selinux/mdp` and produce the host `mdp` tool.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/selinux/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/selinux/install_policy.sh -->
# sources/distributed-fs/ceph-client/scripts/selinux/install_policy.sh

Purpose: `install_policy.sh` installs a generated dummy SELinux policy under `/etc/selinux/dummy` and arranges permissive boot-time activation/relabeling.

Important APIs, types, and functions: it requires root, locates `setfiles`, `checkpolicy`, and `selinuxenabled`, obtains policy version via `checkpolicy -V`, runs `mdp -m policy.conf file_contexts`, compiles the policy with `checkpolicy -U allow -M`, creates SELinux directory structure and context files, copies generated policy/context artifacts, writes `/etc/selinux/config`, runs `setfiles`, and creates `/.autorelabel`.

Control flow: after dependency checks, it refuses to proceed if SELinux is currently enabled because relabeling all files is unsafe. It builds the dummy policy in `mdp`, populates `/etc/selinux/dummy`, backs up an existing `/etc/selinux/config`, relabels `/` plus selected mounted filesystem roots, and schedules autorelabel.

State and persistence: it writes system policy files, may rename `/etc/selinux/config` to `.bak`, relabels filesystem labels, and writes `/.autorelabel`. This is intentionally invasive.

Dependencies and integration points: depends on the `mdp` host binary, SELinux userspace tools, root permissions, and Linux filesystem layout. It is a helper for testing/bootstrapping SELinux rather than normal kernel build output.

Risks: the script has broad host-system side effects and should not be run accidentally. The mount-list command uses shell/awk quoting that should be reviewed before changes. Running on an active SELinux system is blocked but permissive/relabel behavior still affects the machine.

Test signals: test only in disposable VMs or containers with appropriate privileges. Validate generated policy compiles, expected files exist, `/etc/selinux/config` content is correct, and relabel commands receive intended mount paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/selinux/install_policy.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/selinux/mdp/Makefile -->
# sources/distributed-fs/ceph-client/scripts/selinux/mdp/Makefile

Purpose: this Makefile builds the SELinux `mdp` host program and declares its cleanup outputs.

Important APIs, types, and functions: `hostprogs-always-y += mdp` always builds the host tool. `HOST_EXTRACFLAGS` adds include paths for kernel headers, SELinux headers, and generated object-tree includes. `clean-files := policy.* file_contexts` removes generated policy outputs.

Control flow: Kbuild consumes these variables during host tools build and clean phases.

State and persistence: build state includes the `mdp` executable and generated policy artifacts cleaned by `make clean`.

Dependencies and integration points: depends on `mdp.c` and generated/in-tree headers such as class maps. It is reached through `scripts/selinux/Makefile`.

Risks: incorrect include paths can make `mdp.c` use stale or missing SELinux class/policycap definitions. Cleaning patterns should stay limited to generated outputs.

Test signals: host build should compile `mdp`; `make clean` should remove `policy.*` and `file_contexts` without deleting source files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/selinux/mdp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/selinux/mdp/mdp.c -->
# sources/distributed-fs/ceph-client/scripts/selinux/mdp/mdp.c

Purpose: `mdp.c` generates a minimal dummy SELinux policy and file contexts. The generated policy contains one type with broad self-permissions and enough class, sid, capability, filesystem, role, and user declarations to boot/test SELinux.

Important APIs, types, and functions: it defines `struct security_class_mapping` to satisfy included SELinux class-map data, includes `classmap.h`, `initial_sid_to_string.h`, and `policycap_names.h`, and has a single `main()` with optional `-m` MLS mode. Macros `FS_USE` and `GENFSCON` emit filesystem labeling statements based on kernel config macros.

Control flow: `main()` parses `[-m] policy_file context_file`, writes class declarations, sid declarations, class permissions, optional MLS sensitivities/categories/constraints, all policy capabilities, `base_t`/`base_r` type-role-user statements, allow-all rules for each class, default SID contexts, filesystem labeling rules gated by config, and finally writes two file-context defaults for `/` and `/.*`.

State and persistence: it writes the policy output and context output files supplied on the command line. It has no external state beyond compile-time `CONFIG_*` macros.

Dependencies and integration points: built as a host tool by Kbuild and used by `install_policy.sh`. Its output is consumed by `checkpolicy` and SELinux userspace tools.

Risks: the generated policy grants extremely broad permissions and is only suitable as a dummy/test policy. Filesystem rules are compile-time dependent, so mismatched config headers produce incomplete labels. The OCFS2 string appears as `ocsfs2`, which should be verified against expected filesystem names.

Test signals: compile against current SELinux headers, run with and without `-m`, pass output through `checkpolicy`, and verify generated contexts cover expected configured filesystems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/selinux/mdp/mdp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/setlocalversion -->
# sources/distributed-fs/ceph-client/scripts/setlocalversion

Purpose: `setlocalversion` computes the kernel release suffix by combining `KERNELVERSION`, `localversion*` files, `CONFIG_LOCALVERSION`, `LOCALVERSION`, and optional Git-derived SCM state.

Important APIs, types, and functions: `try_tag()` accepts annotated tags that are ancestors of HEAD and records commit count. `scm_version()` emits `+`, `-NNNNN-g<12hex>`, and optionally `-dirty` depending on tag distance and repository state. `collect_files()` concatenates localversion files while ignoring backup names containing `~`.

Control flow: the script parses `--no-local` and optional source tree, requires `KERNELVERSION`, collects build-tree and source-tree localversion fragments, and either emits a no-local version or validates `include/config/auto.conf`. It extracts `CONFIG_LOCALVERSION`, uses `CONFIG_LOCALVERSION_AUTO` to decide full SCM suffix behavior, and prints the final release string.

State and persistence: it only reads files and Git metadata. It deliberately avoids Git commands that create index locks when checking dirty state.

Dependencies and integration points: heavily used by Kbuild to produce `kernelrelease`. Depends on Git when SCM suffixes are needed, `sed`, `grep`, and `include/config/auto.conf`.

Risks: output changes affect module install paths, package names, and ABI labels. Dirty detection can be misleading on older Git fallback because `git diff-index` does not refresh the index. Annotated tag selection must preserve mainline, stable, linux-next, and RT conventions.

Test signals: test at exact tags, ahead of tags, dirty trees, absent Git metadata, separate object/source trees, `LOCALVERSION` set/empty/unset, and `--no-local`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/setlocalversion -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/show_delta -->
# sources/distributed-fs/ceph-client/scripts/show_delta

Purpose: `show_delta` reformats printk/dmesg lines with `[seconds]` timestamps to include deltas either from the previous timestamp or from a specified base timestamp/message.

Important APIs, types, and functions: `usage()` prints help. `get_time(line)` parses bracketed timestamps and returns `(float_time, rest)`. `convert_line(line, base_time)` preserves unparseable lines and emits `[%5.6f < %5.6f >]` for parseable lines. `main()` handles `-b` and `-h`, reads the whole file, resolves a numeric or string base, and prints converted lines.

Control flow: without `-b`, the global `last_time` tracks previous line time. With `-b`, all deltas are relative to the chosen base. A string base is matched against the beginning of the message rest.

State and persistence: no persistence; state is in memory and output is stdout.

Dependencies and integration points: intended as a developer utility for CONFIG_PRINTK_TIME or `time` kernel command-line logs. It uses Python 3 but contains Python 2-era `string.split`, `string.atof`, and `string.find` calls, which are not available in modern Python 3.

Risks: as written for Python 3, the `string` module calls will fail unless compatibility shims exist, so this script likely needs modernization to `str.split`, `float`, and `str.find`. It reads the whole file at once.

Test signals: run on sample dmesg output with and without `-b`, include unparseable lines, and verify Python 3 compatibility. A failing smoke test today would point to the legacy `string` API usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/show_delta -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/sign-file.c -->
# sources/distributed-fs/ceph-client/scripts/sign-file.c

Purpose: `sign-file.c` signs kernel modules by appending a PKCS#7/CMS signature, a `struct module_signature`, and the module signature marker. It can sign with PEM or PKCS#11 keys, append an externally generated raw signature, or save a detached signature.

Important APIs, types, and functions: `format()` prints usage. `pem_pw_cb()` supplies `KBUILD_SIGN_PIN` once to encrypted private keys. `read_private_key_pkcs11()` uses OpenSSL 3 providers or older engines. `read_private_key()` selects PKCS#11 URI versus PEM file. `read_x509()` detects DER versus PEM certificates. `main()` parses `-s`, `-d`, `-p`, and `-k`, prepares CMS flags, handles ML-DSA/OpenSSL 3.5 `CMS_NOATTR` compatibility, streams module bytes, writes signature data, `module_signature`, and marker, then optionally renames the signed temp over the original.

Control flow: raw-signature mode changes argument interpretation. Non-raw mode loads key/cert, resolves digest, creates a detached CMS signature over the module BIO, optionally writes `.p7s`, and may exit early for sign-only. Append mode writes the destination module copy before appending signature metadata.

State and persistence: it writes either an explicit destination or a temporary `module.~signed~` which is renamed over the module. `-p` writes `module.p7s`. It reads `KBUILD_SIGN_PIN` from the environment.

Dependencies and integration points: depends on OpenSSL headers/libraries, `ssl-common.h`, and `linux/module_signature.h`. Kbuild uses it for module signing and certificate workflows.

Risks: OpenSSL API compatibility is complex across 1.1, 3.x, providers, engines, PKCS#11, and post-quantum key handling. In-place signing has rename behavior but leaves temp files on some failures. Raw signatures are trusted as supplied and only length-stamped.

Test signals: sign/verify modules with PEM, encrypted PEM, PKCS#11, raw signatures, `-d`, `-p`, `-k`, DER and PEM certs, unknown digest, and OpenSSL 3 provider configurations. Kernel module loader acceptance is the integration test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/sign-file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/sorttable.c -->
# sources/distributed-fs/ceph-client/scripts/sorttable.c

Purpose: `sorttable.c` rewrites linked kernel ELF images so exception tables, and conditionally ORC unwind and mcount location tables, are sorted before boot/runtime use. It also clears `main_extable_sort_needed`.

Important APIs, types, and functions: it uses `elf-parse.h` abstraction for endian/class access. Core helpers include `compare_extable_32/64()`, `get_secindex()`, `do_sort()`, `do_file()`, `sort_relative_table()`, and `sort_relative_table_with_data()`. With `UNWINDER_ORC_ENABLED`, `sort_orctable()` sorts `.orc_unwind_ip` and `.orc_unwind` together using relative IP values and weak terminator ordering. With `MCOUNT_SORT_ENABLED`, `parse_symbols()`, `fill_relocs()`, `fill_addrs()`, `sort_mcount_loc()`, and `get_mcount_loc()` sort `__start_mcount_loc` to `__stop_mcount_loc` and optionally filter addresses against an nm symbol list.

Control flow: `main()` optionally parses `-s nm-file`, maps each vmlinux as `ET_EXEC` or `ET_DYN`, and calls `do_file()`. `do_file()` selects architecture-specific exception table entry layout and relative sort strategy, then `do_sort()` locates `__ex_table`, `.symtab`, `.strtab`, optional `.init.data`, and optional ORC sections, launches optional sort threads, sorts the exception table, finds and clears `main_extable_sort_needed`, then joins worker threads and propagates errors.

State and persistence: it mmaps the target through `elf_map()` and mutates table contents in place before `elf_unmap()`. Conditional global state stores ORC pointers, mcount function lists, relocation mode, and error strings.

Dependencies and integration points: invoked late in the kernel link/build process. It depends on symbol names, section names, architecture relocation conventions, pthreads, and optional generated ORC/mcount build defines.

Risks: corrupting sort order or relative encoding breaks exception handling, unwinding, or ftrace. Threaded optional sorts can overwrite `rc` in join paths. Architecture-specific entry sizes and relative encodings must match runtime lookup code. Missing symbols/sections are fatal for the expected configuration.

Test signals: boot tests, exception table selftests, objtool/ORC validation, ftrace tests, and `readelf`/custom checks showing sorted tables and cleared `main_extable_sort_needed`. Exercise all supported architectures and both relocation-backed and direct-address mcount cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/sorttable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/spdxcheck-test.sh -->
# sources/distributed-fs/ceph-client/scripts/spdxcheck-test.sh

Purpose: `spdxcheck-test.sh` is a smoke test for the SPDX checker against text, binary, stdin, and full-tree inputs.

Important APIs, types, and functions: it loops over `Makefile` and `Documentation/images/logo.gif`, running `python3 scripts/spdxcheck.py $FILE` and stdin mode via `python3 scripts/spdxcheck.py - < $FILE`, then runs a complete tree check redirected to `/dev/null`.

Control flow: there is no `set -e`, so the effective failure behavior depends on the shell or caller. Commands run sequentially.

State and persistence: no persistent state; stdout from full tree scan is discarded.

Dependencies and integration points: depends on Python 3, `scripts/spdxcheck.py`, and the referenced files existing in a full kernel tree.

Risks: without `set -e`, a failed command may not stop the script when run directly in some contexts. Referenced paths must exist in the source tree variant.

Test signals: nonzero exit from any `spdxcheck.py` call should be captured by the invoking test harness. Add `set -e` if direct execution should fail fast.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/spdxcheck-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/spdxcheck.py -->
# sources/distributed-fs/ceph-client/scripts/spdxcheck.py

Purpose: `spdxcheck.py` validates SPDX license identifier expressions in source files against the in-tree `LICENSES` metadata and can report directory/file coverage.

Important APIs, types, and functions: `SPDXdata` stores license and exception sets. `read_spdxdata()` walks `LICENSES/preferred`, `dual`, `deprecated`, and `exceptions` from the Git tree and validates exception license lists. `id_parser` uses PLY lex/yacc to parse license expressions with `AND`, `OR`, `WITH`, and parentheses, validating license IDs and exception applicability. `pattern` implements exclude-file matching, while `scan_git_tree()`, `scan_git_subtree()`, and `read_exclude_file()` drive repository traversal.

Control flow: command-line parsing supports paths, stdin, directory statistics, depth, excludes, missing-file output, max scan lines, and verbose stats. It initializes a GitPython repo, loads SPDX metadata, reads exclude rules, then parses stdin, specified files/directories, or the full Git tree. Per file, `parse_lines()` scans up to `maxlines` for `SPDX-License-Identifier:`, strips comment closures for C/XML/Jinja/list forms, parses the expression, and updates coverage counters.

State and persistence: no file writes. Runtime state includes parser counters and per-directory missing-file summaries.

Dependencies and integration points: depends on Python 3, GitPython, PLY, locale decoding, and the kernel `LICENSES` tree. Used by licensing checks and developer validation.

Risks: only the first matching SPDX line is parsed. File existence checks use `os.path.isfile(el.path)` against Git tree paths, so invocation must occur from a compatible worktree. Parser precedence treats `AND` and `OR` at the same non-associative level, matching the script's grammar expectations but requiring tests for complex expressions.

Test signals: `spdxcheck-test.sh`, known valid/invalid expressions, exception-license mismatch cases, stdin binary input, exclude rules, and verbose directory reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/spdxcheck.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/ssl-common.h -->
# sources/distributed-fs/ceph-client/scripts/ssl-common.h

Purpose: `ssl-common.h` provides shared OpenSSL error-draining and error-checking helpers for signing/certificate host tools such as `sign-file` and `extract-cert`.

Important APIs, types, and functions: `drain_openssl_errors(int l, int silent)` prints and clears pending OpenSSL errors, optionally with a source line banner. `ERR(cond, fmt, ...)` drains OpenSSL errors, evaluates a condition, and calls `errx(1, ...)` on failure.

Control flow: callers use `ERR()` after OpenSSL calls so queued library errors do not accumulate and so failures include OpenSSL diagnostics.

State and persistence: it mutates OpenSSL's per-thread error queue by consuming errors. No file state.

Dependencies and integration points: requires OpenSSL error APIs, stdio, err, and bool definitions from including files. `sign-file.c` includes it after OpenSSL headers.

Risks: the printed banner says `main.c` regardless of actual source file, which can confuse diagnostics. `ERR()` drains errors even when the condition is false, which is intentional cleanup but may hide warnings from later code.

Test signals: inject OpenSSL failures in sign-file/extract-cert paths and verify useful diagnostics and nonzero exits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/ssl-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/stackdelta -->
# sources/distributed-fs/ceph-client/scripts/stackdelta

Purpose: `stackdelta` compares two stack-usage reports produced by `stackusage` and prints size deltas for functions present in both reports.

Important APIs, types, and functions: `read_stack_usage_file()` reads lines split into file, function, size, and type; skips numeric-only GCC-generated names; strips suffixes after `.` from function names; strips line numbers from file names; and returns a hash keyed by `file\tfunction`. The main block requires two arguments, intersects keys, and prints old size, new size, and signed delta for changed entries.

Control flow: both files are read fully, common keys are sorted, and only nonzero deltas are emitted.

State and persistence: no writes except stdout.

Dependencies and integration points: companion to `stackusage`, useful for compiler/config/change impact analysis of stack usage.

Risks: stripping at the first dot collapses functions with meaningful dots and intentionally ignores inlining suffix differences. Functions that appear or disappear are not reported.

Test signals: compare small synthetic `.su` reports with common, changed, added, removed, numeric-suffix, and dotted function names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/stackdelta -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/stackusage -->
# sources/distributed-fs/ceph-client/scripts/stackusage

Purpose: `stackusage` runs `make` with GCC/Clang stack-usage generation enabled and aggregates newly created `.su` files into a sorted report.

Important APIs, types, and functions: it parses `-o outfile` and `-h`, records the current epoch time, defaults `outfile` to a temporary file, invokes `KCFLAGS="${KCFLAGS} -fstack-usage" make "$@"`, then finds `.su` files newer than the start time. A Perl one-liner prepends directory names, removes column numbers, tab-separates fields, and the result is sorted by stack size descending.

Control flow: option parsing stops at first non-option make argument. Build happens before report collection. The output path is printed at the end.

State and persistence: it creates compiler `.su` files through the build and writes the aggregated report.

Dependencies and integration points: depends on a compiler supporting `-fstack-usage`, make/Kbuild, `find`, `xargs`, Perl `File::Basename`, `sort`, and `mktemp`.

Risks: filenames with unusual whitespace may be fragile through `xargs` and Perl field parsing. Only files newer than script start are included, so clock issues or preexisting outputs may affect reports.

Test signals: run on a small build target, verify `.su` records are normalized and sorted, then compare two outputs with `stackdelta`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/stackusage -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/syscallhdr.sh -->
# sources/distributed-fs/ceph-client/scripts/syscallhdr.sh

Purpose: `syscallhdr.sh` generates a UAPI syscall number header from an architecture syscall table.

Important APIs, types, and functions: options include `--abis`, `--emit-nr`, `--offset`, and `--prefix`. It computes a header guard from the output basename, filters table rows with `grep -E`, emits `#define __NR_${prefix}${name} ${nr}`, optionally applies an offset expression, and optionally emits `__NR_${prefix}syscalls` under `__KERNEL__`.

Control flow: after option parsing and two-argument validation, a pipeline writes the entire header atomically through shell redirection to the output path. `max` tracks the last processed number for syscall count.

State and persistence: writes the output header file.

Dependencies and integration points: used by architecture builds to derive generated syscall headers from `.tbl` files. Depends on table rows formatted as documented in the file header.

Risks: ABI regex is built directly from the option string and should be supplied by trusted build logic. Hex syscall numbers pass the grep but shell arithmetic for `emit_nr` may not handle all forms consistently. Input ordering matters for `max`.

Test signals: generate headers for all ABIs, selected ABI lists, offsets, prefixes, and `--emit-nr`; compare against expected generated headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/syscallhdr.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/syscallnr.sh -->
# sources/distributed-fs/ceph-client/scripts/syscallnr.sh

Purpose: `syscallnr.sh` generates a small header containing only the number of syscalls for selected ABIs.

Important APIs, types, and functions: options are `--abis` and `--prefix`. It filters matching rows, sorts them numerically, tracks the last syscall number, and emits `#define __NR_${prefix}syscalls $((max + 1))` inside a generated include guard.

Control flow: the script validates two positional arguments, computes the guard, streams filtered/sorted rows through a while loop, and writes the header to the output file.

State and persistence: writes one generated header.

Dependencies and integration points: used by architecture syscall generation where the full number header is not wanted or is split. Depends on sort, grep, sed, and shell arithmetic.

Risks: sorting with `sort -n` and arithmetic assumes numeric syscall identifiers; hexadecimal rows may not behave as expected despite the grep accepting them. ABI regex is caller-controlled.

Test signals: syscall tables with gaps, ABI filters, prefixes, and highest-number edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/syscallnr.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/syscalltbl.sh -->
# sources/distributed-fs/ceph-client/scripts/syscalltbl.sh

Purpose: `syscalltbl.sh` generates a C-style syscall dispatch macro table from architecture syscall table input.

Important APIs, types, and functions: it accepts `--abis`, reads rows as `nr abi name native compat noreturn`, fills gaps with `__SYSCALL(n, sys_ni_syscall)`, emits `__SYSCALL_WITH_COMPAT`, `__SYSCALL_NORETURN`, `__SYSCALL_COMPAT_NORETURN`, normal `__SYSCALL`, or default `sys_ni_syscall` based on columns.

Control flow: `nxt` tracks the expected next number. If a row number is lower than `nxt`, the script reports unsorted/duplicate input and exits. For each gap it emits dummy rows, normalizes `compat=-` to unset, validates the optional `noreturn` token, emits the appropriate macro, and advances `nxt`.

State and persistence: writes the generated output file.

Dependencies and integration points: part of syscall wrapper/header generation for architectures. Depends on trusted table formatting and downstream macro definitions.

Risks: only decimal rows are selected by grep, unlike the number-header scripts. Error output for invalid `noreturn` is missing explicit stderr redirection in one branch. ABI regex is direct from caller input.

Test signals: tables with gaps, duplicate/unsorted numbers, compat entries, `-` compat placeholders, noreturn entries, and missing native symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/syscalltbl.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/tags.sh -->
# sources/distributed-fs/ceph-client/scripts/tags.sh

Purpose: `tags.sh` generates source navigation databases for the kernel tree: ctags `tags`, etags `TAGS`, GNU GLOBAL `gtags`, or cscope files.

Important APIs, types, and functions: source discovery helpers include `find_arch_sources()`, `find_arch_include_sources()`, `find_include_sources()`, `find_other_sources()`, `all_sources()`, `all_compiled_sources()`, `all_target_sources()`, and `all_kconfigs()`. Generators include `docscope()`, `dogtags()`, `setup_regex()`, `exuberant()`, `emacs()`, and `xtags()`. Large regex arrays teach taggers kernel macro-generated symbols for assembly, C, and Kconfig.

Control flow: the script builds ignore expressions from `RCS_FIND_IGNORE`, `*.mod.c`, and `IGNORE_DIRS`; selects source-root path style from `srctree`, `KBUILD_ABS_SRCTREE`, and gtags constraints; resolves `ALLSOURCE_ARCHS`; handles UML `SUBARCH`; then dispatches by mode. For tags/TAGS it removes previous output, runs the best supported tagger mode, and removes struct forward-declaration tags with sed.

State and persistence: writes `tags`, `TAGS`, `GTAGS`/GLOBAL files, `cscope.files`, and `cscope.out` depending on mode.

Dependencies and integration points: invoked by Kbuild developer targets. Depends on bash arrays, find, awk, grep, sed, xargs, realpath, ctags/etags/gtags/cscope, and kernel build `.cmd` files when `COMPILED_SOURCE` is set.

Risks: find expression construction uses shell-expanded ignore strings and requires trusted inputs. Very large trees can stress command-line length through `xargs`, though xargs mitigates. Regex compatibility differs between universal/exuberant/emacs taggers.

Test signals: generate each mode in in-tree and O= builds, with `ALLSOURCE_ARCHS=all`, `COMPILED_SOURCE=1`, UML arch, and both universal and emacs ctags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/tags.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/tools-support-relr.sh -->
# sources/distributed-fs/ceph-client/scripts/tools-support-relr.sh

Purpose: `tools-support-relr.sh` probes whether the configured compiler/binutils pipeline supports RELR packed relative relocations well enough for kernel use.

Important APIs, types, and functions: it creates a temporary C object defining `void *p = &p;`, links it as a shared object with either LLD `--pack-dyn-relocs=relr` or GNU/compatible `-z pack-relative-relocs`, verifies `nm` can inspect it without stderr output, and runs `objcopy -O binary`.

Control flow: `set -eu` aborts on unset variables or failures. A trap removes temp files. If the LLD-style option fails, it tries the `-z` form and treats an error mentioning `pack-relative-relocs` as unsupported.

State and persistence: only temporary files under `mktemp`, removed on exit.

Dependencies and integration points: used by Makefiles/Kconfig probes for RELR support. Depends on `CC`, `LD`, `NM`, and `OBJCOPY` environment variables.

Risks: tool diagnostics are parsed by substring, so message changes can affect detection. GNU nm's zero exit with RELR stderr is explicitly handled by requiring empty stderr.

Test signals: run with supported binutils, old LLD before 15, unsupported GNU ld, and nm versions that print RELR errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/tools-support-relr.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/tracepoint-update.c -->
# sources/distributed-fs/ceph-client/scripts/tracepoint-update.c

Purpose: `tracepoint-update.c` checks ELF objects for tracepoints that are defined but not referenced through the tracepoint verification section, warning about unused tracepoints.

Important APIs, types, and functions: it uses `elf-parse.h` and globals for `__tracepoint_check` and `__tracepoints_strings` sections. `add_string()` grows an array of string pointers. `for_each_shdr_str` iterates NUL-terminated strings in a section. `make_trace_array()` builds and sorts the checked tracepoint names. `find_event()` uses `bsearch()`. `check_tracepoints()` warns for strings not present in the checked array. `process_tracepoints()` locates sections and handles module-specific absence rules.

Control flow: `main()` accepts optional `--module`, maps each input with `elf_map(..., 1 << ET_REL)`, and processes it. For modules, absence of both sections is allowed, absence of check section with tracepoints warns but does not fail, and absence of tracepoint strings can mean only exported references. For non-modules, missing sections are fatal. Found tracepoint strings are compared against the sorted check list.

State and persistence: no file mutation despite the name. It allocates and frees a transient string-pointer array and writes warnings to stderr.

Dependencies and integration points: tied to kernel tracepoint section names and object build steps. The non-module usage text says `vmlinux`, but the mapping mask accepts `ET_REL`, so callers need to supply the expected relocatable object form.

Risks: global section pointers are not reset inside `process_tracepoints()`, which matters if processing multiple files with different section presence. String section iteration assumes well-formed NUL-terminated data. Misaligned usage expectations around ET_REL versus linked vmlinux can confuse integration.

Test signals: objects with no tracepoints, all-used tracepoints, unused tracepoints, module-only exported references, and multiple input files with different section combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/tracepoint-update.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/tracing/ftrace-bisect.sh -->
# sources/distributed-fs/ceph-client/scripts/tracing/ftrace-bisect.sh

Purpose: `ftrace-bisect.sh` helps isolate a function that crashes or hangs the system when enabled under function or function-graph tracing.

Important APIs, types, and functions: it takes `full-file`, `test-file`, and `non-test-file`. It uses `wc -l` to count candidates and `sed` to split the list into first half and second half. Existing output files trigger interactive delete confirmations.

Control flow: if one function remains, it prints that candidate and exits. Otherwise it halves the input line count, checks the input file exists, prompts if output files already exist, then writes lines `1..x` to the test file and `x+1..end` to the non-test file.

State and persistence: writes two candidate files and reads the full candidate list. Users manually move files between iterations based on crash/no-crash outcome.

Dependencies and integration points: designed for manual use with `/sys/kernel/tracing/set_ftrace_filter`, `available_filter_functions`, and `current_tracer`.

Risks: unquoted variables make paths with spaces unsafe. The script counts the file before verifying it exists. Interactive prompts are unsuitable for automation.

Test signals: run against synthetic lists with odd/even counts, one-line inputs, preexisting outputs, and missing input. Manual ftrace workflows are the real integration validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/tracing/ftrace-bisect.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/unifdef.c -->
# sources/distributed-fs/ceph-client/scripts/unifdef.c

Purpose: `unifdef.c` removes or preserves C preprocessor conditional blocks according to supplied `-D`, `-U`, `-iD`, and `-iU` symbols. It is a standalone source-filtering utility imported from Tony Finch's unifdef.

Important APIs, types, and functions: key enums model line types (`Linetype`), conditional processing states (`Ifstate`), comment states, and line parser states. Global options implement `-b`, `-B`, `-c`, `-d`, `-e`, `-K`, `-k`, `-n`, `-s`, `-S`, `-t`, and output file behavior. `main()` parses options and sets up input/output, using a temp file when overwriting. `process()` drives the `trans_table` state machine. `parseline()` classifies preprocessor lines while tracking comments. `ifeval()`, `eval_table()`, and `eval_unary()` evaluate a subset of preprocessor expressions. `flushline()`, `keywordedit()`, `nest()`, and `unnest()` implement output and nesting behavior.

Control flow: after setup, `process()` repeatedly parses a line and invokes a state transition function indexed by current `Ifstate` and `Linetype`. Known true/false blocks are dropped or printed, unknown blocks pass through, and some `#elif`/`#else` lines are rewritten to maintain valid nesting after deletion. The expression parser supports numeric constants, `defined`, identifiers, `!`, parentheses, comparison, equality, `&&`, and `||`, with strict or short-circuit ambiguity rules.

State and persistence: it streams input to stdout or an output file. In overwrite mode, it writes a temp file with the original mode and renames it only after successful close. Exit status is 1 if any lines were deleted, 0 if unchanged, and 2 for errors.

Dependencies and integration points: used by build/config tooling that needs conditional source pruning. Depends only on libc/POSIX file APIs.

Risks: fixed limits (`MAXLINE`, `MAXDEPTH`, `MAXSYMS`) can reject extreme inputs. "Dodgy" directives with continuations/comments are intentionally conservative and may error. `debug()` uses `vwarnx` with a `va_list` in a way that merits portability review. Expression support is not a full C preprocessor.

Test signals: nested if/elif/else cases, ignored symbols, complement mode, symlist modes, CRLF input, overwrite mode, malformed directives, comments/strings containing preprocessor-looking text, and ambiguous expressions under `-K` and default mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/unifdef.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/ver_linux -->
# sources/distributed-fs/ceph-client/scripts/ver_linux

Purpose: `ver_linux` is an awk utility that prints versions of system tools relevant to kernel compilation and installation, along with the running kernel and loaded modules.

Important APIs, types, and functions: the `BEGIN` block defines regexes, prints a note pointing to `Documentation/process/changes.rst`, runs `uname -a`, then calls `printversion(name, version(command))` for many tools. `version(cmd)` executes a command, returns the first version-like number matched in its output, and closes the pipe. `printversion()` formats non-empty values. It also scans `ldconfig -p` for libc/libstdc++ paths and `/proc/modules` for loaded modules.

Control flow: all work happens during awk startup; there is no input file processing requirement.

State and persistence: it reads host command output and prints a report to stdout. No files are modified.

Dependencies and integration points: developer support script for diagnosing build environment minimums. Depends on many optional commands being in PATH and on GNU-ish awk/system behavior.

Risks: version regex is intentionally broad and can pick a non-version number from unusual output. Missing tools are silently omitted. Command execution from awk means PATH should be trusted.

Test signals: run on minimal and full development hosts, compare emitted versions against expected tool versions, and verify no hard failure when optional tools are missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/ver_linux -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/verify_builtin_ranges.awk -->
# sources/distributed-fs/ceph-client/scripts/verify_builtin_ranges.awk

Purpose: `verify_builtin_ranges.awk` verifies that `modules.builtin.ranges` correctly maps built-in module address ranges to symbols in `System.map` and linker maps.

Important APIs, types, and functions: `get_module_info()` reads object-specific `.cmd` files to recover `DKBUILD_MODFILE` or `RUST_MODFILE`, validates single-module names against `modules.builtin`, caches results, and normalizes module names. `addr2val()` converts kernel hex addresses to AWK numeric values by stripping high bits when needed. Main processing uses `ARGIND` phases for ranges, System.map annotation, built-in module list, vmlinux.map, and optional vmlinux.o.map.

Control flow: phase 1 stores ranges. Phase 2 walks System.map symbols, advancing current range and recording `addr-name -> module` annotations. Phase 3 loads built-in modules. Phases 4/5 parse GNU ld or LLD map formats, identify sections/objects/symbols, handle `vmlinux.o` fallback, apply section addends, compare symbol module annotations against object module membership, and count matches, mismatches, and missing records. END prints a summary and exits nonzero on mismatch/missing.

State and persistence: no writes; it reads several generated build artifacts and object `.cmd` files. It caches module info and address annotations in AWK arrays.

Dependencies and integration points: used in kernel build validation for built-in module range metadata. Requires GNU awk features such as `ARGIND` and `strtonum`, plus linker map formats from GNU ld or LLD.

Risks: linker map parsing is necessarily format-sensitive. Address truncation assumes all kernel addresses lie in the same high region. Missing `.cmd` files cause a diagnostic suggesting running from the object directory for O= builds. Duplicate symbols can complicate classification.

Test signals: generated fixture maps for GNU ld and LLD, O= builds, Rust module objects, vmlinux.o fallback, duplicate symbols, zero-size boundary symbols, and intentionally corrupted range data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/verify_builtin_ranges.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/xen-hypercalls.sh -->
# sources/distributed-fs/ceph-client/scripts/xen-hypercalls.sh

Purpose: `xen-hypercalls.sh` generates a list of Xen hypercall macro invocations from preprocessed hypercall definition headers.

Important APIs, types, and functions: it accepts an output path followed by input headers. For each input it runs `eval $CPP $LINUXINCLUDE -dD -imacros "$i" -x c /dev/null`, then awk collects `#define __HYPERVISOR_*` macros whose names match lowercase hypercall naming and maps numbers to names. The END block prints an auto-generated comment and `HYPERCALL(name)` lines for values without reverse duplicates, sorted uniquely.

Control flow: all inputs are preprocessed and concatenated into one awk pass; sorted output is redirected to the requested output file.

State and persistence: writes the generated output file.

Dependencies and integration points: depends on `CPP` and `LINUXINCLUDE` environment variables, Xen header macro naming, awk, and sort. Used by architecture Xen integration generation.

Risks: `eval` makes CPP/LINUXINCLUDE trusted build variables important. Macro parsing assumes `#define` field layout and numeric values in `$3`. Duplicate-value filtering is compact and should be tested when aliases exist.

Test signals: headers with unique hypercalls, aliases/duplicates, nonmatching uppercase names, and CPP include path failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/xen-hypercalls.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/xz_wrap.sh -->
# sources/distributed-fs/ceph-client/scripts/xz_wrap.sh

Purpose: `xz_wrap.sh` wraps `xz` for kernel image compression, selecting architecture-appropriate BCJ filters and LZMA2 literal-position options.

Important APIs, types, and functions: `is_enabled()` tests `include/config/auto.conf` for a `CONFIG_* = y` line. The script reads `XZ_VERSION` from `$XZ --robot --version`, sets `ALIGN` and `BCJ` based on `$SRCARCH`, and maps alignment to `LZMA2OPTS`: none for 1-byte, `lp=1` for 2-byte, and `lp=2,lc=2` for 4-byte instruction alignment.

Control flow: the architecture case handles ARM/Thumb2, arm64 with XZ 5.4 arm64 filter gating, csky, loongarch, mips/micromips, parisc, powerpc big-endian filter, riscv compressed ISA with XZ 5.6 filter gating, s390, sh, sparc, x86, and a warning fallback. It then execs `$XZ --check=crc32 --threads=1 $BCJ --lzma2=$LZMA2OPTS,dict=128MiB`.

State and persistence: no internal output file handling; it replaces itself with xz and lets caller-provided stdin/stdout or xz arguments control data flow.

Dependencies and integration points: used by architecture compressed kernel image rules. Depends on `XZ`, `SRCARCH`, generated config, and an xz version whose robot version is numerically comparable.

Risks: missing arch tuning falls back to 2-byte alignment and may reduce compression. New BCJ filters are version-gated by numeric thresholds that must track XZ Utils releases. It forces single-threaded compression for ratio/RAM reasons, affecting build time.

Test signals: run for each supported `SRCARCH` and relevant config combinations, verify chosen command line, and compare decompressor compatibility with `lib/decompress_unxz.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/xz_wrap.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/Kconfig -->
# sources/distributed-fs/ceph-client/security/Kconfig

Purpose: `security/Kconfig` defines top-level Linux security configuration options and sources individual LSM and integrity Kconfig files.

Important APIs, types, and functions: options include `SECURITY_DMESG_RESTRICT`, the `/proc/pid/mem` override choice (`PROC_MEM_ALWAYS_FORCE`, `PROC_MEM_FORCE_PTRACE`, `PROC_MEM_NO_FORCE`), `MSEAL_SYSTEM_MAPPINGS`, `SECURITY`, `HAS_SECURITY_AUDIT`, `SECURITYFS`, `SECURITY_NETWORK`, `SECURITY_INFINIBAND`, `SECURITY_NETWORK_XFRM`, `SECURITY_PATH`, `INTEL_TXT`, `LSM_MMAP_MIN_ADDR`, `STATIC_USERMODEHELPER`, `STATIC_USERMODEHELPER_PATH`, legacy default major LSM choice, `LSM`, and `SECURITY_COMMONCAP_KUNIT_TEST`.

Control flow: Kconfig dependency/default logic gates each option. It sources `security/keys/Kconfig`, multiple LSM Kconfigs, `security/integrity/Kconfig`, and `security/Kconfig.hardening`. The `LSM` string default changes based on the legacy major LSM selection and controls runtime initialization order unless overridden by `lsm=`.

State and persistence: user selections persist in `.config` and generated headers, influencing compiled objects and runtime security behavior.

Dependencies and integration points: top-level integration for security subsystems, KUnit tests, usermode helper hardening, securityfs, audit, networking hooks, and architecture features.

Risks: defaults affect system security posture. `MSEAL_SYSTEM_MAPPINGS` explicitly breaks software such as checkpoint/restore, UML, gVisor, and rr, so dependencies are conservative. The `LSM` order string must stay synchronized with available LSMs and ordering rules.

Test signals: Kconfig dependency tests, allnoconfig/defconfig/allmodconfig builds, boot tests with default and custom `lsm=`, KUnit commoncap tests, and securityfs/LSM module runtime checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/Makefile -->
# sources/distributed-fs/ceph-client/security/Makefile

Purpose: `security/Makefile` maps security-related Kconfig selections to compiled objects and subdirectories.

Important APIs, types, and functions: it always builds `commoncap.o`, conditionally builds `keys/`, `lsm_syscalls.o`, `min_addr.o`, `security.o`, `lsm_notifier.o`, `lsm_init.o`, `inode.o`, individual LSM subdirectories (`selinux/`, `smack/`, `tomoyo/`, `apparmor/`, `yama/`, `loadpin/`, `safesetid/`, `lockdown/`, `bpf/`, `landlock/`, `ipe/`), `lsm_audit.o`, `device_cgroup.o`, and `integrity/`.

Control flow: Kbuild evaluates `obj-y` and `obj-$(CONFIG_*)` assignments to decide which objects and directories are linked into the kernel.

State and persistence: no runtime state in the Makefile, but it controls kernel object composition.

Dependencies and integration points: directly corresponds to `security/Kconfig` options and subsystem directories. `commoncap.o` is always included as the default capability implementation.

Risks: missing an object here can make a Kconfig option silently incomplete at link/runtime. Spacing inconsistency is cosmetic, but config variable names must exactly match Kconfig definitions.

Test signals: build matrices for each LSM/security config, link checks for selected objects, and boot/runtime smoke tests for enabled security modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/Makefile -->
