# Research: subset-b-009207

Grouped research for the requested CrashMonkey/ACE files. Each section preserves the original source path and is bounded by the markers required by the reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/ace/specific_generator_scripts/seq3nestedgenerator.py -->
# sources/test-tools/crashmonkey/ace/specific_generator_scripts/seq3nestedgenerator.py

## Purpose

`seq3nestedgenerator.py` is intended to enumerate ACE/CrashMonkey three-operation workloads over nested directory/file names, generate j-lang files under `code/tests/seq3-nested/`, and invoke a workload translator to produce C++ test cases. It specializes the broader sequence-generator idea for link/rename-heavy workloads on `A`, `B`, and nested `AC` paths. The checked-in file also embeds a catalog of known filesystem-crash bugs and expected operation/sync sequences, used as a sanity oracle by `isBugWorkload`.

## Important APIs, Types, and Functions

- Global option sets define the search space: `FallocOptions`, `FileOptions`, `SecondFileOptions`, `DirOptions`, `SecondDirOptions`, `WriteOptions`, `dWriteOptions`, `TruncateOptions`, and `OperationSet`. In this variant `OperationSet = ['link','rename']`, so most dependency and j-lang emission logic is broader than the active search.
- `expected_sequence` and `expected_sync_sequence` encode known bug-triggering command and sync patterns.
- `SiblingOf`, `Parent`, and `file_range` model the small synthetic namespace and compute related paths for sync/dependency candidates.
- `buildTuple(command)` expands an operation name into legal parameter tuples.
- `buildCustomTuple(file_list)` is intended to build per-position sync choices from used files, including `fsync`, `sync`, and `none`.
- `insert*` helpers create synthetic dependency operations and mutate `open_file_map`, `open_dir_map`, and `file_length_map`.
- `check*Dep` helpers enforce preconditions such as parent directory existence, file existence/open state, directory cleanup, xattr setup, and nonzero file length.
- `satisfyDep` walks a candidate sequence and injects setup/cleanup operations before unsafe commands.
- `buildJlang` converts internal operation tuples into j-lang text lines with concrete offsets and checkpoint commands.
- `doPermutation` enumerates operation permutations, filters disconnected parameter combinations, attaches sync permutations, satisfies dependencies, writes `j-langN`, and invokes `python workload_seq2.py`.
- `main` parses `--sequence_len`, logs generator statistics, populates parameter lists, iterates the operation product, and moves generated j-lang files into `code/tests/seq3-nested/j-lang-files/`.

## Control Flow

The intended flow is: parse sequence length, build parameter choices for the active operations, enumerate all length-N operation products, enumerate parameter products for each operation tuple, filter combinations that do not share a file/directory dependency, compute the set of used files, build sync choices for that used set, interleave operation and sync/checkpoint tuples, run dependency repair, emit a j-lang file, translate it with `workload_seq2.py`, and finally collect generated j-lang files.

For each candidate sequence, the dependency state machine keeps maps for open files, open directories, and file lengths. It uses these maps to insert parent `mkdir`, `open`, `close`, `unlink`, `rmdir`, and seed `write` operations so that the target command can execute in the generated C++ test harness. The j-lang emitter then maps path names like `A/foo` to flattened names such as `Afoo`, assigns append and overlap offsets, and adds `checkpoint 0/1` after sync operations.

## State and Persistence Behavior

State is mostly process-local mutable globals: `global_count`, `parameterList`, `SyncSet`, `syncPermutations`, `permutations`, `count`, `count_param`, and `log_file_handle`. Persistent side effects include timestamped `*-bugWorkloadGen.log` files, temporary `j-lang*` files in the current directory, generated C++ tests through the translator call, and a final `mv j-lang* code/tests/seq3-nested/j-lang-files/`. The generated workloads ultimately persist as files under the CrashMonkey test tree and become build inputs for the Makefile.

## Dependencies and Integration Points

This script depends on Python 2 syntax and modules (`xrange`, backtick repr, `print` statements, `string.maketrans`). It shells out to `workload_seq2.py` and assumes relative paths such as `code/tests/seq3-nested/base-j-lang` and `code/tests/seq3-nested/base.cpp` from the working directory. The output C++ tests depend on the ACE j-lang grammar understood by `workload_seq2.py`, CrashMonkey `BaseTestCase`, and the user tools/wrapper APIs compiled by `sources/test-tools/crashmonkey/code/Makefile`.

## Risks and Edge Cases

- The checked-in file appears syntactically invalid in several regions: indentation is broken around `buildCustomTuple`, `checkDirDep`, `checkParentExistsDep`, `checkExistsDep`, `satisfyDep`, `buildJlang`, `doPermutation`, and `main`. As stored, it is unlikely to run without manual repair.
- `elif option == 'overlap' or 'overlap_aligned' or 'overlap_unaligned'` is logically always true because nonempty string literals are truthy.
- The generator mutates dictionaries while iterating them when closing open files/directories, which is unsafe if Python notices size changes.
- Generated shell commands use relative paths and `shell=True`, so running outside the expected CrashMonkey root can write or move the wrong files.
- `min = 0` shadows the built-in `min`.
- `buildJlang` depends on `length_map[file]` being initialized for append fallocate, which may fail if dependency insertion did not seed the file.
- Active `OperationSet` only contains `link` and `rename`, while much of the bug catalog and implementation covers other operations, so coverage is narrower than the file name implies.

## Test Signals

Useful validation signals are: successful execution under Python 2 after indentation repair; a nonempty timestamped log with parameter and workload counts; generated `j-lang*` files under `code/tests/seq3-nested/j-lang-files/`; generated C++ files under `code/tests/seq3-nested/`; successful `make seq1` or an added target that builds these generated tests; and CrashMonkey runs that hit expected bug sequences reported by `isBugWorkload`. Negative tests should include running from a wrong working directory and malformed nested directory cases because path assumptions are strong.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/ace/specific_generator_scripts/seq3nestedgenerator.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/ace/specific_generator_scripts/seq3writegenerator.py -->
# sources/test-tools/crashmonkey/ace/specific_generator_scripts/seq3writegenerator.py

## Purpose

`seq3writegenerator.py` is a Python 2 workload enumerator focused on three-operation write/data-manipulation sequences. It searches combinations of buffered write, mmap write, fallocate, and direct write on `A/foo`, records whether they match a catalog of known filesystem crash bugs, and contains code to generate j-lang/C++ workloads for `code/tests/seq3write/`. In the checked-in version, most actual file emission is commented out, so it primarily logs and optionally matches bug workloads.

## Important APIs, Types, and Functions

- Search-space globals: `FileOptions = ['A/foo']`, `SecondFileOptions`, `DirOptions`, `SecondDirOptions`, `WriteOptions`, `dWriteOptions`, `TruncateOptions`, and `OperationSet = ['write', 'mmapwrite', 'falloc', 'dwrite']`.
- `expected_sequence` and `expected_sync_sequence` contain the same known-bug oracle catalog used by related generators.
- `buildTuple(command)` expands file/range/mode combinations. This variant uses larger 32 KiB append lengths, unaligned 5 KiB ranges, 8 KiB direct-write overlaps, and one primary file.
- `buildCustomTuple(file_list)` emits sync choices over the used files and includes both `fsync` and `fdatasync` plus `none`; global `sync` is intentionally commented out.
- Dependency helpers (`insertOpen`, `insertWrite`, `checkParentExistsDep`, `checkExistsDep`, `checkFileLength`, `satisfyDep`) are present to construct executable j-lang, though the generation block that uses them is currently commented.
- `buildJlang(op_list, length_map, mmaplist)` converts internal tuples into j-lang lines. It also records deferred `msync` operations for mmap writes in `mmaplist`.
- `doPermutation(perm)` filters candidate operation and parameter combinations, builds sync permutations, interleaves operation and sync/checkpoint tuples, and logs generated candidates.
- `main` initializes logging and globals, prints the bug catalog, constructs parameter lists, enumerates the operation products, and moves any generated `j-lang*` files into `code/tests/seq3write/j-lang-files/`.

## Control Flow

The intended pipeline is enumeration-first. `main` creates a log, builds all operation parameter choices, builds a general `SyncSet`, and calls `doPermutation` for each product of the active operation set. `doPermutation` skips all-write permutations, requires the first parameter tuple to contain `append`, rejects all-append sequences, computes the used file set, generates per-position sync permutations, and produces an interleaved `seq` list. If uncommented, the lower block would satisfy dependencies, write a j-lang file from `code/tests/seq3write/base-j-lang`, insert deferred `msync`/`munmap` before closing `Afoo`, invoke `workload_seq3.py`, and call `isBugWorkload`.

## State and Persistence Behavior

The persistent output actually guaranteed by current code is a timestamped `*-bugWorkloadGen.log`. The move command at the end may move any matching `j-lang*` files if they exist from a prior or partially uncommented run. The commented generation path would persist j-lang files and C++ generated tests in `code/tests/seq3write/`. Runtime state is stored in global counters and maps; range state during j-lang emission is stored in `length_map`, and mmap sync state is stored in `mmaplist`.

## Dependencies and Integration Points

This file uses Python 2 constructs and assumes it is run from the CrashMonkey repository layout where `code/tests/seq3write/base-j-lang`, `code/tests/seq3write/base.cpp`, and `workload_seq3.py` are reachable by relative path. Generated tests integrate with `workload_seq3.py`, the CrashMonkey C++ harness, and the Makefile's generated workload build rules if copied into a built test directory. Its j-lang commands overlap with `xfstestAdapter.py` translation semantics for `write`, `dwrite`, `mmapwrite`, `falloc`, `fsync`, and `fdatasync`.

## Risks and Edge Cases

- The script is Python 2 only and will fail directly under Python 3.
- Current file generation and bug matching are commented out in `doPermutation`, so the script may produce logs but no workloads.
- The final `mv j-lang* ...` can fail or move stale files unrelated to the current run.
- `elif option == 'overlap_unaligned_start' or ...` is always true for non-append options due to Python boolean semantics.
- `buildJlang` assumes `length_map[file]` exists for overlap/end/extend modes; that depends on the first command being append and on dependency insertion if generation is re-enabled.
- Direct I/O and mmap paths use fixed sizes and offsets; invalid alignment or insufficient file size would produce generated tests that fail before testing crash consistency.
- The one-file search space is useful for data-operation stress, but it misses cross-directory rename/link bugs represented in the shared oracle list.

## Test Signals

Signals include a log showing nonzero inspected workload counts, no accidental stale `j-lang*` movement, generated j-lang/C++ files if the commented block is intentionally enabled, successful `workload_seq3.py` translation, and generated tests that compile against the CrashMonkey harness. Runtime filesystem tests should verify append followed by unaligned fallocate, direct write overlap, mmapwrite plus deferred `msync`, and `fdatasync` versus `fsync` consistency expectations.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/ace/specific_generator_scripts/seq3writegenerator.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/ace/specific_generator_scripts/workload_seq1.py -->
# sources/test-tools/crashmonkey/ace/specific_generator_scripts/workload_seq1.py

## Purpose

`workload_seq1.py` translates a j-lang workload skeleton into a CrashMonkey C++ test by inserting generated C++ snippets into a copied base test file. It is the first sequence translator variant and supports a wide set of filesystem operations including open, mkdir, fallocate, sync range, write, direct write, mmap write, link, rename, xattr operations, truncate, checkpoint, and sync.

## Important APIs, Types, and Functions

- CLI from `build_parser`: `--base_file`, `--test_file`, `--target_path`, and `--output_name`.
- `create_dir` ensures the target directory exists.
- `updateSetupMap`, `updateRunMap`, `updateCheckMap`, and `updateDefineMap` maintain insertion offsets as generated lines are inserted into the C++ file.
- `insertDefine` declares and initializes path strings in setup, run, check, and private sections.
- `insertDeclare` inserts integer local declarations in the run section.
- Operation emitters include `insertFalloc`, `insertSyncRange`, `insertMkdir`, `insertOpenFile`, `insertMknodFile`, `insertOpenDir`, `insertRemoveFile`, `insertTruncateFile`, `insertClose`, `insertFsync`, `insertSync`, `insertLink`, `insertCheckpoint`, `insertRename`, `insertFsetxattr`, `insertRemovexattr`, and `insertWrite`.
- `insertFunctions` dispatches j-lang lines to the proper emitter based on the first token and writes the modified C++ file back to disk.
- `main` discovers insertion points in the base C++ file, copies the base to a generated target, then processes the j-lang file section by section.

## Control Flow

The translator validates that the j-lang file exists, creates the target path, computes `base_file` as `target_path + basename(base_file)`, scans that base file for `setup()`, `run(`, `check_test(`, and `private:` insertion anchors, copies it to `target_path + test_file + "_" + output_name + ".cpp"`, and walks the j-lang file. Lines starting with `#` switch the active destination method (`define`, `declare`, `setup`, or `run`); other lines are inserted according to the active method.

## State and Persistence Behavior

The only durable product is the generated C++ test file. The translator edits this file repeatedly with read/insert/write cycles. `redeclare_map` is a global process-local guard to avoid duplicate declarations of generated variables such as file descriptors, mmap pointers, and direct-I/O buffers. `index_map` and `new_index_map` track evolving insertion offsets and are critical for keeping generated code in the intended C++ sections.

## Dependencies and Integration Points

The generated C++ depends on CrashMonkey `cm_` wrapper methods (`CmOpen`, `CmClose`, `CmFsync`, `CmFdatasync`, `CmSync`, `CmCheckpoint`, `CmMmap`, `CmMsync`, `CmMunmap`), helper functions such as `WriteData`, and symbols such as `TEST_FILE_PERMS`. It also emits direct Linux/POSIX calls like `mkdir`, `mknod`, `truncate`, `fallocate`, `link`, `symlink`, `rename`, `fsetxattr`, `removexattr`, `posix_memalign`, and `pwrite`. The output is meant to be built by the CrashMonkey Makefile as a shared test object.

## Risks and Edge Cases

- Python 2 only: uses `print` statements and `xrange`.
- `base_file` is resolved inside `target_path`, while the copy from the source base is commented out. A pre-existing base file must already be present in the target directory.
- File and variable names are made by removing slashes, so collisions are possible for different paths that flatten to the same string.
- The insertion-offset accounting uses hard-coded line counts for generated snippets; any snippet edits can corrupt subsequent insertion points.
- `insertMknodFile` treats `mknod` as returning a file descriptor, but POSIX `mknod` returns 0 on success, which can make generated close/error logic semantically wrong.
- Direct write uses plain `open` rather than `cm_->CmOpen`, unlike later variants, so it may bypass CrashMonkey instrumentation.
- Mmap write always `msync`s and unmaps 4096 bytes, regardless of the generated length, which can under-test larger mappings.

## Test Signals

Good signals are a generated `.cpp` file with populated setup/run/check/private sections, successful compilation through the CrashMonkey Makefile, and runtime execution where checkpoint return values stop at the intended crash points. Specific tests should cover `syncrange`, `mmapwrite`, `dwrite`, repeated variable use without redeclaration, and j-lang files containing all supported `#` sections.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/ace/specific_generator_scripts/workload_seq1.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/ace/specific_generator_scripts/workload_seq2.py -->
# sources/test-tools/crashmonkey/ace/specific_generator_scripts/workload_seq2.py

## Purpose

`workload_seq2.py` is the second C++ workload translator for ACE j-lang. It retains most of `workload_seq1.py` but adjusts generated code for later sequence workloads: checkpoint return values are taken from the j-lang line, rename goes through `cm_->CmRename`, direct write goes through `cm_->CmOpen`, `rmdir` is supported, and generated output no longer appends `output_name` to the j-lang-derived filename.

## Important APIs, Types, and Functions

- CLI arguments mirror `workload_seq1.py`.
- Insertion-map helpers and `insertDefine`/`insertDeclare` are shared in purpose with seq1.
- Operation emitters cover fallocate, mkdir, open file/dir, mknod, remove/unlink, truncate, close, rmdir, fsync/fdatasync, sync, link/symlink, checkpoint, rename, xattr, write, direct write, mmap write, and no-op `none`.
- `insertCheckpoint` emits `return <line argument>` when the local checkpoint equals the requested checkpoint.
- `insertRename` emits `cm_->CmRename` rather than raw `rename`.
- `insertWrite` differentiates buffered `WriteData`, direct `pwrite` through an O_DIRECT/O_SYNC `cm_->CmOpen`, and mmap-based writes with offset-aware mapping/msync.
- `insertFunctions` is the central dispatcher.

## Control Flow

`main` validates input, creates the target directory, resolves the base file inside that target directory, scans anchor lines, copies the base file to `target_path + test_file + ".cpp"`, and processes the j-lang file. The j-lang `#` markers select the insertion area and each operation line is translated into C++ text inserted at the tracked anchor offset.

## State and Persistence Behavior

The translator persists one generated C++ file and mutates it in place for every inserted operation. `redeclare_map` prevents duplicate declarations for file descriptors, mmap pointers, and direct-write buffers. Checkpoint state is generated into the C++ runtime as `local_checkpoint`, and the return value at a checkpoint is controlled by the j-lang argument.

## Dependencies and Integration Points

This script is integrated with sequence generators such as `seq3nestedgenerator.py`, which shells out to `workload_seq2.py`. Generated C++ relies on CrashMonkey wrappers for open/close/fsync/fdatasync/sync/checkpoint/rename/mmap/msync/munmap, and on POSIX/Linux syscalls for fallocate, mkdir, mknod, truncate, xattr, direct I/O, and pwrite. It expects a `base.cpp` already staged under the target path.

## Risks and Edge Cases

- Python 2 only.
- `operation_map` is created but unused, indicating drift from an older permutation generator.
- Path flattening can collide.
- Insertion offsets are brittle and depend on exact snippet line counts.
- `insertMknodFile` still models `mknod` as a file descriptor.
- Direct and mmap generated code has fixed text buffers and manual close/unmap behavior; repeated writes to the same file can depend heavily on `redeclare_map` side effects.
- Output naming as `target_path + test_file + ".cpp"` can produce surprising nested/duplicated paths when `test_file` includes directories.

## Test Signals

Validation should include generator-to-translator smoke tests from `seq3nestedgenerator.py`, compilation of generated C++ tests, and runtime crash tests that verify `cm_->CmRename`, checkpoint return values, `rmdir`, direct write, and mmap paths are observed by CrashMonkey. A regression fixture comparing seq1 and seq2 output for the same j-lang can make intentional behavior differences explicit.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/ace/specific_generator_scripts/workload_seq2.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/ace/specific_generator_scripts/workload_seq3.py -->
# sources/test-tools/crashmonkey/ace/specific_generator_scripts/workload_seq3.py

## Purpose

`workload_seq3.py` is the third j-lang to C++ translator variant. It is close to `workload_seq2.py` but adds explicit j-lang support for separate `msync` and `munmap` operations, changes mmap write generation so mappings can stay live across operations, and emits a fixed 256 KiB mapping for mmap workloads. It supports workloads where mmap writes and later sync/unmap operations are distinct crash points.

## Important APIs, Types, and Functions

- CLI arguments mirror seq1/seq2.
- `insertMsync(contents, option, line, index_map, method)` emits `cm_->CmMsync(filep_<file> + offset, length, MS_SYNC)`.
- `insertMunmap(contents, option, line, index_map, method)` emits `cm_->CmMunmap(filep_<file>, 262144)`.
- `insertWrite` handles buffered write, direct write, and mmapwrite. For mmapwrite, it fallocates, maps 262144 bytes once per file, writes bytes into `filep_<file> + offset`, and leaves msync/munmap to explicit later lines.
- `insertFunctions` dispatches the expanded command set, including `msync` and `munmap`.
- `main` performs the same base scan, copy, and section-driven insertion process as seq2.

## Control Flow

The translation flow is unchanged from seq2 until operation dispatch. When a j-lang `mmapwrite` is encountered, the generated C++ writes into a shared mapping and does not immediately `msync` or unmap. Later `msync` and `munmap` j-lang lines can be placed at specific points in the run section and get their own generated snippets. This enables crash tests that distinguish dirty mapped data, msync persistence, and unmap behavior.

## State and Persistence Behavior

`redeclare_map` tracks mmap offsets and direct-I/O variables to avoid duplicate declarations. Because mmap state now persists across j-lang operations in the generated C++ file, `filep_<file>` becomes a generated runtime state variable whose lifetime is controlled by explicit `munmap` lines rather than by `mmapwrite` itself. The persistent output remains one generated `.cpp` file.

## Dependencies and Integration Points

The generated C++ depends on the same CrashMonkey wrapper APIs as seq2 plus explicit `CmMsync` and `CmMunmap` calls. It is the natural downstream translator for write-intensive sequence generators that model mmap persistence separately from the write operation. Generated tests integrate with the Makefile via the generated workload or sequence test shared-object rules.

## Risks and Edge Cases

- Python 2 only.
- The generated mmap declaration is embedded as one long string with limited newlines, which can make line-count updates and compiler diagnostics harder to reason about.
- Fixed 262144-byte mappings may be too large or too small for generated ranges if future generators expand offsets.
- `insertMunmap` always unmaps 262144 bytes and does not guard against repeated unmaps.
- As with seq2, generated filenames can be surprising when `test_file` includes directory prefixes.
- Offset-map declarations are keyed by `moffset_<file>`, but file pointer lifetime is keyed indirectly; malformed j-lang can emit `msync` before the first `mmapwrite`.

## Test Signals

Strong tests include j-lang fixtures with `mmapwrite`, `msync`, and `munmap` in different orders, generated C++ compilation, and CrashMonkey execution that verifies consistency changes only after `msync` where expected. Regression tests should verify direct writes still close/reopen with O_DIRECT/O_SYNC and that seq2-to-seq3 differences are intentional rather than insertion drift.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/ace/specific_generator_scripts/workload_seq3.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/ace/xfstestAdapter.py -->
# sources/test-tools/crashmonkey/ace/xfstestAdapter.py

## Purpose

`xfstestAdapter.py` converts ACE j-lang workloads into xfstests shell tests and matching `.out` files. It supports two j-lang formats: V1 sectioned files with setup/run commands and V2 concise single-command templates with argument option arrays. Its role is to let ACE-generated crash-consistency workloads run in xfstests/flakey infrastructure instead of only through the CrashMonkey C++ harness.

## Important APIs, Types, and Functions

- `FallocTranslate` maps ACE fallocate modes to `$XFS_IO_PROG` commands (`falloc`, `falloc -k`, `fzero`, `fzero -k`, `fpunch`).
- File constants (`FILE_ATTR_KEY`, `WRITE_VALUE`, `MMAPWRITE_VALUE`, `DWRITE_VALUE`) define stable data patterns and xattr names.
- `get_row_from_filename`, `translate_filename`, `parent`, and `is_file_or_dir` translate j-lang names through `common.JLANG_FILES` into `$SCRATCH_MNT/...` paths.
- `State` tracks `opened_files`, `synced_files`, and `data_synced_files`, preserving the invariant that metadata-synced files are data-synced and data-synced files are opened/known.
- `translate_*` functions map individual j-lang operations to shell snippets and update `State`.
- `translate_functions` dispatches V1 command lines, paying attention to prefix ordering (`opendir` before `open`).
- `build_test_v1` translates a sectioned j-lang file into a linear flakey mount script plus `check_consistency`.
- `function_name_from_commands`, `build_command_dependencies`, `build_template_function`, `build_array_lines`, `build_for_loops`, and `add_sync_check_consistency` support concise V2 templated tests.
- `build_test_v2` emits a parameterized shell function and nested option loops.
- `main` selects V1 or V2 based on the first line containing `J2-Lang`, validates test number, creates the output directory, and builds the test.

## Control Flow

For V1, the adapter finds `base_xfstest.sh`, replaces template parameters, reads setup/run j-lang commands, starts with `_mount_flakey`, translates each command while updating consistency state, appends a `check_consistency` command for the currently synced file set, appends `clean_dir`, and writes `<test_number>` plus `<test_number>.out`.

For V2, it finds `base_xfstest_concise.sh`, parses option declarations and exactly one command, builds setup/dependency commands for that command, adds either `do_fsync_check` or a direct `check_consistency`, emits a shell function, emits sorted option arrays with translated file paths, and emits nested loops over all options and fsync targets.

## State and Persistence Behavior

The persistent outputs are two xfstests files under the target path: the executable test body and a `.out` file containing the expected quiet output. `State` is transient but determines the final `check_consistency` arguments for V1. Rename and remove operations deliberately mutate synced/opened sets so the final consistency oracle reflects the crash-persistence model rather than just command execution.

## Dependencies and Integration Points

The adapter depends on `common.JLANG_FILES`, xfstests helpers (`_mount_flakey`, `_pwrite_byte`, `_dwrite_byte`, `_mwrite_byte_and_msync`, `check_consistency`, `clean_dir`, `ensure_file_size_one_block`, `translate_range`, `do_falloc`, `do_fsync_check`), `$XFS_IO_PROG`, `attr`, and the `rename` command. It uses base templates from `../code/tests/ace-base` or the current ACE directory. Generated scripts are intended to be copied into an xfstests suite directory under a filesystem group such as `generic`, `ext4`, `btrfs`, `xfs`, or `f2fs`.

## Risks and Edge Cases

- `is_dir` computes a comparison but does not return it.
- `find_basefile` has an unreachable `print` after `return`.
- `translate_filename` assumes `get_row_from_filename` returns a row; unknown names raise `TypeError`.
- V2 asserts exactly one command, so multi-command concise workloads are unsupported.
- V2 rename dependency uses `create_file(parts[1])` even if the source is a directory option.
- Shell emission is mostly string formatting without quoting; unusual paths or options can break scripts, though ACE's synthetic names are constrained.
- `State.rename_file` has special handling for directory renames only for hard-coded dirs `A`, `B`, and `AC` and children `foo`, `bar`.

## Test Signals

Signals include generated executable and `.out` files, successful xfstests dry runs, V1 fixtures covering every `translate_*` function, V2 fixtures covering each command type and fsync loop generation, and consistency-command assertions for operations that only sync data (`fdatasync`) versus metadata (`fsync`/`sync`). Unknown file names should be tested as failures because translation depends on `JLANG_FILES`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/ace/xfstestAdapter.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/Makefile -->
# sources/test-tools/crashmonkey/code/Makefile

## Purpose

This Makefile builds the CrashMonkey kernel modules, C++ harness, user tools, test shared objects, generated ACE tests, sequence tests, and permuter plugins into `sources/test-tools/crashmonkey/build`. It also adapts some build flags and test inclusion rules to the running kernel version.

## Important APIs, Targets, and Variables

- `KERNEL_VERSION`, `KERNEL_MAJ`, and `KERNEL_MIN` derive version gates from `uname -r`.
- `MODULES = cow_brd disk_wrapper` and `obj-m` feed kbuild.
- `BUILD_DIR = $(CURDIR)/../build` isolates build products outside the source directory.
- `XATTR_DEF_FLAG` selects `-DNEW_XATTR_INC` for kernels 4.15 and newer.
- `FALLOC_ZERO_RANGE_TESTS` and `FALLOC_EXCLUDE` skip zero-range fallocate tests on kernels older than 3.15.
- `DELAY_DEFINE` selects harness timing macros (`THREE_THIRTEEN`, `FOUR_FOUR`, `FOUR_FIFTEEN`, `FOUR_SIXTEEN`, or `TWO_SEC`).
- High-level targets: `all`, `modules`, `c_harness`, `user_tools`, `tests`, `seq1`, `gentests`, `permuters`, and `clean`.
- Static pattern rules build generic_042 tests, seq1 generated tests, generated workloads, normal tests, permuter `.so` files, utility objects, and user tools.

## Control Flow

`all` builds kernel modules first, then the C++ harness, user tools, tests, seq1 workloads, and permuters. `modules` creates a build Makefile placeholder and delegates to the kernel build directory with `M=$(BUILD_DIR) src=$(CURDIR) modules`. C++ targets compile objects into mirrored build subdirectories and link tests as shared objects with `-shared -fPIC`. User tools link standalone executables against action and socket communication objects. `clean` delegates module cleanup to kbuild and removes selected testing binaries.

## State and Persistence Behavior

All normal build artifacts persist under `../build`: kernel module outputs, object files, shared-object tests, permuter plugins, user tool binaries, and `c_harness`. The source tree is read for tests via wildcard expansions, so generated `.cpp` files under `code/tests/seq1` or `code/tests/generated_workloads` automatically enter the build unless excluded.

## Dependencies and Integration Points

The Makefile depends on kernel headers at `/lib/modules/$(uname -r)/build`, GCC/G++, Linux kbuild, C++11, `dl`, and the CrashMonkey source layout. It consumes generated tests produced by ACE workload translators and builds them against `BaseTestCase`, `workload`, `actions`, `wrapper`, `DiskMod`, socket communication utilities, and result classes. Kernel module compilation consumes `cow_brd.c`, `disk_wrapper.c`, `bio_alias.h`, and ioctl headers.

## Risks and Edge Cases

- Kernel version gates are narrow and manually curated; unsupported versions can fail either in `bio_alias.h` or during kbuild.
- `DELAY_DEFINE` defaults to `TWO_SEC` when `CM` is unset, which can hide timing assumptions in harness behavior.
- Several object pattern rules use broad `%.cpp` prerequisites, so current-directory assumptions matter.
- Generated source files can unexpectedly enter `seq1` or `gentests` targets due to wildcard discovery.
- `clean` only removes module build outputs and a few binaries; many C++ build artifacts under `../build` may remain.
- Xattr include flags are based on running kernel version, not necessarily the target headers if cross-building.

## Test Signals

Core signals are successful `make modules`, `make c_harness`, `make user_tools`, `make tests`, `make seq1`, and `make permuters` on supported kernel versions. Generated workload signals include a new `.cpp` file appearing in the expected test directory and a corresponding `.so` under `../build`. Negative build tests should cover old kernels for fallocate-zero exclusion and unsupported kernels for expected `bio_alias.h` failure.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/bio_alias.h -->
# sources/test-tools/crashmonkey/code/bio_alias.h

## Purpose

`bio_alias.h` is a kernel-version compatibility shim for CrashMonkey block-device modules. It hides differences in Linux `struct bio` fields, endio APIs, discard flags, and write-operation tests behind stable macros used by `cow_brd.c` and likely `disk_wrapper.c`.

## Important APIs and Macros

- `BI_RW` maps to `bi_rw` on older kernels and `bi_opf` on newer kernels.
- `BI_DISK` maps to either `bi_bdev->bd_disk` or `bi_disk`.
- `BI_SIZE` maps to `bi_size` for older 3.12/3.13 kernels and `bi_iter.bi_size` for later kernels.
- `BI_SECTOR` maps to `bi_sector` or `bi_iter.bi_sector`.
- `BIO_ENDIO(bio, err)` abstracts the signature change from `bio_endio(bio, err)` to `bio_endio(bio)`.
- `BIO_IO_ERR(bio, err)` abstracts error completion between `bio_endio(bio, err)` and `bio_io_error(bio)`.
- `BIO_DISCARD_FLAG` maps from `REQ_DISCARD` to `REQ_OP_DISCARD`.
- `BIO_IS_WRITE(bio)` maps from `bio_rw(bio) & REQ_WRITE` to `op_is_write(bio_op(bio))`.

## Control Flow

The file is entirely preprocessor control flow. It selects one macro block based on `LINUX_VERSION_CODE` ranges: 3.12-3.13, 3.16 or 4.1, 4.4, 4.8-4.9, selected 4.14-4.16 and 5.5/5.6 patch ranges. Any other kernel version hits a compile-time `#error`.

## State and Persistence Behavior

There is no runtime state. Persistence is compile-time ABI selection: the chosen macro expansion is compiled into kernel modules and determines how they access bios and signal completion.

## Dependencies and Integration Points

The header depends on `<linux/version.h>` and is included by `cow_brd.c`. Its macros are used in `brd_make_request` for disk lookup, sector/size access, write/discard checks, and bio completion. The Makefile's kernel-version logic complements this header but does not replace its compile-time checks.

## Risks and Edge Cases

- Supported kernel ranges are sparse. Kernels outside tested patch windows fail to compile even if their APIs are compatible.
- Some ranges are patch-specific, especially 5.5.0-5.5.2 and 5.6.0-5.6.6, which suggests local compatibility fixes rather than general modern-kernel support.
- Macro abstraction can hide semantic differences, especially discard operation checks before and after `REQ_OP_*`.
- Error completion behavior differs by kernel generation; using the wrong branch can silently report successful I/O or double-complete a bio.

## Test Signals

The primary signal is successful module compilation against each supported kernel range. Runtime signals include correct write/read/discard behavior through `cow_brd`, no bio completion warnings, and correct rejection of unsupported kernels through the explicit `#error`. Compile tests should include at least one old `bi_rw` kernel and one newer `bi_opf`/`bi_disk` kernel.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/bio_alias.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/code/cow_brd.c -->
# sources/test-tools/crashmonkey/code/cow_brd.c

## Purpose

`cow_brd.c` implements CrashMonkey's copy-on-write RAM block device kernel module. It is derived from Linux brd/ramdisk code and adds snapshot devices: base `cow_ramN` disks can be made read-only for snapshotting, while `cow_ram_snapshotS_N` devices read unchanged pages from their parent and store modified pages locally. This supports crash-consistency experiments where tests run against snapshots and can restore or wipe device state through ioctls.

## Important APIs, Types, and Functions

- Constants: `SECTOR_SHIFT`, `PAGE_SECTORS_SHIFT`, `PAGE_SECTORS`, `DEFAULT_COW_RD_SIZE`, and `DEVICE_NAME`.
- `struct brd_device` holds the device number, parent pointer, writable/snapshot flags, request queue, gendisk, list node, spinlock, and radix-tree page store.
- Page-store functions: `brd_lookup_page`, `brd_insert_page`, `brd_free_page`, `brd_zero_page`, and `brd_free_pages`.
- Data movement functions: `copy_to_brd_setup`, `discard_from_brd`, `copy_to_brd`, `copy_from_brd`, and `brd_do_bvec`.
- Request path: `brd_make_request` validates bounds/writability, handles discard, iterates bio segments, and completes or errors the bio using `bio_alias.h`.
- Optional XIP path: `brd_direct_access`.
- Control path: `brd_ioctl` handles `COW_BRD_SNAPSHOT`, `COW_BRD_UNSNAPSHOT`, `COW_BRD_RESTORE_SNAPSHOT`, and `COW_BRD_WIPE`.
- Module/device lifecycle: module params (`num_disks`, `num_snapshots`, `disk_size`, `max_part`), `brd_alloc`, `brd_free`, `brd_init_one`, `brd_del_one`, `brd_probe`, `brd_init`, and `brd_exit`.

## Control Flow

On module load, `brd_init` registers a block major, validates partition/minor limits, allocates `num_disks * (1 + num_snapshots)` devices, links snapshot devices to their parent base disk by `i % num_disks`, adds disks, registers the block region, and logs the number of disks and snapshots. `brd_alloc` creates the queue, installs `brd_make_request`, configures discard capabilities, allocates a gendisk, names it as base or snapshot, and sets capacity.

For I/O, `brd_make_request` obtains the target `brd_device` from the bio disk, rejects out-of-range requests, rejects writes/discards to non-writable base devices after snapshot activation, handles discard by zeroing pages, and otherwise iterates bio segments. `brd_do_bvec` inserts local pages before writes, maps pages with `kmap_atomic`, copies data into or out of the radix-tree store, and unmaps. Reads first consult the device's local pages, then the parent snapshot source, then return zeroes.

For snapshot control, ioctls on base devices toggle `is_writable` or wipe base pages. Ioctls on snapshot devices can restore the snapshot by freeing its local changed pages. Snapshot devices cannot be snapshotted/unsnapshotted/wiped as bases.

## State and Persistence Behavior

The device contents are volatile RAM pages stored in each device's `brd_pages` radix tree. Base devices persist data only until module unload or wipe. Snapshot devices persist only their changed pages; unchanged reads are served from the parent base disk. `COW_BRD_RESTORE_SNAPSHOT` discards a snapshot's local pages so it again reflects the parent. `COW_BRD_SNAPSHOT` makes the base read-only to preserve parent state while snapshots are active, and `COW_BRD_UNSNAPSHOT` makes it writable again.

## Dependencies and Integration Points

The module depends on Linux block-layer headers, radix trees, gendisk/request-queue APIs, module parameters, and version-specific bio aliases. It includes `disk_wrapper_ioctl.h` for ioctl constants and is built as `cow_brd.ko` by the Makefile through kbuild. User-space CrashMonkey tools and harness code interact with the exposed block devices and ioctls to create, restore, and wipe crash-test disks.

## Risks and Edge Cases

- Kernel API support is limited by `bio_alias.h` and in-file version conditionals.
- The discard path zeroes only full pages while `n >= PAGE_SIZE`; partial discards are ignored.
- `copy_to_brd` and `copy_from_brd` use pointer arithmetic on `void *`, which is a GNU C extension.
- `brd_mutex` is defined but unused; synchronization relies on spinlocks for radix-tree mutation and assumptions about open device lifetime.
- `brd_insert_page` copies parent data after insertion without locking the parent page against concurrent changes beyond the broader test assumptions.
- `COW_BRD_WIPE` assumes snapshots are not active, but the module does not enforce that beyond rejecting the ioctl on snapshot devices.
- In `brd_init`, some early validation failures return without unregistering a previously registered block major.
- Device major aliasing uses `MODULE_ALIAS_BLOCKDEV_MAJOR(RAMDISK_MAJOR)` while `register_blkdev` may allocate a dynamic major if `major_num` starts at 0.

## Test Signals

Build signals are successful kbuild compilation of `cow_brd.ko` for supported kernels. Runtime signals include module load creating expected `/dev/cow_ram*` and `/dev/cow_ram_snapshot*` devices, successful read/write round trips, snapshot reads falling back to parent pages, writes to snapshots not mutating parents, base writes rejected while snapshotted, restore clearing snapshot-local changes, wipe clearing base pages, discard returning zeroes, and clean module unload freeing pages without leaks or block-layer warnings.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/code/cow_brd.c -->
