<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/fuchsia.go -->
# Research: sources/test-tools/syzkaller/pkg/report/fuchsia.go

Purpose: implements the Fuchsia and Starnix reporter backend for syzkaller crash logs. It recognizes Zircon kernel panics, recursion/double-fault cases, KVM internal errors, user fatal exceptions, unexpected reboots, Starnix Rust panics, common syzkaller failures, and Go runtime fatal errors. Unlike most reporters, Fuchsia symbolization is part of parsing because raw Zircon backtraces may contain only PCs.

Important APIs/types/functions: `type fuchsia` embeds shared `config` and stores a resolved kernel object path. `ctorFuchsia` appends Fuchsia-specific ignore regexps, derives `obj` from `KernelDirs.Obj`, and returns executor fatal-exception suppressions. `ContainsCrash` delegates to `containsCrash` over `fuchsiaOopses`. `Parse` calls `symbolize`, `simpleLineParser`, remaps positions through the line-to-line map, then compacts Zircon or Starnix reports. `shortenStarnixPanicReport`, `shortenReport`, `processPC`, `trimFile`, and `Symbolize` handle report trimming and PC-to-frame conversion. Data tables include `fuchsiaIgnores`, Zircon/Starnix frame patterns, stack params, and `zirconOopses`/`starnixOopses`.

Control flow: construction selects ignore/suppression policy, parse pre-symbolizes the full log, detects the first matching oops in symbolized text, translates start/end offsets back to the raw log, and trims unrelated panic-shell, DSO, uptime, halted, or overly long Starnix lines. `symbolize` scans lines, repairs split assert lines, recognizes `RIP` and `bt#` PCs, and emits one line per symbolizer frame. `processPC` canonicalizes short kernel PCs, adjusts return PCs for call frames, demangles C++ names, caps lambda names, and writes file:line data.

State and persistence: reporter state is in-memory only: resolved kernel object path, inherited target/kernel dirs, ignores, and symbolizer lifetime inside a parse. The only persistent artifacts are caller-provided kernel object files read by the symbolizer. Offset remapping is per-parse transient state and is fragile because symbolization changes line lengths and sometimes line counts.

Dependencies and integration points: integrates with `report.go` through the `reporterImpl` interface and is selected for both `targets.Fuchsia` and `targets.Starnix`. It depends on `pkg/symbolizer`, shared `oops`/`stackParams` helpers, demangling, and Fuchsia kernel object naming from `targets.Target`. Fixtures under `testdata/fuchsia/report` exercise the oops table and report compaction.

Risks: pre-symbolization makes `StartPos`/`EndPos` mapping more complex than other OSes; bad line-to-line mapping can misplace reports. The split-assert-line repair assumes a fixed long-line behavior. Short PC reconstruction is x86/Zircon-specific. Aggressive `shortenReport` filtering can drop diagnostically useful lines if new Zircon output uses a previously unrelated prefix. Starnix truncation thresholds balance compactness against missing separated frames.

Test signals: useful tests are parse fixtures for ASSERT FAILED, double fault, KVM internal error, fatal exception, unexpected reboot, recursion in interrupt handler, and Starnix panics. Symbolization should be validated with and without a kernel object. Regression tests should check report trimming, suppression of `/tmp/syz-executor` fatal exceptions, and raw-position sanity for Fuchsia's special mapping.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/fuchsia.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/fuzz.go -->
# Research: sources/test-tools/syzkaller/pkg/report/fuzz.go

Purpose: provides a package-level fuzz entry point that stress-tests every non-stub reporter implementation against arbitrary byte slices. It asserts core reporter invariants rather than validating one OS-specific title.

Important APIs/types/functions: `Fuzz(data []byte) int` is the exported fuzz target. `fuzzReporters` is an initialized map from OS name to `*Reporter`, built by iterating `ctors`, skipping Windows/stubs and unsupported AMD64 targets, and calling `NewReporter` with minimal `mgrconfig.Config`.

Control flow: for each reporter, the fuzzer checks that `ContainsCrash(data)` agrees with `Parse(data) != nil`. If a report is found, it calls `Symbolize`, verifies non-empty title/report/output, validates start/end/skip position relationships for all OSes except Fuchsia, and reparses from `StartPos` to ensure stable discovery of the same report. Any invariant failure panics so go-fuzz/native fuzzing can minimize the input.

State and persistence: reporter instances are package-level cached test objects with no persistent storage. The only mutable state is per-report symbolization state; the fuzzer intentionally calls `Symbolize` once per parsed report to exercise that guard.

Dependencies and integration points: depends on `mgrconfig`, `targets`, the global `ctors` table in `report.go`, and every concrete reporter. It is an integration-level harness for parser consistency across Linux, BSDs, Darwin, Fuchsia, gVisor, and common syzkaller runtime errors.

Risks: because `fuzzReporters` is initialized at package load time, constructor panics or target-definition changes can break all fuzzing. Minimal configs mean symbolization paths are usually absent, so full addr2line paths are not fuzzed. Fuchsia is exempted from position checks because its parse-time symbolization currently makes positions imperfect, so regressions there need fixture tests.

Test signals: `TestFuzz` in `report_test.go` seeds historically problematic inputs, including malformed Linux prefixes, truncated Zircon panics, BSD vnode panics, and boot messages. Fuzz failures are high-value because they expose parser panics, crash-detection disagreement, empty reports, or invalid offsets.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/fuzz.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/gvisor.go -->
# Research: sources/test-tools/syzkaller/pkg/report/gvisor.go

Purpose: implements the gVisor reporter backend. It recognizes gVisor/Sentry panics, signals, fatal errors, data races, invalid partial-result messages, common Go runtime failures, and syzkaller common failures while suppressing known resource-exhaustion noise.

Important APIs/types/functions: `type gvisor` embeds `config`; `ctorGvisor` returns resource/OOM/PID-exhaustion suppressions; `ContainsCrash` and `Parse` delegate to shared `containsCrash` and `simpleLineParser`; `shortenReport` compacts enormous Go panic dumps; `Symbolize` is a no-op; `gvisorTitleReplacement` normalizes container/sandbox names and PIDs; `gvisorOopses` defines Panic, SIGSEGV, SIGBUS, FATAL ERROR, DATA RACE, partialResult, fatal error, and BUG-on patterns.

Control flow: parsing locates the first gVisor oops, extracts a title with no stack-specific frame extraction, applies gVisor-specific dynamic title replacements, and shortens the report to the first goroutine block. For data races, shortening keeps both relevant stacks by extending to a second blank-line block.

State and persistence: no persistent state. Suppressions and replacement tables are immutable process data; parsed reports hold raw output, normalized title, and compacted report bytes.

Dependencies and integration points: selected from `ctors` for `targets.GVisor`; shares `commonOopses`, `replacement`, `oops`, and `simpleLineParser` from `report.go`. Its output participates in generic syzkaller crash deduplication through normalized titles and `crash.TitleToType`.

Risks: Go panic formats change over time, and fixed five-line-plus-blank-block truncation can lose context for unusual panics. Normalizing all container/sandbox names and PIDs improves deduplication but can merge distinct environment-specific issues. Suppression rules for OOM/PID exhaustion must be kept aligned with gVisor runtime error text.

Test signals: parse fixtures in the shared `all` directory cover Go panic/SYZFATAL behavior that gVisor also consumes. Dedicated gVisor fixtures should include data race dual-stack preservation, container/sandbox title replacement, and each suppression string.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/gvisor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/impact_score.go -->
# Research: sources/test-tools/syzkaller/pkg/report/impact_score.go

Purpose: ranks normalized crash titles by estimated security/operational impact. It converts syzkaller crash types into integer scores and explains title-frequency statistics with rank metadata.

Important APIs/types/functions: `impactOrder` is an ordered severity list of `crash.Type`, highest first. `TitlesToImpact(title string, otherTitles ...string) int` maps one or more titles through `crash.TitleToType` and returns the highest rank as `len(impactOrder)-index`, or `-1` for unknown/unranked types. `TitleFreqRank` stores title, observed count, total report count, and rank. `ExplainTitleStat(ts *titleStat)` walks a title-stat trie, de-duplicates titles within each report group, aggregates counts, and sorts by rank, frequency, and title.

Control flow: ranking is table-driven. For multiple titles, the function scans every title and every severity entry, preserving the maximum score. `ExplainTitleStat` visits grouped title paths, aggregates per-title counts only once per visited group, computes ranks, then returns a sorted slice for UI/reporting consumers.

State and persistence: no direct persistence. It consumes `titleStat`, which is serialized by `title_stat.go`, but this file itself only builds transient maps and result slices. The severity table is process-global static policy.

Dependencies and integration points: depends on `pkg/report/crash` for title classification and on the local `titleStat` visitor contract. It integrates with any dashboard or batch tool that wants to prioritize frequent crash titles by impact rather than count alone.

Risks: severity is policy encoded in source order; omitted crash types return `-1` and sink in sorted lists. `crash.TitleToType` normalization changes can silently alter scores. The current nested scan is small enough to be fine, but adding many impact classes would benefit from a precomputed map.

Test signals: unit tests cover unknown titles, unrecognized KASAN titles, a low-priority hang, and multi-title selection of a higher impact KASAN invalid-free over a hang. Additional tests should cover `ExplainTitleStat` sorting ties and per-group de-duplication.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/impact_score.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/impact_score_test.go -->
# Research: sources/test-tools/syzkaller/pkg/report/impact_score_test.go

Purpose: unit-tests the impact-score policy in `impact_score.go`, especially unknown handling and multi-title highest-impact selection.

Important APIs/types/functions: constants `testHangTitle` and `testKASANInvalidFreeTitle` provide stable crash titles. `TestImpactScore` table-tests `TitlesToImpact` for unknown titles, unknown KASAN titles, and a known hang. `TestTitlesToImpact2` checks that a KASAN invalid-free alternative title outranks the primary hang title.

Control flow: each table row calls `TitlesToImpact` and compares the exact expected score. The multi-title test computes the desired KASAN score from `impactOrder` using `slices.Index`, and fails if the returned rank remains at the hang's low score.

State and persistence: no state beyond test constants. The tests are deterministic and do not touch filesystem or external tools.

Dependencies and integration points: imports `testing`, `slices`, and `pkg/report/crash`. It is tightly coupled to `impactOrder`; inserting/removing severity entries can change expected numeric ranks and should update tests intentionally.

Risks: the second test only asserts that the result is not the hang score, not exact equality, so a too-high score could pass. Coverage does not include `ExplainTitleStat`, duplicate titles in one report group, or sorting ties.

Test signals: run with the package tests. A failure usually means crash title classification changed or the severity table was reordered.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/impact_score_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/linux.go -->
# Research: sources/test-tools/syzkaller/pkg/report/linux.go

Purpose: implements the Linux reporter backend, the package's most complex parser. It detects Linux kernel oopses, normalizes crash titles, extracts report byte ranges, tracks corruption/panic/executor metadata, symbolizes stack frames, decompiles `Code:` opcode snippets, extracts guilty source files, and optionally resolves maintainers.

Important APIs/types/functions: `type linux` embeds `config` and stores kernel object path, symbol tables per module, console/context regexps, frame filters, guilty-file filters, report-start ignores, info-stack markers, and a symbolizer cache. `ctorLinux` reads vmlinux/module symbols and initializes all regexps/suppressions. Publicly used methods are `ContainsCrash`, `Parse`, `Symbolize`, `extractFaultInjectionInfo`, `extractGuiltyFileRaw`, and `GetLinuxMaintainers`. Internal helpers include `findFirstOops`, `findReport`, `stripLinePrefix`, `extractContext`, `parseLinuxBacktraceLine`, `symbolizeLine`, opcode parsing/decompilation helpers, `isCorrupted`, `setExecutorInfo`, and stall/hang frame extractors. Data tables include `linuxStackParams`, corrupted-title regexps, skip-frame lists, and the large `linuxOopses` registry.

Control flow: parsing scans line by line for the first non-ignored oops, accounting for replay-truncated printk messages. `findReport` then replays the log, collecting same-context prefix lines, filtering questionable frames, preserving CPU traceback when NMI dumps all CPUs, detecting second reports, and trimming panic-on-warn or deadlock tails after enough primary report lines. `extractDescription` applies the matching oops format and stack extraction; the result is classified with `crash.TitleToType`, executor IDs are parsed from `Comm: syz.proc.exec`, corruption is checked, and `Panicked` is set if any kernel-panic line exists. `Symbolize` optionally opens a target symbolizer, rewrites backtrace lines with file:line and inline frames, appends decompiled code for meaningful opcode dumps, then extracts guilty file and maintainers unless running Android/cuttlefish-like configs.

State and persistence: most state is immutable after construction. Symbol tables are read from kernel object/module files. `symbolizerCache` caches symbolizer lookups for the reporter lifetime. Maintainer lookup shells out to `scripts/get_maintainer.pl` in the kernel source tree but does not persist results. Reports mutate in memory during symbolization and use `reportPrefixLen` to avoid treating prepended context as guilty-file evidence.

Dependencies and integration points: integrates with `NewReporter` for `targets.Linux`, `pkg/symbolizer`, `pkg/cover/backend` for module discovery/path cleaning, `pkg/osutil` for maintainer script execution, `pkg/vcs` recipient parsing, `pkg/report/crash`, target endian/arch data, and `DecompileOpcodes` from `decompile.go`. It is the primary producer of syzbot titles, alternative titles, maintainers, guilty files, opcode disassembly, and executor metadata.

Risks: Linux oops text is highly unstable across kernel versions, architectures, configs, sanitizers, and printk caller settings. Context filtering can drop interleaved but relevant lines or include wrong-CPU lines when context is missing. Huge regex tables are order-sensitive; broad headers such as BUG/WARNING/INFO can shadow newer specific formats. Corruption detection can over-mark reports missing expected frames, while `noStackTrace` formats can under-detect truncation. Opcode decompilation depends on architecture endian/width and external objdump support. Guilty-file extraction is heuristic and can choose generic helper files if ignore lists lag kernel changes.

Test signals: `linux_test.go` covers ignore behavior, fault-injection compaction/deduplication, symbolization including modules/build IDs/inlines, opcode parsing across endian/ARM Thumb cases, and disassembly fixtures. Generic report fixtures exercise many `linuxOopses` entries. High-value additions are new kernel-version title formats, CONFIG_PRINTK_CALLER interleavings, module symbolization, panic-on-warn trimming, and guilty-file edge cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/linux_test.go -->
# Research: sources/test-tools/syzkaller/pkg/report/linux_test.go

Purpose: focused unit tests for Linux-specific reporter behavior that is too detailed for generic parse fixtures: ignore filtering, fault-injection extraction, backtrace symbolization, opcode parsing, and report disassembly.

Important APIs/types/functions: `TestLinuxIgnores` validates configured ignore regexps. `TestExtractFaultInjectionInfo` and `TestExtractFaultInjectionInfoDeduplicates` validate compact extraction and duplicate suppression. `TestLinuxSymbolizeLine` builds fake symbols/modules and a fake symbolizer to test `linux.symbolize`. `prepareLinuxReporter` creates an AMD64 or requested-arch reporter. `TestParseLinuxOpcodes` validates `parseOpcodes` for little-endian, big-endian, ARM Thumb, and malformed strings. `TestDisassemblyInReports` and `testDisassembly` compare `Code:` decompilation fixtures.

Control flow: tests construct minimal `mgrconfig.Config` values, parse synthetic logs, call Linux internals directly where needed, and compare exact strings or structs. Symbolization tests route selected PCs to controlled frames, including inline frames and errors. Disassembly tests walk `testdata/linux/decompile/<arch>` and run only on Linux hosts with available compiler support.

State and persistence: tests read fixture files and may write expected outputs only when the package-level `-update` flag is set. Otherwise they are deterministic and in-memory. Fake module metadata lets module symbolization run without real kernel binaries.

Dependencies and integration points: depends on `targets`, `mgrconfig`, `symbolizer`, `vminfo`, `osutil`, `testify/assert`, and runtime host OS checks. It exercises public reporter APIs plus Linux internals, so refactors must preserve helper semantics or adjust tests deliberately.

Risks: tests are exact-output sensitive, especially file-line formatting and decompiled instruction text. Disassembly tests depend on host platform and cross-toolchain availability. Some branches in the large oops table are only covered by external fixtures, not this file.

Test signals: failures identify regressions in title suppression, report boundaries, prefix stripping, symbol/module lookup, inline frame rendering, opcode endian handling, and decompiler integration. Run with `go test ./pkg/report`; run on Linux for full disassembly coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/netbsd.go -->
# Research: sources/test-tools/syzkaller/pkg/report/netbsd.go

Purpose: configures the shared BSD reporter for NetBSD crash logs. It defines NetBSD-specific oops patterns and stack symbolization regexps while reusing `bsd` parsing/symbolization mechanics.

Important APIs/types/functions: `ctorNetbsd` creates stack and witness symbolization regexps, appends a postfix `event_init` ignore, and calls `ctorBSD`. `netbsdOopses` handles supervisor faults, kernel diagnostic assertions, lock errors, ASan unauthorized access, MSan uninitialized memory, UBSan undefined behavior, group Go runtime errors, and common syzkaller failures.

Control flow: construction injects NetBSD-specific patterns into a generic `bsd` instance. Runtime `ContainsCrash`, `Parse`, and `Symbolize` are inherited from `bsd`: line matching uses `netbsdOopses`, title extraction is `simpleLineParser`, and matching stack lines can be decorated with file:line data from the NetBSD kernel object.

State and persistence: no NetBSD-specific mutable state. Symbol tables and kernel object paths are held by `bsd` if kernel object configuration is supplied.

Dependencies and integration points: selected by `ctors[targets.NetBSD]`; depends on `ctorBSD`, shared `oops` formatting, common syzkaller oopses, and `stackParams`-independent title extraction. Fixtures under `testdata/netbsd` and shared `all` fixtures run through this backend.

Risks: NetBSD panic formats are encoded as multiline regexps; minor wording changes can cause fallback titles or missed reports. The added `event_init` ignore suppresses known postfix output but could hide a real crash if the same text appears in a meaningful context. Symbolization regexps assume `netbsd:function+offset` and witness `#N function+offset` shapes.

Test signals: `netbsd_test.go` validates normal, inline, missing-symbol, and witness symbolization forms. Parse fixtures should cover each sanitizer/panic oops format.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/netbsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/netbsd_test.go -->
# Research: sources/test-tools/syzkaller/pkg/report/netbsd_test.go

Purpose: verifies NetBSD-specific symbolization patterns supplied to the shared BSD reporter.

Important APIs/types/functions: `TestNetbsdSymbolizeLine` builds a table of `symbolizeLineTest` cases and delegates to `testSymbolizeLine` with `ctorNetbsd`. Cases include regular stack frames, inline frames, missing symbols, and witness lines with one- and two-digit frame indexes.

Control flow: the shared BSD test helper constructs a reporter with fake symbol data and checks that NetBSD regexps identify the function/offset region where file:line data should be inserted.

State and persistence: no persistence; all symbol data is test-local.

Dependencies and integration points: depends on `bsd_test.go` helpers and the NetBSD constructor. It indirectly guards `bsd.symbolizeLine` against changes that would break NetBSD's `netbsd:` prefix handling.

Risks: it only tests symbolization, not NetBSD oops detection/title extraction. Regex changes that still pass these narrow cases can still miss real panic formats.

Test signals: failures point to broken NetBSD stack or witness frame symbolization.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/netbsd_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/openbsd.go -->
# Research: sources/test-tools/syzkaller/pkg/report/openbsd.go

Purpose: configures the shared BSD reporter for OpenBSD crash logs. It defines OpenBSD panic/witness/uvm fault/kernel trap title formats and suppresses known unhelpful panics.

Important APIs/types/functions: `ctorOpenbsd` sets stack and witness symbolization regexps, calls `ctorBSD`, and returns suppressions for `vop_generic_badop`, repetitive witness inode lock reversals, and broken-pipe disconnect panics. `openbsdOopses` handles cleaned vnode, many panic subformats, witness lock issues, `uvm_fault`, kernel page/protection traps, group Go runtime errors, and common syzkaller failures.

Control flow: the constructor builds a `bsd` reporter with OpenBSD-specific tables. Parsing is line-based through `simpleLineParser`; title selection prefers more specific panic/witness/uvm regexps before generic corrupted fallbacks. Symbolization is inherited from `bsd` using OpenBSD frame forms like `at func+0xoff` and witness `#N func+0xoff`.

State and persistence: no OpenBSD-specific mutable state beyond suppressions and regex tables. Optional symbol state is held by the embedded `bsd` reporter.

Dependencies and integration points: selected by `ctors[targets.OpenBSD]`. It integrates with common report normalization, shared BSD symbolization, and the generic test fixture runner.

Risks: OpenBSD debugger output includes prompts and carriage-return quirks, so start/end offsets are more fragile than line-only parsing suggests. Broad panic regexps can normalize away detail; suppressions must not mask actionable lock issues. `uvm_fault` has both complete and corrupted formats, so ordering matters.

Test signals: `openbsd_test.go` covers symbolization; parse fixtures under `testdata/openbsd/report` should cover panic, witness, uvm, and kernel trap cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/openbsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/openbsd_test.go -->
# Research: sources/test-tools/syzkaller/pkg/report/openbsd_test.go

Purpose: verifies OpenBSD-specific symbolization regexps used by the shared BSD reporter.

Important APIs/types/functions: `TestOpenbsdSymbolizeLine` defines `symbolizeLineTest` cases and delegates to `testSymbolizeLine` with `ctorOpenbsd`. It covers normal stack frames, inline frame expansion, missing symbols, and witness frame numbering.

Control flow: test data exercises matching of `at func+offset` and `#N func+offset` lines, then validates inserted file:line and inline markers from the fake symbolizer.

State and persistence: no filesystem writes and no persistent state.

Dependencies and integration points: uses common BSD symbolization test helpers and the OpenBSD constructor. It guards that OpenBSD remains compatible with `bsd.symbolizeLine`.

Risks: it does not cover OpenBSD title extraction, suppressions, or carriage-return offset behavior, so those require parse fixtures.

Test signals: failures mean OpenBSD stack/witness symbolization output changed or broke.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/openbsd_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/report.go -->
# Research: sources/test-tools/syzkaller/pkg/report/report.go

Purpose: defines the public reporter abstraction and shared crash parsing machinery used by every OS backend. It owns reporter construction, report metadata, title sanitization, suppression/interest filtering, generic oops matching, stack-frame extraction, report truncation, and report byte merging/splitting.

Important APIs/types/functions: `reporterImpl` is the backend interface. `Reporter` stores backend, type, suppressions, and interests. `Report` carries normalized title, alt titles, crash type, frame, report bytes, raw output, start/end/skip offsets, suppression/corruption flags, maintainers, guilty file, machine info, executor info, panic flag, and internal symbolization state. Public functions include `NewReporter`, `Parse`, `ParseFrom`, `ContainsCrash`, `Symbolize`, `ExtractFaultInjectionInfo`, `ReportToGuiltyFile`, `IsSuppressed`, `ParseAll`, `Truncate`, `MergeReportBytes`, and `SplitReportBytes`. Shared internals include `compileRegexps`, `replaceTable`, `sanitizeTitle`, `oops`/`oopsFormat`, `stackFmt`, `stackParams`, `compile`, `containsCrash`, `matchOops`, `extractDescription`, `extractStackFrame`, `simpleLineParser`, and helper match/replace routines.

Control flow: `NewReporter` discovers local modules when a kernel object is configured, selects constructor by OS/type, compiles ignore/interest/suppression regexps, and returns a `Reporter`. `ParseFrom` delegates to the backend on a suffix, remaps offsets, sanitizes/replaces dynamic title elements, computes suppression/corruption flags, extracts a representative frame, and sets `SkipPos` for `ParseAll`. `Symbolize` enforces single symbolization, calls the backend, and suppresses uninteresting reports. Generic parsing scans for an oops header, extracts a formatted title and alt titles, optionally extracts stack frames, marks corrupted reports, and classifies via `crash.TitleToType`.

State and persistence: reporter state is in-memory and immutable after construction except backend caches. `Report` objects are mutable during parse/symbolization. The package reads kernel/module objects and maintainer data only through backend integrations; this file itself performs no persistence.

Dependencies and integration points: depends on `mgrconfig`, `targets`, `backend.DiscoverModules`, `vminfo`, `vcs`, `crash`, and demangling. It dispatches to Linux, Fuchsia/Starnix, gVisor, FreeBSD, Darwin, NetBSD, OpenBSD, and stub Windows constructors. Its title normalization and stack extraction directly affect syzbot deduplication, bug type classification, suppressions, and maintainer routing.

Risks: title replacement is deliberately broad and can over-deduplicate distinct bugs. Regex order in oops formats is semantically significant. `SkipPos`/`EndPos` invariants are central to multi-report parsing and fuzzing. Stack extraction relies on skip patterns and may mark valid reports corrupted if formats drift. `Symbolize` panics on double calls, so callers must respect ownership.

Test signals: `report_test.go` provides generic parse/symbolize/guilty/fuzz/truncate/split coverage across OS fixture directories. Backend tests add Linux and BSD-specific checks. Any change to title normalization, report offsets, or stack corruption should be validated against fixture updates.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/report.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/report_test.go -->
# Research: sources/test-tools/syzkaller/pkg/report/report_test.go

Purpose: package-level regression tests for parsing, symbolization, guilty-file extraction, helper utilities, and fuzz seed invariants across all registered reporters and shared fixtures.

Important APIs/types/functions: `flagUpdate` enables fixture rewriting. `TestParse`, `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport` implement the report fixture contract. `TestGuiltyFile`, `TestRawGuiltyFile`, and `parseGuiltyTest` validate guilty-file extraction. `TestSymbolize` validates symbolization fixtures. `forEachFile` runs tests for each OS plus shared `all` fixtures. `readDir` selects numeric fixture files. Utility tests cover `replace`, `Fuzz`, `Truncate`, and `SplitReportBytes`.

Control flow: parse fixtures contain metadata headers, a blank line, raw log, and optional `REPORT:` expected extraction. Tests instantiate each non-Windows reporter, run OS-specific and shared fixtures, compare titles/alt titles/type/frame/corruption/suppression/panic/executor/report bytes, and verify output/start/end/skip invariants. When `-update` is used and no explicit offsets are asserted, expected headers can be regenerated from parser output.

State and persistence: normal runs are read-only. With `-update`, fixture files can be rewritten via `os.WriteFile`; this is deliberate test maintenance state. Race mode reduces fixture coverage to limit cost.

Dependencies and integration points: depends on all constructors in `ctors`, `mgrconfig`, `targets`, `crash`, `osutil`, `testutil`, and `testify/assert`. It is the main consumer of `testdata/*/report`, `guilty`, `guilty_raw`, and `symbolize` fixture trees.

Risks: exact fixture comparisons are useful but can make intentional normalization changes noisy. `forEachFile` runs shared `all` fixtures through every OS reporter, so generic runtime panic formats must stay compatible with all backends. The update path can accidentally bless regressions if used without review.

Test signals: failures identify crash-detection disagreement, empty titles, wrong metadata, bad report extraction, invalid offsets, guilty-file drift, symbolization drift, helper regressions, or fuzz seed panics.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/report_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/stub.go -->
# Research: sources/test-tools/syzkaller/pkg/report/stub.go

Purpose: placeholder reporter for targets that are known to the constructor table but do not have an implemented parser, currently Windows.

Important APIs/types/functions: `type stub` embeds `config`; `ctorStub` returns a stub instance with no suppressions; `ContainsCrash`, `Parse`, and `Symbolize` all panic with `not implemented`.

Control flow: `NewReporter` can construct the stub through `ctors`, but callers that use it will panic on reporter operations. Test/fuzz setup explicitly skips Windows and filters stub implementations when building fuzz reporters.

State and persistence: no state beyond embedded config and no persistence.

Dependencies and integration points: integrated through `ctors[targets.Windows]`. Its existence lets target selection fail later for unsupported behavior while preserving a constructor entry.

Risks: accidental use in production paths will panic. Any new target mapped to `ctorStub` must be filtered out of fuzz/test loops or implemented before use.

Test signals: fuzz reporter construction skips stubs; generic test iteration skips Windows. A direct test could assert that Windows remains intentionally unsupported until implemented.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/stub.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/all/report/0 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/all/report/0

Purpose: shared all-OS fixture expecting normalized title `panic: bad arg kind`. It validates common syzkaller/Go runtime crash recognition that every non-stub reporter should handle consistently.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 20 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `DoS`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `panic: bad arg kind`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/all/report/0 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/all/report/1 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/all/report/1

Purpose: shared all-OS fixture expecting normalized title `panic: no result`. It validates common syzkaller/Go runtime crash recognition that every non-stub reporter should handle consistently.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 26 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `DoS`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `panic: no result`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/all/report/1 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/all/report/2 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/all/report/2

Purpose: shared all-OS fixture expecting normalized title `panic: executor NUM: failed: event already set (errno NUM)`. It validates common syzkaller/Go runtime crash recognition that every non-stub reporter should handle consistently.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 23 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `DoS`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `panic: executor 2: failed: event already set (errno 0)`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/all/report/2 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/all/report/3 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/all/report/3

Purpose: shared all-OS fixture expecting normalized title `panic: first open arg is not a pointer to string const`. It validates common syzkaller/Go runtime crash recognition that every non-stub reporter should handle consistently.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 18 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `DoS`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `panic: first open arg is not a pointer to string const`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/all/report/3 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/all/report/4 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/all/report/4

Purpose: shared all-OS fixture expecting normalized title `panic: runtime error: invalid memory address or nil pointer dereference`. It validates common syzkaller/Go runtime crash recognition that every non-stub reporter should handle consistently.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 23 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `DoS`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `panic: runtime error: invalid memory address or nil pointer dereference`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/all/report/4 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/all/report/5 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/all/report/5

Purpose: shared all-OS fixture expecting normalized title `SYZFATAL: executor NUM failed NUM times: call NUM/NUM/NUM: signal overflow: ADDR/ADDR`. It validates common syzkaller/Go runtime crash recognition that every non-stub reporter should handle consistently.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 5 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `SYZ_FAILURE`. Alternative titles expected: SYZFATAL. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `2022/04/21 07:35:27 SYZFATAL: executor 0 failed 11 times: call 15/15/3356: signal overflow: 808464432/16776764`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/all/report/5 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/all/report/6 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/all/report/6

Purpose: shared all-OS fixture expecting normalized title `panic: cannot allocate memory`. It validates common syzkaller/Go runtime crash recognition that every non-stub reporter should handle consistently.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 11 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `DoS`. Explicit flags: SUPPRESSED=Y. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `panic: cannot allocate memory`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/all/report/6 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/darwin/report/0 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/darwin/report/0

Purpose: Darwin fixture expecting normalized title `panic: assertion failed: in6p == NULL || (in6p->inp_vflag & INP_IPV6)`. It validates XNU panic/debugger title extraction through the Darwin BSD-style reporter.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 20 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `DoS`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `panic(cpu 0 caller 0xffffff801f3ada45): assertion failed: in6p == NULL || (in6p->inp_vflag & INP_IPV6), file: /Users/space/kernel/xnu-7195.81.3/bsd/netinet6/in6_mcast.c, line: 1905`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/darwin/report/0 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/darwin/report/1 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/darwin/report/1

Purpose: Darwin fixture expecting normalized title `panic: Kernel trap type NUM=page fault`. It validates XNU panic/debugger title extraction through the Darwin BSD-style reporter.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 36 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `DoS`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `panic(cpu 1 caller 0xffffff8002928989): Kernel trap at 0xffffff80021020ba, type 14=page fault, registers:`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/darwin/report/1 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/darwin/report/2 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/darwin/report/2

Purpose: Darwin fixture expecting normalized title `panic: in6p_route_copyout: wrong or corrupted route`. It validates XNU panic/debugger title extraction through the Darwin BSD-style reporter.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 21 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `DoS`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `panic(cpu 1 caller 0xffffff80186da902): "in6p_route_copyout: wrong or corrupted route: 0xffffff8ae77ba750"@/Users/space/kernel/xnu-7195.81.3/bsd/netinet6/in6_pcb.c:1450`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/darwin/report/2 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/darwin/report/3 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/darwin/report/3

Purpose: Darwin fixture expecting normalized title `panic: zalloc: default.kalloc.NUM retry fail NUM`. It validates XNU panic/debugger title extraction through the Darwin BSD-style reporter.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 23 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `DoS`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `panic(cpu 1 caller 0xffffff8009da2f32): "zalloc: default.kalloc.4096 (357 elements) retry fail 6"@/Users/space/kernel/xnu-7195.81.3/osfmk/kern/zalloc.c:3413`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/darwin/report/3 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/darwin/report/4 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/darwin/report/4

Purpose: Darwin fixture expecting normalized title `panic: pf_send_tcp: not AF_INET or AF_INET6!`. It validates XNU panic/debugger title extraction through the Darwin BSD-style reporter.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 22 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `DoS`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `panic(cpu 1 caller 0xffffff801d080ed5): "pf_send_tcp: not AF_INET or AF_INET6!"@/Users/space/kernel/xnu-7195.81.3/bsd/net/pf.c:2578`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/darwin/report/4 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/darwin/report/5 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/darwin/report/5

Purpose: Darwin fixture expecting normalized title `panic: slab_nextptr_panic: mcache.mbuf buffer ADDR in slab ADDR modified after free at offset NUM: ADDR out of range [AD`. It validates XNU panic/debugger title extraction through the Darwin BSD-style reporter.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 27 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `DoS`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `panic(cpu 0 caller 0xffffff800ac3235c): slab_nextptr_panic: mcache.mbuf buffer 0xffffffa0464b6000 in slab 0xffffffa015c843a0 modified after free at offset 0: 0xccd900000000 out of range [0xffffffa0463a3000-0xffffffa04c3a3000)`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/darwin/report/5 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/darwin/report/6 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/darwin/report/6

Purpose: Darwin fixture expecting normalized title `debugger: Unexpected kernel trap number: 0xe`. It validates XNU panic/debugger title extraction through the Darwin BSD-style reporter.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 39 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `not specified`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `Debugger: Unexpected kernel trap number: 0xe, RIP: 0xffffff80021020ba, CR2: 0x0`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/darwin/report/6 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/0 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/0

Purpose: FreeBSD fixture expecting normalized title `Fatal trap NUM: page fault while in kernel mode in atrtc_settime`. It validates FreeBSD fatal-trap, panic, stack-backtrace, and sanitizer title extraction.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 30 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `not specified`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `Fatal trap 12: page fault while in kernel mode`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/0 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/1 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/1

Purpose: FreeBSD fixture expecting normalized title `Fatal trap NUM: page fault while in kernel mode in sctp_sosend`. It validates FreeBSD fatal-trap, panic, stack-backtrace, and sanitizer title extraction.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 31 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `not specified`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `Fatal trap 12: page fault while in kernel mode`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/1 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/10 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/10

Purpose: FreeBSD fixture expecting normalized title `panic: size_on_all_streams smaller than control length`. It validates FreeBSD fatal-trap, panic, stack-backtrace, and sanitizer title extraction.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 24 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `DoS`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `panic: size_on_all_streams = 2644 smaller than control length 4096`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/10 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/11 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/11

Purpose: FreeBSD fixture expecting normalized title `panic: sbflush_internal: residual data`. It validates FreeBSD fatal-trap, panic, stack-backtrace, and sanitizer title extraction.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 21 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `DoS`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `panic: sbflush_internal: ccc 0 mb 0 mbcnt 768`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/11 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/12 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/12

Purpose: FreeBSD fixture expecting normalized title `panic: sx lock still held in solisten_proto`. It validates FreeBSD fatal-trap, panic, stack-backtrace, and sanitizer title extraction.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 22 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `DoS`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `panic: sx lock still held`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/12 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/13 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/13

Purpose: FreeBSD fixture expecting normalized title `panic: pfi_dynaddr_setup: non-NULL dyn`. It validates FreeBSD fatal-trap, panic, stack-backtrace, and sanitizer title extraction.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 24 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `DoS`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `panic: pfi_dynaddr_setup: dyn is 0x8000`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/13 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/14 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/14

Purpose: FreeBSD fixture expecting normalized title `panic: ASan: Invalid access, NUM-byte read in aesni_encrypt_icm`. It validates FreeBSD fatal-trap, panic, stack-backtrace, and sanitizer title extraction.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 27 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `DoS`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `panic: ASan: Invalid access, 16-byte read at 0xfffffe000793dd20, RedZonePartial(5)`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/14 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/15 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/15

Purpose: FreeBSD fixture expecting normalized title `panic: ASan: Invalid access, NUM-byte write in strlcpy`. It validates FreeBSD fatal-trap, panic, stack-backtrace, and sanitizer title extraction.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 23 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `DoS`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `panic: ASan: Invalid access, 1-byte write at 0xfffffe0057414be0, MallocRedZone(fb)`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/15 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/2 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/2

Purpose: FreeBSD fixture expecting normalized title `Fatal trap NUM: general protection fault while in kernel mode in udp_close`. It validates FreeBSD fatal-trap, panic, stack-backtrace, and sanitizer title extraction.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 31 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `not specified`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `Fatal trap 9: general protection fault while in kernel mode`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/2 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/3 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/3

Purpose: FreeBSD fixture expecting normalized title `panic: ffs_write: type ADDR X (Y,Z)`. It validates FreeBSD fatal-trap, panic, stack-backtrace, and sanitizer title extraction.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 17 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `DoS`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `panic: ffs_write: type 0xfffff80036275ce8 8 (0,230)`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/3 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/4 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/4

Purpose: FreeBSD fixture expecting normalized title `panic: mtx_lock() of destroyed mutex at sys/kern/sys_socket.c:LINE`. It validates FreeBSD fatal-trap, panic, stack-backtrace, and sanitizer title extraction.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 20 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `DoS`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `login: panic: mtx_lock() of destroyed mutex @ /mnt/go/src/github.com/google/syzkaller/bin/managers/freebsd/kernel/sys/kern/sys_socket.c:316`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/4 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/5 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/5

Purpose: FreeBSD fixture expecting normalized title `Fatal trap NUM: general protection fault in unp_dispose`. It validates FreeBSD fatal-trap, panic, stack-backtrace, and sanitizer title extraction.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 39 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `not specified`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `Fatal trap 9: general protection fault while in kernel mode`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/5 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/6 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/6

Purpose: FreeBSD fixture expecting normalized title `Fatal trap NUM: general protection fault in sctp_inpcb_bind`. It validates FreeBSD fatal-trap, panic, stack-backtrace, and sanitizer title extraction.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 35 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `not specified`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `Fatal trap 9: general protection fault while in kernel mode`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/6 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/7 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/7

Purpose: FreeBSD fixture expecting normalized title `Fatal trap NUM: page fault in vm_page_unhold_pages`. It validates FreeBSD fatal-trap, panic, stack-backtrace, and sanitizer title extraction.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 37 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `not specified`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `Fatal trap 12: page fault while in kernel mode`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/7 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/8 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/8

Purpose: FreeBSD fixture expecting normalized title `Fatal trap NUM: page fault in inp_freemoptions`. It validates FreeBSD fatal-trap, panic, stack-backtrace, and sanitizer title extraction.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 37 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `not specified`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `Fatal trap 12: page fault while in kernel mode`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/8 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/9 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/9

Purpose: FreeBSD fixture expecting normalized title `panic: sctp: no chunks on the queues`. It validates FreeBSD fatal-trap, panic, stack-backtrace, and sanitizer title extraction.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 21 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `DoS`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `panic: No chunks on the queues for sid 5.`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/freebsd/report/9 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/0 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/0

Purpose: Fuchsia fixture expecting normalized title `ASSERT FAILED in Dispatcher::UpdateInternalLocked`. It validates Zircon, Starnix, fatal-exception, double-fault, KVM, or reboot parsing through the Fuchsia reporter.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 93 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `not specified`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `executing program`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/0 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/1 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/1

Purpose: Fuchsia fixture expecting normalized title `ASSERT FAILED in size_to_index_helper`. It validates Zircon, Starnix, fatal-exception, double-fault, KVM, or reboot parsing through the Fuchsia reporter.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 64 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `not specified`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture includes a `REPORT:` block, so tests compare the exact extracted report bytes.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `executing program`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/1 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/10 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/10

Purpose: Fuchsia fixture expecting normalized title `unexpected kernel reboot`. It validates Zircon, Starnix, fatal-exception, double-fault, KVM, or reboot parsing through the Fuchsia reporter.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 103 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `REBOOT`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `[00037.711] 07800.07847> PageFault: 500574 free pages`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/10 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/11 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/11

Purpose: Fuchsia fixture expecting normalized title `double fault in x86_df_handler`. It validates Zircon, Starnix, fatal-exception, double-fault, KVM, or reboot parsing through the Fuchsia reporter.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 31 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `not specified`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `gfxconsole: rows 48, columns 113, extray 0`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/11 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/12 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/12

Purpose: Fuchsia fixture expecting normalized title `ASSERT FAILED in fbl::WAVLTree::iterator_impl::advance`. It validates Zircon, Starnix, fatal-exception, double-fault, KVM, or reboot parsing through the Fuchsia reporter.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 50 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `not specified`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `gfxconsole: rows 48, columns 113, extray 0`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/12 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/13 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/13

Purpose: Fuchsia fixture expecting normalized title `double fault`. It validates Zircon, Starnix, fatal-exception, double-fault, KVM, or reboot parsing through the Fuchsia reporter.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 23 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `not specified`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `ZIRCON KERNEL PANIC`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/13 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/14 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/14

Purpose: Fuchsia fixture expecting normalized title `double fault in x86_df_handler`. It validates Zircon, Starnix, fatal-exception, double-fault, KVM, or reboot parsing through the Fuchsia reporter.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 19 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `not specified`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `ZIRCON KERNEL PANIC`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/14 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/15 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/15

Purpose: Fuchsia fixture expecting normalized title `ASSERT FAILED in exception_handler_worker`. It validates Zircon, Starnix, fatal-exception, double-fault, KVM, or reboot parsing through the Fuchsia reporter.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 16 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `not specified`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `ZIRCON KERNEL PANIC`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/15 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/16 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/16

Purpose: Fuchsia fixture expecting normalized title `double fault`. It validates Zircon, Starnix, fatal-exception, double-fault, KVM, or reboot parsing through the Fuchsia reporter.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 22 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `not specified`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `ZIRCON KERNEL PANIC`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/16 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/17 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/17

Purpose: Fuchsia fixture expecting normalized title `KVM internal error`. It validates Zircon, Starnix, fatal-exception, double-fault, KVM, or reboot parsing through the Fuchsia reporter.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 28 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `not specified`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `ZIRCON KERNEL PANIC`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/17 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/18 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/18

Purpose: Fuchsia fixture expecting normalized title `ASSERT FAILED: is_kernel_address(x86_get_percpu()->default_tss.rsp0)`. It validates Zircon, Starnix, fatal-exception, double-fault, KVM, or reboot parsing through the Fuchsia reporter.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 16 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `not specified`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `ZIRCON KERNEL PANIC`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/18 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/19 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/19

Purpose: Fuchsia fixture expecting normalized title `recursion in interrupt handler in arch_spin_lock`. It validates Zircon, Starnix, fatal-exception, double-fault, KVM, or reboot parsing through the Fuchsia reporter.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 34 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `not specified`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `ZIRCON KERNEL PANIC`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/19 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/2 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/2

Purpose: Fuchsia fixture expecting normalized title `ASSERT FAILED in fbl::Canary::Assert`. It validates Zircon, Starnix, fatal-exception, double-fault, KVM, or reboot parsing through the Fuchsia reporter.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 59 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `not specified`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture includes a `REPORT:` block, so tests compare the exact extracted report bytes.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `gfxconsole: rows 48, columns 113, extray 0`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/2 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/20 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/20

Purpose: Fuchsia fixture expecting normalized title `ASSERT FAILED in ProcessDispatcher::GetCurrent`. It validates Zircon, Starnix, fatal-exception, double-fault, KVM, or reboot parsing through the Fuchsia reporter.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 190 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `not specified`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `ZIRCON KERNEL PANIC`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/20 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/21 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/21

Purpose: Fuchsia fixture expecting normalized title `KVM internal error`. It validates Zircon, Starnix, fatal-exception, double-fault, KVM, or reboot parsing through the Fuchsia reporter.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 29 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `not specified`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `[00268.965] 48047.49380> PageFault: 430289 free pages`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/21 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/22 -->
# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/22

Purpose: Fuchsia fixture negative fixture. It intentionally has no `TITLE:` header and verifies that the reporter does not classify the captured log fragment as a crash.

Important APIs/types/functions: the file is consumed by `report_test.go` through `forEachFile`, `readDir`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport`. It is data rather than Go code: metadata headers define expected `Report` fields, the blank-line-separated body is the raw console log, and an optional `REPORT:` block pins exact extraction.

Control flow: during `TestParse`, the relevant reporter for this fixture directory parses the raw log and `ContainsCrash` must agree with whether a title is expected. Parsed output is converted back into a `ParseTest` and compared with the headers. If a `REPORT:` section is present, `checkReport` also requires byte-for-byte equality for the shortened/extracted report. Start, end, and skip offsets are validated for every positive parse.

State and persistence: this fixture is static repository test data with 3 lines. It does not persist runtime state, but `go test ./pkg/report -update` can rewrite headers or expected report text when parser behavior is intentionally changed.

Dependencies and integration points: the fixture lives under the source-tree-aligned testdata hierarchy and is selected only because its basename is numeric. It integrates with the OS-specific reporter tables plus shared title sanitization, dynamic replacement, crash type classification, suppression handling, and report-boundary invariants. Expected crash type is `not specified`. No explicit corrupted/suppressed/panicked/executor flags are declared. The fixture has no explicit `REPORT:` block, so tests focus on metadata and parser invariants.

Risks: fixture expectations can become stale when kernel log formats, title sanitization, or oops ordering changes. Overly broad regexps may make a negative fixture positive; overly narrow regexps may lose this expected title. Exact report blocks are sensitive to trimming changes. First log signal: `gfxconsole: rows 48, columns 113, extray 0`.

Test signals: a pass means the reporter still produces the expected title, type, flags, optional exact report body, and valid offsets for this sample. A failure should be reviewed against the responsible OS reporter table rather than blindly updating the fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/22 -->
