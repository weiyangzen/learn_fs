# Research: subset-b-009206

This grouped report covers the requested CrashMonkey ACE source files. Each file section is wrapped with the exact reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/ace/ace.py -->
# sources/test-tools/crashmonkey/ace/ace.py

## Purpose

`ace.py` is the main Python 3 entry point for Automatic Crash Explorer workload generation. It exhaustively enumerates filesystem operation skeletons of a requested sequence length, expands each skeleton into concrete file/path/range/options combinations, inserts persistence points (`fsync`, `fdatasync`, `sync`, or `none`), repairs preconditions by injecting setup operations, emits J-lang or J2-lang workload files, and invokes either the CrashMonkey C++ adapter or the xfstest adapter to produce runnable tests under `../code/tests/seq*`.

The file also embeds a catalog of expected bug-reproduction signatures in `expected_sequence` and `expected_sync_sequence`. These signatures are used by `isBugWorkload()` as a sanity signal that the generator's search space includes known crash-consistency bugs.

## Important APIs, Types, and Functions

The file is procedural and uses module-level globals rather than classes for generator state. `build_parser()` defines CLI options for sequence length, nested test namespace, demo mode, and test backend. `print_setup()` prints those parsed values.

`SiblingOf()`, `Parent()`, and `file_range()` encode the small synthetic namespace model used by ACE. They map logical J-lang names such as `foo`, `A/foo`, `B/bar`, `AC/foo`, and `test` to sibling and parent choices so persistence operations can be limited to relevant files and directories.

`buildTuple(command, expand_combinations=True)` is the operation-domain builder. It returns all legal parameter tuples for core operations such as `creat`, `mkdir`, `falloc`, `write`, `dwrite`, `mmapwrite`, `link`, `rename`, `unlink`, `remove`, `fsetxattr`, `removexattr`, `truncate`, `fsync`, and `fdatasync`. With `expand_combinations=False`, it returns parameter dimensions for the concise J2-lang path.

`buildCustomTuple(file_list)` builds per-position persistence sequences from the files touched by a workload. It ensures the last operation is followed by a real persistence point for the active sequence length, while allowing `none` before earlier operations. `isBugWorkload()` compares generated operations, parameters, and persistence choices against the known bug catalog and logs matches.

The dependency-injection layer is split between tuple constructors (`insertUnlink()`, `insertRmdir()`, `insertXattr()`, `insertOpen()`, `insertMkdir()`, `insertClose()`, `insertWrite()`) and checkers (`checkCreatDep()`, `checkDirDep()`, `checkParentExistsDep()`, `checkExistsDep()`, `checkClosed()`, `checkXattr()`, `checkFileLength()`). `satisfyDep()` is the central dispatcher that mutates `modified_sequence` and state maps for each operation.

`flatList()` normalizes nested tuple/list command records. `buildJlang()` converts dependency-expanded tuples into the older J-lang text format, including offsets, lengths, and checkpoint return values. `buildJ2lang()` emits the newer grouped J2-lang format for concise xfstests. `doPermutation()` is the full CrashMonkey/xfstest generation path, while `doPermutationV2()` is the concise xfstest-only path. `SlowBar` customizes progress display with the global workload count.

## Control Flow

`main()` opens a timestamped `*-bugWorkloadGen.log`, parses arguments, validates `--test-type`, mutates global operation domains for demo and nested modes, and builds `parameterList` for every operation in `OperationSet`. It then prepares output directories under `../code/tests/seq<num_ops>[_nested][_demo]`, copies `ace-base` templates, initializes persistence operation choices, and iterates `itertools.product(OperationSet, repeat=int(num_ops))`.

For normal CrashMonkey or xfstest generation, each operation skeleton is handed to `doPermutation()`. That function skips all-write length-3 skeletons, records the skeleton, computes the cartesian product of operation parameters, prunes length-3 parameter combinations that do not reuse files, computes the used-file set, chooses persistence combinations, then interleaves each core operation with its selected persistence point. Operations that are themselves persistence-producing (`fdatasync` and `mmapwrite`) skip an extra inserted sync and receive checkpoint return metadata directly.

After skeleton, parameter, and persistence enumeration, `doPermutation()` performs dependency repair. It starts with `open_dir_map = {'test': 0}` and empty file length/open maps, walks the current sequence through `satisfyDep()`, inserts required parent-directory creation, opens, closes, unlinks, writes, xattr setup, and directory cleanup, then closes any remaining open handles. The repaired sequence is serialized to a temporary `j-lang<global_count>` file copied from `base-j-lang`, and then converted by `cmAdapter.py` or `xfstestAdapter.py` through `subprocess.call()`.

For `--test-type xfstest-concise`, `main()` routes skeletons to `doPermutationV2()`. That path currently intends to support only sequence length 1, builds J2-lang from unexpanded parameter dimensions, and invokes `xfstestAdapter.py` with a zero-padded test number.

## State and Persistence Behavior

The generator relies heavily on mutable module globals: `global_count`, `parameterList`, `SyncSet`, `num_ops`, `nested`, `demo`, `syncPermutations`, `count`, `permutations`, `log_file_handle`, and `count_param`. Per-workload transient state is held in `open_file_map`, `open_dir_map`, and `file_length_map`. These maps model logical existence/open state and byte lengths so generated workloads have satisfiable preconditions and deterministic offsets.

Persistent side effects are substantial. The script writes timestamped logs in the current working directory, creates or updates `../code/tests/seq*` directories, copies base J-lang and C++ skeletons, writes many temporary `j-lang*` or `j2-lang*` files, invokes adapter scripts that create `.cpp` tests, and finally moves generated high-level language files into `../code/tests/seq*/j-lang-files/`. It does not maintain a database or durable manifest beyond generated files and logs.

## Dependencies and Integration Points

`ace.py` imports operation domains from `common.py`, uses `progress.bar.FillingCirclesBar` for status, uses `shutil.copyfile` for template copying, and shells out to `cmAdapter.py` and `xfstestAdapter.py`. It assumes a specific directory layout relative to the ACE working directory: `../code/tests/ace-base/base-j-lang`, `../code/tests/ace-base/base.cpp`, and destination directories under `../code/tests/seq*`.

The integration contract with adapters is textual J-lang/J2-lang. `buildJlang()` emits commands such as `open`, `opendir`, `mkdir`, `mknod`, `falloc`, `write`, `dwrite`, `mmapwrite`, `link`, `rename`, `unlink`, `remove`, `fsetxattr`, `removexattr`, `truncate`, `fsync`, `fdatasync`, `sync`, and `checkpoint`. The CrashMonkey adapter expects checkpoint lines to contain a return value that identifies the final crash point.

## Risks and Test Signals

The boolean parsing is fragile: `parsed_args.nested == ('True' or 'true')` and the demo equivalent only compare against `"True"`, not `"true"`. `SecondFileOptions` and `SecondDirOptions` are extended with `AC/bar` and `AC` outside the `if nested` block, so non-nested runs still receive some nested targets. Several option checks use expressions such as `elif option == 'overlap' or 'overlap_aligned' or 'overlap_unaligned'`, which are always true after the first false comparison. `doPermutationV2()` checks `len(num_ops) != 1`, which tests the length of the string instead of the numeric sequence length. Shell command strings are built with concatenation and `shell=True`; current arguments are internally generated or CLI-provided paths, so injection and quoting risks exist.

State is global and not concurrency-safe. The commented multiprocessing code correctly notes that enabling parallel generation would collide on `global_count` and output file names. The generator also mutates imported lists from `common.py`, so repeated runs inside the same interpreter would be unsafe.

Useful test signals include running short demo generations, verifying known bug matches printed by `isBugWorkload()`, checking that generated `j-lang-files/` counts match logged `global_count`, and compiling or running the generated CrashMonkey/xfstest outputs. Unit tests should isolate `buildTuple()`, `buildCustomTuple()`, `Parent()`, `SiblingOf()`, `buildJlang()`, and dependency checkers for representative file, directory, xattr, rename, and direct-write workloads.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/ace/ace.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/ace/cmAdapter.py -->
# sources/test-tools/crashmonkey/ace/cmAdapter.py

## Purpose

`cmAdapter.py` converts ACE J-lang workload descriptions into CrashMonkey-style C++ test files. It starts from a base C++ test skeleton, finds insertion points for `setup`, `run`, `check_test`, and private declarations, then inserts generated C++ snippets for each J-lang command. The generated file becomes a runnable CrashMonkey test that executes filesystem operations through `cm_` wrapper methods and returns checkpoint-specific values.

## Important APIs, Types, and Functions

The CLI is defined by `build_parser()`, accepting `--base_file`, `--test_file`, `--target_path`, and `--output_name`. `create_dir()` ensures the target directory exists. `create_dict()` returns a small operation count map, but it is only initialized in `main()` and not otherwise used.

Insertion offset management is done by `updateSetupMap()`, `updateRunMap()`, `updateCheckMap()`, and `updateDefineMap()`. These functions keep later section indices aligned after lines are inserted into earlier C++ sections.

`insertDeclare()` adds integer declarations near the run section. `insertDefine()` declares and initializes path variables in setup, run, check, and private sections. It maps J-lang logical names to C++ identifier fragments by removing slashes, and maps the special `test` name to `mnt_dir_`.

Operation-specific code emitters include `insertFalloc()`, `insertMkdir()`, `insertOpenFile()`, `insertMknodFile()`, `insertOpenDir()`, `insertRemoveFile()`, `insertTruncateFile()`, `insertClose()`, `insertRmdir()`, `insertFsync()`, `insertSync()`, `insertLink()`, `insertCheckpoint()`, `insertRename()`, `insertFsetxattr()`, `insertRemovexattr()`, and `insertWrite()`. `insertWrite()` handles three materially different write modes: normal `WriteData`, `mmapwrite` through CrashMonkey mmap/msync wrappers, and direct `pwrite` after reopening with `O_DIRECT|O_SYNC`.

`insertFunctions()` is the dispatch function. It reads a J-lang command line, chooses the correct emitter, updates insertion indices, and writes the modified C++ file back. `main()` wires the parser, skeleton copying, insertion-point discovery, J-lang region parsing, and final file generation.

## Control Flow

`main()` validates that the J-lang test file exists, creates the target directory, derives a local `base_file` path inside the target, and reads that base file to discover the line indices of `setup()`, `run(`, `check_test(`, and `private:`. It then copies the base file to a new output path derived from `test_file + ".cpp"` under the target directory.

The J-lang file is processed line by line. Blank lines are skipped. Lines beginning with `#` switch the active destination method, using the last token as the region name. In `define` and `declare` sections, `insertDefine()` and `insertDeclare()` run directly. In `setup` and `run`, `insertFunctions()` dispatches the operation-specific insertion routine.

Each insertion routine reads the current generated C++ file into memory, inserts a formatted C++ snippet at the tracked index for the active method, updates all affected indices, seeks back to the beginning, and rewrites the file. For operations with checkpoints, `insertCheckpoint()` inserts `cm_->CmCheckpoint()`, increments `local_checkpoint`, compares it against the runtime `checkpoint`, and returns the J-lang-provided value when the target checkpoint is reached.

## State and Persistence Behavior

The adapter persists exactly one generated C++ file per invocation, plus any existing copied base file in the target directory. Its principal mutable state is `index_map`, a dictionary of insertion offsets, and the module-level `redeclare_map`, which suppresses repeated `int fd_*`, `filep_*`, and write buffer declarations. `redeclare_map` is never reset inside `main()`, which is harmless for one-process one-file CLI invocations but unsafe if this module is reused in-process for multiple files.

The file uses repeated read-modify-write cycles for every inserted J-lang line. This is simple but expensive for large workloads and exposes partially rewritten output if the process fails mid-generation. There is no atomic temp-file replacement.

## Dependencies and Integration Points

The adapter depends on the base C++ skeleton having recognizable function signatures and a `private:` section in the expected textual format. Generated snippets assume CrashMonkey helpers such as `cm_->CmOpen`, `cm_->CmClose`, `cm_->CmFsync`, `cm_->CmFdatasync`, `cm_->CmSync`, `cm_->CmCheckpoint`, `cm_->CmRename`, `cm_->CmMmap`, `cm_->CmMsync`, and `cm_->CmMunmap`, plus helper functions or system calls such as `WriteData`, `fallocate`, `mkdir`, `mknod`, `remove`, `unlink`, `rmdir`, `truncate`, `link`, `symlink`, `fsetxattr`, `removexattr`, `posix_memalign`, `memcpy`, and `pwrite`.

The upstream integration point is ACE J-lang syntax. Commands emitted by `ace.py` or the legacy sequence generators are consumed verbatim by splitting on spaces. That makes spacing, token order, and option formatting part of the interface.

## Risks and Test Signals

Parsing is fragile because it relies on `line.split(' ')` and exact token positions. Multiple spaces, tabs, or C++ skeleton signature changes can break insertion-point discovery or command parsing. Path-derived C++ identifiers are formed by concatenating path components, so name collisions are possible for different logical names that reduce to the same slashless string.

The base file copy behavior is easy to misread: the code computes `base_file` under `target_path`, but the `copyfile(base_test, base_file)` call is commented out. This means the target base skeleton must already exist before adapter execution, which `ace.py` satisfies by copying `base.cpp` once before invoking the adapter. Running `cmAdapter.py` directly with only `--base_file` may fail if the corresponding basename is absent in `--target_path`.

Generated direct-write and mmap snippets allocate or map resources but do not always free allocated direct I/O buffers, and error paths may close invalid descriptors. `insertMknodFile()` stores the return value of `mknod()` in an `fd_*` variable even though `mknod()` returns status, not an open descriptor. These may be intentional enough for generated tests but are risk points for runtime correctness.

Good validation signals include feeding minimal J-lang files for each supported command, compiling the generated C++, checking checkpoint return behavior, and diffing generated snippets against expected fixtures. Adapter tests should include paths with directories, repeated writes to the same file to exercise `redeclare_map`, and skeletons with the expected section markers.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/ace/cmAdapter.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/ace/common.py -->
# sources/test-tools/crashmonkey/ace/common.py

## Purpose

`common.py` centralizes the small filesystem namespace and operation-domain constants used by the Python 3 ACE generator. It provides the legal parameter values for filesystem operations and the canonical mapping from J-lang logical file names to shell/path names and parent/type metadata.

## Important APIs, Types, and Values

The module exports lists rather than functions or classes. `FallocOptions` enumerates Linux fallocate modes used by generated workloads, including zero-range, zero-range keep-size, punch-hole keep-size, keep-size, and `0`. `FsyncOptions` contains `fsync`, `fdatasync`, and `sync`.

`FileOptions`, `SecondFileOptions`, `DirOptions`, `TestDirOptions`, and `SecondDirOptions` define the default small namespace. The default file set uses `foo` and `A/foo` as first-file options, `bar` and `A/bar` as second-file options, `A` and `B` as subdirectories, and `test` as the root mount/test directory. The split between first and second file options is used by generators to reduce symmetric duplicate workloads.

`WriteOptions`, `dWriteOptions`, and `TruncateOptions` define logical write shapes. Normal writes can append, overlap with an unaligned start, or overlap and extend. Direct writes can append or overlap at the start. Truncates can be aligned or unaligned.

`OperationSet` is the default core-operation set for `ace.py`: `creat`, `mkdir`, `falloc`, `write`, `dwrite`, `mmapwrite`, `link`, `unlink`, `remove`, `rename`, `fsetxattr`, `removexattr`, and `truncate`.

`JLANG_FILES` maps J-lang logical names to bash/runtime paths, parent logical names, and coarse file type. It includes root/test entries, `A`, nested `AC` as `A/C`, `B`, base files `foo` and `bar`, directory-scoped files such as `Afoo` and `Bbar`, and nested files such as `ACfoo`.

## Control Flow

There is no runtime control flow in this module. It is imported by `ace.py`, and the imported lists are consumed by `buildTuple()`, dependency checks, parent/sibling logic, and J-lang emission. Some values are mutated by `ace.py` at runtime for demo and nested modes, so these constants act as process-local defaults rather than immutable configuration.

## State and Persistence Behavior

All state is module-level in-memory Python list data. There is no file I/O, no persistence, and no initialization function. Because importers may mutate these lists directly, repeated generator invocations in the same Python process can observe prior modifications unless the interpreter is restarted or the lists are copied defensively.

## Dependencies and Integration Points

The module has no imports. Its main integration points are `ace.py` and any other generator that wants to share the Python 3 operation domains. `JLANG_FILES` documents an intended bridge between arbitrary J-lang names and actual filesystem paths, although `ace.py` also contains separate hard-coded `Parent()` and `SiblingOf()` logic that must remain consistent with these constants.

## Risks and Test Signals

The largest risk is domain drift. `common.py`, `ace.py`, and the older sequence generator scripts duplicate overlapping operation and namespace definitions. If one list gains a new logical path or operation without matching updates to `Parent()`, `SiblingOf()`, `buildJlang()`, and adapter support, generated workloads can become invalid or silently omit cases.

The `JLANG_FILES` entry for `"test"` has type `"file"` even though comments and generator logic treat `test` as the root directory. If code begins relying on this type field, that mismatch may matter. `FallocOptions` mixes strings and integer `0`, which `buildJlang()` stringifies correctly today but can surprise callers that expect uniform strings.

Good tests are small consistency checks: every file option should have a parent mapping, every sibling should exist in one of the option sets, every operation in `OperationSet` should be supported by `ace.py` and `cmAdapter.py`, and every `JLANG_FILES` logical name should map without collisions after slash removal.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/ace/common.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/ace/specific_generator_scripts/seq1generator.py -->
# sources/test-tools/crashmonkey/ace/specific_generator_scripts/seq1generator.py

## Purpose

`seq1generator.py` is a legacy Python 2 generator specialized for sequence length 1 workloads. It predates the consolidated Python 3 `ace.py` path and duplicates much of the same search-space, dependency-repair, J-lang emission, and CrashMonkey adapter invocation logic. Its output target is `code/tests/seq1/`.

## Important APIs, Types, and Functions

The file defines operation-domain globals inline: fallocate modes, sync operations, first/second file sets, directories, write/direct-write/sync-range/truncate options, and an `OperationSet` that includes `creat`, `mkdir`, `mknod`, `falloc`, `write`, `dwrite`, `link`, `unlink`, `remove`, `rename`, `symlink`, `removexattr`, `fdatasync`, and `fsetxattr`.

`expected_sequence` and `expected_sync_sequence` encode 13 known bug signatures. `isBugWorkload()` logs when a generated sequence matches one of those signatures. `SiblingOf()`, `Parent()`, and `file_range()` implement the logical namespace for `foo`, `bar`, `A/foo`, `A/bar`, `A`, `B`, and `test`.

`buildTuple()` expands one operation into all concrete parameter choices. It supports legacy-only `syncrange` as well as `mmapwrite`, even though those are not currently active in `OperationSet`. `buildCustomTuple()` builds persistence choices for the used file range, but unlike the newer `ace.py` it does not include `none` in the default sync set for sequence length 1.

The dependency layer mirrors ACE: tuple insertion helpers create synthetic operations, `check*` functions enforce existence/open/length/xattr/parent preconditions, `satisfyDep()` dispatches by command, and `buildJlang()` serializes tuple commands to J-lang. `doPermutation()` handles one operation skeleton through parameter expansion, sync insertion, dependency repair, file writing, adapter execution, and bug matching.

## Control Flow

`main()` opens a timestamped log, parses `--sequence_len`, prints all known bug signatures, populates `parameterList`, initializes `SyncSet`, and iterates `itertools.product(OperationSet, repeat=int(num_ops))`. Although the script is named for seq1, it still accepts arbitrary `--sequence_len`; its output paths and workload adapter remain hard-coded to seq1.

`doPermutation()` receives a tuple such as `('write',)`, gets parameter combinations for the operation, computes used files from the selected parameters, expands persistence choices over `file_range(usedFiles)`, and special-cases `fdatasync`, `mmapwrite`, and `syncrange` so they do not receive an extra persistence command. It builds an initial sequence `[core_op_with_params, sync_choice]`, then runs dependency repair over that sequence.

The repaired sequence is appended to a copied `code/tests/seq1/base-j-lang` template. Each generated J-lang file is converted by calling `python workload_seq1.py -b code/tests/seq1/base.cpp -t <j-lang> -p code/tests/seq1/ -o <global_count>`. At the end, all generated `j-lang*` files are moved into `code/tests/seq1/j-lang-files/`.

## State and Persistence Behavior

The script uses Python 2 globals for counters, parameter lists, persistence sets, and logging. Per-workload state is maintained in maps for open files, open directories, and file lengths. The script writes a timestamped log, many `j-lang*` files in the working directory, generated C++ tests under `code/tests/seq1/`, and finally moves high-level language files into the seq1 `j-lang-files` directory.

## Dependencies and Integration Points

This script requires Python 2 syntax and modules, including backtick repr syntax, `print` statements, `xrange`, `basestring`, and `from string import maketrans`. It shells out to `workload_seq1.py`, which is the seq1-specific adapter wrapper in the same folder. It assumes `code/tests/seq1/base-j-lang`, `code/tests/seq1/base.cpp`, and `code/tests/seq1/j-lang-files/` exist relative to the current working directory.

## Risks and Test Signals

The script is not Python 3 compatible. Its command generation is hard-coded to seq1 paths even when `--sequence_len` is not 1. Several conditions are logically faulty, including `elif option == 'overlap' or 'overlap_aligned' or 'overlap_unaligned'`, which always triggers the file-length branch for non-append writes. The `remove`/`unlink` dependency path uses `current_sequence[pos][1][0]` in this file, which can reduce a string filename to its first character for some sequence shapes.

Like `ace.py`, it uses global counters and would collide if multiprocessing were enabled. It also builds shell commands with concatenated paths and `shell=True`. Good validation signals are a very small seq1 generation run, successful conversion through `workload_seq1.py`, generated C++ compilation, expected known-bug match output, and fixture tests for `buildJlang()` offsets for append, aligned overlap, unaligned overlap, truncation, sync-range, and mmapwrite.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/ace/specific_generator_scripts/seq1generator.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/ace/specific_generator_scripts/seq2generator.py -->
# sources/test-tools/crashmonkey/ace/specific_generator_scripts/seq2generator.py

## Purpose

`seq2generator.py` is a legacy Python 2 workload generator specialized around length-2 ACE searches. It enumerates pairs of filesystem operations, fills in concrete parameters, inserts persistence choices after each operation, injects dependency operations, emits J-lang files, and calls a seq2 adapter wrapper to create CrashMonkey tests under `code/tests/seq2/`.

## Important APIs, Types, and Functions

The file duplicates most constants and functions from the later `ace.py`, but with seq2-specific defaults. `OperationSet` includes `creat`, `mkdir`, `falloc`, `write`, `dwrite`, `link`, `unlink`, `remove`, `rename`, `removexattr`, `fdatasync`, `fsetxattr`, `truncate`, and `mmapwrite`; `symlink` and `mknod` are intentionally removed in this version. The expected bug catalog is extended with comments through 29 known or desired sequences, while concrete `expected_sequence` entries cover the first 13 signatures.

`buildTuple()` returns parameter combinations for each operation. For `link`, `symlink`, and `rename`, seq2 allows first operands from both first and second file options, reducing missed cases where the second operation reuses a previously created target. `buildCustomTuple()` returns persistence sequences tailored to sequence length: for length 2 it allows `fsync`, `sync`, or `none` after the first operation, and only `fsync` or `sync` after the last operation.

The state-repair helpers (`insertUnlink()`, `insertRmdir()`, `insertXattr()`, `insertOpen()`, `insertMkdir()`, `insertClose()`, `insertWrite()`, `checkCreatDep()`, `checkDirDep()`, `checkParentExistsDep()`, `checkExistsDep()`, `checkClosed()`, `checkXattr()`, `checkFileLength()`, and `satisfyDep()`) model file existence, directory existence, open handles, and minimum file length. `flatList()` and `buildJlang()` turn the repaired tuple sequence into J-lang text with checkpoint return values.

## Control Flow

`main()` opens a log, parses `--sequence_len`, prints known bug definitions, populates `parameterList`, initializes `SyncSet`, and iterates all `OperationSet ** num_ops` operation skeletons. Although intended for seq2, it accepts any sequence length supported by `buildCustomTuple()`.

`doPermutation()` records each skeleton, builds the cartesian product of parameter choices, flattens the current parameter tuple to compute `usedFiles`, and chooses persistence targets from `file_range(usedFiles)`. For each persistence combination, it interleaves core operations with persistence operations. `fdatasync` and `mmapwrite` are treated as self-persisting and receive checkpoint metadata directly instead of a following sync operation.

The initial sequence is dependency-expanded using `satisfyDep()`, with `test` preloaded as an existing closed directory. Remaining open files and directories are closed. The script copies `code/tests/seq2/base-j-lang`, appends a `# run` section, writes the repaired J-lang commands, and invokes `python workload_seq2.py -b code/tests/seq2/base.cpp -t <j-lang> -p code/tests/seq2/ -o <global_count>`. At completion it moves `j-lang*` into `code/tests/seq2/j-lang-files/`.

## State and Persistence Behavior

State is held in Python 2 module globals (`global_count`, `parameterList`, `SyncSet`, `num_ops`, `syncPermutations`, `count`, `permutations`, `log_file_handle`, `count_param`) and transient per-workload maps (`open_file_map`, `open_dir_map`, `file_length_map`). Persistent outputs include the timestamped log, generated J-lang files, generated C++ tests, and the final moved J-lang archive. There is no manifest or atomic output handling.

## Dependencies and Integration Points

The script depends on Python 2 and the seq2-specific wrapper `workload_seq2.py`. It assumes the repository is run from a directory where `code/tests/seq2/base-j-lang`, `code/tests/seq2/base.cpp`, and `code/tests/seq2/j-lang-files/` are valid. The generated J-lang command set must be accepted by the workload adapter and the CrashMonkey C++ skeleton.

## Risks and Test Signals

The script carries the same always-true write-option conditional as seq1 and ACE. It relies on string splitting and tuple flattening, which can mis-handle malformed operation tuples. `isFadatasync` is set but not used for pruning after assignment. `checkDirDep()` deeply special-cases directory `A` contents and does not generalize to every namespace in comments. Generated command execution uses `shell=True` and non-quoted paths.

Useful tests include verifying that known seq2 bug signatures are reachable, checking that final persistence choices never end in `none`, compiling generated seq2 C++, and comparing generated workloads for representative pairs such as `link/unlink`, `write/falloc`, `rename/creat`, `fsetxattr/removexattr`, `truncate/write`, and `mmapwrite/link`.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/ace/specific_generator_scripts/seq2generator.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/ace/specific_generator_scripts/seq3generator.py -->
# sources/test-tools/crashmonkey/ace/specific_generator_scripts/seq3generator.py

## Purpose

`seq3generator.py` is a legacy Python 2 sequence generator for longer, more constrained workload searches. It enumerates operation triples or quadruples over a reduced operation set and logs the resulting operation/parameter/persistence combinations. Unlike seq1 and seq2, the dependency-repair, J-lang emission, adapter invocation, and bug matching portions inside `doPermutation()` are commented out, so the active script primarily functions as a search-space/logging tool rather than a complete test generator.

## Important APIs, Types, and Functions

The seq3-specific operation domain narrows `FileOptions` to `B/foo` and `A/foo`, `SecondFileOptions` to `B/bar` and `A/bar`, `WriteOptions` to `append` and `overlap_unaligned`, `TruncateOptions` to `unaligned`, and `OperationSet` to `write`, `link`, `unlink`, `rename`, and `truncate`. The script still contains support code for other operations such as `creat`, `mkdir`, `mknod`, `falloc`, `dwrite`, `mmapwrite`, `fdatasync`, `fsetxattr`, `removexattr`, and `symlink`, but those are outside the active search set.

As in other ACE generators, `SiblingOf()`, `Parent()`, and `file_range()` describe the namespace. `buildTuple()` expands operation parameter domains. `buildCustomTuple()` supports sequence lengths 1 through 4, allowing `none` for non-final persistence points and requiring a real `fsync` or `sync` at the final point. `isBugWorkload()` is present but not called in the active path because the call is commented out.

The file includes the same insertion and dependency helpers as seq2: `insert*`, `check*`, `satisfyDep()`, `flatList()`, and `buildJlang()`. These functions remain available but are unreachable from the active `doPermutation()` body because the dependency-repair and output-generation block is commented out.

## Control Flow

`main()` opens a timestamped log, parses `--sequence_len`, prints the known bug catalog, fills `parameterList`, builds `SyncSet`, and loops over every operation skeleton in `itertools.product(OperationSet, repeat=int(num_ops))`.

`doPermutation()` skips skeletons where every operation is `write`, records the skeleton, expands parameter combinations, computes the used-file set, and deliberately chooses persistence points from `usedFiles` instead of `file_range(usedFiles)`. For each persistence choice, it interleaves core operations with sync/checkpoint metadata. `fdatasync` and `mmapwrite` are still treated as self-persisting, although they are not in the active `OperationSet`. The resulting `seq` is logged as the current sequence.

The code that would satisfy dependencies, copy `code/tests/seq3/base-j-lang`, emit J-lang, call an adapter, log the modified sequence, and run `isBugWorkload()` is commented out. `main()` also leaves the final move of generated `j-lang*` files commented. Therefore an active run produces logs and counters, but not test files.

## State and Persistence Behavior

The active persistent side effect is the timestamped `*-bugWorkloadGen.log`. The module-level counters and parameter maps track the number of skeletons and workload combinations inspected. Since generation is disabled, `global_count` counts logged persistence variants rather than generated files.

If the commented block were re-enabled, the script would use the same transient maps as seq2 to model open files, open directories, and file lengths, and would write J-lang/C++ tests under `code/tests/seq3/`.

## Dependencies and Integration Points

The active script only requires Python 2 and local filesystem access for the log. The inactive generation block references `code/tests/seq3/base-j-lang`, `code/tests/seq3/base.cpp`, and `workload_seq2.py` despite the seq3 target directory, suggesting the seq3 adapter integration was unfinished or copied from seq2. The generated J-lang command format is otherwise compatible with the older workload adapters.

## Risks and Test Signals

The biggest risk is that the script looks like a generator but does not currently emit tests. Any automation expecting `code/tests/seq3/` outputs from this file will silently receive only logs. The adapter command in the commented block calls `workload_seq2.py` for seq3 paths, which is suspicious if generation is restored. Like the other legacy scripts, it is Python 2-only, uses always-true option conditionals, and depends on global mutable counters.

Good validation signals include asserting that a run creates no J-lang files in its current form, checking logged `Total workloads inspected`, and, if generation is re-enabled, adding fixture tests around dependency repair for the `A`/`B` namespace and compiling generated seq3 C++ outputs. Tests should also decide whether persistence choices should use only `usedFiles` as the current code does or `file_range(usedFiles)` as comments and other generators often prefer.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/ace/specific_generator_scripts/seq3generator.py -->
