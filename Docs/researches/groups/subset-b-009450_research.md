# subset-b-009450 research

This grouped report covers the requested syzkaller coverage, coverage database, and coverage merger files. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/backend/dwarf.go -->
# sources/test-tools/syzkaller/pkg/cover/backend/dwarf.go

Purpose: implements the shared DWARF-backed coverage backend used by ELF and Mach-O frontends. It discovers sanitizer callback PCs, associates them with symbols and compile units, normalizes source paths, and lazily symbolizes PCs into source frames.

Important APIs/types/functions: `dwarfParams` injects object-format-specific readers; `Arch` describes call scanning for amd64, arm64, and s390x; `makeDWARF` wraps `makeDWARFUnsafe` with panic recovery for DWARF parser failures; `processModule`, `buildSymbols`, `readTextRanges`, `rustRanges`, `symbolizeModule`, `symbolize`, `readCoverPoints`, `objdump`, `CleanPath`, and `archCallInsn` form the main pipeline. `symbolInfo`, `pcRange`, and `Result` carry intermediate symbol/callback state.

Control flow: `makeDWARFUnsafe` launches one goroutine per kernel/module object, each reading symbols, coverage callbacks, text ranges, and compile units. Results are merged, sorted, deduplicated by symbol start, assigned to compile units, path-cleaned, and exposed through `backend.Impl`. Callback discovery prefers direct instruction scanning on supported arches, uses relocation scanning for modules, and falls back to `objdump` on other arches. Symbolization batches PCs by module and runs bounded parallel addr2line instances to control memory.

State and persistence: all state is in-memory (`Impl`, symbolized flags, interner, callback point slices). No persistent writes occur. The interner and `Symbol.Symbolized` flag make repeated symbolization incremental.

Dependencies and integration: depends on Go `debug/dwarf` plus syzkaller `symbolizer`, `mgrconfig`, `vminfo`, `targets`, and object-format frontends. It integrates upward through `backend.Make` and `pkg/cover.ReportGenerator`.

Risks: DWARF5/parser panics are converted to errors but still block coverage. Path normalization is heuristic, especially Android split builds and out-of-tree modules. `buildSymbols` drops symbols without PCs or compile-unit range matches. Compiler KCOV breakage disables strict precision for GCC versions below 14 or unparsable GCC strings. Objdump parsing is architecture-string fragile and intentionally slower.

Test signals: `dwarf_test.go` validates compiler KCOV detection, Android path cleaning, and call-target decoding for arm64/amd64. Broader report tests exercise this backend through compiled test binaries.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/backend/dwarf.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/backend/dwarf_test.go -->
# sources/test-tools/syzkaller/pkg/cover/backend/dwarf_test.go

Purpose: unit-tests high-risk helpers in the DWARF backend: GCC KCOV precision gating, Android source path normalization, and architecture-specific call target decoding.

Important APIs/types/functions: `TestIsKcovBrokenInCompiler`, `TestCleanPathAndroid`, `TestNextCallTargetARM64`, and `TestNextCallTargetAMD64`. Test helper structs `CleanPathAndroidTest` and `NextCallTargetTest` model expected path triples and decoded call targets.

Control flow: compiler-version tests feed representative GCC, g++, clang, and malformed strings into `isKcovBrokenInCompiler`. Android path tests vary delimiters, absolute paths, cache paths, and existence predicates. Call-target tests construct raw instruction byte sequences and pass them to `nextCallTarget` with `arches["arm64"]` or `arches["amd64"]`.

State and persistence: no persistent state; tests use in-memory slices and fake existence functions.

Dependencies and integration: imports only `testing`, but depends on unexported backend internals in the same package. It complements higher-level `report_test.go` by covering deterministic helpers without compiling binaries.

Risks: call-target coverage excludes s390x despite production support. Android path tests use synthetic existence callbacks, so filesystem edge cases remain covered only indirectly. Version parsing expectations encode the current policy that unparseable GCC-like strings are unsafe.

Test signals: failures directly indicate broken callback scanning or path normalization, both of which can cause false callback mismatch errors or missing source files in reports.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/backend/dwarf_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/backend/elf.go -->
# sources/test-tools/syzkaller/pkg/cover/backend/elf.go

Purpose: provides the ELF-specific implementation of the DWARF backend for Linux and other ELF kernels. It reads `.text`, symbol tables, relocations, DWARF ranges, compiler comments, and the Linux PC base.

Important APIs/types/functions: `makeELF`, `getTraceCallbackType`, `elfReadSymbols`, `elfReadTextRanges`, `elfReadTextData`, `elfReadModuleCoverPoints`, `elfGetCompilerVersion`, `elfReadTextSecRange`, `elfReadTextSec`, and `getLinuxPCBase`. Trace callback constants distinguish none, trace-pc, and trace-cmp callbacks.

Control flow: `makeELF` passes ELF reader functions to `makeDWARF`. `elfReadSymbols` scans ELF symbols, keeps function/notype symbols in `.text`, adjusts module starts by module load address, and records sanitizer callback symbol indexes/addresses. `elfReadTextRanges` reads DWARF and applies a KASLR PC fix when `.rela.text` suggests randomized-base debug ranges. `elfReadModuleCoverPoints` scans RELA sections for architecture call relocations into sanitizer callbacks.

State and persistence: no durable state; `symbolInfo` is populated for the active module. The returned section ranges and symbols feed `Impl`.

Dependencies and integration: uses Go `debug/elf`, syzkaller target metadata, module metadata, and manager kernel dirs. It is the primary frontend for Linux coverage and module support.

Risks: symbol filtering allows `STT_NOTYPE` to avoid nested range gaps but may include non-function labels. RELA parsing assumes little-endian `Rela64` and architecture relocation constants. Module symbol indexes are adjusted by `-1`, so malformed relocation tables could panic or misclassify. KASLR fix is approximate and may filter valid ranges.

Test signals: `elf_test.go` covers sanitizer callback name classification. `report_test.go` exercises no-debug-info, no-callback, PIE, and relocation scenarios through `makeELF`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/backend/elf.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/backend/elf_test.go -->
# sources/test-tools/syzkaller/pkg/cover/backend/elf_test.go

Purpose: validates ELF sanitizer callback name classification, including ARM64 veneer names generated by linkers.

Important APIs/types/functions: `TestGetTraceCallbackType` invokes `getTraceCallbackType` and checks `TraceCbNone`, `TraceCbPc`, and `TraceCbCmp` categories.

Control flow: a map from expected callback type to sample symbol names is iterated; any mismatch fails immediately with the tested symbol name.

State and persistence: none.

Dependencies and integration: same-package access to unexported `getTraceCallbackType`; no external fixtures. This protects `elfReadSymbols` and `elfReadModuleCoverPoints`, which rely on callback indexes populated from symbol names.

Risks: coverage is limited to a few symbol forms. New linker-generated sanitizer aliases would require test and production updates.

Test signals: strong unit signal for callback classification, especially preventing `____sanitizer_cov_trace_pc_veneer` from being treated as comparison coverage or ignored.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/backend/elf_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/backend/gvisor.go -->
# sources/test-tools/syzkaller/pkg/cover/backend/gvisor.go

Purpose: implements a non-DWARF backend for gVisor/runsc coverage. gVisor can emit its own `symbolize -all` output, so this backend converts that stream directly into frames and compile units.

Important APIs/types/functions: `makeGvisor`, `gvisorSymbolize`, `gvisorParseLine`, and `gvisorLineRe`. The backend returns `Impl{Units, Frames}` without callback points or lazy symbolization.

Control flow: `makeGvisor` rejects modules, locates `vmlinux` or fallback `runsc`, runs `gvisorSymbolize`, groups frames by source file into compile units, and returns the implementation. `gvisorSymbolize` starts the binary with `symbolize -all`, scans alternating PC and source-location lines, resolves paths under source dir, and attempts a Bazel generated-file fallback. `gvisorParseLine` parses one PC plus one location line into a backend `Frame`.

State and persistence: transient process execution and in-memory frame/unit slices only.

Dependencies and integration: uses `osutil.Command`, syzkaller target/kernel dirs, and `backend.Impl`. It integrates with `pkg/cover` via the same `Impl` shape but bypasses callback verification.

Risks: process cleanup uses deferred `Wait` and `Kill`; scanner token limits may matter on pathological output. Regex only accepts `pkg/...` paths. Generated files under hashed Bazel output paths are only partially recoverable.

Test signals: `gvisor_test.go` parses real saved symbolize outputs and verifies regex extraction for normal, Bazel, and relative paths.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/backend/gvisor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/backend/gvisor_test.go -->
# sources/test-tools/syzkaller/pkg/cover/backend/gvisor_test.go

Purpose: validates parsing of gVisor `symbolize -all` output and the path regex used by the gVisor coverage backend.

Important APIs/types/functions: `TestGvisorParseLine` reads fixture files from `test_data`; `TestGvisorLineRe` checks `gvisorLineRe` path capture.

Control flow: fixture scanning passes a shared scanner through `gvisorParseLine`, which consumes PC and line-info records. Regex tests match sample source paths and compare capture group 2 to the expected `pkg/...` path.

State and persistence: read-only fixture files; no writes.

Dependencies and integration: depends on checked-in `test_data/symbolize_all_gvisor_*` files and same-package backend internals.

Risks: `lineNum` is incremented but not used for diagnostics. Fixture coverage is broad for historical gVisor outputs but does not test process execution or filesystem fallback behavior.

Test signals: parsing failures catch format drift in gVisor symbolize output before report generation loses all gVisor frames.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/backend/gvisor_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/backend/mach-o.go -->
# sources/test-tools/syzkaller/pkg/cover/backend/mach-o.go

Purpose: supplies Mach-O/XNU reader hooks for the shared DWARF backend.

Important APIs/types/functions: `makeMachO`, `machoReadSymbols`, `machoReadTextRanges`, `machoReadTextData`, and `machoReadModuleCoverPoints`.

Control flow: `makeMachO` delegates to `makeDWARF` with Mach-O-specific readers. `machoReadSymbols` opens the binary, finds `__text`, sorts symbol table entries by value, estimates symbol ends from the next symbol or text end, records sanitizer callback indexes, and builds `Symbol` entries. `machoReadTextRanges` opens the companion `.dSYM/Contents/Resources/DWARF/<kernel>` file and feeds DWARF into `readTextRanges`. Text bytes come from `__text`. Module cover points are deliberately unimplemented.

State and persistence: no persisted state. `symbolInfo` and symbol slices are transient.

Dependencies and integration: uses Go `debug/macho`, syzkaller manager dirs and target metadata, and the shared DWARF pipeline. Intended for XNU-style coverage without module support.

Risks: symbol end estimation can be imprecise if non-function symbols interleave. `machoReadSymbols` adds `module.Addr` to start but stores unadjusted `symbEnd`, which is a subtle address-consistency risk. Opened Mach-O files are not explicitly closed in the current code. Module coverage returns an error.

Test signals: no direct tests in this subset. Coverage is indirect only if cross-platform report tests exercise Mach-O, which they currently do not on Linux-only build tags.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/backend/mach-o.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/backend/modules.go -->
# sources/test-tools/syzkaller/pkg/cover/backend/modules.go

Purpose: discovers local kernel and Linux module objects, extracts module names/sizes, and reconciles VM-reported load addresses with local object metadata.

Important APIs/types/functions: `DiscoverModules`, `discoverModulesLinux`, `locateModules`, `getModuleName`, `searchModuleName`, `getKaslrOffset`, and `FixModules`.

Control flow: `DiscoverModules` creates a dummy module for the kernel `.text`, then, for Linux, walks kernel object directories and additional module directories for `.ko` files. Each `.ko` is mapped by module name, keeping first directory priority, and sized from its `.text` section. `getModuleName` prefers `.modinfo` `name=` and falls back to `.gnu.linkonce.this_module`. `FixModules` matches VM modules to local modules by name, subtracts kernel KASLR offset, copies size/path, and drops unknown modules.

State and persistence: all state is in-memory maps/slices. Filesystem walking is read-only.

Dependencies and integration: depends on ELF helpers in `elf.go`, syzkaller `vminfo.KernelModule`, target OS metadata, and logging. It feeds `backend.Make` and callback verification in report generation.

Risks: fallback module-name extraction from `.gnu.linkonce.this_module` returns raw section bytes, potentially including padding. Name fallback in `locateModules` uses `strings.TrimSuffix(filepath.Base(path), "."+filepath.Ext(path))`, which can leave a trailing dot for `.ko` paths. Local/VM mismatches silently drop modules in `FixModules`.

Test signals: `modules_test.go` is manual/skipped unless a module dir flag is provided. Main validation is indirect through report tests and real syz-manager module coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/backend/modules.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/backend/modules_test.go -->
# sources/test-tools/syzkaller/pkg/cover/backend/modules_test.go

Purpose: provides a manual diagnostic test for Linux module discovery.

Important APIs/types/functions: package flag `-module_dir` and `TestLocateModules`.

Control flow: if no module directory is provided, the test skips. Otherwise it calls `locateModules` on the supplied directory and logs name-to-path mappings.

State and persistence: read-only traversal of the user-supplied module directory; no writes.

Dependencies and integration: uses Go `flag` and same-package `locateModules`. It is intended for developer validation against a real Linux build tree.

Risks: not an automated regression test, so module discovery behavior is mostly unguarded in CI. It logs output but has no assertions on expected modules.

Test signals: useful for ad hoc debugging of `.ko` discovery and module-name extraction; weak automated coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/backend/modules_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/backend/pc.go -->
# sources/test-tools/syzkaller/pkg/cover/backend/pc.go

Purpose: normalizes coverage PCs between return-address style values and instruction addresses for different architectures.

Important APIs/types/functions: `PreviousInstructionPC`, `NextInstructionPC`, and `instructionLen`.

Control flow: gVisor PCs bypass adjustment. Other VMs subtract or add an architecture-specific instruction length. ARM clears the low bit after adjustment to normalize THUMB/ARM mode markers. Unknown architectures panic.

State and persistence: pure stateless helpers.

Dependencies and integration: depends on `sys/targets` constants. `report_test.go` uses `PreviousInstructionPC` when converting sanitizer callback return addresses into callback PCs; coverage report endpoints may use these helpers through backend consumers.

Risks: architecture offsets are approximations; amd64/i386 use call length 5, ARM returns 3 then clears the low bit, and MIPS64LE uses 8. Incorrect offsets cause callback mismatch or missed symbols. Panic on new target architectures requires updating this table.

Test signals: no direct test file in this subset; indirect report tests exercise several targets when cross-compilers are available.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/backend/pc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/canonicalizer.go -->
# sources/test-tools/syzkaller/pkg/cover/canonicalizer.go

Purpose: converts coverage PCs/signals between per-instance kernel module load addresses and a canonical module address layout so signals from different fuzzing VMs can be compared.

Important APIs/types/functions: `Canonicalizer`, `CanonicalizerInstance`, `Convert`, `canonicalizerModule`, `NewCanonicalizer`, `NewInstance`, `Canonicalize`, `Decanonicalize`, `findModule`, and `convertPCs`.

Control flow: `NewCanonicalizer` records canonical modules by name and sorted address keys only when module canonicalization is enabled by `flagSignal`. `NewInstance` builds forward and reverse conversion maps between instance and canonical modules, marking modules for discard if missing or size-mismatched. Conversion binary-searches the sorted module base keys; PCs inside known non-kernel modules receive offsets, discarded modules are dropped, and kernel or unknown unmapped PCs are passed through unless not found in a conversion hash.

State and persistence: in-memory module maps and conversion maps only. It logs discarded PC summaries but does not persist state.

Dependencies and integration: uses `vminfo.KernelModule` and `log`. It is designed for manager/RPC paths that ingest fuzzer coverage and fallback signals.

Risks: conversion assumes non-overlapping sorted module address ranges. Missing canonical modules discard coverage, which is correct for changed builds but can hide module coverage if discovery is incomplete. Offset arithmetic casts through `int64`, so very high address differences deserve care.

Test signals: `canonicalizer_test.go` covers nil modules, disabled signals, reordered modules, changing modules, coverage arrays, and bitmap conversion.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/canonicalizer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/canonicalizer_test.go -->
# sources/test-tools/syzkaller/pkg/cover/canonicalizer_test.go

Purpose: exercises canonical and reverse coverage PC conversion across fuzzer instances with different module layouts.

Important APIs/types/functions: local test harness types `RPCServer`, `Fuzzer`, `canonicalizeValue`, helpers `runTest`, `connect`, and `initModules`; tests `TestNilModules`, `TestDisabledSignals`, `TestModules`, and `TestChangingModules`.

Control flow: the fake RPC server initializes the first fuzzer's module list as canonical, then connects additional fuzzers. Tests populate coverage/signature/bitmap arrays, run either canonicalization or decanonicalization, and compare with expected arrays using `reflect.DeepEqual`.

State and persistence: all fake server/fuzzer state is in memory.

Dependencies and integration: imports `vminfo.KernelModule` to mirror real module metadata. It targets public `NewCanonicalizer` and instance conversion methods.

Risks: harness models only simple numeric module names and address ranges. It does not test overlapping modules, zero-size modules, or logging of discarded PCs.

Test signals: strong regression coverage for the intended multi-fuzzer module-address use case, including disabled signal mode and discarding coverage from modules absent in the canonical build.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/canonicalizer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/cover.go -->
# sources/test-tools/syzkaller/pkg/cover/cover.go

Purpose: defines the minimal in-memory coverage set abstraction over raw PCs.

Important APIs/types/functions: `Cover map[uint64]struct{}`, `FromRaw`, `Merge`, `MergeDiff`, and `Serialize`.

Control flow: `FromRaw` initializes a coverage set by merging raw PCs. `Merge` lazily allocates the map and inserts every PC. `MergeDiff` also lazily allocates, mutates the supplied raw slice in place to compact newly seen PCs, inserts them, and returns the new prefix. `Serialize` returns unsorted map keys.

State and persistence: state is only the mutable map held through the pointer receiver. No synchronization is provided.

Dependencies and integration: no external imports. Used wherever syzkaller wants deduplicated coverage PCs and incremental newly-covered signals.

Risks: `MergeDiff` overwrites the input slice, which is documented but easy to misuse. `Serialize` order is nondeterministic and callers must sort if stable output is needed. The type is not concurrent-safe.

Test signals: `cover_test.go` checks nil inputs, merging, diff compaction, and sorted serialized results.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/cover.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/cover_test.go -->
# sources/test-tools/syzkaller/pkg/cover/cover_test.go

Purpose: tests the basic `Cover` set behavior and the per-line range merge logic implemented in `html.go`.

Important APIs/types/functions: `TestMergeDiff` and `TestPerLineCoverage`.

Control flow: `TestMergeDiff` covers nil, empty, full-new, and partially duplicate merges, then sorts `Serialize` output for deterministic comparison. `TestPerLineCoverage` builds covered and uncovered backend ranges spanning single lines, multi-lines, malformed ranges, and overlapping ranges, then compares the produced line chunks.

State and persistence: no persistent state; test slices and maps only.

Dependencies and integration: imports `backend.Range` and `backend.LineEnd` to validate the report-rendering line coverage transformation.

Risks: `TestPerLineCoverage` validates internal chunk shapes, so intentional rendering algorithm changes need expected updates. It does not render HTML, only merge data.

Test signals: catches regressions in both set-diff behavior and the nuanced covered/uncovered/both chunk computation used by HTML and line JSON outputs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/cover_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/file.go -->
# sources/test-tools/syzkaller/pkg/cover/file.go

Purpose: renders merged historical line coverage for a single source file as text or HTML and fetches merge results from BigQuery/GCS-backed coverage exports.

Important APIs/types/functions: `CoverageRenderConfig`, `DefaultTextRenderConfig`, `DefaultHTMLRenderConfig`, `RendFileCoverage`, `GetMergeResult`, `rendResult`, `RendTextLine`, `RendHTMLLine`, and `mainSignalSource`.

Control flow: `RendFileCoverage` fetches the requested file content through a `covermerger.FileVersProvider` and renders every line with the configured renderer. `GetMergeResult` builds a one-job `covermerger.Config`, exports namespace records for a time period, merges them, and returns the first channel result. Rendering optionally shows source explanation, hit count, line number, and escaped HTML.

State and persistence: no persistent state; external reads are file-provider, BigQuery export, and GCS reader operations. Rendering constructs strings in memory.

Dependencies and integration: bridges `pkg/cover`, `pkg/coveragedb`, and `pkg/covermerger`. It is likely used by coverage web handlers for per-file historical coverage.

Risks: `GetMergeResult` appears to return `nil, error` when `mr != nil` and `mr, nil` never happens, likely an inverted condition. The channel read uses a non-blocking `select` after `MergeCSVData`, so it assumes the single result is already buffered. `RendFileCoverage` does not handle a missing file version explicitly beyond empty map lookup.

Test signals: no direct tests in this subset. Integration coverage comes from `covermerger` and `coveragedb` tests, but this file's rendering and `GetMergeResult` branch deserve focused tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/heatmap.go -->
# sources/test-tools/syzkaller/pkg/cover/heatmap.go

Purpose: transforms database file coverage records into hierarchical heatmap template data and renders style/body/JS fragments.

Important APIs/types/functions: `templateHeatmapRow`, `templateHeatmap`, row methods `Filter`, `Transform`, `Sort`, `addParts`, `prepareDataFor`, `Visit`; `FilesCoverageToTemplateData`, `DoHeatMapStyleBodyJS`, `DoSubsystemsHeatMapStyleBodyJS`, `FormatResult`, `Percent` usage, and template helpers.

Control flow: records are inserted into a tree by optional subsystem plus file path parts. Each node aggregates instrumented/covered counts per `TimePeriod`. Columns are sorted by period end date and converted to percentages, covered counts, tooltips, summary values, and file coverage links. Formatting can filter small drops, remove zero-covered files, remove empty directories, and order by coverage drop while rewriting summaries to negative drop counts.

State and persistence: in-memory tree maps/slices. Rendering reads embedded `templates/heatmap.html`; database reads happen via `coveragedb.FilesCoverageWithDetails`.

Dependencies and integration: depends on `coveragedb`, `spannerclient`, embedded templates, and subsystem list side-effect import. It feeds web UI heatmap endpoints.

Risks: `DoSubsystemsHeatMapStyleBodyJS` panics on DB errors while `DoHeatMapStyleBodyJS` returns errors. `FormatResult` calls `slices.Max` on row coverage slices, so callers must avoid rows without coverage data or filter carefully. File coverage links concatenate query parameters without URL escaping.

Test signals: `heatmap_test.go` validates tree construction, date columns, links, and formatting filters/order.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/heatmap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/heatmap_test.go -->
# sources/test-tools/syzkaller/pkg/cover/heatmap_test.go

Purpose: verifies heatmap data construction and formatting transformations.

Important APIs/types/functions: `TestFilesCoverageToTemplateData`, `TestFormatResult`, and helper `makeTimePeriod`.

Control flow: data-construction tests cover empty input, a single file, and a directory tree across two periods, comparing exported fields of `templateHeatmap`. Formatting tests apply `DropCoveredLines0`, `FilterMinCoveredLinesDrop`, and `OrderByCoveredLinesDrop` to small hand-built trees and compare expected pruning, ordering, and negative summaries.

State and persistence: all inputs are in-memory `coveragedb.FileCoverageWithDetails` or template row fixtures.

Dependencies and integration: uses `civil.Date`, `coveragedb.MakeTimePeriod`, and testify assertions. It does not render templates or query Spanner.

Risks: comparisons skip unexported builder and aggregation maps via `assert.EqualExportedValues` for construction tests, so some internal state issues may be invisible. No URL escaping or subsystem heatmap behavior is tested.

Test signals: good coverage for the public heatmap tree semantics that web rendering depends on.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/heatmap_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/html.go -->
# sources/test-tools/syzkaller/pkg/cover/html.go

Purpose: implements coverage report output handlers: HTML, line JSON, raw coverage, raw frame CSV, per-file/function CSV summaries, subsystem/module tables, coverage JSONL, and per-program coverage JSONL.

Important APIs/types/functions: `HandlerParams`, `DoHTML`, `DoLineJSON`, `DoRawCoverFiles`, `CoverageInfo`, `DoCoverJSONL`, `ProgramCoverage`/`FileCoverage`/`FuncCoverage`/`Block`, `DoCoverPrograms`, `DoRawCover`, `DoFilterPCs`, `convertToStats`, `DoFileCover`, `DoSubsystemCover`, `DoModuleCover`, `DoFuncCover`, `fixUpPCs`, `fileContents`, `perLineCoverage`, `mergeRange`, `mergeLine`, `addFunctionCoverage`, `processDir`, `Percent`, and `parseFile`.

Control flow: handlers first filter/fix PCs and prepare file maps through `ReportGenerator`. HTML builds a directory tree, renders source files with span classes for covered/uncovered/both chunks, adds program click metadata, and executes embedded templates. JSONL handlers symbolize callback and program PCs, aggregate frames by PC/file/function, and stream JSON records. CSV/table handlers compute per-file stats and aggregate by subsystem prefixes or module names.

State and persistence: reads source files and embedded templates; writes only to the provided `io.Writer`. `ReportGenerator` frame cache may grow as symbolization is requested.

Dependencies and integration: depends on `backend` range/frame data, `mgrconfig.Subsystem`, embedded templates, and `report.go` file maps. Outputs feed syzkaller web endpoints and CI export paths.

Risks: `DoHTML` assumes `progs[0]` exists when computing `haveProgs`; empty program input can panic. `fileLineContents` has a `start` variable that is not advanced, which can duplicate line classification work. File links and query-like data are mostly template/html escaped but CSV consumers depend on schema stability. `Percent` deliberately caps partial coverage at 99.

Test signals: `cover_test.go` validates range merging; `report_test.go` exercises HTML, CSV, JSONL, and subsystem/file/function outputs through compiled binaries.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/html.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/manager_to_ci.go -->
# sources/test-tools/syzkaller/pkg/cover/manager_to_ci.go

Purpose: combines per-PC coverage JSON records with CI/manager metadata and writes one JSONL record per coverage item.

Important APIs/types/functions: `CIDetails`, `dbCoverageRecord`, generic `WriteJSLine`, and `WriteCIJSONLine`.

Control flow: `WriteCIJSONLine` embeds `CIDetails` and `CoverageInfo` in a `dbCoverageRecord`, then delegates to `WriteJSLine`. `WriteJSLine` marshals to compact JSON, appends a newline, and writes to the target writer.

State and persistence: no internal state. Persistence is caller-defined through the `io.Writer`, commonly a file, pipe, or upload stream.

Dependencies and integration: uses `CoverageInfo` from `html.go`. This is the bridge from manager coverage output to CI/BigQuery ingestion records matching `coveragedb/bq-schema.json`.

Risks: `Timestamp` is a string rather than `time.Time`, so formatting validation is outside this layer. JSON field order is Go struct order, and tests assert the exact compact output. Write failures include only the wrapped write error.

Test signals: `manager_to_ci_test.go` checks exact output for a sample coverage record and metadata set.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/manager_to_ci.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/manager_to_ci_test.go -->
# sources/test-tools/syzkaller/pkg/cover/manager_to_ci_test.go

Purpose: validates JSONL serialization of manager coverage plus CI details.

Important APIs/types/functions: `sampleCoverJSON` and `TestWriteCIJSONLine`.

Control flow: the test unmarshals a sample `CoverageInfo`, writes a combined record into a buffer with `WriteCIJSONLine`, and compares against an exact compact JSON string with trailing newline.

State and persistence: in-memory buffer only.

Dependencies and integration: uses `encoding/json`, testify assertions, `CoverageInfo`, `CIDetails`, and `WriteCIJSONLine`.

Risks: exact string comparison makes field-order changes visible, which is useful for BigQuery schema compatibility but can be brittle if struct field order is intentionally changed.

Test signals: strong guard that manager-to-CI output remains aligned with the expected ingestion shape.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/manager_to_ci_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/report.go -->
# sources/test-tools/syzkaller/pkg/cover/report.go

Purpose: owns the core conversion from raw program PCs to file/function/line coverage structures consumed by HTML, CSV, JSON, and raw report handlers.

Important APIs/types/functions: `ReportGenerator`, `Prog`, `GetPCBase`, `MakeReportGenerator`, internal `file`, `function`, `line`, `fileMap`, `prepareFileMap`, `frame2line`, `coverageCallbackMismatch`, `uniquePCs`, `symbolizePCs`, `fileByFrame`, and `findSymbol`.

Control flow: `MakeReportGenerator` builds a backend `Impl` and appends an `all` subsystem. `prepareFileMap` symbolizes unique program PCs, creates files from compile units, maps PCs to program indexes, checks callback-point membership when precise coverage is enabled, converts frames to covered/uncovered line ranges, computes per-file and per-function PC counts, and sorts functions. `symbolizePCs` finds containing symbols for requested PCs and symbolizes whole symbols once, caching frames and marking symbols.

State and persistence: `ReportGenerator` stores backend data and grows `Frames`; `Symbol.Symbolized` mutates in backend symbols. No files are written here.

Dependencies and integration: depends on `backend.Impl`, `mgrconfig`, target metadata, and module metadata. All report output functions in `html.go` call into this file.

Risks: `findSymbol` uses `pc > s.End` rather than `pc >= s.End`, while symbol ranges elsewhere are `[Start, End)`, creating a boundary inconsistency. Strict callback mismatch errors depend on accurate `CallbackPoints`; module/KASLR issues surface here. `frame2line` fails if no frame matches any covered PC.

Test signals: `report_test.go` is the major integration test, compiling binaries and checking HTML/CSV/JSONL paths and error cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/report.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/report_test.go -->
# sources/test-tools/syzkaller/pkg/cover/report_test.go

Purpose: Linux-only integration tests for report generation across target OS/architecture definitions and multiple binary/debug/coverage configurations.

Important APIs/types/functions: `TestReportGenerator`, `testReportGenerator`, `kcovCode`, `buildTestBinary`, `generateReport`, `checkCSVReport`, `checkJSONLReport`, `TestCoverByFilePrefixes`, and fixtures `sampleJSONLlProgs` plus `makeFileStat`.

Control flow: tests iterate supported targets for the host build OS, compile small C binaries with optional sanitizer coverage, debug info, PIE, and relocation flags, discover modules, build a `ReportGenerator`, optionally run the binary to collect a callback PC, and exercise HTML, subsystem, file, function CSV, coverage JSONL, and per-program JSONL outputs. Expected error regexes cover no coverage callbacks, missing debug info, no PCs, bad PCs, and callback mismatches.

State and persistence: writes temporary source/object/binary files in `t.TempDir`; no repo files modified.

Dependencies and integration: depends on syzkaller target metadata, cross-compilers, `osutil`, `symbolizer`, and backend module discovery. It exercises `backend`, `report.go`, and `html.go` together.

Risks: many subtests skip depending on host, compiler availability, broken compiler metadata, target support, and sanitizer/runtime behavior. PC values are normalized in JSON comparison because exact addresses vary.

Test signals: strongest end-to-end signal for coverage report correctness, including generated JSON schemas and subsystem aggregation exclusions.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/cover/report_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/coveragedb/bq-schema.json -->
# sources/test-tools/syzkaller/pkg/coveragedb/bq-schema.json

Purpose: declares the BigQuery ingestion schema for manager coverage records emitted by `manager_to_ci.go`.

Important fields: required metadata fields `timestamp`, `version`, `fuzzing_minutes`, `arch`, `build_id`, `manager`, `kernel_repo`, `kernel_branch`, `kernel_commit`; source-location fields `file_path`, `func_name`, `sl`, `sc`, `el`, `ec`; coverage fields `hit_count`, `inline`, and `pc`. `pc` is NUMERIC with precision 20 and scale 0 to store full 64-bit-ish PC values.

Control flow: not executable. Its field names align with `CoverageInfo`, `CIDetails`, `covermerger` CSV keys, and BigQuery export queries.

State and persistence: schema governs persistent BigQuery table layout outside the repo.

Dependencies and integration: consumed operationally when creating/updating the `syzkaller.syzbot_coverage.<namespace>` BigQuery tables. `covermerger.InitNsRecords` queries many of these field names.

Risks: descriptions mention "fuzzing hours" while field name says minutes. Typos in descriptions (`StarCol`) are harmless but confusing. Any schema change must be coordinated with manager JSONL output and `covermerger` CSV parser keys.

Test signals: no direct schema test; `manager_to_ci_test.go` and `covermerger` CSV tests indirectly protect selected field names.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/coveragedb/bq-schema.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/coveragedb/coveragedb.go -->
# sources/test-tools/syzkaller/pkg/coveragedb/coveragedb.go

Purpose: persists merged coverage into Spanner, queries coverage summaries/details, computes manager-unique coverage, regenerates file subsystem mappings, and deletes orphaned file rows.

Important APIs/types/functions: `HistoryRecord`, `MergedCoverageRecord`, `JSONLWrapper`, `Coverage`, `SaveMergeResult`, `ReadLinesHitCount`, mutation builders, `NsDataMerged`, `DeleteGarbage`, `FileCoverageWithDetails`, `FileCoverageWithLineInfo`, `SelectScope`, `FilesCoverageStream`, `FilesCoverageWithDetails`, `readCoverageUniq`, `IsComparable`, `UniqCoverage`, `RegenerateSubsystems`, and `getFilePaths`.

Control flow: `SaveMergeResult` decodes JSONL wrappers, creates `files` or `functions` mutations, batches every 1000 records, and appends `merge_history`. Query helpers build Spanner SQL joining `merge_history`, `files`, and `file_subsystems`. Unique coverage reads all-manager and manager-specific line details in parallel, validates comparability, then counts lines whose manager hit count equals total hit count. Garbage collection fetches valid sessions, streams file sessions, and deletes orphan batches with workers.

State and persistence: writes Spanner tables `files`, `functions`, `merge_history`, and `file_subsystems`; reads Spanner through the abstract client. Uses generated UUID sessions and current time for history records.

Dependencies and integration: central database layer for `covermerger`, heatmap rendering, file coverage rendering, and maintenance tasks. Depends on Spanner, civil dates, subsystem matchers, UUIDs, and errgroups.

Risks: `FilesCoverageWithDetails` with an empty `scope.Periods` returns nil before touching a possibly nil client, as tested. `ReadLinesHitCount` errors if more than one DB row matches. `readCoverageUniq` assumes both iterators are sorted by filepath and reports "currupted" on impossible partial-only files. Deferred iterator stops inside loops can accumulate until function return for many periods. Mutation batching is tuned but still sensitive to Spanner index mutation limits.

Test signals: `coveragedb_mock_test.go` verifies save batching and wrapper validation; `coveragedb_test.go` verifies empty and unique coverage query behavior with mocks.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/coveragedb/coveragedb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/coveragedb/coveragedb_mock_test.go -->
# sources/test-tools/syzkaller/pkg/coveragedb/coveragedb_mock_test.go

Purpose: tests `SaveMergeResult` persistence behavior using generated Spanner client mocks.

Important APIs/types/functions: `spannerMockTune` and `TestSaveMergeResult`.

Control flow: table-driven cases feed empty/wrong JSONL, one merged coverage record, one function-lines record, two records, and 2000 records. Mock expectations verify `Apply` call counts and mutation batch sizes, including two 1000-record batches plus one history-only batch for 2000 inputs.

State and persistence: no real Spanner writes; mocks record calls.

Dependencies and integration: uses `coveragedb/mocks.SpannerClient`, Spanner mutation types, `json.Decoder`, and testify mock matchers.

Risks: mutation content is not inspected beyond count. Empty JSON object is expected to error because `JSONLWrapper` has neither `MCR` nor `FL`.

Test signals: good signal for batching, wrapper validation, row-count accounting, and nil/wrong JSON paths in the persistence ingestion flow.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/coveragedb/coveragedb_mock_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/coveragedb/coveragedb_test.go -->
# sources/test-tools/syzkaller/pkg/coveragedb/coveragedb_test.go

Purpose: tests coverage detail queries, especially manager-unique coverage computation, with mocked Spanner iterators.

Important APIs/types/functions: `TestFilesCoverageWithDetails`, `emptyCoverageDBFixture`, `fullCoverageDBFixture`, and `newRowIteratorMock`.

Control flow: test cases cover empty scope, empty DB with and without unique coverage, full coverage with empty partial result, exact manager/full match, and partial manager coverage. Fixture helpers build mock clients whose `Single().Query()` returns row iterators populated by `FileCoverageWithLineInfo` values.

State and persistence: in-memory mocks only.

Dependencies and integration: uses generated mocks for `SpannerClient`, `ReadOnlyTransaction`, `RowIterator`, and `Row`; imports `iterator.Done` to emulate Spanner completion.

Risks: only happy-path unique comparisons are tested; mismatch/corrupted partial-only cases are not asserted. SQL statement contents are not inspected by mocks.

Test signals: validates the subtle semantics that unique manager coverage uses full instrumentation counts but only counts lines whose manager hit count exactly accounts for all hits.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/coveragedb/coveragedb_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/coveragedb/functions.go -->
# sources/test-tools/syzkaller/pkg/coveragedb/functions.go

Purpose: maps file/line pairs to function names using the `functions` Spanner table generated during coverage merging.

Important APIs/types/functions: `FuncLines`, `MakeFuncFinder`, `FunctionFinder`, `addLine`, and `FileLineToFuncName`.

Control flow: `MakeFuncFinder` queries function records for namespace/date/duration, iterates rows into `FuncLines`, and records each line in a nested map keyed by file path then line number. `FileLineToFuncName` returns the mapped function or an explicit missing-file/missing-line error.

State and persistence: reads Spanner; stores the lookup in memory. No writes.

Dependencies and integration: depends on `spannerclient`, Spanner SQL, `TimePeriod`, and `covermerger` output of `FuncLines`. Used by UI/report paths that need function names for line-level coverage.

Risks: later rows overwrite earlier function names for the same file/line. There is no namespace cache or partial loading. Query reads all functions for a period, which may be heavy.

Test signals: no direct tests in this subset. It is indirectly tied to `covermerger` function-line output and database save tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/coveragedb/functions.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/coveragedb/init_db.sh -->
# sources/test-tools/syzkaller/pkg/coveragedb/init_db.sh

Purpose: initializes the Cloud Spanner `coverage` database schema used by `coveragedb.go`.

Important operations: drops and recreates tables `files`, `functions`, `merge_history`, and `file_subsystems`; creates index `merge_history_session`.

Control flow: the script uses `set -e` and `pipefail`, then runs sequential `gcloud spanner databases ddl update` calls against instance `syzbot`, project `syzkaller`, database `coverage`. Table DDL strings are built with `echo -n` and passed as `--ddl`.

State and persistence: destructive persistent database changes. It drops existing tables before creating replacements, so it deletes stored coverage data.

Dependencies and integration: requires authenticated `gcloud`, Cloud Spanner access, and schema alignment with `coveragedb` struct field names and mutation builders.

Risks: highly destructive and hard-coded to production-looking project/instance names. It uses PostgreSQL-like type names (`text`, `bigint`, `timestamptz`) in Spanner DDL, implying a specific dialect. No confirmation prompt or environment guard exists.

Test signals: no tests. Operational safety depends on manual usage discipline.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/coveragedb/init_db.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/coveragedb/mocks/ReadOnlyTransaction.go -->
# sources/test-tools/syzkaller/pkg/coveragedb/mocks/ReadOnlyTransaction.go

Purpose: generated testify mock for the `spannerclient.ReadOnlyTransaction` interface.

Important APIs/types/functions: `NewReadOnlyTransaction`, `ReadOnlyTransaction`, `ReadOnlyTransaction_Expecter`, `EXPECT`, `Query`, and typed call helper `ReadOnlyTransaction_Query_Call`.

Control flow: constructor registers test cleanup to assert expectations. `Query` delegates to `mock.Called(ctx, statement)`, panics if no return value is specified, and type-asserts a `spannerclient.RowIterator`. Helper methods support `Run`, `Return`, and `RunAndReturn`.

State and persistence: stores mock call expectations in memory; no database access.

Dependencies and integration: used by `coveragedb_test.go` to mock `client.Single().Query(...)`. Depends on `cloud.google.com/go/spanner`, `spannerclient`, and testify mock.

Risks: generated code should not be manually edited. Type assertions panic if tests return the wrong type. Expectations assert exact calls unless matchers are used.

Test signals: this file is test infrastructure; its correctness is exercised whenever coverage DB tests use read-only query mocks.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/coveragedb/mocks/ReadOnlyTransaction.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/coveragedb/mocks/Row.go -->
# sources/test-tools/syzkaller/pkg/coveragedb/mocks/Row.go

Purpose: generated testify mock for the `spannerclient.Row` interface.

Important APIs/types/functions: `NewRow`, `Row`, `Row_Expecter`, `EXPECT`, `ToStruct`, and `Row_ToStruct_Call`.

Control flow: `ToStruct` delegates to mock expectations and supports callback population through `Run`, which tests use to fill the pointed destination struct.

State and persistence: in-memory mock expectations only.

Dependencies and integration: used by row iterator fixtures in `coveragedb_test.go` to emulate Spanner row decoding. Depends on testify mock.

Risks: `ToStruct` panics when no return is specified. Because `p` is `any`, test callbacks must type-assert the correct struct pointer.

Test signals: supports deterministic DB query tests without real Spanner.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/coveragedb/mocks/Row.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/coveragedb/mocks/RowIterator.go -->
# sources/test-tools/syzkaller/pkg/coveragedb/mocks/RowIterator.go

Purpose: generated testify mock for `spannerclient.RowIterator`.

Important APIs/types/functions: `NewRowIterator`, `RowIterator`, `Next`, `Stop`, and typed helper call structs for both methods.

Control flow: `Next` returns a mocked `spannerclient.Row` and error, supporting either static returns or function returns. `Stop` records a call and has helper methods for return/run behavior.

State and persistence: mock expectations only.

Dependencies and integration: used by coverage DB tests to stream fake rows and emit `iterator.Done`. Depends on `spannerclient` and testify mock.

Risks: missing `Stop` expectations can fail tests because production code defers `Stop`. Type assertions panic on wrong mocked return types.

Test signals: enables precise query lifecycle tests, especially ensuring iterators are stopped.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/coveragedb/mocks/RowIterator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/coveragedb/mocks/SpannerClient.go -->
# sources/test-tools/syzkaller/pkg/coveragedb/mocks/SpannerClient.go

Purpose: generated testify mock for the `spannerclient.SpannerClient` interface.

Important APIs/types/functions: `NewSpannerClient`, `SpannerClient`, `Apply`, `Close`, `Single`, and typed helper call structs.

Control flow: `Apply` handles variadic `spanner.ApplyOption` by including options in `mock.Called` only when present, then returns a commit timestamp and error. `Single` returns a mocked read-only transaction. `Close` records a call.

State and persistence: in-memory expectations only.

Dependencies and integration: used by `coveragedb_mock_test.go`, `coveragedb_test.go`, and `covermerger_test.go` to validate persistence and query flows without real Spanner.

Risks: variadic option handling must match expectation setup. Return type mistakes panic. Generated code should remain in sync with the interface.

Test signals: core test infrastructure for Spanner mutation count assertions and query fixture assembly.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/coveragedb/mocks/SpannerClient.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/coveragedb/spannerclient/spanner_client.go -->
# sources/test-tools/syzkaller/pkg/coveragedb/spannerclient/spanner_client.go

Purpose: defines small interfaces over Cloud Spanner and adapts the real Spanner client into those interfaces for testability.

Important APIs/types/functions: interfaces `SpannerClient`, `ReadOnlyTransaction`, `RowIterator`, `Row`; proxy types `SpannerClientProxy`, `SpannerReadOnlyTransactionProxy`, `SpannerRowIteratorProxy`; and `NewClient`.

Control flow: proxy methods forward `Close`, `Apply`, `Single`, `Query`, `Next`, and `Stop` to the real Spanner types. `NewClient` constructs a database path under `projects/<projectID>/instances/syzbot/databases/coverage` and returns a proxy.

State and persistence: wraps a real Spanner client, so callers can read/write the coverage DB. The file itself holds only a client pointer.

Dependencies and integration: used throughout `coveragedb` and mocked by generated files. Depends on `cloud.google.com/go/spanner`.

Risks: database instance/name are hard-coded except project ID. `NewClient` returns a proxy even when `spanner.NewClient` returns an error, with the underlying client potentially nil. Interface surface is intentionally small but must be updated when callers need more Spanner behavior.

Test signals: no direct tests; generated mocks and coverage DB tests validate the interface contract.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/coveragedb/spannerclient/spanner_client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/coveragedb/time_period.go -->
# sources/test-tools/syzkaller/pkg/coveragedb/time_period.go

Purpose: models daily, monthly, and quarterly coverage aggregation periods and computes which periods require merging.

Important APIs/types/functions: `TimePeriod`, `DatesFromTo`, `MakeTimePeriod`, constants `DayPeriod`, `MonthPeriod`, `QuarterPeriod`, `AllPeriods`, `MinMaxDays`, `PeriodOps`, `GenNPeriodsTill`, period op structs, `PeriodsToMerge`, and `AtMostNLatestPeriods`.

Control flow: period ops normalize arbitrary dates to the last day of the containing day/month/quarter and compute period length. `MakeTimePeriod` validates that a target date points to the period end. `GenNPeriodsTill` walks backward by period lengths and returns chronological order. `PeriodsToMerge` aggregates source daily rows by target period end, removes periods already merged with matching row counts, and returns missing/stale periods newest first.

State and persistence: pure date/value functions; no persistence.

Dependencies and integration: uses `civil.Date` for date-only values. `coveragedb` queries and `covermerger.InitNsRecords` use these ranges/durations.

Risks: `PeriodsToMerge` constructs returned `TimePeriod` values without setting `Type`, unlike `MakeTimePeriod`/`GenNPeriodsTill`. Quarter day calculations manually decrement months and rely on `civil.Date` month behavior. Leap years are covered by tests.

Test signals: `time_period_test.go` covers day/month/quarter ops, merge-period detection, latest-period limiting, and invalid quarter end dates.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/coveragedb/time_period.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/coveragedb/time_period_test.go -->
# sources/test-tools/syzkaller/pkg/coveragedb/time_period_test.go

Purpose: validates date-period calculations and merge scheduling logic for coverage aggregation.

Important APIs/types/functions: `TestDayPeriodOps`, `TestMonthPeriodOps`, `TestQuarterPeriodOps`, `TestPeriodsToMerge`, helper `makeTimePeriod`, `TestAtMostNLatestPeriods`, and `TestMakeTimePeriod`.

Control flow: tests check last-period date, period validity, period day counts, and generated period sequences for day/month/quarter including leap-year February. `TestPeriodsToMerge` compares daily source rows against already-merged day/month/quarter periods to identify missing or stale merges. Latest-period and invalid date behavior are also asserted.

State and persistence: no external state.

Dependencies and integration: uses `civil.Date` and testify assertions. Tests directly cover `time_period.go`.

Risks: tests use helper-created `TimePeriod` values without `Type` for some merge expectations, matching current `PeriodsToMerge` behavior. They do not test `MinMaxDays` or unknown period errors.

Test signals: strong date math coverage, especially for aggregation correctness around month/quarter boundaries.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/coveragedb/time_period_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/bq_csv_reader.go -->
# sources/test-tools/syzkaller/pkg/covermerger/bq_csv_reader.go

Purpose: exports raw namespace coverage rows from BigQuery to GCS as gzipped CSV shards and exposes them as one concatenated reader.

Important APIs/types/functions: `InitNsRecords`, `initGCSMultiReader`, `gcsGZIPMultiReader`, `Read`, and `Close`.

Control flow: `InitNsRecords` validates namespace, file path, and optional commit, creates a BigQuery client, exports grouped coverage rows for a date range to `gs://syzbot-temp/bq-exports/<uuid>/*.csv.gz`, waits for job completion, then returns a GCS multi-reader. `initGCSMultiReader` lists exported objects. `Read` lazily opens each GCS file, wraps it in gzip, reads until EOF, closes it, and advances to the next file. `Close` closes the current gzip and file readers.

State and persistence: creates temporary GCS export objects and reads them; no cleanup is visible here. Reader state tracks remaining paths and current readers.

Dependencies and integration: BigQuery, GCS client abstraction, validators, UUID, and civil dates. Used by `cover.GetMergeResult` and historical merge jobs.

Risks: SQL is built with `fmt.Sprintf`; validation mitigates namespace/file/commit but date and namespace still influence table/query strings. Temporary GCS exports are not deleted. GCS object ordering follows list order and may affect CSV header repetition handling. BigQuery client is not closed.

Test signals: `bq_csv_reader_test.go` focuses on the multi-gzip reader, including corrupt shard behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/bq_csv_reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/bq_csv_reader_test.go -->
# sources/test-tools/syzkaller/pkg/covermerger/bq_csv_reader_test.go

Purpose: tests `gcsGZIPMultiReader` over one or more mocked gzipped GCS files.

Important APIs/types/functions: `TestGCSGZIPMultiReader_Read`, `makeGCSClientMock`, `readCloserMock`, and `gzBytes`.

Control flow: table cases build gzipped byte payloads, configure a mocked GCS client to return per-byte readers, read all bytes from the multi-reader, close it, and compare bytes/errors. Cases cover single file, multiple reads, multiple files, and a corrupt final gzip payload.

State and persistence: no real GCS; in-memory mocks only.

Dependencies and integration: uses syzkaller GCS mock package, testify mock/assert, gzip, and `io.ReadAll`.

Risks: mock file reader returns one byte per read, which exercises streaming but not larger buffer behavior. It does not test `initGCSMultiReader` listing or BigQuery export.

Test signals: good coverage for sequential shard reading and cleanup/error propagation on gzip header failures.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/bq_csv_reader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/covermerger.go -->
# sources/test-tools/syzkaller/pkg/covermerger/covermerger.go

Purpose: merges CSV coverage rows collected across kernel commits into line coverage for a target base commit and optionally emits gzipped JSONL records for Spanner ingestion.

Important APIs/types/functions: CSV key constants, `FileRecord`, `RepoCommit`, `MergeResult`, `FileCoverageMerger`, `MergeCSVWriteJSONL`, `mergedCoverageRecords`, `bestFuncName`, `batchFileData`, `makeRecord`, `Config`, `FileMergeResult`, `MergeCSVData`, `mergeChanData`, and `groupFileRecords`.

Control flow: `MergeCSVData` reads the first CSV row as schema, streams rows into `FileRecord`s, skips repeated headers, groups contiguous records by file path, and merges groups concurrently according to `Config.Jobs`. Each file batch fetches all required file versions, builds a line merger, and emits a `FileMergeResult`. `MergeCSVWriteJSONL` concurrently consumes results, writes a description then function-line and manager/all coverage wrappers to a gzip JSON encoder, and counts instrumented/covered lines.

State and persistence: in-memory merge state; optional writer receives compressed JSONL. Source file contents are fetched through a `FileVersProvider`.

Dependencies and integration: imports `coveragedb` record types, `go-diff` indirectly through line merger, errgroup, and logging. Feeds `coveragedb.SaveMergeResult`.

Risks: grouping assumes CSV rows are ordered by `file_path`; unsorted input can produce multiple results for one file. If `Config.Jobs` is zero, no workers drain groups. `groupFileRecords` emits an empty filename group on empty input after schema. `MergeCSVWriteJSONL` encodes a raw `HistoryRecord` before JSONL wrappers, so consumers must read it separately as tests do.

Test signals: `covermerger_test.go` covers JSONL-to-Spanner integration, manager aggregation, file deletion, code deletion, line additions/changes, zero-hit instrumentation, and function-name selection.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/covermerger.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/covermerger_test.go -->
# sources/test-tools/syzkaller/pkg/covermerger/covermerger_test.go

Purpose: integration and unit tests for CSV merging, JSONL generation, Spanner save compatibility, manager aggregation, and line-mapping behavior across commits.

Important APIs/types/functions: `TestMergeCSVWriteJSONL_and_coveragedb_SaveMergeResult`, `TestMergerdCoverageRecords`, `TestAggregateStreamData`, `fileVersProviderMock`, `testConfig`, and `TestCheckedFuncName`.

Control flow: the JSONL test pipes `MergeCSVWriteJSONL` output through gzip into `coveragedb.SaveMergeResult` and asserts total line counts plus mutation counts. Aggregation tests feed inline or fixture BigQuery CSV rows, consume merge results from a channel, and compare JSON-encoded expected `MergeResult`s. The mock provider reads file versions from testdata repos by commit.

State and persistence: reads checked-in testdata trees and writes only pipes/buffers. Spanner is mocked.

Dependencies and integration: connects `covermerger`, `coveragedb`, gzip, Spanner mocks, and testdata integration repos.

Risks: tests rely on CSV ordering and fixture file layouts. The test name `TestMergerdCoverageRecords` is misspelled but harmless. Some aggregate comparisons omit line details for broad fixture cases.

Test signals: strong evidence for core merge semantics, especially handling deleted files/code, changed lines, added lines, zero-hit lines, and per-manager/all-manager output.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/covermerger_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/deleted_file_merger.go -->
# sources/test-tools/syzkaller/pkg/covermerger/deleted_file_merger.go

Purpose: implements the `FileCoverageMerger` interface for files absent from the target base commit.

Important APIs/types/functions: `DeletedFileLineMerger`, `Add`, and `Result`.

Control flow: `Add` ignores all records. `Result` returns a `MergeResult` with `FileExists: false`.

State and persistence: stateless; no stored records.

Dependencies and integration: returned by `makeFileLineCoverMerger` when the base file version is missing. `mergedCoverageRecords` drops file results where `FileExists` is false.

Risks: all historical coverage for deleted files is intentionally suppressed from database output. If a missing base file is caused by provider failure rather than deletion, coverage is lost silently aside from provider logs.

Test signals: `covermerger_test.go` includes a `file deleted` aggregation case that expects `FileExists: false`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/deleted_file_merger.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/file_line_merger.go -->
# sources/test-tools/syzkaller/pkg/covermerger/file_line_merger.go

Purpose: maps line coverage records from their original commit file versions onto the base commit file and aggregates hit counts/details per target line.

Important APIs/types/functions: `makeFileLineCoverMerger`, `FileLineCoverMerger`, `Add`, and `Result`.

Control flow: the constructor finds the base file content in `FileVersions`; if missing, it returns `DeletedFileLineMerger`. Otherwise it initializes a `MergeResult` and builds one `LineToLineMatcher` per available repo commit. `Add` skips records with negative line numbers, counts positive-hit records as lost if no matcher exists, maps the source line to a target line, and accumulates hit count plus line details. `Result` logs lost frame counts and returns the merge result.

State and persistence: in-memory hit count maps, line detail maps, matchers, and lost-frame counters. No writes.

Dependencies and integration: depends on `lines_matcher.go`, `RepoCommit`, and logging. Used by `batchFileData`.

Risks: `SameLinePos` is called with `record.StartLine`, while matcher indexes are zero-based over split lines; production CSV `sl` appears one-based, so this relies on historical behavior and may be off by one unless upstream line numbering is zero-based in these exports. Missing commit versions drop positive hits into logs only. Negative line records are ignored even if function-level info exists.

Test signals: aggregate tests cover deleted code/file, changed lines, added lines, and zero-hit instrumentation through this merger.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/file_line_merger.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/lines_matcher.go -->
# sources/test-tools/syzkaller/pkg/covermerger/lines_matcher.go

Purpose: builds a source-line-to-destination-line matcher between two versions of a file, preserving only lines whose text still matches at the mapped destination.

Important APIs/types/functions: `makeLineToLineMatcher`, `LineToLineMatcher`, and `SameLinePos`.

Control flow: the matcher computes a diff between `textFrom` and `textTo` with no timeout. It maps destination character offsets to destination line indexes, then iterates source lines, uses `DiffXIndex` to find the corresponding destination position, and records the destination line only if the destination line text equals the source line text; otherwise it records `-1`.

State and persistence: immutable in-memory `lineToLine` slice.

Dependencies and integration: uses `github.com/sergi/go-diff/diffmatchpatch`. Called by `FileLineCoverMerger` for every available commit version relative to the base file.

Risks: `SameLinePos` does not bounds-check the requested line index. Diff timeout is disabled, so very large files or pathological diffs can be expensive. Identical repeated lines may map ambiguously depending on diff behavior.

Test signals: `lines_matcher_test.go` covers unchanged, inserted, removed, and changed first-line scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/lines_matcher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/lines_matcher_test.go -->
# sources/test-tools/syzkaller/pkg/covermerger/lines_matcher_test.go

Purpose: validates line-to-line mapping across simple file edits.

Important APIs/types/functions: package test text fixtures and `TestMatching`.

Control flow: table cases build matchers for identical text, insertion before the source line, source-line removal, and source-line text change. Each asserts `SameLinePos` for line 0.

State and persistence: in-memory strings only.

Dependencies and integration: uses testify assertions and the real `makeLineToLineMatcher`.

Risks: tests focus on the first line only and do not cover repeated lines, later-line changes, out-of-range indexes, or one-based line inputs from coverage records.

Test signals: basic regression signal for the exact-match-only mapping policy.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/lines_matcher_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/mocks/FileVersProvider.go -->
# sources/test-tools/syzkaller/pkg/covermerger/mocks/FileVersProvider.go

Purpose: generated testify mock for the `covermerger.FileVersProvider` interface.

Important APIs/types/functions: `NewFileVersProvider`, `FileVersProvider`, `GetFileVersions`, and typed call helper `FileVersProvider_GetFileVersions_Call`.

Control flow: constructor registers expectation assertion cleanup. `GetFileVersions` passes the target file and variadic repo commits to `mock.Called`, then returns mocked `covermerger.FileVersions` and error values. Helper methods support `Run`, `Return`, and `RunAndReturn`.

State and persistence: mock expectations only.

Dependencies and integration: used by tests that need to isolate merge logic from real Git/web providers. Depends on `covermerger` and testify mock.

Risks: variadic arguments are packed as a slice for mock matching, so expectations must be configured accordingly. Generated code should not be edited manually.

Test signals: infrastructure for focused covermerger tests; this subset uses a hand-written provider in `covermerger_test.go` instead of this mock.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/mocks/FileVersProvider.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/provider_monorepo.go -->
# sources/test-tools/syzkaller/pkg/covermerger/provider_monorepo.go

Purpose: implements `FileVersProvider` using a local monorepo checkout/cache of kernel commits.

Important APIs/types/functions: `FileVersProvider`, `monoRepo`, `FileVersions`, `GetFileVersions`, `allRepoCommitsPresent`, `addRepoCommit`, `MakeMonoRepo`, and `cloneCommits`.

Control flow: `GetFileVersions` checks under read lock whether all requested commits are available; if not, it releases the read lock and calls `cloneCommits`. It then reads each requested file object from the local repo at the target commit, skipping missing files. `cloneCommits` checks whether commits already exist locally and otherwise checks them out/fetches via `addRepoCommit`.

State and persistence: persistent local VCS checkout under `<workdir>/repos/linux_kernels`; in-memory set of known repo commits protected by a mutex.

Dependencies and integration: uses syzkaller `vcs.NewRepo`, Linux target metadata, and logging. Used by batch/offline merge jobs needing many commit versions.

Risks: `addRepoCommit` records a commit as present before checkout success; failures can poison the cache for that run. It panics if repo or commit is empty. Concurrent clone behavior is protected but long checkouts block all cache updates.

Test signals: no direct tests in this subset; integration tests use a hand-written filesystem provider.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/provider_monorepo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/provider_web.go -->
# sources/test-tools/syzkaller/pkg/covermerger/provider_web.go

Purpose: implements `FileVersProvider` by fetching file contents over HTTPS from repository web endpoints or a caller-provided proxy URI function.

Important APIs/types/functions: `FuncProxyURI`, `webGit`, `GetFileVersions`, `errFileNotFound`, `loadFile`, `isGerritServer`, and `MakeWebGit`.

Control flow: `GetFileVersions` loops over requested repo commits, calls `loadFile`, skips 404s, and returns other errors. `loadFile` builds either a proxy URI or `<repo>/plain/<file>?id=<commit>`, forces HTTPS, performs `http.Get`, reads the response, and base64-decodes the body when headers indicate Gerrit.

State and persistence: no local persistence; network reads only.

Dependencies and integration: standard `net/http`, `net/url`, base64, and `cover.GetMergeResult` for web-backed per-file rendering.

Risks: uses package-level `http.Get` with no timeout or context. It forces scheme to HTTPS, which may break non-HTTP repo strings. Gerrit detection scans all response header values for substring `gerrit`, which is heuristic. Query parameters are manually appended before URL parsing.

Test signals: no direct tests in this subset. Network/provider behavior is therefore less guarded than core merge logic.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/provider_web.go -->
