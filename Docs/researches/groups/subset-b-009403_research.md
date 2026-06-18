# subset-b-009403 Research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/llm_tool_test.go -->
# sources/test-tools/syzkaller/pkg/aflow/llm_tool_test.go

Purpose: validates nested LLM tool behavior where a main `LLMAgent` exposes an `LLMTool` named `researcher`, and that sub-agent has its own `researcher-tool` function tool. `TestLLMTool` proves workflow input state reaches the nested function tool, the nested agent can call tools, recover from an input-token-overflow API error, and still return the main `Reply`. `TestLLMToolMaxIters` stresses the sub-agent tool loop up to `maxLLMIterations`.

Important APIs and control flow: both tests use `testFlow`, `LLMAgent`, `LLMTool`, `NewFuncTool`, `genai.Part`, and `genai.FunctionCall`. The fixture sequence alternates main-agent LLM calls, `researcher` tool invocations, sub-agent LLM calls, subtool calls, and final text replies.

State and persistence: no durable state is written by this file. Runtime state is the workflow state map, especially `Input` and `Reply`; request and trajectory persistence is delegated to `runner_test.go` golden files.

Dependencies and integration: depends on `google.golang.org/genai`, `net/http`, `strings`, and testify assertions. It integrates with aflow LLM agent/tool registration, bad API error handling, nested tool schemas, and the golden files `TestLLMTool.llm.json` and `TestLLMTool.trajectory.json`.

Risks and test signals: the main risk is regressions in nested conversation accounting, repeated sub-agent tool calls, or error recovery after token overflow. Strong signals are the assertion that subtool args have expected prefixes, the nested state assertion `Input == 42`, and golden request/trajectory comparison.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/llm_tool_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/loop.go -->
# sources/test-tools/syzkaller/pkg/aflow/loop.go

Purpose: implements loop actions for aflow: `DoWhile` for repeat-until-empty string conditions, and `ForEach` for iterating over slice inputs while injecting an item variable into state.

Important APIs/types/functions: `DoWhile` exposes `Do Action`, `While string`, `MaxIterations int`, and internal `loopVars`. `ForEach` exposes `List`, `Item`, `Do`, and internal `loopVars`. Both implement `execute(ctx *Context) error` and `verify(ctx *verifyContext)`. Execution emits `trajectory.SpanLoop` and `trajectory.SpanLoopIteration` spans.

Control flow: `DoWhile.execute` opens a loop span, calls `loop`, then closes the span with any error. `loop` zero-initializes body-produced loop variables, runs body iterations up to `MaxIterations`, exits when `ctx.state[While].(string) == ""`, and errors on limit exhaustion. `ForEach.execute` validates the list exists and is a slice, opens a loop span named `ForEach`, zero-initializes body outputs, injects `Item` per element, executes the body, and deletes `Item` at the end.

State and persistence: state is entirely in-memory `ctx.state`. `DoWhile` permits loop variable redefinition to support nested loops and resets loop-carried values before entry. `ForEach` is stricter: loopVars must not already exist at runtime, and `Item` is temporary.

Dependencies and integration: uses `reflect` for type-aware zero values and slice inspection, `maps.Clone` for verification snapshots, and `trajectory` for event emission. It integrates with the broader `Action` verification model where outputs and inputs are checked in separate passes.

Risks and test signals: risks include panics if `While` is not string despite verification, leaked loop variables, duplicate names across loop boundaries, and failure to close spans correctly on body errors. `loop_test.go` covers normal do-while, max-iteration failure, nested-loop variable behavior, and `ForEach` typing/usage errors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/loop.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/loop_test.go -->
# sources/test-tools/syzkaller/pkg/aflow/loop_test.go

Purpose: tests `DoWhile` and `ForEach` registration, verification, execution, state propagation, and golden trajectory output.

Important APIs/functions: uses `testFlow`, `testRegistrationError`, `Pipeline`, `NewFuncAction`, `DoWhile`, and `ForEach`. Local struct types model action inputs/results such as patch generation, patch testing, list item processing, and loop continuation variables.

Control flow: `TestDoWhile` simulates patch generation until a tester clears `TestError` on the third iteration. `TestDoWhileErrors` verifies missing inputs, empty `While`, unused outputs, and invalid `MaxIterations`. `TestDoWhileMaxIters` expects the max-iteration error path. `TestForEach` builds a slice accumulator by uppercasing items. `TestForEachErrors` covers missing names, missing list input, non-slice list, and unused item variable. Nested-loop tests assert inner loop outputs do not panic on re-entry, remain visible to later outer actions, and cannot redefine variables already created outside a loop.

State and persistence: tests mutate only in-memory state and rely on `testFlow` to compare trajectories against files under `testdata`.

Dependencies and integration: imports `fmt`, `strings`, and `testing`; integrates directly with loop verification in `loop.go` and function-action registration in aflow.

Risks and test signals: strong regression signals are exact registration error strings and golden span comparisons. The nested-loop cases are especially important because loop verification deliberately bends normal defined-before-use rules.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/loop_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/mcp.go -->
# sources/test-tools/syzkaller/pkg/aflow/mcp.go

Purpose: exports aflow tools and actions as Model Context Protocol tools for `tools/syz-mcp`, and provides an MCP-ready `Context`.

Important APIs/types/functions: `MCPTools` maps `*mcp.Tool` to `MCPToolFunc`. `NewMCPContext` initializes `Context` with absolute workdir, cache, supplied state, no-op trajectory events, and real time. `registerMCPTool` wraps `funcTool` with input/output schemas and structured results. `registerMCPAction` wraps `funcAction` as an MCP tool with empty input schema and output extracted from context state. `registerMCP` normalizes names by replacing dashes with underscores, de-duplicates names, and skips disabled registration or `llmSetResultsTool`.

Control flow: registrations create `mcp.Tool` descriptors from aflow schema helpers, then install handler closures into the global map. Tool handlers convert bad-call errors into MCP error results while propagating infrastructure errors. Action handlers execute the action and convert context state to declared result shape.

State and persistence: global process state includes `MCPTools`, `registerMCPTools`, and `mcpToolNames`. Per-call state lives in `Context.state`; no on-disk persistence is introduced.

Dependencies and integration: depends on `modelcontextprotocol/go-sdk/mcp`, syzkaller `osutil`, `trajectory`, and schema conversion helpers. The `init` function registers `session-initializer`, which seeds `ReproSyz`, `ReproOpts`, and `ReproC` for MCP workflows.

Risks and test signals: risks are global registration order, name collisions after dash-to-underscore normalization, schema panics from missing tags, and inconsistent error mapping. Coverage is indirect through schema/tool tests and MCP consumers rather than explicit tests in this file.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/mcp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/runner_test.go -->
# sources/test-tools/syzkaller/pkg/aflow/runner_test.go

Purpose: central test harness for executing aflow workflows and comparing produced trajectories and LLM requests with golden files.

Important APIs/functions: `testFlow[Inputs, Outputs]` registers a test flow, installs a stub `generateContent`, executes the flow, serializes spans and LLM requests through JSON, optionally updates golden files via `-update`, and compares results. `testRegistrationError` asserts registration failures. `setupDefaults` fills defaults for `LLMAgent`, `pipeline`, `If`, `DoWhile`, and `ForEach`.

Control flow: the LLM stub records model/config/request snapshots, consumes provided replies, supports callback replies, and converts `*genai.Part` or `[]*genai.Part` into `GenerateContentResponse`. After `Flow.Execute`, the harness compares either output maps or expected error strings, then checks `testdata/<TestName>.trajectory.json` and optional `.llm.json`.

State and persistence: test state is held in local slices `requests` and `spans`, a temporary workdir, and a test cache. Persistent golden files are read or rewritten only when `-update` is supplied.

Dependencies and integration: depends on `context`, `encoding/json`, `flag`, `os`, `filepath`, `reflect`, `slices`, `time`, syzkaller `trajectory`/`osutil`, testify `require`, and `genai`. It is the integration point for most aflow unit tests that need deterministic time and LLM behavior.

Risks and test signals: exact golden matching is high signal but brittle when span schemas, timestamps, config serialization, or default prompts change. The `lastConfig` elision logic means `.llm.json` files intentionally omit repeated configs unless they change.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/runner_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/schema.go -->
# sources/test-tools/syzkaller/pkg/aflow/schema.go

Purpose: provides reflection-based schema validation, JSON schema generation, map-to-struct conversion, struct-to-map extraction, and field iteration helpers for aflow actions/tools.

Important APIs/functions: `schemaFor`, `uncheckedSchemaFor`, `checkSchemaType`, `mustSchemaFor`, `convertToMap`, `convertFromMap`, `convertFromMapReflect`, `setField`, `setSliceField`, `extractOutputs`, `foreachField`, and `foreachFieldOf`.

Control flow: schema generation requires a struct type and recursively enforces `jsonschema` descriptions on visible fields. Conversion clones the input map, walks exported visible fields, enforces required fields unless `omitempty`, optionally rejects unused fields in strict mode, and delegates each assignment to `setField`. `setField` handles pointer targets, `json.RawMessage`, JSON float-to-int conversion with truncation checks, exact type matches, `json.Unmarshaler` types such as `time.Time`, nested structs, and slices.

State and persistence: no durable state. The functions transform in-memory maps and structs; `extractOutputs` intentionally panics if state lacks required outputs after verification.

Dependencies and integration: depends on `encoding/json`, `reflect`, `maps`, `iter`, `strings`, and `github.com/google/jsonschema-go/jsonschema`. It underpins action/tool argument conversion, MCP schemas, LLM tool schemas, and test helpers.

Risks and test signals: risks include reflection panics on unsupported shapes, silent non-strict nested-field tolerance, JSON number precision/truncation, missing `jsonschema` tags, and nil handling in slices. `schema_test.go` exercises error wording and common conversion paths.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/schema.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/schema_test.go -->
# sources/test-tools/syzkaller/pkg/aflow/schema_test.go

Purpose: verifies schema type validation and `convertFromMap` behavior for tool and non-tool error modes.

Important APIs/functions: `TestSchema`, `TestConvertFromMap`, and helper `testConvertFromMap`. The tests call `schemaFor` and `convertFromMap` with a broad set of struct shapes.

Control flow: `TestSchema` checks non-struct rejection, missing `jsonschema` tag errors, and successful tagged struct schema generation. `TestConvertFromMap` covers integer and uint conversion from JSON float64, strings, `json.RawMessage`, missing fields, wrong types, truncating floats, unused strict fields, `omitempty`, slices of structs and strings, nested structs, pointer numeric fields, slice item errors, nil slice entries, pointer slice nil allowance, and `time.Time` unmarshaling.

State and persistence: no persistent state. Each case creates input maps and expected typed outputs.

Dependencies and integration: imports `encoding/json`, `fmt`, `testing`, `time`, `jsonschema`, and testify. It locks down the conversion behavior consumed by actions, tools, MCP handlers, and LLM tool-call argument parsing.

Risks and test signals: the strongest signal is paired tool/non-tool error text, because tool mode must produce LLM-facing `BadCallError` messages while internal mode returns ordinary errors. Changes to Go reflection formatting or map ordering may require careful fixture updates.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/schema_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/template.go -->
# sources/test-tools/syzkaller/pkg/aflow/template.go

Purpose: validates and renders text templates used by aflow prompts, with support for crash-title predicates and JSON formatting.

Important APIs/functions: `formatTemplate`, `verifyTemplate`, `walkTemplate`, `parseTemplate`, `templateFuncs`, and `titleIs`. `templateFuncs` includes `titleIsUAF`, `titleIsKASANNullDeref`, `titleIsWarning`, and `jsonMarshal`.

Control flow: `verifyTemplate` parses with `missingkey=error`, walks the parse tree to collect root field names, verifies each used variable is provided, builds zero values for those variables, and executes the template once. `formatTemplate` reparses and executes against runtime state, panicking on errors that should have been caught during verification. `walkTemplate` handles common nodes: lists, if/range/action/pipe/command, fields, variables, chains, literals, identifiers, dot, and reports unsupported parse node types.

State and persistence: no persistence. Runtime input is the template string and state map.

Dependencies and integration: uses Go `text/template` and `parse`, `reflect`, `bytes`, `encoding/json`, `slices`, and syzkaller `pkg/report/crash`. It integrates with agent/action prompt validation and rendering.

Risks and test signals: risks include unsupported template node kinds, only top-level field tracking for chains, panic-on-render if verification was skipped, and function behavior tied to crash title classification. `template_test.go` verifies variable discovery and warning-title rendering.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/template.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/template_test.go -->
# sources/test-tools/syzkaller/pkg/aflow/template_test.go

Purpose: tests template variable discovery, validation errors, and custom template functions.

Important APIs/functions: `TestTemplate` drives `verifyTemplate` with text-only templates, conditionals, local variables, ranges, missing variables, builtin functions, chains, parenthesized chains, and comparisons. `TestTemplateRender` executes `parseTemplate` with crash-title predicate functions.

Control flow: each `TestTemplate` case supplies a template, available variable types, expected used roots, or an error. It asserts used variables with `ElementsMatch`, so order is irrelevant. Render testing checks that only `titleIsWarning` matches a warning title.

State and persistence: no persistence; all data is local maps and buffers.

Dependencies and integration: imports `bytes`, `fmt`, `maps`, `reflect`, `slices`, `testing`, and testify. It directly validates `template.go`, which is used by LLM prompt and instruction formatting.

Risks and test signals: good coverage exists for common parse nodes, but unsupported template constructs remain a risk because `walkTemplate` intentionally handles only a practical subset. The rendering test detects regressions in crash-title classification wiring.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/template_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/test_action.go -->
# sources/test-tools/syzkaller/pkg/aflow/test_action.go

Purpose: helper for unit-testing a single aflow `Action` without registering a full `Flow`.

Important APIs/functions: `TestAction` accepts an action, workdir, initial args, expected results, and expected error. It depends on the action implementing a private `testVerify` helper interface that returns verified state, expected results, and an output extraction function.

Control flow: creates a verification context, asks the action to verify/prepare test state, finalizes verification, builds a minimal `Context` with state, workdir, no-op event callback, and real-time stub, then executes the action. It compares either the error string or extracted outputs.

State and persistence: all state is in-memory except the caller-supplied workdir. `ctx.Close` is deferred to release context resources.

Dependencies and integration: uses `testing`, `time`, `trajectory`, and testify. It integrates with action implementations that expose test-only verification hooks.

Risks and test signals: the helper intentionally initializes only fields needed by current action tests, so actions requiring cache, context cancellation, or richer stubs need additional setup. Exact string comparison catches error regressions but can be brittle.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/test_action.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/test_tool.go -->
# sources/test-tools/syzkaller/pkg/aflow/test_tool.go

Purpose: helper utilities for testing aflow `Tool` implementations and fuzzing tool execution.

Important APIs/types/functions: `TestToolOption`, `testToolContext`, `TestTool`, `TestErrorPrefix`, `TestWorkdir`, and `FuzzTool`. `TestTool` requires tools to implement a private `testVerify` helper; `FuzzTool` requires `checkFuzzTypes`.

Control flow: `TestTool` builds and finalizes a verification context, checks the declaration path does not crash, applies optional context modifiers, executes the tool, validates exact or prefix error text, ensures expected tool errors are `badCallError`, and runs the result checker. `FuzzTool` converts fuzz input into state/args and executes against a minimal context.

State and persistence: test state lives in a minimal `Context`; workdir is optional via `TestWorkdir`. No persistent writes are done by the helper itself.

Dependencies and integration: imports `errors`, `strings`, `testing`, and testify. It integrates with all tool tests needing consistent verification/execution checks and bad-call semantics.

Risks and test signals: minimal context setup may hide dependencies until a tool needs cache/workdir/stubs. The bad-call assertion is a strong signal that user/LLM input validation remains distinct from infrastructure failures.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/test_tool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/test_util.go -->
# sources/test-tools/syzkaller/pkg/aflow/test_util.go

Purpose: provides `NewTestContext`, a small helper for internal aflow and tool unit tests that need a cache-backed context.

Important APIs/functions: `NewTestContext(t *testing.T) *Context` creates a temporary cache with `NewCache(t.TempDir(), 10000000)` and returns `&Context{cache: cache}`.

Control flow: the helper fails the test immediately if cache creation fails, then leaves other `Context` fields unset for the caller to populate as needed.

State and persistence: uses the test framework's temporary directory for cache storage. The cache is bounded by the hard-coded size parameter and is cleaned with the test tempdir lifecycle.

Dependencies and integration: imports `testing` and testify `require`. Integrates with tool/action tests that need real cache behavior but do not need full flow execution.

Risks and test signals: the returned context is intentionally partial; tests that require `Workdir`, cancellation, event callbacks, or stubs must set them explicitly. The helper centralizes cache setup so cache API changes affect fewer tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/test_util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestDoWhile.trajectory.json -->
# sources/test-tools/syzkaller/pkg/aflow/testdata/TestDoWhile.trajectory.json

Purpose: golden trajectory for `TestDoWhile`, recording a successful do-while repair loop that needs three iterations before the condition clears.

Important structure: 22 spans total: 2 flow spans, 2 loop spans, 6 iteration spans, and 12 action spans. Names include `test`, loop iterations `0`, `1`, `2`, `patch-generator`, and `patch-tester`.

Control flow: the flow starts, enters a loop, and records three iterations. The first two iterations produce `Patch: bad`; `patch-tester` returns empty `Diff` and `TestError: error`, so the loop continues. The third iteration produces `Patch: good`; `patch-tester` returns `Diff: diff` and empty `TestError`, causing loop exit.

State and persistence: this JSON is persistent golden state consumed by `runner_test.go`. It stores deterministic stub timestamps and serialized action results, not runtime cache data.

Dependencies and integration: generated from `loop_test.go` via `testFlow` and compared with `osutil.ReadJSON`. It exercises `DoWhile` span emission and output extraction.

Risks and test signals: any change to loop span nesting, action result fields, timestamp stubbing, or exit condition semantics will fail the golden comparison. Final flow result is `{"Diff":"diff"}`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestDoWhile.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestDoWhileMaxIters.trajectory.json -->
# sources/test-tools/syzkaller/pkg/aflow/testdata/TestDoWhileMaxIters.trajectory.json

Purpose: golden trajectory for the do-while max-iteration failure path.

Important structure: 16 spans total: 2 flow, 2 loop, 6 iteration, and 6 action spans. Names include `test`, loop iterations `0`, `1`, `2`, and action `nop`.

Control flow: each iteration runs `nop`, which returns `Error: failed`. Because the `While` variable remains non-empty, the loop continues until `MaxIterations: 3` is exhausted. The loop and flow finish with `DoWhile reached max iteration limit 3`.

State and persistence: persistent test fixture with deterministic times and serialized error fields. No external state is referenced.

Dependencies and integration: consumed by `TestDoWhileMaxIters` in `loop_test.go`, through `runner_test.go` golden comparison.

Risks and test signals: high signal for preserving error propagation from `DoWhile.loop` through loop and flow spans. It also detects accidental off-by-one changes in iteration naming or iteration count.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestDoWhileMaxIters.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestFlowConsts.trajectory.json -->
# sources/test-tools/syzkaller/pkg/aflow/testdata/TestFlowConsts.trajectory.json

Purpose: golden trajectory for a flow that consumes constant-provided input.

Important structure: 4 spans total: flow start/finish and `input-consumer` action start/finish.

Control flow: the action `input-consumer` executes successfully inside flow `test`; final flow result is an empty object. The short fixture verifies const injection without additional branching, loops, or LLM calls.

State and persistence: stores only deterministic span timing and empty final results. The constants themselves are visible through the action args during execution, but the final fixture records no durable application state.

Dependencies and integration: consumed by a flow const test elsewhere in the aflow package via `testFlow`.

Risks and test signals: detects regressions where consts are not available to action argument conversion, or where no-output actions stop producing an empty final result map.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestFlowConsts.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestForEach/Basic.trajectory.json -->
# sources/test-tools/syzkaller/pkg/aflow/testdata/TestForEach/Basic.trajectory.json

Purpose: golden trajectory for the basic `ForEach` list-processing test.

Important structure: 16 spans total: 2 flow, 2 loop, 6 iteration, and 6 action spans. Loop name is `ForEach`; iterations are `0`, `1`, and `2`; action is `process-item`.

Control flow: the flow enters a `ForEach` loop over `["a","b","c"]`. Each iteration injects the current `Item` and appends the uppercase value to `Result`, producing `["A","B","C"]`.

State and persistence: persistent golden JSON captures deterministic spans and per-action results. It does not persist temporary `Item`, which is deleted after loop execution.

Dependencies and integration: consumed by `TestForEach/Basic` in `loop_test.go`, and validates `ForEach.execute` span behavior and accumulator state.

Risks and test signals: catches regressions in item injection, accumulator zero-value initialization, iteration span names, temporary item cleanup side effects, and final output extraction.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestForEach/Basic.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestForEach/UnexportedOutput.trajectory.json -->
# sources/test-tools/syzkaller/pkg/aflow/testdata/TestForEach/UnexportedOutput.trajectory.json

Purpose: golden trajectory for a `ForEach` scenario involving an action output that is internal/unexported from the final flow output.

Important structure: 16 spans total: 2 flow, 2 loop, 4 iteration, and 8 action spans. Names include `ForEach`, iterations `0` and `1`, `process-item`, and `consume-hidden`.

Control flow: each of two iterations runs `process-item` and then `consume-hidden`. The final exported result is `{"Result":["A","B"]}`, while intermediate hidden output is consumed within the loop body rather than exported.

State and persistence: persistent golden file records action-level results and final exported outputs. It verifies loop body internal state can be passed between actions without appearing in final outputs.

Dependencies and integration: consumed by a `TestForEach/UnexportedOutput` subtest in the aflow suite.

Risks and test signals: detects changes in output-use verification, unexported/intermediate state handling, and loop body span nesting.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestForEach/UnexportedOutput.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/BoolFalse.trajectory.json -->
# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/BoolFalse.trajectory.json

Purpose: golden trajectory for an `If` action with a boolean false condition and no else branch.

Important structure: 4 spans total: flow start/finish and `If` action start/finish. Final result is `{"Done":""}`.

Control flow: `If` receives `Cond: false`, records only the wrapper action, and does not execute `if-body`.

State and persistence: persistent golden fixture containing deterministic timestamps and serialized `If` args.

Dependencies and integration: consumed by `If` tests through `testFlow`; validates false boolean truthiness and default empty output behavior.

Risks and test signals: catches regressions that execute the body on false, drop wrapper args, or omit zero-valued output fields.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/BoolFalse.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/BoolTrue.trajectory.json -->
# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/BoolTrue.trajectory.json

Purpose: golden trajectory for an `If` action with a boolean true condition.

Important structure: 6 spans total: flow start/finish, `If` action start/finish, and `if-body` action start/finish. Final result is `{"Done":"done"}`.

Control flow: `If` receives `Cond: true`, executes `if-body`, and then closes the wrapper action.

State and persistence: persistent golden data with deterministic timestamps, the boolean argument, and body result.

Dependencies and integration: validates `If` truthiness and nested action span emission under the runner harness.

Risks and test signals: catches regressions where condition args are not logged, true branch nesting changes, or body output stops propagating to flow outputs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/BoolTrue.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/DisjointOutputsFalse.trajectory.json -->
# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/DisjointOutputsFalse.trajectory.json

Purpose: golden trajectory for an `If` with disjoint outputs where the false branch runs.

Important structure: 6 spans total: flow, `If`, and `else` action start/finish pairs. Final result is `{"DoDone":"","ElseDone":"else"}`.

Control flow: the condition evaluates false, so the `else` branch executes and the `do` branch is skipped. The missing branch output is represented as its zero value.

State and persistence: persistent golden fixture records branch choice and final merged output shape.

Dependencies and integration: consumed by `If` tests that verify branch output reconciliation.

Risks and test signals: detects regressions in branch-disjoint output handling, zero-value filling for skipped branch outputs, and else branch span naming.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/DisjointOutputsFalse.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/DisjointOutputsTrue.trajectory.json -->
# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/DisjointOutputsTrue.trajectory.json

Purpose: golden trajectory for an `If` with disjoint outputs where the true branch runs.

Important structure: 6 spans total: flow, `If`, and `do` action start/finish pairs. Final result is `{"DoDone":"do","ElseDone":""}`.

Control flow: the true condition executes the `do` branch and skips `else`. The skipped branch's output remains a zero value while preserving the full output schema.

State and persistence: persistent golden data for branch output merge behavior.

Dependencies and integration: consumed by `If` tests and validates output extraction from branch-specific actions.

Risks and test signals: catches regressions in disjoint output verification, zero-value defaults, or branch span naming.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/DisjointOutputsTrue.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/ElseFalse.trajectory.json -->
# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/ElseFalse.trajectory.json

Purpose: golden trajectory for an `If` with an else branch where the condition is false.

Important structure: 6 spans total: flow, `If`, and `else-body` action start/finish pairs. Final result is `{"Done":"else"}`.

Control flow: false condition causes `else-body` to execute; `if-body` is not present in the span stream.

State and persistence: stores deterministic spans, condition args, and else result.

Dependencies and integration: consumed by `If` tests through the common runner.

Risks and test signals: detects regressions in false-branch dispatch, final result propagation, and wrapper span closure after else execution.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/ElseFalse.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/ElseTrue.trajectory.json -->
# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/ElseTrue.trajectory.json

Purpose: golden trajectory for an `If` with an else branch where the condition is true.

Important structure: 6 spans total: flow, `If`, and `if-body` action start/finish pairs. Final result is `{"Done":"done"}`.

Control flow: true condition executes `if-body` and skips `else-body`.

State and persistence: persistent fixture containing deterministic span timings and branch result.

Dependencies and integration: consumed by `If` tests and validates branch choice with an available else branch.

Risks and test signals: catches regressions where both branches execute, the wrong branch runs, or branch results fail to propagate.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/ElseTrue.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/False.trajectory.json -->
# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/False.trajectory.json

Purpose: minimal golden trajectory for a statically false/no-op conditional path.

Important structure: only 2 spans, flow start and flow finish. Final result is `{"Done":""}`.

Control flow: no `If` wrapper or body action appears, indicating the tested construction optimized or bypassed execution for this false case.

State and persistence: persistent golden fixture with only flow-level data.

Dependencies and integration: consumed by `If` tests to validate the simplest false condition path.

Risks and test signals: detects accidental introduction of wrapper/action spans for this no-op false path, or failure to preserve zero-valued output fields.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/False.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/IntFalse.trajectory.json -->
# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/IntFalse.trajectory.json

Purpose: golden trajectory for integer condition truthiness where zero is false.

Important structure: 4 spans total: flow and `If` start/finish pairs. Final result is `{"Done":""}`.

Control flow: the `If` action logs a zero integer condition, skips `if-body`, and finishes.

State and persistence: persistent fixture with deterministic times and args/results.

Dependencies and integration: consumed by `If` tests that exercise non-boolean condition coercion.

Risks and test signals: catches regressions in integer truthiness, zero-value output handling, and condition argument serialization.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/IntFalse.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/IntTrue.trajectory.json -->
# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/IntTrue.trajectory.json

Purpose: golden trajectory for integer condition truthiness where non-zero is true.

Important structure: 6 spans total: flow, `If`, and `if-body` start/finish pairs. Final result is `{"Done":"done"}`.

Control flow: non-zero integer condition executes the body and propagates its result.

State and persistence: persistent span/result fixture for the runner.

Dependencies and integration: validates condition coercion used by the aflow `If` action.

Risks and test signals: detects regressions in truthiness for numeric conditions or nested body span emission.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/IntTrue.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/SliceEmpty.trajectory.json -->
# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/SliceEmpty.trajectory.json

Purpose: golden trajectory for slice condition truthiness where an empty non-nil slice is false.

Important structure: 4 spans total: flow and `If` start/finish pairs. Final result is `{"Done":""}`.

Control flow: the `If` action records the condition and skips the body because the slice is empty.

State and persistence: persistent deterministic trajectory, with no durable state beyond JSON fixture data.

Dependencies and integration: consumed by `If` tests for slice truthiness.

Risks and test signals: catches changes that treat empty slices as true or alter zero-result preservation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/SliceEmpty.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/SliceNil.trajectory.json -->
# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/SliceNil.trajectory.json

Purpose: golden trajectory for slice condition truthiness where nil slice is false.

Important structure: 4 spans total: flow and `If` start/finish pairs. Final result is `{"Done":""}`.

Control flow: nil slice condition does not execute `if-body`.

State and persistence: persistent golden span fixture.

Dependencies and integration: consumed by `If` tests and complements `SliceEmpty` and `SliceTrue`.

Risks and test signals: detects regressions that distinguish nil and empty slices incorrectly for false-case branch selection.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/SliceNil.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/SliceTrue.trajectory.json -->
# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/SliceTrue.trajectory.json

Purpose: golden trajectory for slice condition truthiness where a non-empty slice is true.

Important structure: 6 spans total: flow, `If`, and `if-body` start/finish pairs. Final result is `{"Done":"done"}`.

Control flow: non-empty slice condition executes `if-body`.

State and persistence: persistent JSON fixture with deterministic span timing and result data.

Dependencies and integration: consumed by `If` tests for non-boolean condition support.

Risks and test signals: catches truthiness regressions for slices and body-output propagation changes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/SliceTrue.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/StringFalse.trajectory.json -->
# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/StringFalse.trajectory.json

Purpose: golden trajectory for string condition truthiness where an empty string is false.

Important structure: 4 spans total: flow and `If` start/finish pairs. Final result is `{"Done":""}`.

Control flow: empty string condition skips the body.

State and persistence: persistent golden fixture with deterministic timestamps.

Dependencies and integration: consumed by `If` tests and parallels integer/slice false cases.

Risks and test signals: catches regressions in string truthiness and zero-value final output behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/StringFalse.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/StringTrue.trajectory.json -->
# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/StringTrue.trajectory.json

Purpose: golden trajectory for string condition truthiness where a non-empty string is true.

Important structure: 6 spans total: flow, `If`, and `if-body` start/finish pairs. Final result is `{"Done":"done"}`.

Control flow: non-empty string condition executes the body and propagates `Done`.

State and persistence: persistent golden JSON for the runner harness.

Dependencies and integration: consumed by `If` tests for string condition support.

Risks and test signals: detects changes to string truthiness, branch execution, or span nesting.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/StringTrue.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/True.trajectory.json -->
# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/True.trajectory.json

Purpose: minimal golden trajectory for a statically true conditional path.

Important structure: 6 spans total: flow, `If`, and `if-body` start/finish pairs. Final result is `{"Done":"done"}`.

Control flow: the true condition executes the body once and closes the wrapper action.

State and persistence: persistent deterministic fixture.

Dependencies and integration: consumed by `If` tests through `testFlow`.

Risks and test signals: catches regressions in the basic true branch path, final result extraction, and body span naming.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/True.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMTool.llm.json -->
# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMTool.llm.json

Purpose: golden record of LLM requests emitted by `TestLLMTool`, including main-agent calls, nested sub-agent calls, function-call history, and config changes.

Important structure: JSON array of request records with `Model`, optional `Config`, and `Request`. The first request targets `model` with a tool declaration for `researcher`; nested requests target `sub-agent-model` with a tool declaration for `researcher-tool`. Repeated configs are omitted by the harness unless changed.

Control flow: the request history starts with the main prompt, then records the sub-agent prompt `What do you think?`, then the function-call/function-response turn for `researcher-tool`. Later records repeat the pattern for `But really?`, include additional subtool calls, and preserve the request chain around the simulated token overflow before final completion.

State and persistence: persistent golden fixture for serialized `genai.GenerateContentConfig` and content requests. It stores schemas, tool descriptions, system instructions, thinking config, and conversation turns.

Dependencies and integration: produced and consumed by `runner_test.go` for `TestLLMTool`; tied to `llm_tool_test.go`, schema generation, and GenAI request formatting.

Risks and test signals: highly sensitive to config serialization, tool schema generation, default instruction text, request history pruning, and function-call response formatting. It is the best signal for nested LLM tool API compatibility.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMTool.llm.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMTool.trajectory.json -->
# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMTool.trajectory.json

Purpose: golden trajectory for `TestLLMTool`, showing nested agent/tool execution and recovery from a model input-token overflow.

Important structure: 36 spans total: 2 flow, 6 agent, 18 llm, and 10 tool spans. Names include `test`, main agent `smarty`, sub-agent/tool `researcher`, and nested `researcher-tool`.

Control flow: the main agent starts and calls the `researcher` tool with `What do you think?`. That tool starts a sub-agent, which calls `researcher-tool` and returns `Nothing.`. The main agent then calls `researcher` again with `But really?`; the sub-agent calls its tool multiple times, records an API error for token overflow, continues, returns `Still nothing.`, and the main agent finally returns `YES`.

State and persistence: persistent golden span fixture with deterministic timestamps, prompts, instructions, args, results, and the serialized API error. Final flow result is `{"Reply":"YES"}`.

Dependencies and integration: consumed by `llm_tool_test.go` through `testFlow`; validates `LLMAgent`, `LLMTool`, nested tool execution, trajectory emission, and error propagation/continuation.

Risks and test signals: strong signal for span nesting, nested agent prompt/instruction formatting, tool result shape, and API error handling. It will fail on harmless but intentional changes to wording, ordering, or request loop behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMTool.trajectory.json -->
