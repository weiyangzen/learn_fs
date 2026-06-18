# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json lines 205638-224309

Chunk id: `subset-b-009415`

## Scope

This chunk covers one oversized-file slice of the golden LLM request transcript for `TestLLMToolMaxIters`. The source file is JSON testdata consumed by `sources/test-tools/syzkaller/pkg/aflow/runner_test.go`, not executable code. The complete fixture has 787,904 lines; this chunk spans lines 205638-224309 and contains 18,672 lines from the middle of the generated request history.

The visible data is a repeated sequence of `sub-agent-model` requests. Each request begins with the prompt text `What do you think?` and then contains alternating `functionCall` and `functionResponse` content parts for the nested tool named `researcher-tool`. The calls all use id `id1` and integer argument objects shaped as `{"Arg": N}`.

## Purpose

The chunk preserves the exact wire-level request history expected while testing that an `LLMTool` sub-agent can keep invoking its own tool up to the configured maximum iteration behavior. The corresponding Go test constructs a parent `LLMAgent` with an `LLMTool` named `researcher`; that sub-agent exposes a regular `NewFuncTool` named `researcher-tool`. The generated golden file lets the harness compare every recorded request against stable JSON, catching regressions in conversation ordering, tool schema serialization, tool response insertion, and long-running sub-agent loop behavior.

This slice specifically exercises the growth pattern of the sub-agent request transcript. The chunk starts mid-request at argument `Arg: 26`, continues through `Arg: 127`, then includes several later `sub-agent-model` request objects that restart at `Arg: 0` and replay progressively longer histories. Inside this chunk, counters show 745 visible `functionCall` markers, 744 `functionResponse` markers, 744 `Arg` fields, five `Model: "sub-agent-model"` request headers, and five prompt entries. The one-call difference is expected for a chunk boundary: the slice begins and ends inside larger JSON structures rather than at whole-file semantic boundaries.

## Important JSON APIs and Schema Fields

The fixture records the test harness `llmRequest` shape:

- `Model`: the model name used for a `GenerateContent` call. In this chunk the visible model is `sub-agent-model`.
- `Request`: ordered `genai.Content` history sent to the model.
- `parts`: ordered message parts. The chunk uses text parts, function-call parts, and function-response parts.
- `role`: serialized content role. The visible entries use `user`, matching how the test stub wraps synthetic model responses and appended tool outputs.
- `functionCall`: a serialized Gemini function call with `id`, `name`, and `args`.
- `functionResponse`: the paired tool response with `id` and `name`; the nested test tool returns an empty struct, so there is no payload body in these response objects.
- `Arg`: integer argument passed to `researcher-tool`; this comes from the test-local `toolArgs` struct with JSON schema metadata.

The relevant tool declarations are outside this chunk but are visible earlier in the same file. `researcher-tool` has `parametersJsonSchema` with one required integer property `Arg` and an empty-object response schema. The parent-facing `researcher` tool accepts `Question` and returns `Answer`.

## Control Flow Represented

The control flow encoded by the chunk is:

1. The sub-agent request starts with text prompt `What do you think?`, supplied by `LLMTool.execute` through the temporary `AFLOW_LLMTOOL_PROMPT` state entry.
2. The model requests a `researcher-tool` call with `id: "id1"` and argument `Arg: N`.
3. The AFLOW runner appends the model function-call content to the request history.
4. The runner executes the Go `NewFuncTool` callback, which returns `struct{}{}` and no error.
5. The runner appends a matching `functionResponse` content part with the same id and tool name.
6. The next model request includes the original prompt plus the complete accumulated function-call/function-response history.
7. The sequence repeats until the sub-agent finally emits text later in the complete fixture.

Within lines 205638-224309, the visible segment boundaries show repeated replay rather than isolated calls:

- A partial request continues `Arg` values 26-127.
- The next full visible request replays `Arg` values 0-128.
- Later visible requests replay 0-129, 0-130, 0-131, and then a partial 0-119 before the chunk ends.

This pattern matches `agentSession.chat`, which appends each model response and each tool response to `a.req` before calling the model again. It also matches `TestLLMToolMaxIters`, where replies are constructed by appending one `researcher-tool` function call for each `i` in `range maxLLMIterations`; the constant is defined as 250 in `llm_agent.go`.

## State and Persistence Behavior

This JSON file is persisted golden testdata. It is not runtime state, but it captures runtime state transitions in serialized form:

- Conversation state is represented by an ever-growing `Request` array. Every later request repeats earlier prompt, function-call, and function-response content.
- Tool-call correlation state is represented by the stable id `id1`; each function response mirrors the preceding call id and `researcher-tool` name.
- Sub-agent prompt state is represented as the repeated text `What do you think?`, derived from the parent `researcher` call's `Question`.
- Tool return state is intentionally empty because the nested tool returns an empty struct. The presence of `functionResponse` rather than response data is the signal that the tool completed.
- Golden persistence is handled by `runner_test.go`: test execution marshals collected requests through JSON, optionally rewrites the file under `-update`, and otherwise reads this file back and compares it with `require.Equal`.

The chunk has no caches, locks, external persistence, or mutable configuration of its own. Its integrity matters because even formatting-equivalent semantic changes can still alter golden JSON ordering or field presence.

## Dependencies and Integration Points

Primary integration points inferred from the fixture and adjacent tests:

- `sources/test-tools/syzkaller/pkg/aflow/runner_test.go` defines the snapshot harness, records `GenerateContent` requests, and compares them against `testdata/TestLLMToolMaxIters.llm.json`.
- `sources/test-tools/syzkaller/pkg/aflow/llm_tool_test.go` defines `TestLLMToolMaxIters`, constructs the repeated `researcher-tool` calls, and expects the final parent output `Reply: "YES"`.
- `sources/test-tools/syzkaller/pkg/aflow/llm_tool.go` defines `LLMTool`, its parent-facing function declaration, and the temporary state keys used to pass the question into the nested `LLMAgent` and read back the answer.
- `sources/test-tools/syzkaller/pkg/aflow/llm_agent.go` owns the chat loop, `maxLLMIterations`, request-history append behavior, tool execution path, and special handling around final-answer forcing.
- `google.golang.org/genai` supplies the serialized content, part, function call, function response, and generate-content config structures.
- `github.com/google/syzkaller/pkg/osutil` provides JSON read/write and deep-copy behavior used by the test harness.

The chunk is therefore an integration snapshot between the AFLOW action framework and the GenAI request schema, especially for nested agent tools.

## Risks and Edge Cases

- The fixture is extremely large because each request stores the full accumulated history. Small changes in max iteration limits, summarization, context sliding, role assignment, or tool response shape can produce large diffs.
- This chunk begins and ends inside JSON request structures. Any chunk-level review must avoid assuming the first or last visible object is complete.
- Function responses are empty objects by design. A serializer change that starts emitting explicit empty response bodies could break the golden file even if tool behavior remains logically equivalent.
- All visible `researcher-tool` calls use the same id `id1`. If production code changes to unique ids per call, this testdata will catch the serialized contract change.
- The visible role is consistently `user`. Changes in GenAI SDK role defaults or AFLOW wrapping logic may alter this field and invalidate snapshots.
- Because the test compares complete request histories, changes to compression or context-window handling in `agentSession.chat` could be noisy. The chunk is a useful signal for whether history replay remains stable before final answer forcing.
- The source is generated testdata; manual edits are error-prone. Regeneration through the test harness with `-update` is the safer route when intentional behavior changes occur.

## Test Signals

This chunk contributes to the `TestLLMToolMaxIters` golden request assertion. Passing tests indicate:

- The parent agent exposes the nested `researcher` LLM tool with the expected schema.
- The sub-agent receives the expected prompt and `sub-agent-model` request configuration.
- Tool-call history is appended in call/response order across many iterations.
- The nested `researcher-tool` callback can be invoked repeatedly without corrupting request history.
- The loop reaches the max-iteration stress path defined by `maxLLMIterations` and still allows the overall flow to produce `Reply: "YES"` later in the full fixture.

Useful focused verification commands are:

```sh
go test ./sources/test-tools/syzkaller/pkg/aflow -run TestLLMToolMaxIters
```

and, when intentionally updating golden files:

```sh
go test ./sources/test-tools/syzkaller/pkg/aflow -run TestLLMToolMaxIters -update
```

No test command was run for this chunk research pass; the work item only required reading the mapped source range and writing the chunk research artifact.
