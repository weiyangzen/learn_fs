# subset-b-009518 Research

This grouped report covers the assigned syzkaller tool and fixture files. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-crush/crush.go -->
# sources/test-tools/syzkaller/tools/syz-crush/crush.go

Purpose: `syz-crush` repeatedly replays a syzkaller execution log or C reproducer across all VMs in a manager config to amplify elusive crash reproduction. It accepts `-config`, `-debug`, `-restart_time`, `-infinite`, and `-strace`, builds a VM pool, creates a report parser, and uses the reproducer basename as the manager tag when no tag is configured.

Important APIs and flow: `main` validates flags, loads `mgrconfig.Config`, creates `vm.Pool` and `report.Reporter`, chooses `LogFile` versus `CProg` from the input suffix, and starts one goroutine per VM. Each worker loops through `runInstance`, sends a `*instance.RunResult` on `runDone`, and stops on interrupt or non-infinite mode. `runInstance` creates an execprog-backed VM instance, runs either `RunSyzProgFile` with `csource.DefaultOpts` (`Repeat` and `Threaded` enabled) or `RunCProgRaw` with raw C source, and returns only when a parsed crash report is present. `storeCrash` hashes the report title, allocates a sequential crash index, and writes description, log, tag, report, reproducer, and optional memory dump.

State and persistence: runtime state is mostly channels and atomics (`shutdown`, `stoppedWorkers`). Persistent output is stored beside the reproducer under `crashes/<hash(title)>/`, with append-only `logN`, `tagN`, `reportN`, `reproducerN`, and `memory_dumpN` files. Temporary memory dumps are removed when no crash is kept.

Dependencies and integration: this command depends on syzkaller manager config, VM backends, `pkg/instance`, crash reporting, C-source options, and `osutil.HandleInterrupts`. It integrates directly with VM shutdown through global `vm.Shutdown`.

Risks: a missing `strace_bin` is fatal when `-strace` is set; C source read errors call `log.Fatalf` inside workers; crash directory indexing is not synchronized across processes; infinite mode runs until signal and can accumulate crash artifacts indefinitely. Non-crash execution errors are logged and treated as no result.

Test signals: no local unit test is assigned. Behavior is indirectly covered by VM/instance/report package tests and by integration use of crash artifact layout.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-crush/crush.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-db-export/reprolist.go -->
# sources/test-tools/syzkaller/tools/syz-db-export/reprolist.go

Purpose: this dashboard export helper downloads public or authenticated syzbot bug metadata and one C reproducer per bug into an on-disk export tree. It is configured by dashboard URL, namespace, access level, bearer token, output directory, parallelism, and verbosity flags.

Important APIs and flow: `main` creates the output directory, validates namespace, and calls `exportNamespace`. `exportNamespace` uses `dashboard/api.Client`, fetches open and fixed bug groups, starts `errgroup` workers, and feeds bug indexes through a channel. Each worker loads full bug details, calls `saveBug`, checks the first crash's `CReproducerLink`, downloads text with `cli.Text`, extracts the repro ID through `reproIDFromURL`, and writes it with `saveCRepro`. `saveBug` marshals `api.Bug` to JSON and writes `bugs/<bugID>/details.json`; `saveCRepro` writes `bugs/<bugID>/<reproID>.c`.

State and persistence: all durable state is the export directory. There is no resume manifest or deduplication; reruns overwrite details and C reproducer files with mode `0666`. Parallel workers share the same dashboard client and output root but operate per bug directory.

Dependencies and integration: depends on `dashboard/api`, `errgroup`, JSON marshaling, and filesystem writes. It is an offline corpus/dashboard-data collection utility, not a manager runtime component.

Risks: `reproIDFromURL` assumes exactly one `&` and one `=` in the URL tail and panics otherwise. `bug.Crashes[0]` assumes every returned bug has at least one crash. Worker cancellation is limited; the feeder selects on one error channel but then calls `g.Wait` again. File permissions are broad and writes are not atomic.

Test signals: no direct test file is assigned. Useful future tests would mock `api.Client` responses, malformed repro URLs, bugs without crashes, and parallel export errors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-db-export/reprolist.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-db/syz-db.go -->
# sources/test-tools/syzkaller/tools/syz-db/syz-db.go

Purpose: `syz-db` manipulates syzkaller corpus database files. Commands include `pack`, `unpack`, `merge`, `bench`, `print`, and `rm`, with optional target OS/arch and database version handling.

Important APIs and flow: `main` parses flags, obtains a `prog.Target` when needed, and dispatches subcommands. `pack` reads every file in a directory, preserves optional sequence suffixes in names of the form `<hash>-<seq>`, normalizes program serialization when a target is available, fixes mismatched hash keys, and writes `db.Create`. `unpack` opens the DB and writes each record to a file named by key plus optional sequence. `merge` delegates to `db.Merge` and reports deserialization failures. `bench` deserializes records, forces a GC, prints memory stats, corpus count, and call-count percentiles. `print` sorts keys and emits key plus serialized program. `rm` deserializes each program, removes calls whose metadata name contains the requested syscall string using backward iteration, saves modified programs, deletes empty records, and flushes.

State and persistence: `pack`, `merge`, and `rm` modify or create corpus DB files; `unpack` creates files under the destination directory. In-memory state is a map of DB records and temporary `prog.Prog` values. `rm` mutates the opened DB in place and requires `Flush`.

Dependencies and integration: imports syzkaller `pkg/db`, `pkg/hash`, `prog`, all `sys` descriptions for target lookup, `tool.Fail*`, and `maps/slices` helpers. It is a developer/CI utility around manager corpus files.

Risks: `pack` reads all directory entries without skipping subdirectories; target-less packing cannot validate program syntax. `rm` uses substring matching against syscall names, so broad strings can remove more calls than intended. `bench` indexes `lens[n*9/10]`, which is safe for nonzero `n` but coarse for small corpora. `print` may emit large outputs.

Test signals: `syz-db_test.go` specifically covers `rm` removing a producer call and leaving dependent uses rewritten to invalid resources rather than crashing or leaving stale references.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-db/syz-db.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-db/syz-db_test.go -->
# sources/test-tools/syzkaller/tools/syz-db/syz-db_test.go

Purpose: this test validates `syz-db rm` behavior for a corpus record where a removed syscall produces a resource used by later calls.

Important APIs and flow: `TestDBRemoveMatchLine` creates a temporary corpus DB, saves a three-call Linux program containing `open$dir`, an ioctl that consumes `r0`, and `close(r0)`, then obtains the Linux/AMD64 target and calls `rm(fn, "open$dir", target)`. It reopens the DB and asserts the record contains only the ioctl and close calls with `0xffffffffffffffff` substituted for the removed fd resource.

State and persistence: the test owns a temporary DB path and deletes it with `defer os.Remove`. It depends on `db.Open`, `Save`, `Flush`, and reopening to observe on-disk state.

Dependencies and integration: uses `pkg/db`, `pkg/osutil.TempFile`, `prog.GetTarget`, Linux AMD64 target constants, and `testify/assert`.

Risks: the test covers one resource-rewrite case and one match string. It does not cover deleting all calls, multiple records, sequence preservation, broad substring matches, or deserialization failures.

Test signals: it is the primary regression signal for the `rm` command's backward removal and serialization semantics.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-db/syz-db_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/declextract.go -->
# sources/test-tools/syzkaller/tools/syz-declextract/declextract.go

Purpose: `syz-declextract` runs a clang-based declaration extractor against a Linux kernel tree and turns discovered syscalls, ioctl/file operations, io_uring ops, netlink families, types, constants, coverage, and probe information into generated syzkaller descriptions in `sys/linux/auto.txt` plus an `.info` sidecar.

Important APIs and flow: `main` loads manager config, builds a `clangtool.Config`, wires `probe` as `loadProbeInfo`, and calls `run`. `run` calls `prepare`, runs `pkg/declextract.Run`, writes generated descriptions and serialized interface info, reparses all descriptions, typechecks them, removes unused declarations, extracts constants, enriches interface metadata with manual-description and subsystem information, removes unused constants/includes, reformats through `ast.Parse`/`ast.Format`, and rewrites the auto file. `prepare` concurrently runs the clang tool, interface probing, syscall table rename map construction, and optional coverage loading. `buildSyscallRenameMap` finds `*.tbl` files for selected arches, parses syscall names to implementation names, and sorts candidates with Linux/AMD64 and 64-bit preference. `parseTblFile` filters unused, unsupported, and intentionally skipped syscalls.

State and persistence: persistent outputs are `cfg.autoFile`, `cfg.autoFile+".info"`, clang cache in manager workdir, interface probe cache `interfaces.json`, and possible syz-manager side effects from `-mode iface-probe`. The in-memory state includes `declextract.Result`, parsed AST descriptions, unused node lists, coverage records, and syscall rename maps.

Dependencies and integration: integrates `pkg/clangtool`, `tools/clang/declextract`, `pkg/declextract`, `pkg/compiler`, `pkg/ast`, `pkg/cover`, `pkg/ifaceprobe`, `pkg/subsystem`, manager config, Linux target metadata, and `syz-manager` iface-probe mode. It is part of syzkaller's automatic syscall description generation pipeline.

Risks: generation depends on a complete kernel source/object tree, clang extractor availability, `syz-manager` probing, and parsable manual descriptions. `removeUnused` deletes nodes by type/name keys, which can collide if positions are intentionally ignored. Syscall table parsing has explicit filters and may miss unusual arch-specific mappings. Coverage JSON uses `DisallowUnknownFields`, so schema drift is fatal. Running probe can take up to 30 minutes.

Test signals: `declextract_test.go` validates the clang tool wrapper, golden-cache based extraction for each fixture, description compilation, size/alignment parity for generated structs, and golden `.txt`/`.info` output comparison.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/declextract.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/declextract_test.go -->
# sources/test-tools/syzkaller/tools/syz-declextract/declextract_test.go

Purpose: this file provides regression tests for the clang extraction wrapper and end-to-end description generation from synthetic kernel fixture files.

Important APIs and flow: `TestClangTool` delegates to `tooltest.TestClangTool` for `clangtoolimpl.Tool`. `TestDeclextract` iterates all clang-tool fixture C files, symlinks the corresponding `.json` golden into the clang cache to avoid invoking the real extractor, symlinks `manual.txt`, stubs `cfg.Tool`, loads optional `.probe` and `.cover` fixtures, and calls `run`. It then parses all generated descriptions, extracts constants, fabricates constant values, compiles the descriptions, checks generated type size/alignment against `res.StructInfo`, and compares `autoFile` plus `.info` to golden files. With update mode it copies generated output back to goldens on failure.

State and persistence: the test writes symlinks and generated auto files into the temporary kernel object directory prepared by `tooltest`. It reads fixture JSON, optional probe/coverage files, manual descriptions, and golden text/info outputs.

Dependencies and integration: uses `pkg/clangtool/tooltest`, `pkg/compiler`, `pkg/ast`, `pkg/ifaceprobe`, `pkg/osutil`, and the real `run` function. It checks the integration boundary between cached clang JSON and generated syzkaller DSL.

Risks: because the clang tool is replaced by a cache symlink, these tests emphasize downstream processing rather than live clang invocation. The TODO notes missing coverage for whether generated syscalls survive `TransitivelyEnabledCalls`.

Test signals: strong signal for fixture-level semantics, struct layout parity, compiler acceptance, and formatting/golden stability.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/declextract_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/cover.c -->
# sources/test-tools/syzkaller/tools/syz-declextract/testdata/cover.c

Purpose: this fixture exercises switch-scope extraction and coverage mapping for a synthetic syscall and helper.

Important APIs and flow: it defines `COVER_IOCTL1` through `COVER_IOCTL4`, a static `cover_helper(int cmd)` with a switch over `COVER_IOCTL3` and `COVER_IOCTL4`, and `SYSCALL_DEFINE1(cover, int cmd)` with switch cases for all four constants. Cases 3 and 4 call the helper.

State and persistence: there is no persistent state. Local `tmp` variables test return-value fact extraction and branch-local increments.

Dependencies and integration: includes the fixture `syscall.h` macro that expands to `__do_sys_cover`. Its paired JSON and golden generated descriptions verify declextract's interpretation.

Risks: this is deliberately simple; it does not cover default cases, nested ranges, or real kernel macros.

Test signals: paired `cover.c.json` should expose functions, constants, syscall args, switch scopes, helper calls, and argument-flow facts.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/cover.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/cover.c.json -->
# sources/test-tools/syzkaller/tools/syz-declextract/testdata/cover.c.json

Purpose: this golden clang extraction output describes the `cover.c` fixture for downstream declextract tests.

Important structure: top-level keys are `functions`, `consts`, and `syscalls`. Functions include `__do_sys_cover` and static `cover_helper`. Constants define `COVER_IOCTL1` through `COVER_IOCTL4` with numeric values 1 through 4. The syscall record maps `__do_sys_cover` to one integer `cmd` argument.

Control-flow and facts: `__do_sys_cover` has an arg-independent return fact from local `tmp`, separate scopes for `COVER_IOCTL1`, `COVER_IOCTL2`, and combined `COVER_IOCTL3`/`COVER_IOCTL4`; the combined scope calls `cover_helper` and records argument 0 flowing to helper argument 0. `cover_helper` has separate scopes for constants 3 and 4.

State and persistence: this is static JSON consumed through the clangtool cache symlink in tests. It must remain in sync with source line numbers and fixture constants.

Risks and test signals: schema drift or source line changes break golden tests. It specifically tests switch grouping, helper-call propagation, syscall argument typing, and constant extraction.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/cover.c.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/file_operations.c -->
# sources/test-tools/syzkaller/tools/syz-declextract/testdata/file_operations.c

Purpose: this fixture models Linux `struct file_operations` discovery, ioctl command extraction, nested helper ioctl dispatch, array initializers, ternary function initializers, and unused ioctl filtering.

Important APIs and flow: it includes UAPI ioctl constants and local headers, defines `FOO_IOCTL12`, simple operation callbacks, `foo_ioctl2` handling `FOO_IOCTL6`/`7`, and `foo_ioctl` handling `FOO_IOCTL1` through `5` and `10` through `12` before delegating to `foo_ioctl2`. It declares `const struct file_operations foo` with open/read/write/unlocked_ioctl/mmap callbacks; `mmap` uses a ternary expression to force extraction of the first function. It also declares an array `proc_ops[]` with two operation entries and an `unused` operations table whose ioctl constants should not surface as reachable interface descriptions.

State and persistence: no runtime state; all behavior is encoded in static const tables and switch statements.

Dependencies and integration: uses fixture `fs.h`, `file_operations.h`, and `unused_ioctl.h`. It is consumed by declextract golden tests to produce `file_ops`, `ioctls`, constants, and struct layout output.

Risks: initializer syntax and macro expansion are intentionally kernel-like. Changes to operation field names, ternary handling, or unused-interface pruning can change generated descriptions.

Test signals: paired JSON includes file operation entries, ioctl command metadata, `foo_ioctl_arg` struct layout, call facts from `foo_ioctl` to `foo_ioctl2`, and constants extracted from both macros and enums.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/file_operations.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/file_operations.c.json -->
# sources/test-tools/syzkaller/tools/syz-declextract/testdata/file_operations.c.json

Purpose: this golden JSON captures expected extraction for the file-operations fixture.

Important structure: top-level keys are `functions`, `consts`, `structs`, `file_ops`, and `ioctls`. Functions include helper functions from `include/fs.h`, all `foo_*`, `proc_*`, and `unused_ioctl` callbacks. Constants include the reachable `FOO_IOCTL*` values and local `FOO_IOCTL12`. Structs include `foo_ioctl_arg` with size 8, alignment 4, and fields `a` and `b`.

Control-flow and integration: `foo_ioctl` contains a command scope for direct ioctls and facts mapping its `cmd` and `arg` parameters into `foo_ioctl2`. `foo_ioctl2` contributes scopes for `FOO_IOCTL6` and `FOO_IOCTL7`. File operation records associate operation tables with callbacks, while ioctl records encode command names, directions, and argument struct usage.

State and persistence: static test cache input; line numbers and enum/macro values must track the C fixture.

Risks and test signals: verifies that reachable file operations are retained, unused ioctl-only operations are not over-promoted into descriptions, and nested ioctl helper calls are represented. It is sensitive to JSON schema and source line churn.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/file_operations.c.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/functions.c -->
# sources/test-tools/syzkaller/tools/syz-declextract/testdata/functions.c

Purpose: this fixture tests function call graph extraction, return-value facts, builtin handling, syscall-to-helper flows, and simple typed field assignment facts.

Important APIs and flow: static `func_foo` is called by `func_bar`; `func_baz` calls `func_foo`, conditionally calls `func_bar`, ignores a `__builtin_constant_p` branch for practical reachability, and returns either `from_kuid()` or `alloc_fd()`. `func_qux` returns a local fd. `SYSCALL_DEFINE1(functions, long x)` passes `x` to `__fget_light` and returns `func_baz(1)`. `struct Typed`, `typing1`, and `typing` model simple struct pointer field reads/writes and local variable propagation.

State and persistence: no persistence; local variables and struct fields are used to test data-flow facts.

Dependencies and integration: includes fixture `fs.h`, `syscall.h`, and `types.h` for helper functions, syscall macros, and atomic helpers.

Risks: source is synthetic and intentionally tiny; real kernel call graphs have indirect calls and macro-generated functions not represented here.

Test signals: paired JSON includes function list, call edges, return facts from helpers to `func_baz` and from `func_baz` to the syscall, syscall argument-to-helper facts, and typed assignment information.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/functions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/functions.c.json -->
# sources/test-tools/syzkaller/tools/syz-declextract/testdata/functions.c.json

Purpose: this golden JSON represents extracted function graph and syscall metadata for `functions.c`.

Important structure: top-level keys are `functions` and `syscalls`. Functions include `__do_sys_functions`, helper functions from `fs.h` and `types.h`, `func_bar`, `func_baz`, `func_foo`, `func_qux`, `typing`, and `typing1`. The syscall entry exposes `__do_sys_functions`.

Control-flow and facts: `__do_sys_functions` records calls to `__fget_light` and `func_baz`, argument 0 flowing into `__fget_light`, and `func_baz` return flowing to syscall return. `func_baz` records calls to `func_foo`, `func_bar`, `from_kuid`, and `alloc_fd`, with return facts from the latter helpers. The typing functions provide a compact data-flow case for struct-field/local-variable propagation.

State and persistence: static cache input for tests. It must remain synchronized with source line numbers and function names.

Risks and test signals: validates call graph and return fact extraction but does not include constants or structs as top-level outputs. It is useful for catching accidental pruning of static helpers and builtin handling regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/functions.c.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/fs.h -->
# sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/fs.h

Purpose: this fixture header provides a minimal Linux-like `struct file_operations` and helper functions used by declextract C fixtures.

Important APIs and flow: `struct file_operations` contains callback fields for `open`, `read`, `write`, `read_iter`, `write_iter`, `unlocked_ioctl`, and `mmap`. Static helpers `alloc_fd`, `__fget_light`, and `from_kuid` model fd allocation, fd consumption, and uid conversion return facts.

State and persistence: no persistent state; functions return constants or no-op.

Dependencies and integration: included by `file_operations.c`, `functions.c`, and `scopes.c`. Its function definitions appear in golden JSON outputs when reachable or visible.

Risks: the header is intentionally incomplete; it only contains fields needed by fixtures and may not reflect full kernel API evolution.

Test signals: validates recognition of file operation callback fields and helper functions in the generated JSON call/fact graph.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/netlink.h -->
# sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/netlink.h

Purpose: this fixture header defines enough generic netlink and netlink attribute policy types for declextract netlink-family tests.

Important APIs and flow: it declares NLA type enum values, `struct nla_policy` with type/validation/length and union members for masks, nested policies, and ranges, `NLA_POLICY_NESTED`, generic netlink permission flags, operation structs (`genl_ops`, `genl_split_ops`, `genl_small_ops`), and `struct genl_family` fields for family name, operation counts, policy, ops, small ops, and split ops.

State and persistence: static declarations only.

Dependencies and integration: includes `types.h` for fixed-width aliases and `ARRAY_SIZE`. Used by `netlink.c` to test policy extraction, nested policies, split ops, and family metadata.

Risks: `genl_family` contains a likely intentional typo field `mall_ops`; extraction code must rely on the fields it supports. The fixture models only the subset of kernel netlink metadata needed for tests.

Test signals: paired netlink JSON should expose policies, family records, command constants, callback functions, and struct sizes for UAPI payload types.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/syscall.h -->
# sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/syscall.h

Purpose: this fixture header provides minimal syscall-definition macros that expand synthetic `SYSCALL_DEFINE*` declarations into `__do_sys_<name>` functions.

Important APIs and flow: `SYSCALL_DEFINE1` and `SYSCALL_DEFINE2` forward to `SYSCALL_DEFINEx`, which emits a prototype and definition for `long __do_sys_NAME(__VA_ARGS__)`.

State and persistence: preprocessor-only definitions; no state.

Dependencies and integration: included by syscall-oriented declextract fixtures such as `cover.c`, `functions.c`, `scopes.c`, `syscall.c`, and `types.c`. It lets clang extraction see stable function names matching kernel syscall implementation naming.

Risks: the macro ignores true Linux syscall wrapper complexity, calling conventions, and metadata sections. It is intentionally small for deterministic tests.

Test signals: golden JSON should map syscalls to `__do_sys_*` functions with extracted argument types.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/types.h -->
# sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/types.h

Purpose: this fixture header supplies kernel-style integer aliases, `__user` pointer annotation, `ARRAY_SIZE`, and atomic helper functions for declextract tests.

Important APIs and flow: typedefs define `s8/s16/s32/s64` and `u8/u16/u32/u64`. `__user` expands to a BTF type tag attribute. `ARRAY_SIZE` computes element count. `atomic_load32` and `atomic_load64` wrap `__atomic_load_n` and appear in JSON function outputs.

State and persistence: no state beyond static inline function bodies.

Dependencies and integration: included by `functions.c`, `netlink.h`, and `types.c`, and indirectly by netlink fixtures. It supports type extraction and user-pointer recognition.

Risks: compiler-specific attributes and builtins are simplified. The atomic helpers are present for extraction visibility, not for runtime execution.

Test signals: golden JSON confirms fixed-width aliases, user pointer handling, inline/static function extraction, and array-size macro use.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/uapi/file_operations.h -->
# sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/uapi/file_operations.h

Purpose: this UAPI fixture defines ioctl command constants and a payload struct for file-operation extraction tests.

Important APIs and flow: includes `ioctl.h`, defines `FOO_IOCTL1` through `FOO_IOCTL9` with `_IO`, `_IOR`, `_IOW`, and `_IOWR`, declares enum constants `FOO_IOCTL10` and `FOO_IOCTL11`, and defines `struct foo_ioctl_arg { int a, b; }`.

State and persistence: static declarations only.

Dependencies and integration: included by `file_operations.c` and `scopes.c`. Its constants are expected to surface in golden JSON and generated syzkaller descriptions when reachable.

Risks: numeric values depend on the local `_IOC` macro definitions and `sizeof` behavior for fixture types.

Test signals: validates ioctl direction/size extraction, enum and macro constants, and struct argument layout.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/uapi/file_operations.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/uapi/io_uring.h -->
# sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/uapi/io_uring.h

Purpose: this UAPI fixture defines a small `enum io_uring_op` for io_uring operation-table extraction.

Important APIs and flow: enum values are `IORING_OP_NOP`, `IORING_OP_READV`, `IORING_OP_WRITEV`, and `IORING_OP_NOT_SUPPORTED`.

State and persistence: static enum only.

Dependencies and integration: included by `io_uring.c`, where an indexed `ops[]` table maps operation constants to prep/issue callbacks. The extractor should retain supported issue ops and skip not-supported sentinel behavior.

Risks: minimal enum does not model the real io_uring opcode space or aliases.

Test signals: paired JSON should expose four constants and three generated `iouring_ops` mappings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/uapi/io_uring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/uapi/ioctl.h -->
# sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/uapi/ioctl.h

Purpose: this fixture recreates the basic Linux ioctl encoding macros used by ioctl extraction tests.

Important APIs and flow: it defines direction constants, bit widths, shifts, `_IOC`, and convenience macros `_IO`, `_IOR`, `_IOW`, and `_IOWR`. `_IOC` composes direction, type, number, and size into a command integer.

State and persistence: preprocessor constants only.

Dependencies and integration: included by file-operation UAPI fixtures and unused ioctl fixtures. Numeric ioctl values generated from these macros appear in JSON constants and command scopes.

Risks: this is a simplified architecture-independent copy; real kernel ioctl definitions may vary by arch or include extra helper macros.

Test signals: validates that clang constant extraction and declextract's ioctl decoder can interpret macro-generated command values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/uapi/ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/uapi/netlink_family.h -->
# sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/uapi/netlink_family.h

Purpose: this UAPI fixture defines a hypothetical generic netlink family command/attribute namespace and payload structs.

Important APIs and flow: `enum netlink_foo_cmds` defines FOO and BAR commands. `enum netlink_foo_attrs` defines non-dense attributes with `NETLINK_FOO_ATTR3 = NETLINK_FOO_ATTR2 + 3`. `struct netlink_foo_struct1` has three ints, and `netlink_foo_struct2` is a typedef struct with three doubles.

State and persistence: declarations only.

Dependencies and integration: included by `netlink.c` and reflected in netlink policy extraction. The non-dense enum tests attribute numbering and constant inclusion.

Risks: synthetic family data is small and omits many real netlink validation features.

Test signals: paired JSON should report command and attribute constants plus struct sizes/alignments for both payload types.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/uapi/netlink_family.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/uapi/unused_ioctl.h -->
# sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/uapi/unused_ioctl.h

Purpose: this UAPI fixture defines an ioctl constant that is intentionally used only by an otherwise unused file operation table.

Important APIs and flow: includes `ioctl.h` and defines `UNUSED_IOCTL1` as `_IO('c', 1)`.

State and persistence: macro only.

Dependencies and integration: included by `file_operations.c`, where `UNUSED_IOCTL1` and a local `UNUSED_IOCTL2` appear in `unused_ioctl`. The extraction pipeline should avoid turning unreachable unused operations into final descriptions.

Risks: if reachability pruning changes, this constant may appear or disappear in generated output.

Test signals: validates unused-interface pruning and include/constant usage accounting.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/uapi/unused_ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/io_uring.c -->
# sources/test-tools/syzkaller/tools/syz-declextract/testdata/io_uring.c

Purpose: this fixture tests extraction of io_uring operation tables from indexed const arrays.

Important APIs and flow: defines `struct io_issue_def` with `prep` and `issue` function pointers, simple prep/issue functions for nop/read/write, and an `ops[]` table indexed by `IORING_OP_*`. Supported entries map NOP to `io_nop`, READV to `io_read`, and WRITEV to `io_write`; `IORING_OP_NOT_SUPPORTED` uses an unsupported prep sentinel but an issue function that should not become a supported operation.

State and persistence: static table only.

Dependencies and integration: includes UAPI `io_uring.h`; paired JSON feeds declextract tests for `iouring_ops`.

Risks: fixture only models one table shape and simple function names.

Test signals: generated JSON should include functions, four opcode constants, and three supported `iouring_ops` records.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/io_uring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/io_uring.c.json -->
# sources/test-tools/syzkaller/tools/syz-declextract/testdata/io_uring.c.json

Purpose: this golden JSON records expected extraction for the io_uring table fixture.

Important structure: top-level keys are `functions`, `consts`, and `iouring_ops`. Functions include all prep and issue callbacks. Constants include NOP, READV, WRITEV, and NOT_SUPPORTED with values 0 through 3. `iouring_ops` maps NOP to `io_nop`, READV to `io_read`, and WRITEV to `io_write`.

State and persistence: static clang-cache input for tests; it must track source line numbers and enum values.

Dependencies and integration: consumed by `TestDeclextract` to validate generated descriptions and interface info.

Risks and test signals: catches regressions in indexed initializer parsing and unsupported-op filtering. It does not cover SQE argument structures or real kernel io_uring complexity.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/io_uring.c.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/netlink.c -->
# sources/test-tools/syzkaller/tools/syz-declextract/testdata/netlink.c

Purpose: this fixture exercises generic netlink family, operation, split-operation, policy, nested-policy, and payload-size extraction.

Important APIs and flow: it defines local nested attr constants, nested and top-level `nla_policy` arrays with scalar, string, nested, and `sizeof`-based payload entries, a dump-only policy, and reject-all/forward-declared policies. It defines callback functions and `genl_ops` for `foo_family`, including doit and dumpit variants. It defines `bar_family` using `genl_split_ops` with pre/do/post callbacks, `noops_family` with no operations, and `nopolicy_family` with ops but no family policy.

State and persistence: static const arrays and family structs only.

Dependencies and integration: includes generic netlink fixture types and UAPI family constants. Paired JSON feeds declextract tests for `netlink_families` and `netlink_policies`.

Risks: pointer-to-policy and array-size inference are sensitive to C initializer forms. Non-dense attributes and local non-UAPI constants intentionally exercise include versus value emission decisions.

Test signals: golden JSON includes functions, constants, payload structs, families `BAR`, `NOOPS`, `foo family`, and `nopolicy`, and policy metadata.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/netlink.c.json -->
# sources/test-tools/syzkaller/tools/syz-declextract/testdata/netlink.c.json

Purpose: this golden JSON describes expected generic netlink extraction for `netlink.c`.

Important structure: top-level keys are `functions`, `consts`, `structs`, `netlink_families`, and `netlink_policies`. Functions include atomic helpers, `foo_cmd`, `bar_cmd`, and split-op callbacks. Constants include UAPI family command/attribute values plus local nested/no-policy command constants. Structs include `netlink_foo_struct1` size 12 align 4 and `netlink_foo_struct2` size 24 align 8.

Control-flow and integration: family records cover normal ops, split ops, no-ops family, and no-policy family. Policy records represent scalar, string length, nested policy, and `sizeof`-derived binary payload lengths.

State and persistence: static test cache. Its line numbers, constants, and policy shapes must match the C fixture.

Risks and test signals: strong signal for netlink-family extraction and UAPI versus local constant treatment. It is sensitive to schema naming and nested policy representation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/netlink.c.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/scopes.c -->
# sources/test-tools/syzkaller/tools/syz-declextract/testdata/scopes.c

Purpose: this fixture stresses switch-scope extraction for syscall arguments, command ranges, helper calls, default cases, large integer constants, and fact propagation.

Important APIs and flow: defines large unsigned/signed macros, `scopes_helper(long cmd, long aux)` with cases for `FOO_IOCTL7`, `FOO_IOCTL8`, and large constants, and `SYSCALL_DEFINE1(scopes0, int x, long cmd, long aux)` that consumes `aux`, switches on `cmd`, handles individual ioctls, grouped cases, macro ranges (`FOO_IOCTL4 ... FOO_IOCTL4 + 2`), numeric ranges (`100 ... 102`), helper calls, and default assignment.

State and persistence: no persistence. Local `tmp` tests return and local-value facts.

Dependencies and integration: includes file operation UAPI constants, syscall macros, and fs helpers. Paired JSON is consumed by declextract tests.

Risks: large constants intentionally overflow signed/unsigned boundaries in ways extractor code must handle deterministically.

Test signals: paired JSON should include syscall metadata, ioctl constants, `foo_ioctl_arg` struct, scopes for individual/range cases, helper call facts, and argument-to-helper flow.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/scopes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/scopes.c.json -->
# sources/test-tools/syzkaller/tools/syz-declextract/testdata/scopes.c.json

Purpose: this golden JSON captures expected extraction for scope/range handling in `scopes.c`.

Important structure: top-level keys are `functions`, `consts`, `structs`, `syscalls`, and `ioctls`. Functions include `__do_sys_scopes0`, fs helpers, and `scopes_helper`. Constants include `FOO_IOCTL*` values relevant to the fixture. Structs include `foo_ioctl_arg` size 8 align 4.

Control-flow and facts: `__do_sys_scopes0` has an arg-independent scope for `aux` flowing to `__fget_light` and `tmp` flowing to return, separate command scopes for `FOO_IOCTL1`, `FOO_IOCTL2/3`, expanded `FOO_IOCTL4` range, `FOO_IOCTL7/8` helper flow, numeric range `100..102`, and default assignment. Helper scopes cover fd allocation, fd lookup, and large constants.

State and persistence: static test cache; source line and numeric command expansion changes must be reflected here.

Risks and test signals: validates command range expansion, local-return facts, helper call propagation, and large constant handling.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/scopes.c.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/syscall.c -->
# sources/test-tools/syzkaller/tools/syz-declextract/testdata/syscall.c

Purpose: this fixture tests basic syscall extraction from macro-expanded definitions and pointer/string argument typing.

Important APIs and flow: includes `syscall.h` and defines `SYSCALL_DEFINE1(open, const char* filename, int flags, int mode)` and `SYSCALL_DEFINE1(chmod, const char* filename, int mode)`, each returning zero.

State and persistence: none.

Dependencies and integration: macro expansion creates `__do_sys_open` and `__do_sys_chmod` for JSON syscall records.

Risks: it uses `SYSCALL_DEFINE1` despite multiple variadic arguments because the fixture macro ignores the count parameter; this is intentional but not a faithful kernel macro.

Test signals: paired JSON should expose both syscalls, const string pointers for filename args, and integer mode/flags args.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/syscall.c.json -->
# sources/test-tools/syzkaller/tools/syz-declextract/testdata/syscall.c.json

Purpose: this golden JSON describes basic syscall extraction for `syscall.c`.

Important structure: top-level keys are `functions` and `syscalls`. Functions are `__do_sys_chmod` and `__do_sys_open`. Syscall records include typed arguments: const string buffer pointer for `filename` and 4-byte integer fields for `flags` and `mode`.

State and persistence: static cache input for the declextract tests.

Dependencies and integration: consumed through `TestDeclextract` to generate and compile descriptions.

Risks and test signals: focused signal for syscall arg typing; it does not cover syscall renaming or arch table lookup.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/syscall.c.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/types.c -->
# sources/test-tools/syzkaller/tools/syz-declextract/testdata/types.c

Purpose: this fixture stresses type extraction: anonymous structs/unions, typedefs, forward pointers, bitfields, packed/aligned attributes, recursive structs, enum typedefs, user pointers, counted-by attributes, zero-length arrays, and alignment edge cases.

Important APIs and flow: it defines `anon_t`, `empty_struct`, `fd_t`, `forward_t`, `struct anon_struct` with nested anonymous members, arrays, pointers, and pointer arrays; bitfield enum and `struct bitfields` with unnamed bitfield and counted pointer; packed/aligned structs; mutually recursive `various` and `recursive`; syscalls `types_syscall`, `types_syscall2`, and `align_syscall`; `anon_flow` assigns one input into nested fields; and several alignment test structs.

State and persistence: no persistence. Struct fields and local assignments exist to test extracted field facts and layout.

Dependencies and integration: includes fixture `types.h` and `syscall.h`. Paired JSON feeds struct layout, enum, syscall, and field-flow checks in declextract tests.

Risks: generated anonymous struct names are synthetic and can be unstable if naming algorithms change. Layout expectations depend on the compiler target ABI.

Test signals: paired JSON lists many structs with size/alignment, enum constants, syscall arg types, user-pointer annotations, counted-by metadata, and `anon_flow` field facts.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/types.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/types.c.json -->
# sources/test-tools/syzkaller/tools/syz-declextract/testdata/types.c.json

Purpose: this golden JSON records expected type, enum, syscall, and field-flow extraction for `types.c`.

Important structure: top-level keys are `functions`, `consts`, `enums`, `structs`, and `syscalls`. Functions include the three syscall implementations, `anon_flow`, and atomic helpers. Structs include alignment cases, anonymous struct expansions, `bitfields`, `packed_t`, recursive pairs, and empty/aligned-empty structs. Consts include enum values such as `a`, `b`, `c`, `enum_foo_*`, and `enum_bar_*`.

Control-flow and facts: `anon_flow` records argument-to-field facts for nested anonymous fields, union members, typedef fields, array elements, pointer fields, and pointer-array fields. Syscall records encode nested pointer types, `__user` tags, enum args, typedef-backed fd args, and struct pointers.

State and persistence: static cache input. It is line-, ABI-, and naming-sensitive.

Risks and test signals: high-value regression signal for struct layout parity, anonymous naming stability, bitfield layout, counted-by metadata, user annotations, and recursive type handling.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-declextract/testdata/types.c.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-diff/benchmark/base.cfg -->
# sources/test-tools/syzkaller/tools/syz-diff/benchmark/base.cfg

Purpose: this JSON manager config template defines the baseline VM setup for syz-diff benchmark experiments.

Important fields and flow: placeholders `%KERNEL%`, `%IMAGE%`, and `%SYZKALLER%` are patched by `run.sh`. It names the instance `base`, listens on `0.0.0.0:50543`, targets `linux/amd64`, uses QEMU, three procs, four VMs, `workdir_fs`, KVM-enabled q35 machine args, 2 CPUs, 2048 MB memory, and disables experimental edge coverage.

State and persistence: syz-manager state goes under `%SYZKALLER%/workdir_fs`; this config itself is copied into per-experiment directories.

Dependencies and integration: consumed by benchmark `run.sh` and `bin/syz-diff` as the reverted/base kernel side.

Risks: the workdir is shared with fs experiments, so benchmark scripts remove crash state elsewhere. Placeholder replacement must happen before use. Fixed ports can collide with local managers.

Test signals: no unit test; validation is successful syz-diff launch with patched placeholders.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-diff/benchmark/base.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-diff/benchmark/patched_fs.cfg -->
# sources/test-tools/syzkaller/tools/syz-diff/benchmark/patched_fs.cfg

Purpose: this syz-diff manager config template defines the patched-kernel side for filesystem-focused benchmark experiments.

Important fields and flow: it targets Linux/AMD64 QEMU, uses `%KERNEL%`, `%IMAGE%`, and `%SYZKALLER%` placeholders, names the manager `patched`, listens on port 50544, enables a broad filesystem syscall set plus filesystem ioctls, disables some risky mount image families, sets `procs` to 3, `fuzzing_vms` to 10, and runs 18 VMs with 3072 MB memory.

State and persistence: uses `%SYZKALLER%/workdir_fs`, and `run.sh` removes its `crashes` directory before each experiment and later copies crashes into the experiment workdir.

Dependencies and integration: paired with `base.cfg` and selected by `run.sh` for filesystem bug commits.

Risks: shared workdir and fixed HTTP port can conflict. The syscall allowlist is manually curated and may age as syscall descriptions change. KVM/q35 assumptions are host-dependent.

Test signals: benchmark success is based on syz-diff producing patched-only crashes in the experiment log.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-diff/benchmark/patched_fs.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-diff/benchmark/patched_net.cfg -->
# sources/test-tools/syzkaller/tools/syz-diff/benchmark/patched_net.cfg

Purpose: this syz-diff manager config template defines the patched-kernel side for networking-focused benchmark experiments.

Important fields and flow: it enables common socket/syscall operations plus BPF, cgroup, tun/ppp, namespace procfs, 802.11, ethernet, TCP resource extraction, net socket initialization, and VHCI helpers. It uses QEMU with 18 VMs, 4 procs, no sandbox, 3072 MB memory, and disabled edge coverage.

State and persistence: despite being network-focused, `workdir` is `%SYZKALLER%/workdir_fs` in this template. `run.sh` prepares and copies crash artifacts around this workdir.

Dependencies and integration: selected by `run.sh` for network bug commits and passed to `bin/syz-diff` as the new/patched config.

Risks: duplicate `bpf` entry, shared `workdir_fs`, fixed port, host KVM requirements, and manually maintained syscall allowlist. Network fuzzing may need external kernel config support not enforced here.

Test signals: benchmark output filtered for `patched-only` lines indicates useful differential crashes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-diff/benchmark/patched_net.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-diff/benchmark/run.sh -->
# sources/test-tools/syzkaller/tools/syz-diff/benchmark/run.sh

Purpose: this benchmark driver builds base and patched Linux kernels for known bug-introducing commits and runs `syz-diff` experiments for network and filesystem bug lists.

Important APIs and flow: it requires base repo, patched repo, and image path arguments; computes script/base directories; downloads a kernel config; patches `%KERNEL%`, `%SYZKALLER%`, and `%IMAGE%` placeholders; defines `run_experiment` to reset/build the base kernel with the guilty commit reverted, build the patched kernel at the guilty commit, create a timestamped experiment workdir, save commit metadata and patch, copy/personalize configs, clear patched crashes, run `timeout 3h bin/syz-diff -patch`, tee logs, grep `patched-only`, and copy crashes. It then calls `run_experiment` for hard-coded net and fs commits/titles.

State and persistence: destructive git state changes happen inside both kernel repos (`git clean -fxfd`, `git reset --hard`, `git revert`). Experiment outputs are stored under `experiment/<timestamp>_<commit>/`.

Dependencies and integration: uses `wget`, `git`, `make`, clang/lld, syzkaller `bin/syz-diff`, benchmark configs, QEMU/KVM image, and existing `workdir_net`/`workdir_fs` corpuses per script comment.

Risks: highly destructive to supplied kernel repos; no cleanup of temp kernel config; fixed build parallelism `-j32`; no error checking for failed builds because subshell output is redirected and script lacks `set -e`; grep may affect pipeline status. Requires large disk/time resources.

Test signals: no automated unit test. Evidence is per-experiment log, patch.diff, description, and copied crashes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-diff/benchmark/run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-diff/diff.go -->
# sources/test-tools/syzkaller/tools/syz-diff/diff.go

Purpose: `syz-diff` compares fuzzing behavior between a base and new manager configuration, optionally focusing the new config using a git patch.

Important APIs and flow: `main` requires a build with known git revision, parses `-base`, `-new`, `-debug`, and `-patch`, enables log caching, loads both manager configs, optionally reads a patch and calls `diff.PatchFocusAreas(newCfg, ...)`, then runs `diff.Run` with a `manager.DiffFuzzerStore` rooted at the new config workdir and a shutdown context.

State and persistence: manager/diff state is stored under `newCfg.Workdir` through `DiffFuzzerStore`. Log cache is in memory. VM shutdown is context-driven.

Dependencies and integration: uses `pkg/manager/diff`, `pkg/manager`, `mgrconfig`, `vm`, syzkaller build revision metadata, and optional patch parsing through the diff package.

Risks: missing/invalid configs are fatal. Patch focusing mutates the new config's focus areas and depends on diff package heuristics. It refuses non-`make` builds with unknown git revision.

Test signals: no direct test here; benchmark configs and `run.sh` exercise it. Package-level tests for `manager/diff` would be the primary logic signal.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-diff/diff.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-env -->
# sources/test-tools/syzkaller/tools/syz-env

Purpose: `syz-env` runs syzkaller development commands inside the official syzkaller Docker environment image or a locally built equivalent.

Important APIs and flow: it collects proxy settings into Docker build/run args, rewrites `SOURCEDIR=<path>` arguments into a mounted `/syzkaller/kernel`, defaults to interactive `-it` outside CI, picks `env` or `old-env` image based on executable basename, uses rootless Docker detection to decide whether to pass `--user`, pulls `gcr.io/syzkaller/<image>` unless `SYZ_ENV_BUILD` is set, and finally runs Docker with syzkaller source, cache, Docker socket, GOPATH, CI/GitHub/Fuzzit environment variables, and the requested command via `-c`.

State and persistence: uses host source checkout, `$HOME/.cache`, and Docker image cache. Local build mode creates/updates `syz-env` or `syz-old-env` images.

Dependencies and integration: requires Docker, optional local Dockerfile under `tools/docker/<image>`, and host project layout. It is intended to wrap `make` and extraction commands.

Risks: `[ -n $http_proxy ]` style unquoted tests can behave unexpectedly for empty or whitespace-containing values. Mounting Docker socket gives container broad host Docker control. Command construction is string-based and can be sensitive to shell quoting.

Test signals: no automated test. Manual signal is successful container pull/build and command execution with correct file ownership.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-env -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-execprog/execprog.go -->
# sources/test-tools/syzkaller/tools/syz-execprog/execprog.go

Purpose: `syz-execprog` executes syzkaller programs or corpus databases locally through the executor/RPC stack, optionally collecting coverage, hints, output, glob expansion results, or running as a simple stress fuzzer.

Important APIs and flow: `main` parses target/executor/sandbox/feature/repeat/procs/coverage/stress/glob flags, resolves `prog.Target`, converts csource feature flags to FlatRPC feature masks, parses stress syscall filters, builds executor environment and exec flags, loads programs from DB or logs, creates a `Context`, and runs `rpcserver.RunLocal` with a `LocalConfig`. `Context.machineChecked` receives feature/syscall data, sets stress choice tables, and returns queue options. `Next` generates glob requests, random/mutated stress programs, or sequenced corpus programs. `Done` prints call results, hints, and coverage, increments atomics, and cancels when repeat count is satisfied. Coverage is dumped per program/call with PCs normalized through `backend.PreviousInstructionPC`.

State and persistence: state includes loaded programs, random source, queue position, result counters, and optional coverage files named from `-coverfile`. It reads corpus DBs/logs and executor binary path. Stress mode is long-running when repeat is 0.

Dependencies and integration: integrates `pkg/rpcserver`, `pkg/fuzzer/queue`, `flatrpc`, executor binary, target descriptions, `pkg/db`, `prog`, coverage backend, csource features, and VM info. It is a key standalone executor harness used by reproducer and debugging workflows.

Risks: unsupported or mismatched executor/target features can fail at runtime. `loadPrograms` silently skips DB records that fail deserialization but fatals on unreadable files. Coverage dumping creates many files. Stress mode without syscall filtering can generate broad workloads. The deprecated `-collide` flag is accepted but ignored for compatibility.

Test signals: no direct test in this subset. Indirect coverage comes from executor, RPC server, queue, DB, and target parser tests plus real syzkaller reproducer workflows.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-execprog/execprog.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-expand/expand.go -->
# sources/test-tools/syzkaller/tools/syz-expand/expand.go

Purpose: `syz-expand` parses one syzkaller program and prints it in verbose form with defaults expanded.

Important APIs and flow: `main` parses `-os`, `-arch`, `-prog`, and `-strict`, resolves the target, reads the program file, selects `prog.Strict` or `prog.NonStrict`, deserializes the program, and prints `SerializeVerbose()`.

State and persistence: read-only except stdout/stderr. No persistent state is created.

Dependencies and integration: depends on `prog.GetTarget`, all `sys` descriptions, and program serialization/deserialization APIs. It is a developer inspection tool for syzkaller DSL programs.

Risks: exits directly on missing file, target, or parse errors. Strict mode may reject programs accepted by manager workflows.

Test signals: no direct test. Existing parser/serializer tests cover the underlying behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-expand/expand.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-fillreports/fillreports.go -->
# sources/test-tools/syzkaller/tools/syz-fillreports/fillreports.go

Purpose: `syz-fillreports` backfills missing report elements on dashboard bugs, currently guilty file paths extracted from crash reports.

Important APIs and flow: `main` creates a `dashapi.Dashboard`, fetches `BugList`, loads bug reports concurrently with `loadBugReports`, and calls `processReport`. `processReport` skips reports that already have guilty files, are not open/fixed, or lack OS/arch; creates a minimal `mgrconfig.Config` with target info; builds a `report.Reporter`; extracts a guilty file with `ReportToGuiltyFile`; and uploads it through `dash.UpdateReport`.

State and persistence: dashboard is the persistent state. Local state is a work item channel and worker goroutines. No local files are written.

Dependencies and integration: uses dashboard API credentials, syzkaller report parsing, target metadata, and manager config-derived reporter construction.

Risks: `log.Fatalf` on reporter creation stops the whole run for one bad OS/arch. It only handles the first extracted guilty file. Load failures are logged and skipped; update failures are logged but do not abort. Concurrency is fixed at 8.

Test signals: no direct test. Report parser tests and dashboard API mocks would be needed for coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-fillreports/fillreports.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-fix-analyzer/fix-analyzer.go -->
# sources/test-tools/syzkaller/tools/syz-fix-analyzer/fix-analyzer.go

Purpose: `syz-fix-analyzer` estimates how many fixed dashboard bugs look automatically fixable based on bug type and patch shape.

Important APIs and flow: `main` compiles regexes for bug types, creates a dashboard API client, calls `run`, prints fixable bugs by type, and summarizes totals. `run` opens a Linux repo, fetches fixed bug groups, starts `runJobs`, de-duplicates by first fix commit hash, classifies jobs by regex, and accumulates type stats. `runJobs` uses `runtime.GOMAXPROCS` workers. `isFixable` requires a fix commit, matching bug type, fetches the commit patch, parses it with `git-diff-parser`, and declares the bug fixable only when the patch changes exactly one non-binary `.c` or `.h` file with one hunk and no rename.

State and persistence: no local writes. It reads the git repository, dashboard data, and commit patches; results are printed to stdout.

Dependencies and integration: uses `dashboard/api`, `pkg/vcs`, Linux target repo handling, regex classification, and an external git diff parser.

Risks: fixability heuristic is intentionally shallow; TODOs mention matching guilty files and more crash variants. `percent` divides by total and can print NaN when denominator is zero. `runJobs` never closes `jobC`, but all submitted jobs are consumed before returning.

Test signals: no direct tests. Useful future tests would cover regex classification, patch-shape filtering, duplicate commit handling, and zero denominators.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-fix-analyzer/fix-analyzer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-fmt/syz-fmt.go -->
# sources/test-tools/syzkaller/tools/syz-fmt/syz-fmt.go

Purpose: `syz-fmt` formats syzkaller syscall description `.txt` files into canonical AST formatting.

Important APIs and flow: `main` accepts files, directories, or `all`; `all` expands to every `sys/<os>` directory. Directories are scanned for `.txt` files. `processFile` reads a file, parses it with `ast.Parse`, formats it with `ast.Format`, and either reports dry-run failure or renames the original to `file~` and writes formatted content with the original mode.

State and persistence: modifies description files in place unless `-dry-run` is set; creates backup files with `~` suffix.

Dependencies and integration: uses syzkaller AST parser/formatter, OS target list, `osutil.Rename`, and `tool.Init`.

Risks: parse errors exit the process. Backup rename plus write is not atomic as a combined operation, and stale `file~` handling depends on `osutil.Rename`. Directory mode only processes immediate `.txt` children.

Test signals: no direct test here; AST formatting tests cover core behavior. Dry-run exit code 2 is the CI-friendly signal for formatting drift.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-fmt/syz-fmt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-headerparser/headerlib/__init__.py -->
# sources/test-tools/syzkaller/tools/syz-headerparser/headerlib/__init__.py

Purpose: package marker for the legacy Python `headerlib` modules used by `syz-headerparser`.

Important APIs and flow: it contains only copyright/license comments and no runtime symbols.

State and persistence: none.

Dependencies and integration: allows `headerlib.container`, `headerlib.header_preprocessor`, and `headerlib.struct_walker` imports.

Risks: no functional risks beyond Python packaging expectations.

Test signals: import success when running `headerparser.py` is the practical signal.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-headerparser/headerlib/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-headerparser/headerlib/container.py -->
# sources/test-tools/syzkaller/tools/syz-headerparser/headerlib/container.py

Purpose: this legacy Python module converts struct field hierarchies from parsed headers into syzkaller-style metadata structs.

Important APIs and flow: `StructRepr` holds one struct name and a list of `FieldRepr` objects, formats fields with `get_syzkaller_field_body`, and maps native C types to candidate syzkaller types such as `len`, `fileoff`, `intN`, string pointers, arrays, nested structs, and enums. `FieldRepr` is a simple property container for field type, identifier, and optional linked struct metadata. `GlobalHierarchy` is a dict keyed by `"struct <name>"`; it invokes `StructWalker.generate_local_hierarchy`, converts tuples into `StructRepr`, links fields whose type references known structs, and emits sorted metadata with `get_metadata_structs`.

State and persistence: in-memory hierarchy only. Logging handlers are added per object.

Dependencies and integration: depends on `headerlib.struct_walker.StructWalker` and Python logging. Used by `headerparser.py` to print generated metadata.

Risks: type mapping is heuristic and incomplete. Logger setup can add duplicate handlers across repeated objects. `maxcolwidth` assumes at least one field, so empty structs may fail formatting. Python 2-style `object` classes and doctext indicate legacy code.

Test signals: fixture headers `th_a.h` and `th_b.h` exercise nested struct pointers, comments, bools, unknown typedefs, enums, and anonymous unions.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-headerparser/headerlib/container.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-headerparser/headerlib/header_preprocessor.py -->
# sources/test-tools/syzkaller/tools/syz-headerparser/headerlib/header_preprocessor.py

Purpose: this module preprocesses one or more C header files into a pycparser AST for the legacy header parser.

Important APIs and flow: `template` defines compatibility macros and typedefs to make Linux-like headers palatable to pycparser, then includes optional user-provided lines and copied header basenames. `HeaderFilePreprocessor.__init__` records filenames, logging, creates a temp directory/source/object file, copies headers, and runs GCC preprocessing. `_gcc_preprocess` executes `gcc -I. -E -P -c source.c > source.o`; `_get_ast` calls `pycparser.parse_file`; `get_ast` wraps parse errors in `HeaderFilePreprocessorException`.

State and persistence: creates a temporary directory and files but does not remove them in this code. The preprocessed output is stored as `source.o` in that temp dir.

Dependencies and integration: uses `gcc`, shell `cp`, pycparser, tempfile, and logging. Used by `StructWalker` when no AST is supplied.

Risks: command construction uses `shell=True` with joined filenames, so paths with spaces or shell metacharacters are unsafe. Temp files are leaked. It waits for process exit but does not inspect exit status. The compatibility macro set is partial.

Test signals: successful parsing of `test_headers` through `headerparser.py` or `StructWalker` is the practical signal.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-headerparser/headerlib/header_preprocessor.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-headerparser/headerlib/struct_walker.py -->
# sources/test-tools/syzkaller/tools/syz-headerparser/headerlib/struct_walker.py

Purpose: this module traverses a pycparser AST and extracts a local hierarchy of C structs and their fields.

Important APIs and flow: `StructWalker` accepts an AST or header filenames. If needed, it builds an AST with `HeaderFilePreprocessor`. `_recursive_process_item` handles declarations, type declarations, identifiers, named and anonymous structs/unions, pointers, arrays, enums, and function pointers. `_format_item` normalizes types with pointer stars and array dimensions. `_traverse_ast` ignores anonymous top-level structs and recursively lists fields, flattening anonymous nested structs/unions into dotted identifiers. `visit_Struct` records first occurrence of each named struct and skips duplicates. `generate_local_hierarchy` visits the AST and returns a map of struct name to `(type, identifier)` tuples.

State and persistence: all state is in-memory `local_structs_hierarchy` plus logging.

Dependencies and integration: depends on pycparser `c_ast` and `HeaderFilePreprocessor`. It feeds `GlobalHierarchy`.

Risks: array dimensions are cast with `int(item_ast.dim.value)`, so expressions not reduced to integer literals can fail. Anonymous nested structs without parent names raise and are skipped. Duplicate struct names are ignored. Function pointers are generalized to `void (*)()`.

Test signals: doctext and `test_headers` cover arrays, pointers, nested anonymous structs/unions, enum fields, and struct references.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-headerparser/headerlib/struct_walker.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-headerparser/headerparser.py -->
# sources/test-tools/syzkaller/tools/syz-headerparser/headerparser.py

Purpose: command-line entry point for the legacy header parser that emits syzkaller struct metadata from C headers.

Important APIs and flow: `main` parses `--filenames`, `--debug`, and optional `--include`. It chooses logging level, reads include-line content when provided, constructs `GlobalHierarchy` from comma-separated filenames, handles preprocessing errors by logging the final traceback line and exiting `-1`, and prints `gh.get_metadata_structs()`.

State and persistence: reads input headers and optional include file; writes only stdout/stderr.

Dependencies and integration: depends on `headerlib.container.GlobalHierarchy` and `HeaderFilePreprocessorException`. It is a standalone helper around the Python headerlib stack.

Risks: comma-separated filenames cannot represent filenames containing commas. Missing include files are not caught separately. Error reporting intentionally truncates traceback detail.

Test signals: expected output for `test_headers/th_a.h,th_b.h` is the main manual/legacy regression path.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-headerparser/headerparser.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-headerparser/test_headers/th_a.h -->
# sources/test-tools/syzkaller/tools/syz-headerparser/test_headers/th_a.h

Purpose: fixture header for the legacy Python header parser, focused on struct references, pointer typing, comments, bool fields, and unknown typedef-like names.

Important APIs and flow: header guard wraps macros and `struct A`, whose fields include `struct B* B_item`, `const char* char_ptr`, `unsigned int an_unsigned_int`, two bools, and `some_type var`.

State and persistence: declarations only.

Dependencies and integration: intended to be parsed alongside `th_b.h`, which defines `struct B` and enum/union fixtures. Comments exercise preprocessing and parser tolerance.

Risks: `some_type` is intentionally unresolved and may pass through as a native type string. `const char*` handling depends on pycparser and type formatting.

Test signals: confirms `GlobalHierarchy` can link `struct B*`, map char pointers, and preserve unknown types in metadata output.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-headerparser/test_headers/th_a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-headerparser/test_headers/th_b.h -->
# sources/test-tools/syzkaller/tools/syz-headerparser/test_headers/th_b.h

Purpose: companion fixture header for the Python header parser, covering enum declarations, simple structs, and anonymous unions inside structs.

Important APIs and flow: includes `<linux/types.h>`, defines `enum random_enum`, `struct B` with two unsigned long fields, and `struct struct_containing_union` with an int and anonymous union containing `char* a_char` and `struct B* B_ptr`.

State and persistence: declarations only.

Dependencies and integration: parsed with `th_a.h` to supply the referenced `struct B`. Anonymous union fields test dotted field flattening in `StructWalker`.

Risks: pycparser preprocessing must handle the Linux include or be given compatible include lines. Anonymous union flattening may skip malformed parentless cases.

Test signals: validates unsigned long mapping, enum handling, nested anonymous union traversal, and cross-header struct linking.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-headerparser/test_headers/th_b.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-hubtool/hubtool.go -->
# sources/test-tools/syzkaller/tools/syz-hubtool/hubtool.go

Purpose: `syz-hubtool` uploads local reproducers and/or corpus programs to syz-hub and can drain reproducers from the hub for a manager.

Important APIs and flow: `main` parses target and hub credentials plus repro/corpus/workdir/drain flags, resolves `prog.Target`, expands workdir paths into crash repro glob and corpus DB path, loads repro programs with `loadProgs` and corpus DB with `loadCorpus`, connects with `rpctype.NewRPCClient`, obtains an auth token from `pkg/auth` when no key is supplied, calls `Hub.Connect` with corpus, optionally calls `Hub.Sync` with repros, and in drain mode loops `Hub.Sync` with `NeedRepros` until no data remains. `loadProgs` glob-expands, reads, deserializes, and deduplicates programs by raw bytes. `loadCorpus` reads a corpus DB and serializes each program.

State and persistence: no local writes. Persistent state changes happen remotely in syz-hub. It reads crash repro files and corpus DBs.

Dependencies and integration: uses syzkaller RPC types, auth token cache, corpus DB reader, target deserializer, and hub RPC methods.

Risks: missing hub address/client/manager is not validated before RPC. Dedup is byte-based before canonical serialization for repro files. Drain can run for a long time. Auth token retrieval depends on environment and HTTP client behavior.

Test signals: no direct test. Practical signal is successful Hub.Connect/Hub.Sync and hub-side corpus/repro counts.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-hubtool/hubtool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-imagegen/combinations.go -->
# sources/test-tools/syzkaller/tools/syz-imagegen/combinations.go

Purpose: this Linux-only helper computes representative parameter combinations for filesystem image generation, either all combinations or a bounded covering array.

Important APIs and flow: `CoveringArray(params, n)` incrementally extends rows by parameter. If all combinations fit within `n` or `n == 0`, it performs full cartesian expansion. Otherwise it uses `pairCoverage` to choose values that maximize newly covered pairs, then triples, and duplicates rows until reaching `n` or no additional coverage is gained. Rows are sorted deterministically and converted from value indexes to strings. `rowToPairCombos` emits pair or triple coverage keys, also adding a value-diversity singleton encoded in `third`. `extendRow` clones before append.

State and persistence: pure in-memory algorithm, no IO.

Dependencies and integration: used by `imagegen.go` to reduce huge mkfs flag spaces while preserving broad pair/triple coverage.

Risks: greedy algorithm is deterministic but not guaranteed minimal or globally optimal. Empty params return no rows. The synthetic singleton coverage uses `newID+1` positions to avoid zero values but is internal only.

Test signals: `combinations_test.go` fixes behavior for full binary combinations and a bounded pairwise case.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-imagegen/combinations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-imagegen/combinations_test.go -->
# sources/test-tools/syzkaller/tools/syz-imagegen/combinations_test.go

Purpose: this Linux-only test file locks down the expected output of `CoveringArray`.

Important APIs and flow: `TestFullCombinations` checks empty input, a single-value three-parameter case, and full binary cartesian expansion when `n == 0`. `TestPairCombinations` checks the current greedy bounded output for three binary parameters and `n == 4`.

State and persistence: no state; pure tests.

Dependencies and integration: uses `testify/assert`.

Risks: bounded covering arrays can have multiple valid answers; the test intentionally pins the current algorithm's deterministic output to catch accidental changes.

Test signals: direct regression signal for imagegen flag enumeration stability.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-imagegen/combinations_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-imagegen/imagegen.go -->
# sources/test-tools/syzkaller/tools/syz-imagegen/imagegen.go

Purpose: `syz-imagegen` generates syzkaller seed programs under `sys/linux/test/` for `syz_mount_image$...` and `syz_read_part_table` by creating filesystem images with many mkfs flag combinations, compressing/encoding them, and validating the resulting programs.

Important APIs and flow: `FileSystem` describes name, syscall suffix, minimum size, read-only flag, fixed mkfs flags, combinatorial flag groups, max seeds, and optional custom mkfs function. `fileSystems` enumerates many filesystems and partition tables with custom command handling where needed. `main` handles list/debug/populate/keep/fs/from_json flags, loads Linux/AMD64 target, appends empty images for mount-image syscalls without configured mkfs support, enumerates images, creates a populated template dir, runs image generation across `runtime.NumCPU` workers, and prints results. `generateImages` filters filesystems and deletes old generated files. `enumerateFlags` uses `CoveringArray`. `Image.generate` doubles image size up to 128 MiB until `generateSize` works. `generateSize` creates/truncates disk, runs mkfs/custom mkfs, optionally re-execs under sudo to mount/populate, reads and hashes image data, writes a syzkaller program with base64-compressed image data, deserializes/serializes it for validation, and writes the generated seed file. `populate` uses loop devices and mount; `populateDir` creates files, links, symlinks, and xattrs.

State and persistence: modifies `sys/linux/test/<prefix>_<index>` and optional `.img` files, creates temp template dirs, loop devices during population, and removes old generated seeds per filesystem. It may invoke sudo for writable filesystem population.

Dependencies and integration: depends on many external mkfs tools, `fdisk`, `losetup`, `mount`, `sudo`, syzkaller `pkg/image` encoding, target descriptions, program deserialization, and OS utilities. Generated outputs become checked-in syzkaller test seeds.

Risks: destructive removal of matching generated seed files; host-level sudo/mount/loop-device side effects; external tool availability and version-specific behavior; large disk usage; image duplicates; fixed max size may fail some combinations. Custom fdisk failure detection relies on ANSI red color markers. JSON-loaded filesystems can add arbitrary mkfs command behavior via default fields only, not functions.

Test signals: `combinations_test.go` covers flag-space selection. Runtime validation deserializes generated programs and serializes for execution, providing a strong self-check during generation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-imagegen/imagegen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-kcidb/kcidb.go -->
# sources/test-tools/syzkaller/tools/syz-kcidb/kcidb.go

Purpose: `syz-kcidb` converts a syzbot dashboard bug report into KCIDB data and either publishes it to KCIDB or writes it to a JSON file.

Important APIs and flow: `main` parses KCIDB REST/token, dashboard client/address/key, bug ID, input file, and output file flags. It reads a `dashapi.BugReport` from `-input` JSON when supplied, otherwise loads it from dashboard via `dashapi.New` and `LoadBug`. It enables `kcidb.Validate`, creates a KCIDB client with origin `syzbot`, defers close, then calls `PublishToFile` when `-output` is set or `Publish` otherwise.

State and persistence: reads optional bug JSON, writes optional KCIDB JSON, or publishes to the REST API. No other local state.

Dependencies and integration: depends on dashboard API types, `pkg/kcidb`, context, and `tool.Fail`.

Risks: constants for project/topic are defined but unused in this file. Missing flags are not locally validated and will fail in downstream clients. Publishing is high-impact remote state.

Test signals: no direct test. File-output mode is the safest integration test path because it exercises conversion without remote submission.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-kcidb/kcidb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-kconf/kconf.go -->
# sources/test-tools/syzkaller/tools/syz-kconf/kconf.go

Purpose: `syz-kconf` generates Linux kernel config files for dashboard instances from YAML config fragments and a kernel source tree.

Important APIs and flow: `main` opens a Linux repo, parses the main spec, checks config feature constraints, groups instances by kernel revision, checks out each revision, determines release tag, and generates matching instances in parallel. `Context.generate` creates a temp build dir, selects target arch from features, parses Kconfig, derives release features, runs `mrproper` when needed, executes configured shell commands, parses `.config`, adds dependent USB/HID distro configs unless baseline, applies requested configs, converts modules to yes unless module mode, explicitly disables missing bool/tristate configs, writes `.config` and a `.tmp` debug copy, runs `olddefconfig`, verifies final config, converts modules to no if needed, and writes the generated config header plus serialized config and verbatim content. Supporting methods run shell/make commands, apply choice configs, verify optional/selected configs, add dependent configs from distro fragments, set release feature flags, and replace variables.

State and persistence: checks out and may clean the kernel source repo, creates temp build dirs, writes generated `<instance>.config` and `<instance>.config.tmp` files beside the spec, and reads many YAML fragments and Kconfig files.

Dependencies and integration: uses `pkg/vcs`, `pkg/kconfig`, Linux build helpers, target metadata, YAML parser via `parser.go`, and external `make`.

Risks: kernel checkout/build side effects, long-running make commands, parallel generation sharing one source dir per revision, feature mistakes causing incorrect configs, and `.tmp` debug files intentionally left on verification failure. `checkConfigs` warns on `CONFIG_` prefixes but returns all accumulated problems as an error.

Test signals: `kconf_test.go` covers release tag parsing and YAML node parsing. Full generation requires integration tests with a kernel tree.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-kconf/kconf.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-kconf/kconf_test.go -->
# sources/test-tools/syzkaller/tools/syz-kconf/kconf_test.go

Purpose: this test file covers low-level parsing helpers used by `syz-kconf`.

Important APIs and flow: `TestReleaseTag` checks `releaseTagImpl` against Makefile snippets for stable `v<major>.<minor>` extraction and a missing-version error. `TestParseNode` unmarshals YAML list entries and checks `parseNode` for bare yes configs, integer values, quoted strings, `n`, list forms with yes/no/int, and constraints.

State and persistence: no files are written; all inputs are inline strings.

Dependencies and integration: uses `kconfig.No`, `yaml.v3`, and Go testing.

Risks: tests do not cover merge/override semantics, feature matching, Kconfig verification, or actual kernel config generation.

Test signals: direct regression signal for the parser primitives most likely to break due to YAML typing/style changes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-kconf/kconf_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-kconf/parser.go -->
# sources/test-tools/syzkaller/tools/syz-kconf/parser.go

Purpose: this file parses `syz-kconf` YAML specs into `Instance` objects with kernel, compiler, shell, features, verbatim text, and config entries.

Important APIs and flow: data types include `Instance`, `Config`, `Kernel`, `Shell`, and `Features`. `Features.Match` evaluates positive and negative constraints. `parseMainSpec` reads the main YAML, preserves unused feature declarations under `_`, creates normal and `-base` instances with baseline/base-config features, and expands includes. `parseInstance` initializes features, reads included bit files, merges matching fragments, and for reduced instances turns excluded non-reduced yes/no configs into weak disables. `mergeFile` sets singleton kernel/compiler/linker fields, prepends shell commands, appends verbatim blocks, and merges configs. `mergeConfig` parses a YAML node, handles `override`, `optional`, `weak`, and `append`, detects duplicates, appends quoted string values, and records file/line metadata. `parseNode` supports bare names, scalar int/string/no values, and list syntax mixing value and constraints. `Errors` accumulates formatted messages.

State and persistence: reads YAML files only and returns in-memory instances. File and line metadata are preserved for diagnostics.

Dependencies and integration: uses `pkg/kconfig`, `pkg/vcs` validation helpers, `yaml.v3`, slices, and filesystem reads. Consumed by `kconf.go`.

Risks: map iteration over one-key YAML maps takes the first entry; malformed multi-key nodes are not explicitly rejected. Append requires quoted strings. Override without existing non-optional config is an error. Reduced-mode inversion only applies to yes/no values.

Test signals: `kconf_test.go` covers `parseNode`; broader merge behavior currently relies on integration use.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-kconf/parser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-linter/linter.go -->
# sources/test-tools/syzkaller/tools/syz-linter/linter.go

Purpose: `syz-linter` is syzkaller's custom Go analyzer plugin, bundling project-specific style/bug checks with selected standard analyzers and the modernize suite.

Important APIs and flow: `New` returns `SyzAnalyzer` plus analyzers for atomic alignment, copylocks, deep-equal errors, nilness, struct tags, waitgroups, HTTP response handling, and modernize. `run` walks each AST file, tracks statement lines, dispatches node-specific checks, then checks comments and top-level declaration spacing. Custom checks include comment format and punctuation, string `len` comparisons to zero, grouped function args, context argument position/name, flag naming/descriptions, manual slice clone, log/error message capitalization/newline/period rules, redundant var declarations with type and value, min/max if statements, loop variable self-assignment, `interface{}` to `any`, sort API modernization, range-over-int loop modernization, while-style loop scoping, manual map-key extraction followed by sort, `strings.Index` plus slicing, and multi-line struct literals with multiple fields per line.

State and persistence: analyzer-only; no writes. It reports diagnostics through `analysis.Pass`.

Dependencies and integration: uses Go AST/types/printer/token packages and `golang.org/x/tools/go/analysis`. It is intended for golangci-lint plugin use; `main` keeps `New` reachable.

Risks: many checks are heuristic and can produce false positives, especially string/log formatting, sort modernization, and strings.Index slicing. `fmt.Sprintf("%v.%v", fun.X, fun.Sel)` is syntax-string based, not full object resolution. Type info must be available for several checks. Some modern Go version assumptions are embedded, e.g. loop variables since Go 1.22.

Test signals: `linter_test.go` runs `analysistest` over fixture package `lintertest`; the assigned `pkg/tool/tool.go` stub supports expected diagnostics involving `tool.Fail*`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-linter/linter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-linter/linter_test.go -->
# sources/test-tools/syzkaller/tools/syz-linter/linter_test.go

Purpose: this test wires the custom analyzer into Go's analysistest framework.

Important APIs and flow: `TestLinter` calls `analysistest.Run(t, osutil.Abs("testdata"), SyzAnalyzer, "lintertest")`, which compiles fixture packages under `testdata/src` and checks `// want` diagnostics.

State and persistence: read-only testdata use; no writes.

Dependencies and integration: depends on `pkg/osutil.Abs`, `golang.org/x/tools/go/analysis/analysistest`, and the `SyzAnalyzer` symbol.

Risks: this only runs the custom analyzer, not the full `New` analyzer bundle. Coverage depends on the unlisted `lintertest` fixture contents.

Test signals: primary direct regression signal for custom linter diagnostics and fixture import resolution.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-linter/linter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-linter/testdata/src/github.com/google/syzkaller/pkg/tool/tool.go -->
# sources/test-tools/syzkaller/tools/syz-linter/testdata/src/github.com/google/syzkaller/pkg/tool/tool.go

Purpose: this tiny test fixture provides a stub `github.com/google/syzkaller/pkg/tool` package for linter analysistest imports.

Important APIs and flow: package `tool` defines no-op `Failf(msg string, args ...interface{})` and `Fail(err error)` functions.

State and persistence: none.

Dependencies and integration: imported by linter test packages that need `tool.Failf`/`tool.Fail` symbols without depending on the real syzkaller package.

Risks: signatures must stay compatible with fixture expectations. The use of `interface{}` may itself be intentional testdata and should not be updated casually.

Test signals: successful fixture compilation during `analysistest.Run` confirms this stub is sufficient.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-linter/testdata/src/github.com/google/syzkaller/pkg/tool/tool.go -->
