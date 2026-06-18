# Research Group subset-b-009402

This grouped report covers the `pkg/aflow` workflow runtime, AI workflow registrations, and syzkaller/kernel action adapters. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/action/actionsyzlang/crepro.go -->
# sources/test-tools/syzkaller/pkg/aflow/action/actionsyzlang/crepro.go

## Purpose

`crepro.go` defines the `CreateSimplifiedCRepro` aflow action. It converts a syzkaller program reproducer into a simplified C reproducer suitable for LLM prompts, and falls back to a caller-provided C reproducer when no syz reproducer is available.

## Important APIs, Types, and Functions

The exported action is `CreateSimplifiedCRepro = aflow.NewFuncAction("syz-repro-to-c-repro", createCRepro)`. Inputs are `createCReproArgs` (`TargetOS`, `TargetArch`, `ReproSyz`, `ReproC`) and the output is `createCReproResult.SimplifiedCRepro`. `createCRepro` uses `prog.GetTarget`, target `Deserialize`, and `csource.WriteLLM`. `truncateLargeData` uses `stringLiteralSeq` and `maxStringLiteralSeqLen` to replace long C string-literal sequences with a fixed placeholder.

## Control Flow

If `ReproSyz` is empty, the action returns the provided `ReproC` after truncating large string literal data. Otherwise it resolves the syzkaller target, deserializes the syz program in non-strict mode, converts it through `csource.WriteLLM`, and truncates oversized data blobs in the generated C text before returning it.

## State and Persistence Behavior

The action is pure with respect to aflow state: it reads typed inputs from the current state and emits one output field. It does not use the cache, filesystem, or temp directories. The only persistent integration is through aflow registration of the action variable at package initialization.

## Dependencies and Integration Points

It depends on `pkg/aflow` for action wrapping, `pkg/csource` for C rendering, `prog` and imported syzkaller `sys` descriptions for target/program parsing. It is used by security assessment and patch generation flows to include a compact reproducer in LLM prompts.

## Risks and Edge Cases

The non-strict deserializer accepts some malformed or old syz repro variants; this is useful for workflow robustness but can hide minor input issues. The truncation regex is C-string oriented and may replace any long adjacent string literal sequence, not only byte arrays. If `TargetOS` or `TargetArch` is wrong, conversion fails before LLM stages. Empty syz and empty C inputs intentionally produce an empty simplified repro.

## Test Signals

Tests cover linux/amd64 and linux/arm64 conversion where host compilers are available, invalid syz deserialization, empty syz fallback, and multiline/single-line large string truncation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/action/actionsyzlang/crepro.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/action/actionsyzlang/crepro_test.go -->
# sources/test-tools/syzkaller/pkg/aflow/action/actionsyzlang/crepro_test.go

## Purpose

`crepro_test.go` verifies syz-to-C conversion and large-data truncation for the `CreateSimplifiedCRepro` implementation.

## Important APIs, Types, and Functions

The tests call unexported `createCRepro` directly with `createCReproArgs` and call `truncateLargeData` directly. `TestSyzlangToC`, `TestSyzlangToC_Invalid`, `TestSyzlangToC_Empty`, and `TestTruncateLargeData` are the main test cases.

## Control Flow

The conversion test iterates amd64 and arm64, skips unsupported host/compiler combinations using `targets.Get` and `runtime.GOOS`, builds a valid syz program, and asserts the generated C contains `int main`. The invalid test feeds an unknown syscall and checks the wrapped deserialization error. The truncation test compares exact output for multiline adjacent string literals, one long single-line literal, and a short literal that must remain unchanged.

## State and Persistence Behavior

The tests do not create aflow contexts or persistent cache state. They depend on target metadata and host build support for some architectures, and use `t.Skipf` rather than failing when the host cannot build.

## Dependencies and Integration Points

They depend on `sys/targets` and `testify/require`. The conversion case indirectly exercises syzkaller syscall descriptions, `prog.Deserialize`, and `csource.WriteLLM`.

## Risks and Edge Cases

Architecture skips mean CI coverage can vary by host. The empty test passes only `ReproSyz: ""`, so it validates empty fallback but not non-empty `ReproC` passthrough. The truncation expectations are exact and therefore guard accidental placeholder or regex changes.

## Test Signals

These tests are strong signals for parser/converter regressions and prompt-size protection. They do not exercise all target OSes or all C repro forms.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/action/actionsyzlang/crepro_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/action/actionsyzlang/format.go -->
# sources/test-tools/syzkaller/pkg/aflow/action/actionsyzlang/format.go

## Purpose

`format.go` defines the `Format` action that validates and canonicalizes an LLM-generated syzkaller program before it is executed by reproduction workflows.

## Important APIs, Types, and Functions

`Format = aflow.NewFuncAction("syzlang-format", formatActionFunc)` exposes the action. `FormatArgs` contains `TargetOS`, `TargetArch`, and `CandidateReproSyz`; `FormatResult` returns `ReproSyz`. `formatActionFunc` resolves the syzkaller target, deserializes the candidate program with `prog.Strict`, and returns `p.Serialize()`.

## Control Flow

The function obtains the target first. It then strictly deserializes the candidate syz text, returning a contextual `failed to deserialize syzkaller program` error on invalid programs. On success, the serializer normalizes formatting, resource references, and target-specific program syntax.

## State and Persistence Behavior

The action has no persistent state, no filesystem writes, and no cache interaction. It transforms one state field into `ReproSyz` for later actions such as `crash.Reproduce`.

## Dependencies and Integration Points

It integrates `aflow` function actions with syzkaller `prog` target descriptions and the imported `sys` package. In the repro flow it is the validation gate between the LLM candidate and VM execution.

## Risks and Edge Cases

Strict deserialization rejects candidate syntax that non-strict paths might accept, so LLM output must be complete and target-correct. Empty candidates fail as deserialization errors. Target lookup errors propagate without extra context.

## Test Signals

Tests cover valid and invalid linux programs across amd64 and arm64 and assert unknown syscall errors are surfaced.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/action/actionsyzlang/format.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/action/actionsyzlang/format_test.go -->
# sources/test-tools/syzkaller/pkg/aflow/action/actionsyzlang/format_test.go

## Purpose

`format_test.go` validates strict syzkaller program formatting behavior for candidate repros.

## Important APIs, Types, and Functions

`TestFormat` invokes `formatActionFunc` with `FormatArgs` and checks `FormatResult.ReproSyz`. It uses `testify/require` assertions.

## Control Flow

For amd64 and arm64, the test submits a valid `openat` plus `write` syz program and expects non-empty canonical output. It then submits an unknown syscall and expects an error containing `unknown syscall`.

## State and Persistence Behavior

The test is stateless and does not use aflow execution, cache, or filesystem state. It depends on syzkaller target descriptions being registered by package imports.

## Dependencies and Integration Points

It indirectly exercises `prog.GetTarget`, strict target deserialization, and serialization for linux syscall descriptions.

## Risks and Edge Cases

It does not check exact canonical formatting, only non-empty output, so serializer formatting regressions that still produce text may pass. It also does not test bad target names or empty candidates.

## Test Signals

The invalid syscall check is the strongest behavioral signal because it confirms strict validation catches LLM hallucinated syscall names.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/action/actionsyzlang/format_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/action/crash/reproduce.go -->
# sources/test-tools/syzkaller/pkg/aflow/action/crash/reproduce.go

## Purpose

`reproduce.go` implements the crash reproduction action and the lower-level VM test runner. It boots configured kernels, runs syz or C reproducers, aggregates crashes across repeated runs, optionally collects coverage, caches expensive executions, and reports whether the expected crash reproduced.

## Important APIs, Types, and Functions

The exported action is `Reproduce = aflow.NewFuncAction("crash-reproducer", ReproduceFunc)`. `ReproduceArgs` carries manager/VM/kernel/reproducer/strace configuration. `RunTestResult` returns the primary `report.Report`, other reports, boot error, fault injection details, coverage, and raw console output. `RunTest` builds a `mgrconfig.Config`, creates an `instance.Env`, collects runs, and calls `aggregateTestResults`. `ReproduceFuncWithCoverage` caches results in a `cachedExecution` object and returns both the typed action result and cache ID. `LoadCoverage` retrieves cached coverage. `symbolize` maps raw PCs to `symbolizer.Frame`s.

## Control Flow

`RunTest` validates VM type and coverage prerequisites, parses the VM JSON, adjusts QEMU or GCE-specific kernel/image paths, completes a syzkaller manager config, creates an environment and crash reporter, and calls `instance.CollectRuns` for up to six runs looking for three valid runs. Aggregation groups `instance.CrashError`s by title, chooses the most frequent title with lexical tie-breaking, records remaining crash types as secondary reports, records the first boot/test error, and symbolizes coverage only when no crash or boot error occurred. `ReproduceFuncWithCoverage` hashes kernel config, image data, VM config, repros, options, and coverage mode into a cache description. It runs `RunTest` only on a cache miss, converts reports to strings, and converts "no crash" into `aflow.FlowError(ErrDidNotCrash)`.

## State and Persistence Behavior

The action uses aflow's on-disk cache for expensive VM executions and temp directories for per-run work. Cache object IDs are later used by coverage-loading tools. The cache key includes image content hash and repro/option hashes, so VM runs are reused only for equivalent inputs. `Context.Close` releases cached dirs after flow execution.

## Dependencies and Integration Points

It integrates aflow with syzkaller `build`, `instance`, `mgrconfig`, `report`, `symbolizer`, and target metadata. It is used by repro, patching, patch-iteration, and C-repro workflows. GCE support uses `build.EmbedLinuxKernel`; QEMU uses the kernel image path directly. Fault injection extraction comes from the crash reporter.

## Risks and Edge Cases

VM type support is limited to `qemu` and `gce`. Coverage requires a syz repro and is skipped on crashes. Aggregating by report title can conflate or split related crashes depending on title stability. The cache key reads the full image file, which can be expensive. Boot/test errors are returned as normal cached data and later surfaced as errors. `errors.AsType` use for `CrashError` means only correctly wrapped instance errors are recognized. `RunTest` mutates `args.Image` for GCE locally.

## Test Signals

The unit test for `aggregateTestResults` covers single crashes, repeated same-title crashes, flaky runs, majority crash selection, boot errors, and all-ok runs. Full VM behavior requires integration tests or workflow runs with real kernels/images.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/action/crash/reproduce.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/action/crash/reproduce_test.go -->
# sources/test-tools/syzkaller/pkg/aflow/action/crash/reproduce_test.go

## Purpose

`reproduce_test.go` unit-tests crash result aggregation without booting VMs.

## Important APIs, Types, and Functions

`TestAggregateTestResults` constructs `instance.EnvTestResult` slices containing `instance.CrashError`, `instance.TestError`, and successful runs, then calls `aggregateTestResults` with a dummy linux/amd64 reporter.

## Control Flow

Each table case feeds synthetic run results into the aggregator. Assertions check that the selected primary report has the expected title/report body, that boot errors are recorded when no crash wins, and that all-ok inputs produce neither report nor boot error.

## State and Persistence Behavior

The test uses no aflow cache or VM state. The only constructed state is a `report.Reporter` configured with linux/amd64 derived target fields.

## Dependencies and Integration Points

It depends on `pkg/instance`, `pkg/mgrconfig`, `pkg/report`, and `testify/require`. It verifies the contract expected by `RunTest` after `instance.CollectRuns`.

## Risks and Edge Cases

The test does not cover coverage symbolization, fault injection extraction, raw console output, or tie-breaking for equal crash counts with different titles. It also bypasses JSON VM config and manager setup.

## Test Signals

The cases provide strong regression coverage for selecting the most frequent crash and not letting boot errors override crashes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/action/crash/reproduce_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/action/crash/run_c_repro.go -->
# sources/test-tools/syzkaller/pkg/aflow/action/crash/run_c_repro.go

## Purpose

`run_c_repro.go` defines the `RunCRepro` action, which runs a formatted C reproducer in the configured VM and optionally re-runs with strace when the first run does not crash.

## Important APIs, Types, and Functions

`RunCReproArgs` carries target, VM, kernel, formatted C repro, and strace fields. `RunCReproResult` reports reproduction status, console and strace output, primary and secondary crash reports, and boot/test error text. `RunCReproFunc` validates inputs, creates a temp workdir, builds `ReproduceArgs`, calls `RunTest`, and maps `RunTestResult` into action outputs.

## Control Flow

The function rejects empty C repros and empty target arch. It performs a first `RunTest` without strace and records console output, boot error, primary report, and other reports. If the first run neither crashes nor has a boot error and strace was requested with a binary path, it sets `NeedStrace`, reruns the same C repro, stores the second run output as `StraceOutput`, and merges any crash/test results from that run.

## State and Persistence Behavior

It uses `ctx.TempDir()` for VM run work artifacts and relies on the enclosing context to remove the temp directory. It does not use the persistent cache itself, so repeated C repro attempts are not memoized here.

## Dependencies and Integration Points

It is used by the `reproc` workflow after C generation and compilation. It depends on `RunTest` from `reproduce.go` for all VM behavior and on aflow action registration.

## Risks and Edge Cases

`RunCReproArgs.NeedStrace` is only honored when `StraceBin` is non-empty and the first run is clean. The initial `ReproduceArgs` does not copy `NeedStrace`, which is intentional for run 1 but important to preserve. Errors from the second run return the partial first-run result plus the error. Other reports can contain reports from both runs.

## Test Signals

No direct unit test is present in this file set. It is exercised through C-repro workflow integration and depends heavily on `RunTest` behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/action/crash/run_c_repro.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/action/crash/test.go -->
# sources/test-tools/syzkaller/pkg/aflow/action/crash/test.go

## Purpose

`test.go` implements the `TestPatch` action used by patch generation loops. It formats and captures the current kernel source diff, builds the modified kernel, runs the reproducer on it, returns build/boot/crash errors as `TestError`, and restores the scratch source tree afterward.

## Important APIs, Types, and Functions

`TestPatch = aflow.NewFuncAction("test-patch", testPatch)`. `testArgs` carries kernel, VM, repro, and scratch source configuration; `testResult` returns `PatchDiff` and `TestError`. Supporting functions are `testPatchBuild`, `testPatchRepro`, `currentDiff`, `undoChanges`, and `findClangFormatDiff`.

## Control Flow

`testPatch` defers `undoChanges`, computes the formatted current diff, short-circuits with `No patch to test.` when empty, builds a cache key from kernel/image/VM/repro/patch hashes, and caches the sequence of build then repro test. Build errors are converted into `TestError` strings rather than hard errors. Repro testing rejects non-Linux targets as flow errors, runs `RunTest`, and returns the crash report if the bug still reproduces or the boot error otherwise. `currentDiff` marks untracked files intent-to-add, runs `git diff -U0`, pipes it through the newest `clang-format-diff.py`, then returns a full `git diff`.

## State and Persistence Behavior

The scratch repository is intentionally mutated by code-editing tools before this action. `testPatch` always attempts to reset tracked changes and clean untracked files afterward, while keeping ignored build artifacts for speed. Patch test results are cached under `patch-test` using patch and environment hashes.

## Dependencies and Integration Points

It depends on kernel building (`kernel.BuildKernel`), crash testing (`RunTest`), `osutil` command helpers, `hash`, `targets`, and system `git` plus `clang-format-diff.py`. It is the validation gate inside patch generation and patch iteration loops.

## Risks and Edge Cases

`undoChanges` is destructive to scratch-tree edits by design; it must never point at a non-scratch user checkout. Formatting requires distro-specific `clang-format-diff.py` paths. The cache key omits `ReproSyz` and `ReproOpts`, so if only those change while C repro and other fields stay fixed, cache reuse could be surprising. Build failures are currently classified as patch errors, with a TODO about infra-vs-patch distinction.

## Test Signals

No direct unit tests are included. Workflow tests indirectly verify registration, but real confidence requires integration with a scratch git tree, clang-format, kernel build, and VM repro run.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/action/crash/test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/action/kernel/build.go -->
# sources/test-tools/syzkaller/pkg/aflow/action/kernel/build.go

## Purpose

`build.go` defines the kernel build action and reusable `BuildKernel` helper. It turns a kernel source tree and config into a cached object directory containing the kernel image, vmlinux, compile database, and retained generated/source files.

## Important APIs, Types, and Functions

`Build = aflow.NewFuncAction("kernel-builder", buildKernel)`. `buildArgs` contains target, source, commit, and config; `buildResult.KernelObj` is the output directory. `BuildKernel` writes `.config`, adjusts config with `scripts/config`, invokes `make`, extracts root-cause build errors, and optionally cleans intermediate files. `cmdlineRe` preserves existing ARM64 command-line config when appending required boot args.

## Control Flow

The helper writes the config to the build directory, disables x32 and enforces gzip for amd64, appends GCE serial/root command-line defaults for arm64, runs `scripts/config`, derives the image and make arguments, builds the image and `compile_commands.json`, and wraps root-cause build failures as `aflow.FlowError`. If cleanup is enabled, it walks the build directory and deletes files that are not the kernel image, vmlinux, compile database, directories, or source files.

## State and Persistence Behavior

The action uses `ctx.Cache("build", desc, populate)` where `desc` is keyed by kernel commit and config hash. Cached build directories are reference-counted by the aflow cache and released on context close.

## Dependencies and Integration Points

It depends on syzkaller `build`, `codesearch`, `hash`, `osutil`, and target metadata. The build output feeds VM reproduction, code search indexing, and patch testing. It assumes LLVM toolchain defaults and ccache.

## Risks and Edge Cases

Kernel builds are long-running and environment-sensitive. Config rewriting is target-specific and only handles amd64/arm64 special cases. Cleanup must preserve generated source files for code search while reclaiming space; overly broad deletion could harm later tooling. `build.ExtractRootCause` classification determines whether users see actionable root-cause information.

## Test Signals

No direct unit tests are present. Signals come from workflow registration and real kernel build integration runs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/action/kernel/build.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/action/kernel/checkout.go -->
# sources/test-tools/syzkaller/pkg/aflow/action/kernel/checkout.go

## Purpose

`checkout.go` provides cached and scratch Linux kernel checkout actions. It centralizes access to a shared full Linux repo, applies known compatibility fixes/backports, and creates shallow clones for workflow use.

## Important APIs, Types, and Functions

`Checkout` wraps `checkout`, and `CheckoutScratch` wraps `checkoutScratch`. `checkoutArgs` selects `KernelRepo` and `KernelCommit`; `checkoutResult.KernelSrc` is a cached source tree. `checkoutScratchArgs.KernelSrc` produces a temp `KernelScratchSrc`. `kernelBackports` lists commits needed for out-of-tree builds. `UseLinuxRepo` serializes access to the shared repo with `repoMu`. Helpers include `runSandboxedGit` and `shallowGitClone`.

## Control Flow

`checkout` builds a cache key from the requested commit plus backport hashes, enters the shared repo via `UseLinuxRepo`, and populates a cached shallow clone by switching or checking out the commit. It conditionally reverts a known bad compile-commands commit if its revert is absent, applies required backports, commits those backports when applied, and shallow-clones the prepared tree into the cache directory. `checkoutScratch` shallow-clones a cached source tree into a temp dir for edit workflows.

## State and Persistence Behavior

The shared repo lives under `ctx.Workdir/repo/linux` and is protected by a process mutex. Prepared source trees live in aflow cache entries under `src`. Scratch clones live in temp dirs removed by context close.

## Dependencies and Integration Points

It uses syzkaller `vcs`, `osutil`, target constants, and git. All kernel-dependent flows call it before build, code search, reproduction, or patch editing.

## Risks and Edge Cases

The process-local mutex does not coordinate across processes. The shared repo can be left in a transient state if an operation fails before the next checkout repairs it. Backport commits are committed into the shared repo before shallow clone, so user identity is supplied explicitly. `shallowGitClone` assumes the target dir exists and can run `git init`. Network/repo fetch failures propagate as infrastructure errors.

## Test Signals

No direct tests are present in the assigned set. Workflow registration validates dataflow, while integration tests must cover real repo checkout, backport application, bad-commit revert logic, and scratch clone creation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/action/kernel/checkout.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/ai/ai.go -->
# sources/test-tools/syzkaller/pkg/aflow/ai/ai.go

## Purpose

`ai.go` defines stable workflow type names and dashboard-facing output structs shared by `pkg/aflow/...` and dashboard packages. It is the schema contract for persisted AI workflow results.

## Important APIs, Types, and Functions

`WorkflowType` enumerates `patching`, `patch-iteration`, `moderation`, `assessment-kcsan`, `assessment-security`, `repro`, and `repro-c`. Output structs include `PatchingOutputs`, `PatchIterationOutputs`, `AssessmentKCSANOutputs`, `AssessmentSecurityOutputs`, `ModerationOutputs`, `ReproOutputs`, and `ReproCOutputs`. Shared value types include `Recipient`, `FixesTag`, `EmailTag`, `ExternalComment`, `PatchHistoryEntry`, and `CommentReply`.

## Control Flow

The file contains data definitions only. Control flow is created elsewhere by `aflow.Register`, which binds workflow types to concrete `Flow`s and uses these structs to extract typed outputs.

## State and Persistence Behavior

Comments warn that workflow type strings and output struct fields are stored in the dashboard database. Renaming/removing fields or changing string constants can break old persisted jobs and dashboard predicates.

## Dependencies and Integration Points

It imports `time` for external comment timestamps. The types are consumed by flow registration, dashboard config predicates, email/tag handling, and UI/API persistence.

## Risks and Edge Cases

Schema evolution is the main risk. Adding fields is relatively safe, but deleting or renaming fields requires migration or backward-compatibility handling. `AssessmentSecurityOutputs` is explicitly used in dashboard config predicates, making it especially sensitive.

## Test Signals

There are no direct tests for this schema file. Registration tests indirectly verify field names match produced workflow outputs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/ai/ai.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/cache.go -->
# sources/test-tools/syzkaller/pkg/aflow/cache.go

## Purpose

`cache.go` implements aflow's on-disk cache for expensive workflow artifacts such as kernel checkouts, builds, LLM responses, and serialized execution objects. It provides reference-counted cache entry use, metadata-based startup recovery, temporary directories, and size-based purging.

## Important APIs, Types, and Functions

`Cache` stores root dir, max size, time source, mutex, current size, and `entries`. `cacheEntry` tracks dir, size, usage count, and last use. `NewCache` and `newTestCache` initialize from disk. `Create` creates or returns a cache dir for `(typ, desc)`. `cacheCreateObject` and `cacheReadObject` store/load JSON objects. `Release`, `TempDir`, `init`, and `purge` manage lifecycle. Metadata is `cacheMeta` in `aflow-meta`, currently version `1`.

## Control Flow

Initialization scans `dir/*/*`, removes incomplete directories with no metadata, upgrades stale metadata by recomputing disk usage, loads entries, and purges if needed. `Create` locks, hashes `desc` into an entry ID, removes any stale incomplete target dir, populates the final directory, writes metadata after successful population, increments usage, updates metadata mtime, and purges old unused entries. `purge` sorts entries by usage count then last-used time and deletes oldest unused entries until below max size.

## State and Persistence Behavior

Cache state persists on disk under type/hash directories. Validity is marked by the `aflow-meta` file, not by atomic rename, because kernel build paths may be embedded in artifacts. Temporary directories are placed under `tmp` without metadata and are cleaned on next cache init or by `Context.Close`.

## Dependencies and Integration Points

It depends on `hash.String`, `osutil` filesystem helpers, JSON helpers, and disk usage. `execute.go` wraps it through `Context.Cache`, `CacheObject`, `RetrieveObject`, and `TempDir`. Kernel, repro, LLM, and patch-test actions all depend on this cache.

## Risks and Edge Cases

Callers must call `Release` exactly once per successful `Create`; missing releases prevent purging, while double releases panic. Failed `populate` removes the directory. Because creation happens directly in the final path, readers must rely on metadata existence to distinguish complete entries. `purge` requires the mutex to already be locked and panics if not. `currentSize < maxSize` means a cache exactly at max size will attempt purge.

## Test Signals

Tests cover cache hit/miss behavior, failed population cleanup, restart recovery, incomplete-dir cleanup, max-size purging by last use, JSON object storage, cache object retrieval, and invalid cached ID validation through the public context helper.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/cache_test.go -->
# sources/test-tools/syzkaller/pkg/aflow/cache_test.go

## Purpose

`cache_test.go` validates cache persistence, purging, object storage, object retrieval, and cached ID validation.

## Important APIs, Types, and Functions

Tests use `newTestCache`, `Cache.Create`, `Release`, `cacheCreateObject`, `cacheReadObject`, public `CacheObject`, and `RetrieveObject`. `TestCache`, `TestCacheObject`, `TestCacheReadObject`, `TestRetrieveObject`, and `TestRetrieveObject_InvalidID` are the main cases.

## Control Flow

`TestCache` creates entries, verifies hits avoid repopulation, verifies failed population deletes directories, recreates the cache from disk, injects a stray metadata-less directory, and forces max-size purging with a mocked clock. Object tests write/read JSON payloads and verify last-used timestamps. Invalid ID tests cover path traversal, missing slash format, and empty path parts.

## State and Persistence Behavior

The tests use temp directories and mocked time. They intentionally create real files and directories to validate startup scanning, metadata, disk usage, mtime updates, and deletion.

## Dependencies and Integration Points

They use `osutil` for file writes and existence checks, `testify/require`, and `NewTestContext` for public object retrieval.

## Risks and Edge Cases

Disk usage can be filesystem-block dependent, so tests use broad size margins rather than exact byte counts. CI environment differences could affect symlink or disk behavior, but temp-dir isolation keeps blast radius low.

## Test Signals

The tests are strong signals for cache correctness around stale directories, LRU-like purging, reference-count release, JSON object lookup, and safe cached ID parsing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/execute.go -->
# sources/test-tools/syzkaller/pkg/aflow/execute.go

## Purpose

`execute.go` is the main runtime for executing registered aflow workflows. It validates inputs, constructs execution context, manages cache/temp lifecycle, records trajectory spans, calls Gemini/Vertex models, classifies quota/token errors, and exposes helpers used by actions and tools.

## Important APIs, Types, and Functions

`(*Flow).Execute` runs a workflow. Error helpers include `FlowError`, `IsFlowError`, `IsModelQuotaError`, `isInputTokenOverflowError`, `isOutputTokenOverflowError`, and `QuotaResetTime`. `Context` carries `context.Context`, workdir, model override, cache, state map, event callback, span counters, and test stubs. Cache helpers include `Context.Cache`, `CacheObject`, `RetrieveObject`, `CacheReadObject`, `TempDir`, and `Close`. Model functions include `generateContentGemini` and `loadModelList`.

## Control Flow

`Execute` converts inputs to the workflow input struct, clones them, inserts consts, builds `Context`, installs test stubs/default time/model functions, starts a flow span, executes the root action, records extracted outputs on success, finishes the span, checks span nesting balance, and returns outputs. `generateContentGemini` lazily initializes a singleton model client/list, checks model existence, caps temperature to model metadata, disables thinking for non-thinking models, applies a 10-minute request timeout, and maps deadline hangs to retry errors. `loadModelList` chooses exactly one backend from environment variables and either hardcodes Vertex model metadata or queries Gemini Developer API models.

## State and Persistence Behavior

Workflow state is a mutable `map[string]any` scoped to one execution. Cache dirs and temp dirs are tracked in the context and released/removed by `Close`. Model client/list are process-global singletons. Trajectory spans are emitted through `onEvent` at start and finish with sequence and nesting.

## Dependencies and Integration Points

It uses `google.golang.org/genai`, syzkaller `osutil`, trajectory records, and aflow schema conversion helpers. All actions/tools depend on `Context`. Dashboard/job runners depend on `Flow.Execute` and `FlowError` to separate expected workflow failures from infrastructure failures.

## Risks and Edge Cases

Only one of `GOOGLE_API_KEY`, `GOOGLE_VERTEX_API_KEY`, or `GOOGLE_CLOUD_PROJECT` may be set. `onEvent` must be non-nil and reliable because span start/finish errors abort execution. The global model list is initialized once, so environment changes during process lifetime are ignored. Cache must be supplied; nil cache would panic in cache helpers. `RetrieveObject` intentionally rejects non-local or malformed IDs.

## Test Signals

`flow_test.go` covers workflow execution, missing inputs, quota reset time, const handling, and span-driven stubs. `cache_test.go` covers cache helpers. LLM tests exercise model error classification through lower-level functions.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/execute.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow.go -->
# sources/test-tools/syzkaller/pkg/aflow/flow.go

## Purpose

`flow.go` defines aflow's workflow registry and typed dataflow contract. It binds workflow input/output schemas to concrete action graphs and verifies those graphs at registration time.

## Important APIs, Types, and Functions

`Flow` contains name, consts, root action, model list, and `FlowType`. `FlowType` stores the stable `ai.WorkflowType`, description, input checker, and output extractor. `Flows` is the global registry. Public `Register[Inputs, Outputs]` delegates to `register`, which builds a `FlowType` and calls `registerOne`.

## Control Flow

Registration creates conversion functions for `Inputs` and `Outputs`. Each flow name is normalized to the workflow type string for the main implementation or `type-name` for secondary implementations. `registerOne` rejects duplicate names, creates a verification context, provides consts and inputs, verifies the root action graph, requires all output fields, finalizes unused/missing checks, collects used model names, and inserts the flow.

## State and Persistence Behavior

The global `Flows` map persists registered flows for the process lifetime. Flow consts are copied into execution state on every run by `Execute`.

## Dependencies and Integration Points

It depends on `ai.WorkflowType` and schema/verification helpers in the aflow package. All concrete flow packages register themselves from `init` functions.

## Risks and Edge Cases

Registration panics through the public `Register`, so broken flow definitions fail during package initialization. Flow names are global. Consts can conflict with inputs or be unused. Model lists are inferred from verification, so tools/agents that fail to verify accurately could affect scheduling/UI metadata.

## Test Signals

Flow tests cover a complex pipeline, no-input errors at execution time, flow consts, and registration errors for const conflicts/unused consts.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/assessment/actions.go -->
# sources/test-tools/syzkaller/pkg/aflow/flow/assessment/actions.go

## Purpose

`actions.go` contains a small shared assessment action that normalizes LLM explanations for email/dashboard presentation.

## Important APIs, Types, and Functions

`formatExplanation = aflow.NewFuncAction("format-explanation", formatExplanationFunc)`. `formatExplanationArgs.ExplanationRaw` is the input and `formatExplanationResult.Explanation` is the output. `formatExplanationFunc` calls `email.WordWrap` at 80 columns.

## Control Flow

The action is a direct transformation: read raw explanation from workflow state, word-wrap it, and emit `Explanation`.

## State and Persistence Behavior

It is stateless and does not use cache, filesystem, or external services. The output becomes a persisted dashboard workflow field through assessment output structs.

## Dependencies and Integration Points

It depends on aflow action wrapping and `pkg/email` word wrapping. KCSAN, moderation, and security assessment flows use it after their LLM agent.

## Risks and Edge Cases

Wrapping may affect markdown/code formatting if the LLM emits structured text. The fixed 80-column width is chosen for readability but may not match all UI contexts.

## Test Signals

No direct unit test is present. It is indirectly verified by flow registration because it consumes `ExplanationRaw` and produces required `Explanation`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/assessment/actions.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/assessment/kcsan.go -->
# sources/test-tools/syzkaller/pkg/aflow/flow/assessment/kcsan.go

## Purpose

`kcsan.go` registers the KCSAN assessment workflow, which determines whether a reported data race is benign and only needs annotations.

## Important APIs, Types, and Functions

`kcsanInputs` describes target, crash report, kernel repo/commit/config fields. `kcsanPrompt` embeds the crash report. The package `init` registers `ai.WorkflowAssessmentKCSAN` with output type `ai.AssessmentKCSANOutputs`.

## Control Flow

The workflow checks out and builds the kernel, prepares a code-search index, runs an `LLMAgent` named `expert` with the embedded KCSAN instruction prompt and `common.CodeAccessTools`, requests a structured `Benign` bool plus raw textual explanation, then runs `formatExplanation`.

## State and Persistence Behavior

Kernel checkout and build artifacts are cached by their actions. The LLM result and formatted output are stored in aflow state and later extracted into persisted dashboard output fields.

## Dependencies and Integration Points

It integrates kernel actions, `codesearcher.PrepareIndex`, common prompt loading, and code access tools. The prompt content is embedded by `prompts.go`.

## Risks and Edge Cases

The assessment relies on LLM use of actual code access tools; misleading reports or missing code index/build failures can affect output. The workflow always builds before assessment, so build failures block moderation-style classification.

## Test Signals

Global flow registration tests load this package and verify required dataflow. There are no semantic tests for KCSAN classifications.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/assessment/kcsan.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/assessment/moderation.go -->
# sources/test-tools/syzkaller/pkg/aflow/flow/assessment/moderation.go

## Purpose

`moderation.go` registers a moderation workflow that judges whether a bug report is internally consistent and actionable.

## Important APIs, Types, and Functions

`moderationInputs` includes target, bug title, crash report, and kernel repo/commit/config fields. The init function registers `ai.WorkflowModeration` producing `ai.ModerationOutputs`. The LLM structured output is `Actionable`.

## Control Flow

The pipeline checks out/builds the kernel, prepares a code search index, runs an `LLMAgent` named `expert` with the embedded moderation instruction and crash report prompt, uses `common.CodeAccessTools`, and word-wraps the raw explanation.

## State and Persistence Behavior

State follows normal aflow dataflow. Kernel source/build outputs are cached. The final `Actionable` and formatted `Explanation` are persisted as moderation outputs.

## Dependencies and Integration Points

It depends on kernel actions, codesearcher, common prompt substitution, embedded prompts, and aflow LLM structured outputs.

## Risks and Edge Cases

The prompt only includes `CrashReport` despite `BugTitle` being an input, so title-specific context is not directly shown unless report includes it. Build/index failures prevent moderation output even for reports that could perhaps be assessed text-only.

## Test Signals

No direct semantic tests exist. Package import through `flow/flows.go` triggers registration verification.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/assessment/moderation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/assessment/prompts.go -->
# sources/test-tools/syzkaller/pkg/aflow/flow/assessment/prompts.go

## Purpose

`prompts.go` embeds the markdown prompt files used by assessment workflows.

## Important APIs, Types, and Functions

The single package variable is `prompts embed.FS`, populated by `//go:embed prompts/*.md`.

## Control Flow

There is no runtime control flow in this file beyond Go embed initialization. Other files pass this `embed.FS` to `common.Prompt`.

## State and Persistence Behavior

Prompt text is compiled into the binary. Changes to prompt files require rebuild and can alter workflow behavior without Go code changes.

## Dependencies and Integration Points

It depends on the standard `embed` package and is consumed by KCSAN, moderation, and security assessment registrations.

## Risks and Edge Cases

Missing prompt files break the build at compile time or panic at prompt load depending on path usage. Empty prompt contents are caught by `common.Prompt`.

## Test Signals

Prompt loading behavior is tested in `flow/common/prompts_test.go`, not specifically for assessment prompt files.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/assessment/prompts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/assessment/security.go -->
# sources/test-tools/syzkaller/pkg/aflow/flow/assessment/security.go

## Purpose

`security.go` registers the security assessment workflow, which evaluates exploitability and reachable attack surfaces for syzkaller kernel bugs.

## Important APIs, Types, and Functions

`assessmentSecurityInputs` includes crash report, syz/C repros, and kernel environment fields. `securityOutputs` defines structured booleans for exploitability, denial-of-service, unprivileged/user namespace access, VM guest/host triggers, network/remote/peripheral/filesystem triggers. The init function registers `ai.WorkflowAssessmentSecurity` producing `ai.AssessmentSecurityOutputs`.

## Control Flow

The pipeline first creates a simplified C repro, checks out/builds the kernel, prepares the code index, runs an expensive-model `LLMAgent` named `expert` with security instruction/prompt and code access tools, and wraps its raw explanation. The prompt includes crash report and conditionally includes the simplified C repro.

## State and Persistence Behavior

Kernel source/builds are cached. LLM structured booleans and formatted explanation become persisted dashboard output fields. The simplified C repro is transient workflow state.

## Dependencies and Integration Points

It integrates `actionsyzlang.CreateSimplifiedCRepro`, kernel build/index actions, common prompt loading, and code access tools. The output schema matches `ai.AssessmentSecurityOutputs`, which is used by dashboard predicates.

## Risks and Edge Cases

Security labels are high-impact and LLM-derived, so prompt/tool reliability matters. The prompt text has a typo (`followint`) but behavior is unaffected. If `ReproSyz` is absent, the simplified C repro may be just the provided C repro or empty. Build failures block the assessment.

## Test Signals

Registration tests verify dataflow and schema matching. There are no ground-truth exploitability classification tests in this set.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/assessment/security.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/common/common.go -->
# sources/test-tools/syzkaller/pkg/aflow/flow/common/common.go

## Purpose

`common.go` provides reusable workflow helpers, chiefly the standard set of code access tools and shared prompt instruction discouraging source-code assumptions.

## Important APIs, Types, and Functions

`CodeAccessTools` is the default tool slice with git support. `CodeAccessToolsWithGit(enableGit bool)` creates a `codeexpert` LLM tool and combines its inner tools with the expert tool itself through `aflow.Tools`. `InstructionDontMakeAssumptionsAboutSourceCode` is a prompt fragment used by multiple workflows.

## Control Flow

Tool construction calls `codeexpert.New(enableGit)`, then returns a flattened tool list. Prompt constants are concatenated or substituted by other files.

## State and Persistence Behavior

Tool instances are package-level values and persist for the process. They do not themselves store workflow state here; tool execution state is handled by the tool implementations and aflow context.

## Dependencies and Integration Points

It depends on aflow tool composition and `tool/codeexpert`. Assessment, repro, patching, and reproc flows use these helpers.

## Risks and Edge Cases

Package-level `CodeAccessTools` creates tool instances at init time; duplicate registration behavior must be compatible with tests and MCP registration. The shared instruction names concrete tools such as `{{.toolGrepper}}`, so templates must provide matching tool template variables.

## Test Signals

Common prompt substitution is tested in `prompts_test.go`; tool composition is indirectly checked by flow registration tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/common/common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/common/prompts.go -->
# sources/test-tools/syzkaller/pkg/aflow/flow/common/prompts.go

## Purpose

`prompts.go` loads embedded prompt files and applies shared prompt substitutions.

## Important APIs, Types, and Functions

`Prompt(fs embed.FS, name string) string` reads a file, replaces `{{.CommonInstructionDontMakeAssumptions}}` with the trimmed shared instruction, trims whitespace, and panics on read failure or empty prompt.

## Control Flow

The function reads from the supplied embedded filesystem, performs a global string replacement, trims the final prompt, validates non-empty content, and returns it. It intentionally panics because prompts are static build-time resources and broken prompt paths should fail early.

## State and Persistence Behavior

No runtime state is persisted. Prompt content is embedded in binaries by caller packages.

## Dependencies and Integration Points

It uses `embed.FS`, `fmt`, `strings`, and the shared instruction constant. All concrete workflows with markdown prompt files use it to produce `LLMAgent.Instruction`.

## Risks and Edge Cases

Panics during package initialization or registration can take down the process when prompt files are missing or empty. Replacement is literal and global, so prompt authors must use the exact placeholder spelling.

## Test Signals

Tests validate successful substitution and panic on empty prompt files.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/common/prompts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/common/prompts_test.go -->
# sources/test-tools/syzkaller/pkg/aflow/flow/common/prompts_test.go

## Purpose

`prompts_test.go` verifies common prompt loading, shared instruction substitution, trimming, and empty prompt rejection.

## Important APIs, Types, and Functions

The file embeds `test_prompts/*.md` into `testPrompts`. `TestPrompt` calls `Prompt` and compares exact output. `TestPromptEmpty` asserts `Prompt` panics for an empty prompt.

## Control Flow

`TestPrompt` loads a fixture containing the common placeholder and expects it to be replaced with the multi-line source-code assumption instruction. `TestPromptEmpty` wraps the call in `require.Panics`.

## State and Persistence Behavior

Prompt fixtures are compile-time embedded. No filesystem writes or persistent state are used.

## Dependencies and Integration Points

It uses Go embed and `testify/require`. The test is a local signal for the prompt infrastructure used by assessment and patching workflows.

## Risks and Edge Cases

Exact string comparison will catch whitespace changes in the shared instruction or trimming logic. It does not test missing file paths.

## Test Signals

These tests strongly guard the behavior relied on by workflow registration when loading prompt markdown.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/common/prompts_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/flows.go -->
# sources/test-tools/syzkaller/pkg/aflow/flow/flows.go

## Purpose

`flows.go` is the aggregate import package that registers all built-in aflow workflows through blank imports.

## Important APIs, Types, and Functions

The file has no exported APIs. It blank-imports `flow/assessment`, `flow/patching`, `flow/repro`, and `flow/reproc`.

## Control Flow

Importing package `flow` triggers the `init` functions in all concrete workflow packages, which call `aflow.Register` and populate `aflow.Flows`.

## State and Persistence Behavior

The side effect is process-global workflow registration. No other state is stored in this file.

## Dependencies and Integration Points

Dashboard/job runners can import this package when they want all standard workflows registered. Tests import it to verify registration and MCP tool naming.

## Risks and Edge Cases

Blank imports hide registration side effects. Adding/removing imports changes which workflows are available at runtime. Registration panics in any imported package prevent package initialization.

## Test Signals

`flows_test.go` imports this package and thereby verifies all registrations complete.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/flows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/flows_test.go -->
# sources/test-tools/syzkaller/pkg/aflow/flow/flows_test.go

## Purpose

`flows_test.go` verifies package-level workflow registration and MCP tool naming after all workflow packages are imported.

## Important APIs, Types, and Functions

`TestMCPTools` iterates `aflow.MCPTools`, logs each tool name, and fails if an MCP tool name contains `-`.

## Control Flow

The test's package import triggers all blank-imported flow registrations. It then checks the already-populated global MCP tool registry.

## State and Persistence Behavior

It reads global `aflow.MCPTools` state populated during init. It does not mutate persistent storage.

## Dependencies and Integration Points

It depends on the aggregate `flow` package side effects and aflow MCP registration behavior.

## Risks and Edge Cases

The test enforces an MCP naming restriction that differs from Gemini tool names, where hyphens are permitted. It does not verify that every expected workflow exists, only that registration did not panic and MCP tool names satisfy the dash rule.

## Test Signals

The most important signal is implicit: if any workflow has broken dataflow verification, package init panics and the test binary fails before or during this test.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/flows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/patching/actions.go -->
# sources/test-tools/syzkaller/pkg/aflow/flow/patching/actions.go

## Purpose

`actions.go` contains helper actions for patching workflows: base commit selection, maintainer discovery, recent commit summaries, applying previous patches, and forwarding patch diffs.

## Important APIs, Types, and Functions

Actions are `baseCommitPicker`, `getMaintainers`, `getRecentCommits`, `applyGitPatch`, and `forwardPatchDiff`. `pickBaseCommit` resolves `HEAD`, `RC`, or exact commits. `maintainers` runs Linux `scripts/get_maintainer.pl`. `recentCommits` parses modified files from a diff and runs `git log`. `applyGitPatchFunc` applies the latest patch history diff to a scratch tree.

## Control Flow

Base commit selection uses `kernel.UseLinuxRepo` to checkout branch, fetch tags for `RC`, resolve a release tag or exact commit, and output normalized repo/branch/commit. Maintainer lookup switches the shared repo to the target commit, pipes the patch diff to `get_maintainer.pl`, and converts parsed recipients into `ai.Recipient`s. Recent commits extracts file names from the patch diff and runs a non-merge log from the target commit over those files. Patch application validates non-empty history and runs `git apply` on the latest diff when present.

## State and Persistence Behavior

These actions mutate the shared Linux repo checkout via `UseLinuxRepo` or mutate a scratch source tree for patch application. Outputs are transient workflow state. No aflow cache is created directly here, but `UseLinuxRepo` uses the workflow workdir.

## Dependencies and Integration Points

They depend on kernel checkout helpers, syzkaller `vcs`, `osutil`, `ai` schemas, and external git/get_maintainer scripts. Patching and patch-iteration workflows use them around LLM patch generation.

## Risks and Edge Cases

The shared repo mutex is process-local. `RC` resolution depends on tag fetches and release-tag logic. `recentCommits` returns a flow error for empty diffs. `get_maintainer.pl` requires a non-shallow checkout. Applying previous patches assumes the scratch tree matches the base of the latest patch.

## Test Signals

`actions_test.go` covers `recentCommits` against the syzkaller repo when not running in shallow CI. Other actions need integration tests with a Linux repo.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/patching/actions.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/patching/actions_test.go -->
# sources/test-tools/syzkaller/pkg/aflow/flow/patching/actions_test.go

## Purpose

`actions_test.go` validates recent commit extraction for modified files in a patch diff.

## Important APIs, Types, and Functions

`TestRecentCommits` uses `aflow.TestAction` to run `getRecentCommits` with `recentCommitsArgs` and compare `recentCommitsResult`.

## Control Flow

The test skips on CI because shallow checkouts may not contain the reference commit. Locally, it creates a temp workdir, symlinks the repository into `repo/linux` to satisfy `kernel.UseLinuxRepo`, supplies a diff touching two files, and expects a fixed list of recent non-merge subjects.

## State and Persistence Behavior

It creates temp dirs and a symlink but no persistent repository changes. It reads the current local git history.

## Dependencies and Integration Points

It depends on `osutil`, aflow test harness, and the local repository containing the expected history.

## Risks and Edge Cases

The test is intentionally environment-sensitive and skipped in CI. Expected commit subjects can become stale if repository history is rewritten, though syzkaller history should be stable.

## Test Signals

It provides a targeted signal that `vcs.ParseGitDiff` file extraction and `git log` invocation work in the expected workdir layout.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/patching/actions_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/patching/iteration.go -->
# sources/test-tools/syzkaller/pkg/aflow/flow/patching/iteration.go

## Purpose

`iteration.go` registers the patch-iteration workflow that processes reviewer feedback, updates tags, decides whether to produce a new patch version, regenerates code/description/fixes metadata when needed, and drafts direct replies.

## Important APIs, Types, and Functions

`PatchIterationInputs` describes environment, bug context, patch history, base tags, base commit selection, and strace fields. Structured outputs include `verdictAgentOutputs` and `changelogGeneratorOutputs`, with validators `validateVerdictOutputs` and `validateChangelogOutputs`. Helper tools/actions include `viewPatchHistoryTool`, `extractTriageResults`, `extractNewComments`, `extractLatestPatchInfo`, `resolveFixes`, and `appendCommentReply`.

## Control Flow

The registered workflow prepares the base kernel, reproduces the bug, indexes code, extracts new/latest patch-history state, asks a verdict agent to categorize feedback into code/description/fixes/resend needs, extracts and merges review tags, computes whether a new version is needed, and conditionally enters a patch update branch. In that branch it creates a scratch tree, applies the previous patch, runs code generation only when `CodeItems` exist or forwards the old diff otherwise, optionally refreshes the Fixes tag, resolves final Fixes metadata, gathers recent commits, generates changelog/description, and gets maintainers. Finally it iterates over `NewComments` to decide and append direct comment replies.

## State and Persistence Behavior

State is accumulated in the aflow execution map, including persistent semantic fields such as `NeedNewVersion`, `PatchDiff`, tags, `NewChangeLog`, and `Replies`. Scratch source mutations happen only inside the conditional branch and are reset by `crash.TestPatch`. No new cache is used directly here beyond actions in the pipeline.

## Dependencies and Integration Points

It integrates patching helpers, kernel actions, crash reproduction, code search, `aflow.If`, `aflow.ForEach`, LLM structured outputs, common code tools, and email word wrapping. It produces `ai.PatchIterationOutputs`.

## Risks and Edge Cases

Patch history must be non-empty; helper actions return flow errors otherwise. Prompt-injection risk from external comments is mitigated by JSON-encoding comments and explicit instructions, but LLM compliance remains critical. `NeedNewVersion` is true even for resend-only requests. If only description changes are requested, the old patch is applied and forwarded without code generation. Reply generation trusts LLM-provided `Action` strings and only appends when exactly `reply` with non-empty text.

## Test Signals

No dedicated tests cover the whole workflow. Registration tests validate dataflow. Validators are small and deterministic but currently not separately tested in the assigned files.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/patching/iteration.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/patching/patching.go -->
# sources/test-tools/syzkaller/pkg/aflow/flow/patching/patching.go

## Purpose

`patching.go` registers the main patch generation workflow. It reproduces a bug, investigates root cause, edits a scratch kernel tree with LLM assistance, tests the patch in a loop, finds Fixes metadata, selects recipients, and generates a commit description.

## Important APIs, Types, and Functions

`Inputs` describes bug, kernel, VM, syzkaller, base branch/commit, and strace settings. `patchGenerationLoop` constructs a `DoWhile` loop around a patch-generating `LLMAgent` and `crash.TestPatch`. Prompt constants define debugger, patch, description, and shared fault-injection/description instructions. Fixes helpers include `fixesFinderState`, `fixesFinderArgs`, `validateFixesHashes`, `formatFixes`, and `queryFixesTag`.

## Control Flow

The workflow picks a base commit, creates a simplified C repro, checks out/builds the kernel, verifies the crash reproduces, prepares code search, asks a debugger agent for root-cause explanation, creates a scratch checkout, runs the patch generation/test loop until `TestError` clears or max iterations is reached, asks a fixes-finder agent for the introducing commit, formats the Fixes tag, gets maintainers and recent commit subjects, and asks a description generator for a wrapped commit message.

## State and Persistence Behavior

Kernel checkouts/builds and repro results are cached by underlying actions. The scratch checkout is mutable and temporary. `patchGenerationLoop` repeatedly updates `PatchExplanation`, `PatchDiff`, and `TestError` in state. Final outputs match `ai.PatchingOutputs`, including tags initialized from const empty slices.

## Dependencies and Integration Points

It integrates actions from `actionsyzlang`, `crash`, `kernel`, tools `codeeditor`, `codesearcher`, `patchdiff`, common code access tools, email wrapping, and `vcs` commit lookup. It is one of the dashboard-facing automated patch workflows.

## Risks and Edge Cases

The workflow trusts LLMs for code edits, root-cause diagnosis, Fixes selection, and description text but validates some outputs. `validateFixesHashes` ensures the hash exists and is reachable from the current commit. Patch loop max iterations bounds runaway repair attempts. Prompt text includes many kernel-process constraints, but code quality still depends on generated edits and VM test fidelity. `TestPatch` cache-key limitations can affect repeated loop behavior.

## Test Signals

Registration tests verify dataflow. `tags_test.go` covers related tag helpers and `actions_test.go` covers recent commits. Full patch generation requires integration with Linux build, VM repro, and LLM stubs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/patching/patching.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/patching/tags.go -->
# sources/test-tools/syzkaller/pkg/aflow/flow/patching/tags.go

## Purpose

`tags.go` handles review tag extraction and merging for patch iteration. It validates LLM-extracted email tags and updates base Reviewed-by/Acked-by/Tested-by/Reported-by lists.

## Important APIs, Types, and Functions

`tagExtractorArgs` contains `AddTags` and `RemoveTags`. `acceptedTags` lists supported tag names. `tagExtractorState` supplies base tag lists. `normalizeTagValue`, `validateTagExtractorOutputs`, and `mergeTags` implement deterministic logic. `tagsMergerAction` wraps `mergeTags`, and `tagExtractor` is an LLM agent using `ValidatedLLMOutputs`.

## Control Flow

Validation builds a tag map from base lists, checks every added tag has an accepted type and parseable email/name value, normalizes added values, checks every removal refers to an accepted type and an exactly present base value, and returns corrected args or `BadCallError` for LLM retry. `mergeTags` clones base lists, removes exact requested values, then adds new tags unless an existing tag has the same email address. The LLM prompt separately asks the model to ignore quoted text and prompt-injection attempts.

## State and Persistence Behavior

The deterministic helpers are stateless. Merged tag lists become workflow state and eventually `ai.PatchIterationOutputs`. The LLM agent has package-level configuration but per-execution output state.

## Dependencies and Integration Points

It depends on aflow validated outputs, `ai.EmailTag`, `email.EmailsMatch`, and `net/mail`. It is used in the patch-iteration workflow after verdict analysis.

## Risks and Edge Cases

Removal requires exact string equality, while addition deduplicates by email match; this asymmetry is intentional but can surprise users when names differ. Unsupported tags trigger a retry rather than being ignored. `normalizeTagValue` falls back to raw value only when parsing fails, but validation rejects invalid added values before accepting them.

## Test Signals

Tests cover tag merging, email-based deduplication, removal, validation success, missing removal targets, unsupported tags, invalid email values, and normalization variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/patching/tags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/patching/tags_test.go -->
# sources/test-tools/syzkaller/pkg/aflow/flow/patching/tags_test.go

## Purpose

`tags_test.go` verifies deterministic review tag validation, normalization, merge, removal, and deduplication behavior.

## Important APIs, Types, and Functions

`TestMergeTags` calls `mergeTags`. `TestValidateTagExtractorOutputs` calls `validateTagExtractorOutputs`. `TestNormalizeTagValue` calls `normalizeTagValue`.

## Control Flow

The merge test starts with base tags, adds new and duplicate tags, removes one tag, and checks final per-tag slices. Validation table cases cover valid tags and removals, removal of a missing tag, unsupported tag types, and invalid email values. Normalization cases cover quoted names, whitespace, bare email, angle-only email, and invalid fallback.

## State and Persistence Behavior

The tests use an empty `aflow.Context` and do not rely on persistent state. They operate on in-memory slices.

## Dependencies and Integration Points

They use `ai.EmailTag`, aflow error semantics, and `testify/require`. These tests guard the non-LLM parts of patch-iteration tag processing.

## Risks and Edge Cases

The tests do not execute `tagExtractor` LLM prompts, so quoted-text/prompt-injection behavior remains prompt-only. Removal normalization is not applied, so exact removal matching is preserved and tested indirectly.

## Test Signals

The suite provides strong coverage for accepted tag policy and duplicate prevention by email address.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/patching/tags_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/repro/repro.go -->
# sources/test-tools/syzkaller/pkg/aflow/flow/repro/repro.go

## Purpose

`repro.go` registers the syzkaller-program reproduction workflow. It asks an LLM to generate a syzlang reproducer for a kernel crash, formats it, executes it in VMs, and reports whether it reproduced the original title.

## Important APIs, Types, and Functions

`ReproInputs` carries agent, target, bug, kernel, image/VM, syzkaller, and strace fields. The init function registers `ai.WorkflowRepro` producing `ai.ReproOutputs`. Consts include syzkaller commit, syzlang docs, syscall description file list, empty `ReproC`, and `NeedStrace=false`. The inline `compare` action outputs `Reproduced`.

## Control Flow

The pipeline checks out/builds the kernel, prepares code search, runs an expensive-model `crash-repro-finder` LLM with code tools plus syzlang description/reproduce/coverage tools, requests `ReproOpts` and `CandidateReproSyz`, formats the candidate strictly via `actionsyzlang.Format`, reproduces the crash via `crash.Reproduce`, and compares the original `BugTitle` to `ReproducedBugTitle`.

## State and Persistence Behavior

Kernel artifacts and reproduction executions are cached by underlying actions. The generated syz program, options, syzkaller commit, crash reports, and reproduced flag become persisted output fields.

## Dependencies and Integration Points

It integrates syzkaller docs, program revision metadata, kernel actions, code search, syzlang tools, crash reproduction, and aflow LLM structured outputs. It is a dashboard workflow for generating syz repros.

## Risks and Edge Cases

Title equality is a strict reproduced check even when crashes may be equivalent under a different title. The LLM may produce invalid syzlang, caught by strict formatting. `ReproC` is set to empty only to satisfy `crash.Reproduce` inputs. The workflow builds/indexes the kernel before generation, increasing cost but enabling code-aware tools.

## Test Signals

Registration tests validate dataflow. Full behavior depends on LLM stubs or integration runs with VM images and syzkaller tools.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/repro/repro.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/reproc/reproc.go -->
# sources/test-tools/syzkaller/pkg/aflow/flow/reproc/reproc.go

## Purpose

`reproc.go` registers and supports the C reproducer generation workflow. It iteratively researches a bug, generates/probes/compiles/runs standalone C reproducers, asks an oracle agent to classify failures or equivalence, and saves a successful `repro.c`.

## Important APIs, Types, and Functions

Inputs are `ReproCInputs`; outputs are `ai.ReproCOutputs`. Helper actions include `FormatC`, `CompileCProg`, `MergeReproC`, `TruncateLog`, `LoopController`, `ExpandToolkit`, `MergeStrategy`, and `SaveReproC`. Important validators are `validateGeneratorOutputs` and `validateOracleOutputs`. `OracleResult`, `GeneratorResult`, `LoopControllerArgs`, and `LoopControllerResult` carry loop state. Prompt constants define researcher/refiner/generator/oracle behavior.

## Control Flow

The workflow checks out/builds/indexes the kernel, asks an initial researcher for strategy, then enters a `DoWhile` loop controlled by `ContinueSignal`. Each iteration optionally refines strategy from oracle feedback, merges strategy, asks a generator for C code, marks the first candidate as a capability probe until verified, repairs compile errors for up to three inner iterations, runs the C repro with optional strace, truncates logs, asks an oracle to validate probe/repro results, and updates loop state. On success, `LoopController` clears `ContinueSignal`, records the C repro and crash report, and `SaveReproC` writes `repro.c` under the workflow workdir.

## State and Persistence Behavior

Loop state persists in the aflow state map across iterations, especially `CapabilitiesVerified`, `OracleFeedback`, `RawCandidateReproC`, `FormattedReproC`, and `ContinueSignal`. `SaveReproC` writes a real file to `ctx.Workdir/repro.c` only when reproduction succeeds. Kernel/build and VM temp behavior is delegated to underlying actions.

## Dependencies and Integration Points

It depends on kernel actions, crash `RunCRepro`, codesearcher, common tools without git, toolkit expansion, `csource` formatting/building, syzkaller `prog` targets, and aflow control-flow actions. It produces the dashboard-facing `repro-c` workflow.

## Risks and Edge Cases

`FormatCFunc` suppresses formatting errors and returns original code, while `CompileCProg` performs actual compile validation. `extractCCode` returns only the first fenced block. Capability probing is enforced through validation state, but LLM compliance and oracle classification remain important. Terminal environment failures are wrapped as `FlowError`. `SaveReproC` prints to stdout, which can be noisy in service contexts.

## Test Signals

Unit tests cover formatting, log truncation, loop controller success/collision/probe/terminal cases, C code extraction, and oracle validation rules. Full VM reproduction requires integration tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/reproc/reproc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/reproc/reproc_test.go -->
# sources/test-tools/syzkaller/pkg/aflow/flow/reproc/reproc_test.go

## Purpose

`reproc_test.go` covers deterministic helper behavior for the C reproducer workflow.

## Important APIs, Types, and Functions

Tests call `FormatCFunc`, `TruncateLogFunc`, `LoopControllerFunc`, `extractCCode`, and `validateOracleOutputs` using `aflow.NewTestContext`.

## Control Flow

The tests validate C formatting returns non-empty output, log truncation preserves short logs and crash report, loop controller handles success, collision, successful/failed probes, preservation of capability state, and terminal errors, code extraction handles C fenced blocks/plain fenced blocks/no fences/multiple blocks, and oracle validation enforces probe/repro feedback requirements.

## State and Persistence Behavior

All tests are in-memory except `FormatCFunc`, which may use csource formatting internals. No VM, cache, or file save behavior is exercised.

## Dependencies and Integration Points

They use aflow test context and `testify/assert`. The tests protect workflow loop logic independently of LLM and VM execution.

## Risks and Edge Cases

The tests do not compile generated C, run strace, validate generator output state, or test `SaveReproC`. Multiple fenced code extraction intentionally picks the first block.

## Test Signals

The strongest signals are validation rules that force oracle feedback on failed probes/collisions/non-reproduction and prevent inconsistent terminal/probe states.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow/reproc/reproc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow_test.go -->
# sources/test-tools/syzkaller/pkg/aflow/flow_test.go

## Purpose

`flow_test.go` is the main integration-style unit test suite for the aflow runtime. It verifies typed dataflow, function actions, LLM agents, tools, candidates, structured outputs, missing input errors, quota reset time, tool misbehavior handling, flow consts, and registration errors.

## Important APIs, Types, and Functions

`TestWorkflow`, `TestNoInputs`, `TestQuotaResetTime`, `TestToolMisbehavior`, `TestFlowConsts`, and `TestFlowRegistrationErrors` are the main tests. They use `testFlow`, `NewFuncAction`, `LLMAgent`, `LLMOutputs`, `NewFuncTool`, `Pipeline`, and GenAI stub responses.

## Control Flow

`TestWorkflow` builds a multi-step pipeline with function action, LLM with parallel tool calls and `set-results`, another action, multi-candidate LLM, and aggregator. It verifies state propagation, numeric conversion from JSON float64, thoughts/replies, arrays from candidates, and template ranges. `TestToolMisbehavior` feeds wrong tool args, missing args, extra args, nonexistent tools, bad set-results, missing final replies, and eventual success. Registration tests assert precise verifier errors for const conflicts and unused consts.

## State and Persistence Behavior

Tests run with temporary workdirs and stubbed model responses. Golden trajectory files are handled by the broader test harness, while this file focuses on expected outputs/errors.

## Dependencies and Integration Points

It integrates nearly all aflow runtime pieces: schema conversion, verification, execution, trajectory spans, LLM parsing, tool execution, and cache-backed model stubs.

## Risks and Edge Cases

The tests are tightly coupled to exact error strings and model response sequencing. They do not call real model APIs. Complex LLM runtime behaviors such as token compression are tested in `llm_agent_test.go`.

## Test Signals

This is a high-value regression suite for core dataflow semantics and LLM/tool protocol handling.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/flow_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/func_action.go -->
# sources/test-tools/syzkaller/pkg/aflow/func_action.go

## Purpose

`func_action.go` adapts ordinary typed Go functions into aflow actions that consume and produce named workflow state fields.

## Important APIs, Types, and Functions

`NewFuncAction[Args, Results]` creates a `funcAction`, registers it for MCP, and returns it as `Action`. `funcAction.execute` converts `ctx.state` into `Args`, records an action span, calls the function, converts results to a map, merges outputs into state, and finishes the span. `verify` checks name, required inputs, and provided outputs. `testVerify` supports the test harness.

## Control Flow

At execution time, arguments are populated from current state using schema conversion. The action span starts before invoking user code. Results are inserted into both the span and context state before `finishSpan`, even when the function returns an error.

## State and Persistence Behavior

The only persistent side effect here is global MCP action registration. Runtime state mutation is limited to inserting result fields into `ctx.state`; any filesystem/cache effects come from the wrapped function.

## Dependencies and Integration Points

It depends on schema conversion helpers, verification helpers, trajectory spans, and MCP registration. All non-LLM workflow steps in the assigned flows use this adapter.

## Risks and Edge Cases

Results are inserted even if `fnErr` is non-nil, which can be useful for partial diagnostics but may surprise downstream logic if errors are handled differently. Conversion requires field names/types to match state. Empty action names are registration errors.

## Test Signals

The broad flow tests exercise function actions in pipelines, const consumption, and verifier behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/func_action.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/func_tool.go -->
# sources/test-tools/syzkaller/pkg/aflow/func_tool.go

## Purpose

`func_tool.go` adapts typed Go functions into tools callable by `LLMAgent`. It generates JSON schemas for tool parameters/results, separates hidden workflow state from LLM-provided args, and distinguishes recoverable bad tool calls from hard workflow failures.

## Important APIs, Types, and Functions

`NewFuncTool[State, Args, Results]` creates a `funcTool` and registers it for MCP. `BadCallError` wraps errors that should be returned to the LLM. `funcTool.declaration` returns a GenAI `FunctionDeclaration`; `execute` converts state and args, calls the Go function, and converts results. `verify`, `testVerify`, and `checkFuzzTypes` support registration and tests.

## Control Flow

When an LLM calls a tool, aflow converts hidden `State` from current workflow state in non-strict tool mode, converts LLM args also in non-strict mode to tolerate extra fields, invokes `Func`, and returns map results plus any error. `LLMAgent.callTools` decides whether `BadCallError` is fed back to the model or a hard error aborts the workflow.

## State and Persistence Behavior

The adapter itself has no persistent runtime state beyond MCP registration. Tool functions may read/cache/mutate through `*Context`.

## Dependencies and Integration Points

It depends on GenAI function declarations, JSON schema helpers, aflow schema conversion, verification, and MCP registration. Code search, syzlang, git, patchdiff, and other workflow tools use this abstraction.

## Risks and Edge Cases

Tool args are intentionally parsed non-strictly, so hallucinated extra fields are ignored rather than rejected. Missing or mistyped required fields still become errors. `BadCallError` should be used carefully so genuine infrastructure failures are not hidden as LLM-correctable mistakes.

## Test Signals

`func_tool_test.go`, `flow_test.go`, and `llm_agent_test.go` cover bad calls, hard errors, duplicate call detection, nil args, schema verification, and tool state isolation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/func_tool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/func_tool_test.go -->
# sources/test-tools/syzkaller/pkg/aflow/func_tool_test.go

## Purpose

`func_tool_test.go` verifies tool error semantics and per-run duplicate-call history behavior.

## Important APIs, Types, and Functions

Tests include `TestToolErrors`, `TestToolLoopDetection`, `TestToolHistorySequentialLeak`, and helper `newTestContext`.

## Control Flow

`TestToolErrors` has a tool return first `BadCallError` and then a hard error, verifying the former is sent to the LLM and the latter aborts with diagnostic args. `TestToolLoopDetection` directly checks duplicate-call thresholds in `agentSession.recordAndCheckDuplicate`. `TestToolHistorySequentialLeak` runs the same agent in two fresh contexts and asserts duplicate-call history does not leak between executions.

## State and Persistence Behavior

Tests use stub contexts with temp caches and stubbed model responses. Duplicate tool history is expected to be session-local, not stored on `LLMAgent`.

## Dependencies and Integration Points

They depend on `LLMAgent`, `NewFuncTool`, GenAI function call parts, and aflow test execution helpers.

## Risks and Edge Cases

The duplicate-call tests rely on exact default limits. `newTestContext` creates a zero-size cache and no-op event callback, so it is suitable for LLM stubs but not for cache behavior tests.

## Test Signals

These tests specifically guard a subtle state leak risk where tool histories from one run could block valid tool calls in later runs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/func_tool_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/if.go -->
# sources/test-tools/syzkaller/pkg/aflow/if.go

## Purpose

`if.go` implements aflow's conditional action node. It chooses between `Do` and optional `Else` based on a workflow state value and reconciles branch outputs so downstream actions see stable fields.

## Important APIs, Types, and Functions

`If` has `Condition`, `Do`, `Else`, and internal `ifVars`. Methods are `execute`, `verify`, and `verifyOutputs`.

## Control Flow

Execution looks up the condition in `ctx.state`, treats non-zero values as true, and gives slices/maps/arrays/channels special truthiness based on length. It records an `If` span with condition arg, executes `Do` or `Else`, and on success fills any branch-only outputs absent from the executed branch with zero values recorded during verification. Verification checks the condition input, verifies branches, ensures branch-only outputs are represented, and rejects incompatible output types.

## State and Persistence Behavior

The action mutates the in-memory state map by adding outputs from the executed branch and zero-valued placeholders for non-executed branch outputs. It has no filesystem or cache state.

## Dependencies and Integration Points

It depends on reflection, state verification, maps cloning, and trajectory spans. Patch iteration and C-repro workflows use nested `If` nodes for conditional LLM/tool branches.

## Risks and Edge Cases

Truthiness uses `reflect.IsZero`, with container length overriding non-nil empty slices/maps to false. Channels are checked by length, which is usually zero and may be surprising. Verification mutates `ifVars` on the `If` object, so action objects are not immutable after registration.

## Test Signals

`if_test.go` covers truthiness for strings, bools, ints, slices, nil/empty slices, else branches, missing condition, and branch output mismatch errors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/if.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/if_test.go -->
# sources/test-tools/syzkaller/pkg/aflow/if_test.go

## Purpose

`if_test.go` validates conditional execution truthiness, else behavior, zero-value output filling, and registration-time branch errors.

## Important APIs, Types, and Functions

`TestIf` builds simple actions with `NewFuncAction` and wraps them in `If`. `TestIfErrors` uses `testRegistrationError` to assert verifier failures.

## Control Flow

The true/false tests cover strings, booleans, integers, non-empty slices, empty slices, nil slices, and explicit else branches. Error tests check empty condition, missing condition input, output produced only by Else, and output type disagreement between Do and Else.

## State and Persistence Behavior

The tests run in the aflow test harness with no persistent state. Golden trajectory output may be managed by the shared harness outside this file.

## Dependencies and Integration Points

They depend on `testFlow`, `NewFuncAction`, and the verifier. They protect control-flow semantics used by patch and repro workflows.

## Risks and Edge Cases

The tests do not cover maps, arrays, or channels, though code supports them. They assume zero string output for non-executed branches.

## Test Signals

Coverage is strong for common workflow conditions and branch dataflow validation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/if_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/llm_agent.go -->
# sources/test-tools/syzkaller/pkg/aflow/llm_agent.go

## Purpose

`llm_agent.go` implements aflow's LLM action runtime. It formats prompts, configures Gemini/Vertex requests, executes iterative tool-calling chats, handles structured outputs, validates/fixes replies, supports multiple candidates, compresses long histories, detects tool-call loops, caches model responses, and classifies retry/quota/token errors.

## Important APIs, Types, and Functions

Core types are `LLMAgent`, `agentSession`, `TaskType`, `Tool`, `llmReply`, and `llmOutputs`. Public helpers include `Tools`, `LLMReply`, `LLMOutputs`, and `ValidatedLLMOutputs`. Execution paths are `execute`, `executeMany`, `executeOne`, `chat`, `callTools`, `checkFinalReply`, `generateContent`, and `generateContentCached`. History management is `slide`, `maybeCompressContext`, and `compressContext`. Error handling is `parseLLMError`, `parseLLMResp`, `llmBackoffDuration`, and retry/overflow/quota types. Verification is in `LLMAgent.verify` and `verifyTemplate`. Loop detection is `recordAndCheckDuplicate`.

## Control Flow

Execution builds config/instruction/prompt/tools from current state, starts an agent span, and opens an `agentSession` with a user prompt. Each chat iteration may compress history, starts an LLM span, applies sliding-window summary hints, sends a cached model request, parses reply/thoughts/function calls, appends model content to history, and either validates final reply/results or executes requested tools. Tool calls produce tool spans and function responses; `BadCallError`s are returned to the model, while hard errors abort. Structured outputs require a successful `set-results` call before the final reply unless the agent is output-only. Multiple candidates run `executeOne` repeatedly and aggregate replies/outputs into slices.

## State and Persistence Behavior

Workflow-visible state is updated only after successful agent execution. Per-execution `agentSession` holds request history, tool history, summary pointer, outputs, and answer-now flag. LLM responses are persisted in the aflow cache under `llm` with hashes of model, config, request, and candidate. Model thoughts/tokens/replies are persisted in trajectory spans via `onEvent`.

## Dependencies and Integration Points

It depends on GenAI types, aflow schema/template/verification/cache/trajectory helpers, `osutil.JSONDeepCopy`, and HTTP error codes. Every LLM-based workflow uses this runtime. Tools implement the local `Tool` interface and are declared as GenAI function declarations.

## Risks and Edge Cases

The runtime assumes `resp.Candidates[0]` exists after `parseLLMResp`. Tool-call history must be session-local to avoid false loop detection. Caching model responses means prompt/config hash stability matters. Token compression invokes another model and may lose details despite explicit summary requirements. Sliding-window summary is prompt-based and can accidentally become final reply. `parseLLMErrorImpl` depends on provider message substrings that may change. `verify` mutates default `compressTokens` and validated reply names.

## Test Signals

`llm_agent_test.go`, `func_tool_test.go`, and `flow_test.go` cover retry classification, backoff, token compression, history reset, output overflow thinking reduction, structured outputs, validated outputs/replies, tool prompt variables, bad tool calls, duplicate loops, and registration errors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/llm_agent.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/llm_agent_test.go -->
# sources/test-tools/syzkaller/pkg/aflow/llm_agent_test.go

## Purpose

`llm_agent_test.go` verifies LLM runtime error classification, retry backoff, summary window behavior, token compression, structured outputs, output overflow handling, validated outputs/replies, nil tool args, tool template variables, and registration errors.

## Important APIs, Types, and Functions

Tests call `parseLLMError`, `llmBackoffDuration`, `testFlow`, `LLMAgent`, `LLMOutputs`, `ValidatedLLMOutputs`, `LLMReply`, and helper `createToolCallResponse`. They construct `genai.APIError`, `GenerateContentResponse`, `FunctionCall`, and `Part` stubs.

## Control Flow

Error tests map specific HTTP/provider messages to retry, quota, input overflow, output overflow, or raw errors and verify max retry behavior. Compression tests simulate token counts that exceed thresholds and assert history truncates to anchor plus summary and duplicate-call history resets. Structured-output tests verify `set-results` can be non-last, output-only agents can finish after set-results, validators can reject or rewrite results, and output-token overflow progressively lowers thinking level before failing. Registration tests assert invalid template functions, tool names, duplicate tools, mutually exclusive context options, and reply conflicts are caught.

## State and Persistence Behavior

All model calls are stubbed in-memory through the test harness. Token compression changes per-session request history only. No real model or persistent cache behavior is exercised beyond the harness.

## Dependencies and Integration Points

It depends on GenAI response shapes, aflow test helpers, and `testify`. It is the primary safety net for the complex LLM/tool protocol.

## Risks and Edge Cases

Provider error parsing tests encode exact message substrings; provider changes may require updates. Tests verify compression mechanics but not semantic quality of summaries. They do not cover real network behavior.

## Test Signals

The suite is high-value for preventing regressions in retry behavior, context management, structured output contracts, and validator feedback loops.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/llm_agent_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/llm_tool.go -->
# sources/test-tools/syzkaller/pkg/aflow/llm_tool.go

## Purpose

`llm_tool.go` implements an LLM-backed tool: a parent `LLMAgent` can call a tool whose implementation is another `LLMAgent` with its own prompt, tools, and context. This enables sub-research without polluting the parent conversation window.

## Important APIs, Types, and Functions

`LLMTool` exposes fields similar to `LLMAgent`: `Name`, `Model`, `TaskType`, `Description`, `Instruction`, and inner `Tools`. `declaration` returns a GenAI function schema accepting `llmToolArgs.Question` and returning `llmToolResults.Answer`. `execute` runs the inner agent. Constants `llmToolPrompt` and `llmToolReply` are temporary state keys. `verify` constructs and verifies the inner agent.

## Control Flow

When invoked, `execute` converts args, writes the question into `ctx.state[AFLOW_LLMTOOL_PROMPT]`, runs the prepared inner agent, deletes the prompt key, reads and deletes `AFLOW_LLMTOOL_REPLY`, and returns it as `Answer`. Verification prebuilds the inner `LLMAgent` with prompt `{{.AFLOW_LLMTOOL_PROMPT}}`, reply key `AFLOW_LLMTOOL_REPLY`, and the configured instruction/tools.

## State and Persistence Behavior

The tool temporarily mutates workflow state with reserved keys and cleans them up. The inner agent may use normal LLM cache and trajectory spans. `verify` stores the constructed inner agent on the `LLMTool` object for later execution.

## Dependencies and Integration Points

It depends on GenAI function declarations, aflow schema conversion, and the `LLMAgent` runtime. It can be included in any parent agent's `Tools` list.

## Risks and Edge Cases

Reserved state keys could conflict with user-defined workflow fields if not treated as internal. If the inner agent fails to set `AFLOW_LLMTOOL_REPLY`, execution errors. The parent context state is shared, so inner tools can see existing workflow state according to their `State` types.

## Test Signals

No direct tests are in this file set, but general tool and LLM agent tests cover the underlying execution primitives.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/llm_tool.go -->
