# Research Group subset-b-009448

Grouped research for the requested subset. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolMisbehavior.trajectory.json -->
# sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolMisbehavior.trajectory.json

## Purpose
Golden trajectory fixture for an aflow test where an LLM agent misuses tools before eventually completing. It records the expected span stream for a `test` flow, a `smarty` agent, repeated LLM turns, tool invocations, typed tool-call errors, and the final set-results path.

## Important Data and APIs
The file is JSON data consumed by aflow tests rather than executable code. Its schema matches `trajectory.Span`: `Seq`, `Nesting`, `Type`, `Name`, timestamps, tool `Args`, `Results`, `Error`, agent `Instruction`/`Prompt`/`Reply`, and LLM metadata. It contains flow, agent, llm, and tool spans.

## Control Flow
The fixture models start/finish span pairs in sequence. The agent starts, an LLM turn emits tool calls, successful and failing tools execute, more LLM turns follow after runtime feedback, and the workflow finishes with agent and flow result spans.

## State and Persistence Behavior
It is persisted testdata for deterministic comparison. State is represented only as serialized event history; there are no mutable runtime side effects.

## Dependencies and Integration Points
Integrated by aflow workflow tests and trajectory serialization logic. It also exercises HTML/console consumers that expect stable `SpanType` strings.

## Risks and Test Signals
Risk is fixture drift when span serialization, error wording, or tool validation changes. Strong test signal is exact JSON comparison because it catches ordering, nesting, and bad-call error regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolMisbehavior.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestValidatedLLMOutputs.llm.json -->
# sources/test-tools/syzkaller/pkg/aflow/testdata/TestValidatedLLMOutputs.llm.json

## Purpose
Golden LLM request fixture for validation of structured LLM outputs. It captures model calls that include a synthetic `set-results` function declaration and retry context after an invalid result.

## Important Data and APIs
The top-level array stores two request snapshots with `Model`, optional `Config`, and `Request`. The config includes system instruction text, tool schemas, response modality, temperature, and thinking config. The tool schema validates a required integer `Result` field and mirrors aflow's JSON schema generation.

## Control Flow
The first request sends the initial prompt with the result-setting tool available. The second request includes prior conversation and verification feedback so the model can correct output after the validator rejects a result.

## State and Persistence Behavior
Persistent test fixture only. It stores serialized LLM requests, not responses or live state.

## Dependencies and Integration Points
Used by aflow tests for LLM validation/retry behavior and by genai request serialization code. It depends on exact schema names and generated JSON schema layout.

## Risks and Test Signals
Schema churn, instruction text changes, or altered retry prompts will break exact comparisons. The fixture is a high-signal regression check for validator-tool wiring and request history preservation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestValidatedLLMOutputs.llm.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestValidatedLLMOutputs.trajectory.json -->
# sources/test-tools/syzkaller/pkg/aflow/testdata/TestValidatedLLMOutputs.trajectory.json

## Purpose
Golden trajectory for structured-output validation where the first `set-results` call returns an unacceptable value and a later call succeeds.

## Important Data and APIs
The file follows `trajectory.Span` JSON and covers flow, agent, llm, and tool spans. Tool spans carry `Result` arguments/results and the validation error text `result cannot be 42`.

## Control Flow
Execution starts the flow and agent, records an LLM turn, executes `set-results` with invalid output, records another LLM retry, executes `set-results` with corrected output, then closes the agent and flow.

## State and Persistence Behavior
It is immutable testdata representing event chronology. The only state transition encoded is validator failure followed by successful result capture.

## Dependencies and Integration Points
Integrated with aflow validated-output tests, span serialization, and downstream trajectory renderers.

## Risks and Test Signals
The important risks are unstable error text, changed retry sequencing, or missing tool results on error spans. Exact fixture comparison catches those regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestValidatedLLMOutputs.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestValidatedLLMReply.llm.json -->
# sources/test-tools/syzkaller/pkg/aflow/testdata/TestValidatedLLMReply.llm.json

## Purpose
Golden LLM request fixture for validating plain-text LLM replies rather than structured tool outputs.

## Important Data and APIs
The JSON array contains two model requests. The first has instruction and prompt only. The second appends the prior bad reply and a verification-failure message telling the model to correct the reply.

## Control Flow
The modeled flow is initial model call, validator rejects `reply1`, then retry prompt includes the rejection reason before asking for a corrected response.

## State and Persistence Behavior
Static serialized request history; no mutable state or external persistence beyond repository testdata.

## Dependencies and Integration Points
Used by aflow LLM-agent tests that verify retry prompt construction for reply validators. It depends on stable genai request JSON and validator-feedback wording.

## Risks and Test Signals
Risk is accidental loss of the previous reply or changed error prompt shape. The exact fixture is a regression signal for conversational retry context.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestValidatedLLMReply.llm.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestValidatedLLMReply.trajectory.json -->
# sources/test-tools/syzkaller/pkg/aflow/testdata/TestValidatedLLMReply.trajectory.json

## Purpose
Golden trajectory for a plain reply validation scenario where the first LLM reply fails validation and the final agent reply is changed.

## Important Data and APIs
The file serializes `trajectory.Span` records for flow, agent, and two LLM attempts. The closing agent span contains `Reply: changed-reply`; the closing flow span stores `Results.Result` with the same value.

## Control Flow
The agent starts, performs one LLM call, performs a second retry LLM call after validation failure, then returns the corrected reply through flow results.

## State and Persistence Behavior
Immutable fixture state only. It records retry chronology and final accepted reply.

## Dependencies and Integration Points
Used by aflow validation tests and trajectory renderers. It validates that reply-level verification does not require tool spans.

## Risks and Test Signals
Potential regressions include missing retry spans, wrong final reply propagation, or changed nesting. Exact JSON comparison is the primary signal.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestValidatedLLMReply.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestWorkflow.llm.json -->
# sources/test-tools/syzkaller/pkg/aflow/testdata/TestWorkflow.llm.json

## Purpose
Comprehensive golden LLM request fixture for a multi-step aflow workflow with tools, result-setting, candidate agents, and aggregation.

## Important Data and APIs
The array contains eight model request snapshots across `model1`, `model2`, and `model3`. Config sections include generated tool declarations for `tool1`, `tool2`, and `set-results`, thinking config, temperature, and instruction prompts. Request histories include function call and function response parts.

## Control Flow
The fixture models an action feeding an agent prompt, tool calls and tool responses, structured result setting, multiple candidate-agent calls, and an aggregation prompt that sees candidate replies.

## State and Persistence Behavior
It persists request history used by deterministic tests. Conversation state is captured by appending model/tool turns rather than by any runtime store.

## Dependencies and Integration Points
Integrated with aflow workflow tests, schema generation, genai serialization, and agent-candidate orchestration.

## Risks and Test Signals
Any change in prompt text, tool schema ordering, function-response shape, or candidate aggregation order will surface through exact fixture mismatch. It is a broad regression signal for workflow-to-LLM request construction.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestWorkflow.llm.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestWorkflow.trajectory.json -->
# sources/test-tools/syzkaller/pkg/aflow/testdata/TestWorkflow.trajectory.json

## Purpose
Comprehensive golden trajectory for the aflow workflow exercised by `TestWorkflow.llm.json`.

## Important Data and APIs
The fixture contains `Span` records for flow, function actions, a `smarty` agent, nested LLM/tool spans, `agent-candidates`, `swarm` agents, and an `aggregator` agent. It records arguments, results, thoughts, model names, replies, and closing flow results.

## Control Flow
The workflow runs a function action, invokes the main agent, executes tools, records `set-results`, runs candidate agents as a logical group, aggregates their replies, runs another action, and closes the flow.

## State and Persistence Behavior
Static event history. State flow is visible through action outputs, tool results, agent replies, and final flow result fields.

## Dependencies and Integration Points
Used by aflow workflow tests, trajectory serialization, HTML rendering, and any tooling relying on nesting/sequence invariants.

## Risks and Test Signals
The fixture catches regressions in span pairing, nested candidate representation, model attribution, result propagation, and deterministic ordering of arguments/results.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestWorkflow.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/codeeditor/codeeditor.go -->
# sources/test-tools/syzkaller/pkg/aflow/tool/codeeditor/codeeditor.go

## Purpose
Implements the `codeeditor` aflow tool that lets an agent apply one source edit by replacing an exact or fuzzy multi-line snippet in a scratch kernel source tree.

## Important APIs, Types, and Functions
`Tool` is an `aflow.NewFuncTool`. `state` supplies `KernelScratchSrc`; `args` supplies `SourceFile`, `CurrentCode`, and `NewCode`. `codeeditor` validates paths and source-file status, normalizes trailing newlines, splits file/snippet/replacement with `bytes.Lines`, and delegates matching to `replace`. `replace` scans line slices and can match exactly or with whitespace/blank-line tolerant fuzzy comparison.

## Control Flow
The tool rejects path traversal, missing/non-source files, and empty current snippets. It first attempts exact replacement, then fuzzy replacement if no exact match exists. Zero matches and multiple matches are bad calls; one match is written back with `osutil.WriteFile` if the data changed.

## State and Persistence Behavior
It mutates only the selected file under `KernelScratchSrc`. It does not update codesearch indexes, which is explicitly warned in the tool description.

## Dependencies and Integration Points
Depends on `aflow` for tool registration/errors, `codesearch.IsSourceFile` for source filtering, and `osutil` for filesystem helpers. Integrated into patch-generating agent workflows alongside `patchdiff`.

## Risks and Test Signals
Fuzzy matching can delete or replace more lines than expected if context is underspecified, so multiple-match rejection is important. Tests cover traversal, missing/non-source files, empty snippets, no-op edits, exact/fuzzy replacements, deletion, duplicate matches, and fuzzing of arbitrary file/snippet data.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/codeeditor/codeeditor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/codeeditor/codeeditor_test.go -->
# sources/test-tools/syzkaller/pkg/aflow/tool/codeeditor/codeeditor_test.go

## Purpose
Tests the code editing tool's validation, matching, replacement, and fuzz robustness.

## Important APIs, Types, and Functions
Uses `aflow.TestTool`, `require`, `writeTestFile`, and `FuzzTool`. Test cases call exported `Tool` and private `replace` directly.

## Control Flow
Negative tests assert bad-call messages for traversal, missing files, directories/non-source files, empty snippets, no matches, multiple matches, and no-op edits. Replacement tests create temp source files, invoke the tool, then read files back. `TestReplace` isolates exact and fuzzy line matching. `Fuzz` writes arbitrary bytes and feeds arbitrary snippets through the tool.

## State and Persistence Behavior
All file mutations happen in per-test temp directories. No shared state persists across tests.

## Dependencies and Integration Points
Depends on aflow's test harness, osutil writes, and Go fuzzing. It is the primary regression guard for `codeeditor.go` behavior.

## Risks and Test Signals
The tests signal boundary correctness around newline normalization, fuzzy whitespace handling, ambiguity checks, and panic resistance on arbitrary input.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/codeeditor/codeeditor_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/codeexpert/codeexpert.go -->
# sources/test-tools/syzkaller/pkg/aflow/tool/codeexpert/codeexpert.go

## Purpose
Defines an LLM-backed `codeexpert` tool for complex Linux kernel source-code reasoning.

## Important APIs, Types, and Functions
`New(enableGit bool)` returns an `*aflow.LLMTool` configured with name, model, task type, description, instruction, and tools. It selects codesearch and grepper always, and gitlog tools only when `enableGit` is true. Constants hold the public description and instruction fragments.

## Control Flow
Construction concatenates instruction fragments depending on git availability. With git enabled it also adds history-source guidance and restrictions; without git it only exposes source search tools.

## State and Persistence Behavior
No persistent state. It creates tool metadata and instruction strings for runtime use.

## Dependencies and Integration Points
Depends on `aflow`, `codesearcher`, `grepper`, and `gitlog`. It is meant to be invoked by other agents when a kernel question is too complex for direct local tools.

## Risks and Test Signals
Risks are prompt drift, overbroad git usage, or missing tools when git is disabled. There is no direct test in this subset; integration tests should verify tool lists and instruction assembly.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/codeexpert/codeexpert.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/codesearcher/codesearcher.go -->
# sources/test-tools/syzkaller/pkg/aflow/tool/codesearcher/codesearcher.go

## Purpose
Wraps syzkaller's clang-based kernel code search index as aflow tools for file entity lists, comments, source definitions, references, and struct layouts.

## Important APIs, Types, and Functions
Exports `ToolFileIndex`, `ToolDefinitionComment`, `ToolDefinitionSource`, `ToolFindReferences`, `ToolStructLayout`, `Tools`, and `PrepareIndex`. `prepare` builds or reuses a cached clangtool index keyed by kernel commit/config/database hash. The private `index` wrapper prevents full JSON marshaling/unmarshaling of the index object.

## Control Flow
`prepare` calls `ctx.Cache`, runs clangtool if needed, then opens `codesearch.NewIndex` over source/object roots. Tool functions forward arguments into the index and translate result structs. `findReferences` chooses output limits based on snippet context size.

## State and Persistence Behavior
Index state is cached under aflow cache storage and intentionally not serialized into journals. Tool calls are read-only over kernel source/index files.

## Dependencies and Integration Points
Depends on `aflow`, `clangtool`, `pkg/codesearch`, `pkg/hash`, and `tools/clang/codesearch`. Integrated by codeexpert and source-inspection agents.

## Risks and Test Signals
Risks include stale cache keys, huge reference output, and accidental index serialization. Tests in `codesearcher_test.go` cover struct layout success/error; broader integration depends on clangtool index generation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/codesearcher/codesearcher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/codesearcher/codesearcher_test.go -->
# sources/test-tools/syzkaller/pkg/aflow/tool/codesearcher/codesearcher_test.go

## Purpose
Tests the struct-layout aflow wrapper against a small prebuilt codesearch test index.

## Important APIs, Types, and Functions
`TestStructLayout`, `TestStructLayoutNonExistent`, and `createIndex` use `codesearch.NewTestIndex` and `aflow.TestTool`.

## Control Flow
The positive test asks for `struct_in_c_file` and expects fields with bit offsets and sizes. The negative test asks for a missing name and expects the tool error.

## State and Persistence Behavior
Uses testdata through a temporary test index wrapper; no persistent writes.

## Dependencies and Integration Points
Depends on aflow's tool harness and `pkg/codesearch` test index fixtures.

## Risks and Test Signals
Good signal for wrapper shape and error propagation, but it does not cover index preparation, comments, source, or reference search.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/codesearcher/codesearcher_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/codesearcher/filesystem.go -->
# sources/test-tools/syzkaller/pkg/aflow/tool/codesearcher/filesystem.go

## Purpose
Provides lightweight filesystem-style source browsing tools for aflow agents: directory index and bounded file reads.

## Important APIs, Types, and Functions
Exports `ToolDirIndex`, `ToolReadFile`, and `FilesystemTools`. `fsState` carries `KernelSrc`; `getSrcDir` validates it. `dirIndex` returns direct subdirectories and source files. `readFile` returns up to the codesearch layer's capped slice of file contents.

## Control Flow
Both tools resolve the root from state, then call `codesearch.DirIndex` or `codesearch.ReadFile` over that root. Errors from missing state or invalid paths propagate.

## State and Persistence Behavior
Read-only. No cache, no mutation, no durable state.

## Dependencies and Integration Points
Depends on `aflow` and `pkg/codesearch`. These tools are included in the larger `codesearcher.Tools` set and codeexpert.

## Risks and Test Signals
Risk is accidental exposure outside source roots, delegated to codesearch path handling. The 100-line cap is important to bound LLM context. Direct tests are absent in this subset.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/codesearcher/filesystem.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/gitlog/gitlog.go -->
# sources/test-tools/syzkaller/pkg/aflow/tool/gitlog/gitlog.go

## Purpose
Exposes bounded git history, show, and blame operations as aflow tools for Linux kernel research.

## Important APIs, Types, and Functions
Exports `ToolLog`, `ToolShow`, `ToolBlame`, and `Tools`. `gitLog` supports code-regexp, symbol `-L`, message regexps, path history, count limiting, and no-merge behavior. `gitShow` validates commits and optional file presence. `gitBlame` clamps line ranges. `gitBadCallError`, `truncate`, and `runGit` normalize errors/output.

## Control Flow
Each tool runs inside `kernel.UseLinuxRepo`. `gitLog` builds arguments from mutually constrained search modes and caps count at 100. `gitShow` checks commit existence with `cat-file` and optional path presence with `ls-tree` before `git show`. `gitBlame` bounds ranges to `maxOutputLines`.

## State and Persistence Behavior
Read-only over the Linux git repository. It temporarily switches/uses the repo through the kernel action helper but stores no durable state.

## Dependencies and Integration Points
Depends on `aflow`, `kernel.UseLinuxRepo`, `osutil`, and `vcs`. Integrated by codeexpert when git support is enabled.

## Risks and Test Signals
Risks are broad/time-consuming history searches, invalid regexes, missing commits, and excessive diff output. Tests cover show, blame, log search modes, no matches, bad arguments, missing files/commits, and bad regex handling.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/gitlog/gitlog.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/gitlog/gitlog_test.go -->
# sources/test-tools/syzkaller/pkg/aflow/tool/gitlog/gitlog_test.go

## Purpose
Regression tests for git-log, git-show, and git-blame aflow wrappers using synthetic repositories.

## Important APIs, Types, and Functions
Uses `vcs.MakeTestRepo`, `CommitChangeset`, `aflow.TestTool`, regex assertions, and `aflow.TestWorkdir` to point helpers at the temporary repo layout.

## Control Flow
Tests create commits, then exercise message, code, symbol, and path log modes; blame line ranges; show full commits and commit:path objects; and negative validation paths.

## State and Persistence Behavior
Creates temporary git repos under test dirs. No repository state survives tests.

## Dependencies and Integration Points
Depends on syzkaller `vcs` test helpers and aflow test harness. It validates interaction between gitlog tools and `kernel.UseLinuxRepo` workdir conventions.

## Risks and Test Signals
Strong signal for command construction and bad-call conversion. It intentionally does not cover timeouts or very large output truncation beyond core wrappers.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/gitlog/gitlog_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/grepper/grepper.go -->
# sources/test-tools/syzkaller/pkg/aflow/tool/grepper/grepper.go

## Purpose
Provides a bounded `git grep` aflow tool for broad textual searches in kernel sources.

## Important APIs, Types, and Functions
`Tool` registers `grepper`. `state` carries `KernelSrc`; `args` carries an extended regexp and optional path prefix; `results` returns formatted output. The implementation invokes `git grep --extended-regexp --line-number --show-function -C1`.

## Control Flow
The tool builds git args, runs under a one-hour timeout, converts no-match and bad-expression cases into `BadCallError`, then truncates long lines to 200 characters and long outputs to 500 lines with a header.

## State and Persistence Behavior
Read-only over the git checkout. No cache or persisted state.

## Dependencies and Integration Points
Depends on `aflow` and `osutil.RunCmd`. Used by codeexpert and agents when precise codesearch is insufficient.

## Risks and Test Signals
Risks include expensive regexes, binary/very long lines, and huge match sets. Tests cover normal output, long-line truncation, output truncation, no matches, bad regex, path prefix filtering, and expressions beginning with dash.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/grepper/grepper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/grepper/grepper_test.go -->
# sources/test-tools/syzkaller/pkg/aflow/tool/grepper/grepper_test.go

## Purpose
Linux-only tests for the grepper tool against a synthetic git repository.

## Important APIs, Types, and Functions
Uses `vcs.MakeTestRepo`, `aflow.TestTool`, and assertions on output strings.

## Control Flow
The test commits several files, then searches for normal matches, long-line matches, excessive matches, no matches, invalid regexes, path-restricted results, and dash-prefixed expressions.

## State and Persistence Behavior
Temporary repository only; no durable side effects.

## Dependencies and Integration Points
Depends on git behavior and Linux-specific error messages. It validates the user-facing output format expected by LLM agents.

## Risks and Test Signals
Good signal for truncation and error normalization. It may be sensitive to git version wording for invalid regex diagnostics.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/grepper/grepper_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/patchdiff/patchdiff.go -->
# sources/test-tools/syzkaller/pkg/aflow/tool/patchdiff/patchdiff.go

## Purpose
Implements an aflow tool that shows the current scratch-source patch with `git diff` so agents can inspect edits invisible to original-source tools.

## Important APIs, Types, and Functions
`Tool` registers `patch-diff`. `state` supplies `KernelScratchSrc`; `args.File` optionally restricts output; `result.Output` holds diff text. `patchDiff` runs `git diff HEAD --function-context -U10`.

## Control Flow
It validates `KernelScratchSrc`, appends `-- <file>` when requested, runs git in the scratch repo, maps outside-repository and timeout failures to bad-call errors, and returns raw diff output.

## State and Persistence Behavior
Read-only over the scratch git worktree. It reports uncommitted state but does not mutate it.

## Dependencies and Integration Points
Depends on `aflow` and `osutil`. Integrated with `codeeditor` in patch-generation workflows.

## Risks and Test Signals
Risk is large diff output with no explicit truncation. Tests cover expanded-context diff, file restriction, nonexistent file empty output, and path escape failure.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/patchdiff/patchdiff.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/patchdiff/patchdiff_test.go -->
# sources/test-tools/syzkaller/pkg/aflow/tool/patchdiff/patchdiff_test.go

## Purpose
Tests `patch-diff` behavior in a temporary git repository with a modified source file.

## Important APIs, Types, and Functions
Uses `vcs.MakeTestRepo`, `osutil.WriteFile`, `aflow.TestTool`, and regex cleanup for dynamic git index lines.

## Control Flow
The test commits a C file, changes one line, verifies expanded-context diff output, restricts to `foo.c`, checks nonexistent file empty output, and verifies outside-repo bad-call conversion.

## State and Persistence Behavior
All mutations occur in a temp git repo. No persistent state remains.

## Dependencies and Integration Points
Depends on git diff output format and aflow test harness.

## Risks and Test Signals
Good signal for command flags and path safety. It does not test timeout or very large diffs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/patchdiff/patchdiff_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/syzlang/coverage.go -->
# sources/test-tools/syzkaller/pkg/aflow/tool/syzlang/coverage.go

## Purpose
Provides aflow coverage-inspection tools for executed syz reproducer runs.

## Important APIs, Types, and Functions
Exports `CoverageFiles`, `FileCoverage`, and `Coverage`. `CoverageFilesArgs`/`Result` list covered files from cached execution coverage. `FileCoverageArgs`/`Result` format per-function snippets with covered lines prefixed by `*`.

## Control Flow
Both tools load coverage via `crash.LoadCoverage`. `getCoverageFiles` extracts, sorts, and compacts non-empty frame file paths. `getFileCoverage` validates a local relative filename, groups matching frame lines by function, reads the source file, selects ten lines of context around covered ranges, marks hits, sorts snippets, and returns them.

## State and Persistence Behavior
Reads cached coverage objects and source files. No mutation.

## Dependencies and Integration Points
Depends on `aflow`, `crash.LoadCoverage`, source files under `reproduceState.KernelSrc`, and symbolizer frame data from reproducer execution.

## Risks and Test Signals
Risks include stale cached IDs, unsafe filenames, missing source files, and map iteration ordering; sorting snippets mitigates output nondeterminism. Tests cover file listing and snippet formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/syzlang/coverage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/syzlang/coverage_test.go -->
# sources/test-tools/syzkaller/pkg/aflow/tool/syzlang/coverage_test.go

## Purpose
Tests coverage file listing and per-file snippet rendering using cached synthetic coverage.

## Important APIs, Types, and Functions
Uses `aflow.NewTestContext`, `aflow.CacheObject`, `symbolizer.Frame`, temporary source files, and `require` assertions.

## Control Flow
`TestCoverageFiles` stores two call-coverage entries and expects sorted unique file paths. `TestFileCoverage` stores line hits for `foo`, writes a source file, invokes `getFileCoverage`, and compares the exact formatted snippet.

## State and Persistence Behavior
Coverage is persisted only in the test context cache; source files live in temp dirs.

## Dependencies and Integration Points
Validates `crash.LoadCoverage` cache contract and `reproduceState.KernelSrc` file lookup.

## Risks and Test Signals
Strong signal for sorting, deduplication, line numbering, and covered-line prefixes. It does not test missing coverage or unsafe filenames.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/syzlang/coverage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/syzlang/descriptions.go -->
# sources/test-tools/syzkaller/pkg/aflow/tool/syzlang/descriptions.go

## Purpose
Exposes Linux syzlang description files to aflow agents.

## Important APIs, Types, and Functions
`DescriptionFiles` lists embedded `sys/linux` entries from `sys.Files`. `ReadDescription` registers a `read-description` tool. `readDescription` reads a requested file and returns its contents.

## Control Flow
Listing reads the Linux sys directory and panics on embedded filesystem errors. Reading joins `targets.Linux` with the user-supplied file using slash paths, reads from embedded files, and converts errors to bad-call errors.

## State and Persistence Behavior
Read-only access to embedded syzlang files. No runtime persistence.

## Dependencies and Integration Points
Depends on `aflow`, `sys.Files`, and `targets.Linux`. Used by syzlang-focused agents building or validating repro programs.

## Risks and Test Signals
Risk is path handling across embedded FS paths and user-requested missing files. Tests assert many descriptions, presence of `sys.txt`, successful read, and missing-file error.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/syzlang/descriptions.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/syzlang/descriptions_test.go -->
# sources/test-tools/syzkaller/pkg/aflow/tool/syzlang/descriptions_test.go

## Purpose
Tests syzlang description discovery and read behavior.

## Important APIs, Types, and Functions
Uses `DescriptionFiles`, private `readDescription`, and testify `require`.

## Control Flow
The first test verifies the Linux description set is large and includes `sys.txt`. The second reads `sys.txt`, checks expected content, and verifies a nonexistent file errors.

## State and Persistence Behavior
No mutation; reads embedded `sys.Files` data.

## Dependencies and Integration Points
Provides regression coverage for the embedded sys description filesystem.

## Risks and Test Signals
Good signal for embedded data availability. It does not validate every description file or path traversal semantics.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/syzlang/descriptions_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/syzlang/reproduce.go -->
# sources/test-tools/syzkaller/pkg/aflow/tool/syzlang/reproduce.go

## Purpose
Implements the `reproduce-crash` aflow tool that validates and optionally executes syz repro programs in a VM with coverage.

## Important APIs, Types, and Functions
`Reproduce` registers the tool. `ReproduceArgs` carries `ReproSyz`; `ReproduceResult` carries reproduced bug title/report and cached execution ID. `reproduceState` stores target, kernel, image, VM, and syzkaller paths. `reproduce` parses the program via `prog.GetTarget` and `Deserialize`, then calls `crash.ReproduceFuncWithCoverage` when VM config is present.

## Control Flow
Empty programs and parse errors become bad calls. Without image or VM state, the tool only validates compilation/parsing and returns empty success. With VM state, it builds crash reproduction args, executes with coverage, returns cached ID on did-not-crash, and returns report details on crash.

## State and Persistence Behavior
Execution results and coverage are cached by crash reproduction code and referenced by `ExecutionCachedID`. This function itself does not write source files.

## Dependencies and Integration Points
Depends on `aflow`, `crash`, `prog`, and imported sys descriptions. Integrated with coverage tools via cached IDs.

## Risks and Test Signals
Risks include unsafe/unavailable VM configs, parse strictness, and treating non-crashing executions as non-errors. Tests cover empty, valid, syntax-invalid, and unknown-syscall programs in validation-only mode.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/syzlang/reproduce.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/syzlang/reproduce_test.go -->
# sources/test-tools/syzkaller/pkg/aflow/tool/syzlang/reproduce_test.go

## Purpose
Tests `reproduce` validation behavior without requiring VM execution.

## Important APIs, Types, and Functions
Uses private `reproduce`, `reproduceState{TargetOS: linux, TargetArch: amd64}`, `ReproduceArgs`, and testify assertions.

## Control Flow
Table cases cover empty program, a valid syscall, malformed syntax, and unknown syscall. Because VM state is absent, the valid case stops after parse validation.

## State and Persistence Behavior
No VM, cache, or filesystem state is used.

## Dependencies and Integration Points
Validates integration with `prog.GetTarget` and strict syz program deserialization.

## Risks and Test Signals
Strong parse-level signal but no coverage for VM execution, crash report handling, or cached coverage IDs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/syzlang/reproduce_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/toolkit/race_toolkit.h -->
# sources/test-tools/syzkaller/pkg/aflow/tool/toolkit/race_toolkit.h

## Purpose
C header toolkit for race-condition reproducers, providing CPU pinning, barriers, futex events, monotonic timers, unbuffered I/O, and userfaultfd registration.

## Important APIs, Types, and Functions
Macros include `SETUP_UNBUFFERED_IO`, `PIN_TO_CPU`, `MB`, `WAIT_ON`, `SIGNAL`, `TIMER_START`, and `TIMER_NOT_EXPIRED`. Types/functions include `event_t`, `event_init`, `event_reset`, `event_set`, `event_wait`, `timer_elapsed_sec`, and `setup_uffd`.

## Control Flow
Spin waits use acquire loads until a value appears; signals use release stores. Futex events set state and wake waiters. Timers use `CLOCK_MONOTONIC`. `setup_uffd` creates nonblocking userfaultfd, negotiates API, and registers a missing-page range, closing on setup failures.

## State and Persistence Behavior
State is local process memory plus kernel resources such as futex waits and userfaultfd file descriptors. No persistent storage.

## Dependencies and Integration Points
Included by C reproducers via `get-toolkit`; depends on Linux headers, pthread/sched/futex/syscall/ioctl APIs.

## Risks and Test Signals
Risks include privilege-dependent userfaultfd, CPU affinity failures, busy-wait CPU burn, event double-set fatal exit, and timing sensitivity in VMs. C testdata compiles and exercises the main primitives.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/toolkit/race_toolkit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/toolkit/testdata/toolkit_functional_test.c -->
# sources/test-tools/syzkaller/pkg/aflow/tool/toolkit/testdata/toolkit_functional_test.c

## Purpose
Functional C test for `race_toolkit.h` primitives.

## Important APIs, Types, and Functions
Defines `test_wait_on_signal`, `test_event`, `test_setup_uffd`, `test_pin_to_cpu`, `test_timer`, thread entry points, and `main`.

## Control Flow
`main` enables unbuffered I/O, pins to CPU 0, starts a thread blocked on spin-wait and releases it, starts a futex event waiter and sets it, attempts userfaultfd registration with privilege-aware skip cases, and verifies monotonic timer duration.

## State and Persistence Behavior
Uses process-local globals, threads, mmap memory, userfaultfd fd, and temp kernel resources. No file persistence.

## Dependencies and Integration Points
Compiled and executed by `toolkit_test.go` with `-pthread` and include path to the toolkit package.

## Risks and Test Signals
Timer thresholds can be sensitive on slow hosts; userfaultfd may be unavailable and is skipped only for EPERM/ENOSYS. Provides strong compile/run signal for toolkit primitives.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/toolkit/testdata/toolkit_functional_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/toolkit/testdata/toolkit_standalone_test.c -->
# sources/test-tools/syzkaller/pkg/aflow/tool/toolkit/testdata/toolkit_standalone_test.c

## Purpose
Minimal compile-only style smoke test proving `race_toolkit.h` can be included by a standalone C file.

## Important APIs, Types, and Functions
Includes `../race_toolkit.h` and defines `main` returning zero.

## Control Flow
No runtime logic beyond process start and return.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Built by `toolkit_test.go` with the same compiler flags as other toolkit testdata.

## Risks and Test Signals
Signals header self-containment. It does not exercise macros or Linux runtime APIs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/toolkit/testdata/toolkit_standalone_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/toolkit/toolkit.go -->
# sources/test-tools/syzkaller/pkg/aflow/tool/toolkit/toolkit.go

## Purpose
Registers an aflow tool that returns embedded C toolkit snippets, currently the race-condition toolkit.

## Important APIs, Types, and Functions
`ToolGetToolkit` registers `get-toolkit`. `getToolkitArgs.Name` selects a toolkit. `raceConditionToolkit` embeds `race_toolkit.h`. `getToolkit` returns the race toolkit or an unknown-toolkit bad-call error. `GetRaceToolkit` exposes the embedded header to Go callers.

## Control Flow
A simple name switch accepts exactly `race`; all other names fail with available toolkit guidance.

## State and Persistence Behavior
Read-only embedded asset. No runtime mutation.

## Dependencies and Integration Points
Depends on Go embed and `aflow`. Used by agents building C reproducers that need synchronization helpers.

## Risks and Test Signals
Risk is embedded header drift or missing toolkit names. `toolkit_test.go` compiles and runs C testdata to validate the embedded file's source counterpart.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/toolkit/toolkit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/toolkit/toolkit_test.go -->
# sources/test-tools/syzkaller/pkg/aflow/tool/toolkit/toolkit_test.go

## Purpose
Linux-only compile/run tests for C files under toolkit testdata.

## Important APIs, Types, and Functions
`TestToolkitsInTestData` discovers `testdata/*.c`, selects gcc or clang, compiles with `-I . -pthread`, and executes each binary.

## Control Flow
If no compiler exists the test skips. Each C file is compiled into a temp binary, then executed with combined output captured for failures/logging.

## State and Persistence Behavior
Creates temporary binaries only. No persistent state.

## Dependencies and Integration Points
Depends on host C compiler and Linux runtime support for the toolkit tests.

## Risks and Test Signals
Excellent signal for header compile health and functional primitives, but host privileges can affect userfaultfd and CPU affinity behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/tool/toolkit/toolkit_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/trajectory/html/trajectory.go -->
# sources/test-tools/syzkaller/pkg/aflow/trajectory/html/trajectory.go

## Purpose
Renders aflow trajectory spans into full HTML reports or reusable trajectory snippets.

## Important APIs, Types, and Functions
Embeds `report.html` and `trajectory_block.html`. `UIAITrajectorySpan` is the view model. `PopulateToolCalls` associates tool names with the next LLM span at the same nesting. `RenderReport`, `RenderTrajectory`, and `marshalJSON` prepare templates and JSON.

## Control Flow
`RenderReport` converts raw `trajectory.Span` records to UI spans, computes durations, marshals args/results, populates tool-call associations, marshals UI spans to JSON, parses templates with shared HTML funcs, and executes. `RenderTrajectory` does the same for only the shared block.

## State and Persistence Behavior
No persistent state; writes rendered HTML to the provided writer or buffer.

## Dependencies and Integration Points
Depends on `trajectory`, syzkaller `pkg/html` template funcs, Go `html/template`, and embedded templates. Consumes golden trajectory fixtures indirectly through tests/reports.

## Risks and Test Signals
Risks include unsafe JSON embedding, template parse failures, and wrong tool attribution across nesting levels. Tests focus on `PopulateToolCalls` nesting behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/trajectory/html/trajectory.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/trajectory/html/trajectory_test.go -->
# sources/test-tools/syzkaller/pkg/aflow/trajectory/html/trajectory_test.go

## Purpose
Tests inferred tool-call attribution for trajectory HTML view models.

## Important APIs, Types, and Functions
Uses `UIAITrajectorySpan` and `PopulateToolCalls` with testify assertions.

## Control Flow
Tests cover one tool before an LLM, multiple consecutive tools before an LLM, and nested agents where tool calls at one nesting level must not leak to another.

## State and Persistence Behavior
Pure in-memory tests. No rendered files are written.

## Dependencies and Integration Points
Protects the UI tooltip/chart data computed by `trajectory.go`.

## Risks and Test Signals
Good signal for nesting isolation and pending-tool clearing. It does not validate template rendering or JSON escaping.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/trajectory/html/trajectory_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/trajectory/trajectory.go -->
# sources/test-tools/syzkaller/pkg/aflow/trajectory/trajectory.go

## Purpose
Defines aflow execution span data and console string formatting for trajectory logging.

## Important APIs, Types, and Functions
`Span` records sequence, nesting, type, name, model, timestamps, errors, args/results, agent instruction/prompt/reply, LLM thoughts, and token counts. `SpanType` constants define stable string values. `(*Span).String` formats start/finish logs, and `printMap` deterministically prints sorted map keys.

## Control Flow
`String` branches on whether `Finished` is zero and on span type. Start spans print prompts or tool args where relevant. Finished spans print results, replies, LLM tokens/thoughts/replies, or tool results. Unknown span types panic.

## State and Persistence Behavior
`Span` is a serializable record persisted in trajectory JSON and dashboard data. The code itself stores no global state.

## Dependencies and Integration Points
Used throughout aflow for workflow tracing, test fixtures, dashboards, and HTML rendering.

## Risks and Test Signals
Stable `SpanType` strings are database-facing and should not change casually. Map sorting avoids nondeterministic logs. Golden trajectory fixtures are the main regression signal.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/trajectory/trajectory.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/verify.go -->
# sources/test-tools/syzkaller/pkg/aflow/verify.go

## Purpose
Implements static verification helpers for aflow action graphs, checking variable wiring, output usage, model names, and schema validity.

## Important APIs, Types, and Functions
`verifyContext` tracks input/output verification modes, variable state, registered models, and first error. `varState` records producing action, type, and use. Helpers include `newVerifyContext`, `requireInput`, `provideOutput`, `finalize`, `noteError`, `requireInputs`, `provideOutputs`, `provideOutputsMap`, `provideArrayOutputs`, and `requireSchema`.

## Control Flow
Actions call require/provide helpers while a flow is verified. Missing inputs, type mismatches, duplicate outputs, empty required values, invalid schemas, and unused outputs are accumulated through first-error preservation. `finalize` flags any output never consumed.

## State and Persistence Behavior
Verification state is in-memory for one verification pass. No persistence.

## Dependencies and Integration Points
Depends on reflection plus local helpers `foreachFieldOf` and `schemaFor`. Integrated into aflow flow/action/tool definitions before execution.

## Risks and Test Signals
Risks include reflect type equality surprises, map output nil types, and unused-output false positives for intentionally terminal values. Covered indirectly by aflow workflow tests and fixture generation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/verify.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/asset/backend_dummy.go -->
# sources/test-tools/syzkaller/pkg/asset/backend_dummy.go

## Purpose
In-memory/dummy asset storage backend for debugging and tests.

## Important APIs, Types, and Functions
`dummyStorageBackend` tracks current time, object metadata, and optional upload/remove callbacks. Methods implement `StorageBackend`: `upload`, `downloadURL`, `getPath`, `list`, `remove`, plus test helper `hasOnly`. `dummyWriteCloser` discards bytes.

## Control Flow
Uploads record object metadata and delegate to callback or return a discard writer. URLs are mapped to/from `http://download/` paths, with a special unknown-bucket URL. Listing converts map entries to `gcs.Object`; removal invokes callback, checks existence, and deletes.

## State and Persistence Behavior
State is an in-memory map of path to creation/content metadata. It is lost when the backend is dropped.

## Dependencies and Integration Points
Used by `StorageFromConfig` for `dummy://` and by storage tests to inspect uploads/deletions.

## Risks and Test Signals
Not concurrency-safe and does not store bytes unless callbacks do. Tests use it to validate compression, deprecation, duplicate handling, and URL parsing paths.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/asset/backend_dummy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/asset/backend_gcs.go -->
# sources/test-tools/syzkaller/pkg/asset/backend_gcs.go

## Purpose
Google Cloud Storage implementation of the asset `StorageBackend` interface.

## Important APIs, Types, and Functions
`cloudStorageBackend` holds `gcs.Client`, bucket, and tracer. `makeCloudStorageBackend` constructs the client. `writeErrorLogger` logs write/close errors. Backend methods implement upload, download URL generation, URL-to-path parsing, list, and remove.

## Control Flow
Upload checks for existing object, obtains a writer with content metadata, wraps it for logging, and returns the save path. `downloadURL` delegates to GCS helpers. `getPath` parses URLs, accepts only storage Google domains, checks bucket prefix, and strips it. `remove` maps GCS not-found to `ErrAssetDoesNotExist`.

## State and Persistence Behavior
Persists objects in GCS. Local state is just client configuration and tracing.

## Dependencies and Integration Points
Depends on `pkg/gcs`, `debugtracer`, URL parsing, and `Storage` upload/deprecation paths.

## Risks and Test Signals
Risks include best-effort exists check races, allowed-domain regex precedence, bucket mismatch, and delayed writer errors. Tests cover URL generation/parsing and bucket/domain rejection.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/asset/backend_gcs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/asset/backend_gcs_test.go -->
# sources/test-tools/syzkaller/pkg/asset/backend_gcs_test.go

## Purpose
Tests GCS backend download URL construction and URL path parsing.

## Important APIs, Types, and Functions
Uses a `cloudStorageBackend` with nil client and `debugtracer.NullTracer`, then calls `downloadURL` and `getPath`.

## Control Flow
Positive cases cover public and non-public storage URLs. Negative cases cover unknown host and wrong bucket.

## State and Persistence Behavior
No GCS calls or writes are made.

## Dependencies and Integration Points
Validates URL format compatibility with `pkg/gcs.GetDownloadURL` and deprecation URL parsing.

## Risks and Test Signals
Good signal for bucket safety. It does not test upload/list/delete behavior against real GCS.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/asset/backend_gcs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/asset/config.go -->
# sources/test-tools/syzkaller/pkg/asset/config.go

## Purpose
Defines asset upload configuration and validation.

## Important APIs, Types, and Functions
`Config` controls debug tracing, upload destination, deprecation, public access, and per-asset `TypeConfig`. `TypeConfig.Validate`, `Config.IsEnabled`, `Config.IsEmpty`, and `Config.Validate` are the public helpers.

## Control Flow
Validation checks every configured asset type is known, validates its type config, rejects non-empty asset settings without `upload_to`, and permits only `gs://` or `dummy://` upload destinations.

## State and Persistence Behavior
Configuration data is loaded by callers and held in memory. No writes.

## Dependencies and Integration Points
Depends on dashboard asset type constants and `GetTypeDescription`. Consumed by `StorageFromConfig` and upload gating.

## Risks and Test Signals
Risk is nil `Config` method calls except `IsEmpty`; `IsEnabled` expects non-nil config. Storage tests cover disabled asset behavior and supported dummy destination.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/asset/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/asset/storage.go -->
# sources/test-tools/syzkaller/pkg/asset/storage.go

## Purpose
Core asset upload, compression, dashboard reporting, and garbage-collection logic for syzkaller build/crash artifacts.

## Important APIs, Types, and Functions
`Storage` combines config, backend, dashboard API, and tracer. Public methods include `StorageFromConfig`, `AssetTypeEnabled`, `UploadBuildAsset`, `ReportBuildAssets`, `UploadCrashAsset`, and `DeprecateAssets`. Supporting types include `Dashboard`, `ExtraUploadArg`, `DeprecateStats`, `StorageBackend`, `Compressor`, `FileExistsError`, and `wrappedWriteCloser`.

## Control Flow
Uploads validate name/type/enabled status, create a unique or tagged path, pick xz or custom gzip compressor, request a backend writer, stream bytes, close wrappers, and return a download URL. Build uploads add commit prefixes to names. Reporting sends assets to dashboard. Deprecation queries needed URLs, converts them to backend paths, lists existing objects, protects recent uploads, refuses deletion on suspicious zero intersection, and removes stale paths while tolerating concurrent missing-object races.

## State and Persistence Behavior
Persists compressed artifacts in the backend and dashboard asset references via `AddBuildAssets`. Local state is in-memory. Deprecation mutates backend storage by deleting objects older than the embargo and not needed by dashboard.

## Dependencies and Integration Points
Depends on dashboard API types, GCS object metadata, debug tracing, xz/gzip compressors, build metadata, and backend implementations.

## Risks and Test Signals
Risks include upload/write-close error ordering, duplicate-tag races, incorrect content encoding, accidental deletion from malformed dashboard URLs, and time-based embargo mistakes. Tests cover upload naming/compression, HTML gzip extension preservation, disabled types, duplicate content skip, deprecation protection, multi-bucket handling, and invalid URL aborts.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/asset/storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/asset/storage_test.go -->
# sources/test-tools/syzkaller/pkg/asset/storage_test.go

## Purpose
Comprehensive tests for asset storage upload, compression, dashboard reporting, duplicate handling, and deprecation.

## Important APIs, Types, and Functions
Defines `dashMock`, `makeStorage`, `collectBytes`, `validateGzip`, `validateXz`, and helper `sendBuildAsset`. Tests cover build assets, HTML assets, recent deletion protection, configuration, same-content upload, two-bucket deprecation, and invalid URLs.

## Control Flow
Tests use dummy backend callbacks to capture compressed bytes, upload assets through public methods, report them to a mock dashboard, manipulate needed URL sets, and run `DeprecateAssets` under success/error scenarios.

## State and Persistence Behavior
All state is in-memory dummy backend maps and mock dashboard URL maps. Time is controlled through `be.currentTime` for embargo behavior.

## Dependencies and Integration Points
Validates xz/gzip compressor wrappers, dummy backend URL mapping, dashboard API contract, and storage deprecation safety checks.

## Risks and Test Signals
Strong signal for storage behavior without real GCS. It does not cover cloud writer failures or concurrent upload/delete races.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/asset/storage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/asset/type.go -->
# sources/test-tools/syzkaller/pkg/asset/type.go

## Purpose
Defines metadata for supported dashboard asset types.

## Important APIs, Types, and Functions
`TypeDescription` describes multiplicity, title function, content type/encoding, reporting priority, reporting suppression, custom compressor, and extension preservation. `assetTypes` maps dashboard asset types to descriptions. `QueryTypeTitle`, `constTitle`, and `GetTypeDescription` expose lookup behavior.

## Control Flow
Lookup is a simple map access. Kernel object title can use target-specific `KernelObject`; other types use constant titles.

## State and Persistence Behavior
Static package-level metadata only.

## Dependencies and Integration Points
Depends on `dashapi.AssetType` and `targets.Target`. Consumed by config validation, upload content metadata, compression choice, and reporting ordering.

## Risks and Test Signals
Unknown asset types return nil and must be checked by callers. HTML coverage uses gzip with preserved extension and no reporting, which is important browser behavior. Covered indirectly by storage/config tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/asset/type.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ast/ast.go -->
# sources/test-tools/syzkaller/pkg/ast/ast.go

## Purpose
Defines the AST model for syzkaller syscall description (`sys`) files.

## Important APIs, Types, and Functions
Core types are `Pos`, `Description`, `Node`, `Flags`, and `FlagValue`. Top-level nodes include `NewLine`, `Comment`, `Meta`, `Include`, `Incdir`, `Define`, `Resource`, `Call`, `Struct`, `IntFlags`, `StrFlags`, and `TypeDef`. Expression/value nodes include `Ident`, `String`, `Int`, `BinaryExpression`, `Type`, and `Field` with format enums and operators.

## Control Flow
There is no parser logic here; each node implements `Info` and some flag nodes implement mutation/accessor methods. `Clone` and `walk` contracts are declared through the `Node` interface and implemented in other files.

## State and Persistence Behavior
AST nodes are in-memory mutable structs representing parsed source positions and declarations. Persistence happens through formatting elsewhere.

## Dependencies and Integration Points
Used by parser, formatter, clone/filter/walk utilities, compiler stages, and syzlang tooling.

## Risks and Test Signals
Risks include nil subnodes, format-field invariants where only one variant should be set, and stable `Info` type strings. Parser round-trip tests exercise the model broadly.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ast/ast.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ast/clone.go -->
# sources/test-tools/syzkaller/pkg/ast/clone.go

## Purpose
Implements deep-copy behavior for every AST node type.

## Important APIs, Types, and Functions
`(*Description).Clone` and each node's `Clone` method return independent copies. Helpers `cloneFields`, `cloneInts`, `cloneTypes`, and `cloneComments` clone slices.

## Control Flow
Each method copies scalar fields and recursively clones child nodes. Optional fields such as call return type, typedef type/struct, and binary expressions are nil-checked.

## State and Persistence Behavior
Creates in-memory copies only. Clone preserves source positions, comments, formatting choices, and AST shape.

## Dependencies and Integration Points
Used by `Filter`, tests, and callers that need to transform ASTs without mutating originals.

## Risks and Test Signals
Risks include shallow-copy bugs for slices or missing new node fields. `TestParseAll` asserts formatting of cloned descriptions matches original data.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ast/clone.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ast/filter.go -->
# sources/test-tools/syzkaller/pkg/ast/filter.go

## Purpose
Provides top-level AST filtering while preserving deep-copy isolation.

## Important APIs, Types, and Functions
`(*Description).Filter(predicate func(Node) bool) *Description` returns a new description containing clones of nodes for which the predicate returns true.

## Control Flow
Iterates only top-level nodes, applies predicate, clones accepted nodes, and appends them to the result.

## State and Persistence Behavior
No mutation of the original description. Output is in-memory only.

## Dependencies and Integration Points
Depends on node `Clone` implementations. Used by AST consumers selecting subsets of declarations.

## Risks and Test Signals
Filtering is non-recursive, which callers must understand. Parser tests verify all-true and all-false behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ast/filter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ast/format.go -->
# sources/test-tools/syzkaller/pkg/ast/format.go

## Purpose
Serializes AST descriptions and nodes back into syzkaller description syntax.

## Important APIs, Types, and Functions
`Format`, `FormatWriter`, `SerializeNode`, `FormatInt`, `FormatStr`, node `serialize` methods, `fmtType`, `fmtField`, `fmtTypeList`, `fmtExpressionRec`, and `operatorPrio` implement formatting.

## Control Flow
Top-level formatting dispatches through the private `serializer` interface. Structs align field type columns and preserve new blocks/comments. Types serialize atoms, colon parts, arguments, strings/ints, and binary expressions with precedence-aware parentheses.

## State and Persistence Behavior
Writes text to a buffer or writer; does not mutate the AST. Formatting preserves enough layout for round-trip tests but normalizes some spacing/alignment.

## Dependencies and Integration Points
Used by parser round-trip tests and tools that generate or rewrite syzlang descriptions.

## Risks and Test Signals
Unknown node/operator/format values panic. Round-trip tests across all Linux sys files are the main signal for parser/formatter compatibility.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ast/format.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ast/parser.go -->
# sources/test-tools/syzkaller/pkg/ast/parser.go

## Purpose
Recursive-descent parser for syzkaller syscall description files.

## Important APIs, Types, and Functions
Public APIs are `Parse` and `ParseGlob`. Private parser methods handle top-level recovery, declarations, calls, structs/unions, flags, typedefs, fields, comments, resources, includes, type expressions, type lists, identifiers, strings, integers, and C expressions.

## Control Flow
`Parse` scans tokens until EOF, recovers per line on parse errors, normalizes blank lines around structs, and returns nil if the scanner recorded errors. `ParseGlob` reads all matching files and appends parsed nodes. Type parsing uses precedence levels for `||`, comparisons, and `&`; factor parsing handles parentheses, ints, identifiers, strings, colon suffixes, and type arguments.

## State and Persistence Behavior
Parser state is current token/literal/position plus scanner state. It builds an in-memory `Description`; no writes except error callbacks.

## Dependencies and Integration Points
Depends on `scanner.go`, AST node definitions, filesystem glob/read, and error handlers. It is central to syzlang compilation and tests.

## Risks and Test Signals
Risks include recovery skipping too much, precedence bugs, C-expression capture after define, newline normalization drift, and nil returns after partial glob failures. Tests parse all Linux descriptions and error fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ast/parser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ast/parser_test.go -->
# sources/test-tools/syzkaller/pkg/ast/parser_test.go

## Purpose
Round-trip and error tests for the syzkaller AST parser/formatter/walker/clone/filter stack.

## Important APIs, Types, and Functions
`TestParseAll`, `TestParse`, `TestErrors`, `parseTests`, and `NewErrorMatcher` are used. The tests call `Parse`, `Format`, `Clone`, `Walk`, `Recursive`, `PostRecursive`, `SerializeNode`, and `Filter`.

## Control Flow
`TestParseAll` parses every Linux sys file and a broad test file, formats and reparses, compares node equality, checks clone formatting, validates walking counts and node info, and tests filters. `TestErrors` compares expected inline `###` diagnostics against parser output.

## State and Persistence Behavior
Reads repository sys/testdata files and stores diagnostics in memory. No writes.

## Dependencies and Integration Points
High-level integration coverage for scanner, parser, formatter, clone, filter, and walk.

## Risks and Test Signals
Very strong regression signal for syzlang syntax support. It can be sensitive to intentional formatting changes and sys description corpus changes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ast/parser_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ast/scanner.go -->
# sources/test-tools/syzkaller/pkg/ast/scanner.go

## Purpose
Lexical scanner for syzkaller description syntax.

## Important APIs, Types, and Functions
Defines token constants, punctuation/keyword tables, `scanner`, `ErrorHandler`, `LoggingHandler`, `BuiltinFile`, `Pos` helpers, `newScanner`, `Scan`, token-specific scanners, `IsValidStringLit`, and scanner position/error helpers.

## Control Flow
`Scan` skips spaces/tabs, emits EOF after an implicit newline, captures define C expressions based on previous tokens, scans comments, strings/hex strings, integers, chars, identifiers/keywords, multi-char operators, or punctuation. `next` handles CR stripping, line/column updates, NUL errors, and final newline behavior.

## State and Persistence Behavior
Scanner maintains byte offset, line, column, previous tokens, and error count over an input byte slice. It does not persist data.

## Dependencies and Integration Points
Used by `parser.go`. Error handlers integrate with tests and logging.

## Risks and Test Signals
Risks include byte-oriented column handling, limited char literal support, hex string decoding errors, implicit newline edge cases, and C-expression token context. Parser tests and error fixtures exercise scanner behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ast/scanner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ast/test_util.go -->
# sources/test-tools/syzkaller/pkg/ast/test_util.go

## Purpose
Test helper for matching parser diagnostics embedded in testdata files.

## Important APIs, Types, and Functions
`ErrorMatcher`, `errorDesc`, `NewErrorMatcher`, `ErrorHandler`, `Count`, `Check`, and `DumpErrors` collect expected and actual errors. `errorLocationRe` normalizes location substrings inside messages.

## Control Flow
`NewErrorMatcher` reads a file, strips `### expected error` annotations while recording line/text expectations. `ErrorHandler` records actual diagnostics. `Check` matches actual errors to expected by line and text, sorts unmatched/unexpected errors by position, and reports a formatted diff.

## State and Persistence Behavior
Stores stripped data and diagnostics in memory. Reads testdata files only.

## Dependencies and Integration Points
Used by `parser_test.go` error-fixture tests.

## Risks and Test Signals
Risks include exact-message brittleness and only line-level expected positions. It provides clear diagnostics when parser error behavior changes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ast/test_util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ast/walk.go -->
# sources/test-tools/syzkaller/pkg/ast/walk.go

## Purpose
Implements AST traversal helpers and per-node child walking.

## Important APIs, Types, and Functions
`(*Description).Walk`, `Recursive`, `PostRecursive`, and each node's private `walk` method define traversal. Recursive traversal can be pre-order with pruning or post-order without pruning.

## Control Flow
Top-level `Walk` visits only description nodes. `Recursive` wraps a callback so returning true descends into children. `PostRecursive` descends first, then calls callback. Node walk methods enumerate direct children in structural order.

## State and Persistence Behavior
Pure in-memory traversal with caller-supplied callbacks. No mutation unless callbacks mutate nodes.

## Dependencies and Integration Points
Used by AST analysis/transformation code and parser tests.

## Risks and Test Signals
Risks include omitted new child fields and recursion cycles if future nodes introduce backreferences. `TestParseAll` compares recursive and post-recursive counts.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ast/walk.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/auth/auth.go -->
# sources/test-tools/syzkaller/pkg/auth/auth.go

## Purpose
Validates Google OAuth2 identity tokens for dashboard API clients and maps them to syzkaller auth subjects.

## Important APIs, Types, and Functions
Constants `GoogleTokenInfoEndpoint` and `OauthMagic`, `Endpoint`, `MakeEndpoint`, `jwtClaimsParse`, `jwtClaims`, `queryTokenInfo`, and `DetermineAuthSubj` are the core API.

## Control Flow
`DetermineAuthSubj` ignores missing/non-Bearer headers for password auth fallback. Bearer tokens are posted to tokeninfo with up to three HTTP attempts, JSON claims are parsed, audience is checked against `DashboardAudience`, expiration is compared with `now`, and the subject is returned with `OauthMagic` prefix.

## State and Persistence Behavior
No cache in this endpoint path; every bearer verification queries the endpoint. No persistence.

## Dependencies and Integration Points
Depends on net/http, tokeninfo protocol, and `DashboardAudience` from `jwt.go`. Used by dashboard/API authentication.

## Risks and Test Signals
Risks include no response timeout at this layer, strict single-header behavior, and trusting tokeninfo availability. Tests cover valid bearer, wrong audience, expired token, missing/bad headers, and bad HTTP status.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/auth/auth.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/auth/auth_test.go -->
# sources/test-tools/syzkaller/pkg/auth/auth_test.go

## Purpose
Unit tests for OAuth bearer subject determination.

## Important APIs, Types, and Functions
`reponseFor` creates an httptest tokeninfo server returning desired claims. Tests call `Endpoint.DetermineAuthSubj`.

## Control Flow
Cases cover valid bearer subject suffix, wrong audience, expired token, missing header, malformed/non-bearer header, and non-OK tokeninfo status.

## State and Persistence Behavior
Each test uses an in-memory HTTP server and no persistent state.

## Dependencies and Integration Points
Validates `auth.go` behavior with controlled tokeninfo responses.

## Risks and Test Signals
Good signal for server-side token validation branches. It does not cover retry-on-transport-failure or malformed JSON/expiration.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/auth/auth_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/auth/jwt.go -->
# sources/test-tools/syzkaller/pkg/auth/jwt.go

## Purpose
Retrieves and caches Google metadata-server identity JWTs for clients calling the syzkaller dashboard API.

## Important APIs, Types, and Functions
`DashboardAudience`, `expiringToken`, `extractJwtExpiration`, request function types, `retrieveJwtToken`, `TokenCache`, `MakeCache`, and `(*TokenCache).Get` form the API.

## Control Flow
`retrieveJwtToken` builds a metadata-server request with audience and `Metadata-Flavor: Google`, reads the token, checks HTTP status, extracts unverified `exp` from JWT payload, and returns token plus expiration. `MakeCache` fetches an initial token. `Get` locks, refreshes if expiration is less than one minute away, and returns an Authorization header value.

## State and Persistence Behavior
`TokenCache` stores one token in memory protected by a mutex. It performs network refreshes but no disk persistence.

## Dependencies and Integration Points
Used by syz-ci/syz-hub clients that need bearer credentials for dashboard API. Depends on metadata server JWT format and caller-injected request constructor/doer for testability.

## Risks and Test Signals
Risks include unverified expiration parsing, holding lock during HTTP refresh, and metadata-server availability. Tests in this subset focus on server-side auth, not this cache path.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/auth/jwt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/bisect/bisect.go -->
# sources/test-tools/syzkaller/pkg/bisect/bisect.go

## Purpose
Implements syzkaller kernel commit/config bisection for crash causes and fixes, including build/test orchestration, flakiness handling, release-range selection, config minimization, and result confidence.

## Important APIs, Types, and Functions
Public structs are `Config`, `KernelConfig`, `SyzkallerConfig`, `ReproConfig`, and `Result`; public entry point is `Run`. The internal `env` owns repo, bisecter, minimizer, instance environment, current commits, kernel config, timing, report types, reproducibility estimates, cached results, and build config. Major methods include `bisect`, `identifyRewrittenCommit`, `minimizeConfig`, `commitRange*`, `validateCommitRange`, `build`, `test`, `testPredicate`, `revisionHadBug`, `bisectionDecision`, `processResults`, `postTestResult`, `updateFlaky`, `detectNoopChange`, `isTransientError`, and `pickReleaseTags`.

## Control Flow
`Run` validates config, disables coverage, opens repo/env, checks out the branch, and calls `runImpl`. `bisect` prepares the repo, cleans/builds syzkaller, identifies rewritten commits, verifies the crash on the original commit, optionally minimizes config, finds bad/good range for cause or fix bisection, seeds result cache, runs VCS bisection via `testPredicate`, then annotates the result with report, release status, noop-change detection, config, and confidence. `test` builds the kernel for the current revision, runs reproducer trials, classifies results, updates flakiness/confidence, and returns a bisect verdict.

## State and Persistence Behavior
Mutates the kernel checkout by switching commits and building. Uses `instance.Env` to build/test kernels and syzkaller. Saves debug files through the configured tracer, tracks in-memory result cache by commit hash, and returns minimized config bytes. It restores the original HEAD at the end of `runImpl` via defer.

## Dependencies and Integration Points
Depends on `vcs` repository/bisect/config-minimizer interfaces, `instance` build/test environment, `build` error types, manager config, report/crash classification, osutil semaphores, hash signatures, and debug tracing. It is a core backend for syzbot/syz-ci bisection jobs.

## Risks and Test Signals
Risks are high: flaky reproducers, infra errors, build failures on old commits, rewritten branches, cross-tree merge bases, transient crash types, broad config minimization, false negatives, and accidentally deleting confidence through poor report classification. The code contains many safeguards: max trials, skip verdicts, infra aborts, release-tag sampling, recent result cache, transient syz/lost-connection filtering, suspicious deprecation avoidance in other package not here, and noop binary signature detection. The listed subset lacks `bisect_test.go`, so coverage comes from broader package tests and integration bisection runs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/bisect/bisect.go -->
