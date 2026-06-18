# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json lines 18725-37435

## Purpose

This chunk is a middle slice of the golden LLM request log for `TestLLMToolMaxIters` in `pkg/aflow`. The file is not production code; it is serialized testdata consumed by the `testFlow` harness in `runner_test.go`, which records every `GenerateContent` request and compares the run against `testdata/<TestName>.llm.json`.

The test exercises an `LLMTool` named `researcher`, implemented as a nested `LLMAgent`, whose own function tool is `researcher-tool`. The fixture validates that a sub-agent can perform a long sequence of tool calls up to `maxLLMIterations` without corrupting the parent agent conversation, the nested agent request history, or the generated function-call/function-response transcript.

## Chunk Contents

Lines 18725-37435 contain 18,711 lines of repeated Gemini request-history JSON for the nested `sub-agent-model`. The span starts in the middle of one recorded sub-agent request at `researcher-tool` argument `Arg: 21`, continues through `Arg: 37`, then begins later request snapshots that restart from `Arg: 0` and grow by one call/response pair at a time. Near the end of the chunk the active snapshot has reached `Arg: 34` and continues into the next chunk.

The repeated structure is:

- top-level request entry with `"Model": "sub-agent-model"`;
- `"Request"` array beginning with the prompt text `"What do you think?"`;
- alternating `functionCall` and `functionResponse` message parts;
- each call uses id `"id1"`, name `"researcher-tool"`, and args object containing integer `"Arg"`;
- each response uses id `"id1"` and name `"researcher-tool"` with no response payload in this fixture because the Go tool returns `struct{}{}`;
- all recorded contents use role `"user"`, matching how the test stub wraps `genai.Part` responses and how `callTools` appends tool responses.

The full golden file has 253 top-level request entries: one initial main-agent request, one initial nested-agent request, 250 nested-agent continuation requests, and one final main-agent continuation request. This chunk covers part of the large nested-agent continuation region where request history grows quadratically in file size because each new LLM request includes the full previous transcript.

## Important APIs, Types, and Functions

The fixture is generated from `llm_tool_test.go:TestLLMToolMaxIters`. That test builds a reply list where the main agent first calls the `researcher` LLM tool, then the nested sub-agent calls `researcher-tool` for every `i` in `range maxLLMIterations`, then the sub-agent returns `"Nothing."`, and the main agent returns `"YES"`.

Relevant implementation points:

- `LLMTool` in `llm_tool.go` exposes itself to the parent model as a function declaration with `llmToolArgs{Question string}` and `llmToolResults{Answer string}` schemas.
- `LLMTool.execute` converts the parent tool args, stores the question in `ctx.state[AFLOW_LLMTOOL_PROMPT]`, runs an internal `LLMAgent`, reads `ctx.state[AFLOW_LLMTOOL_REPLY]`, deletes the temporary state, and returns `{"Answer": reply}` to the parent model.
- `LLMTool.verify` materializes the nested `LLMAgent` with `Reply: AFLOW_LLMTOOL_REPLY` and `Prompt: "{{.AFLOW_LLMTOOL_PROMPT}}"`.
- `LLMAgent.chat` in `llm_agent.go` drives the conversation loop. It starts with a single prompt content, repeatedly calls `generateContent`, parses any function calls, appends model content, executes tools, and appends function responses for the next request.
- `maxLLMIterations` is 250. The loop condition is intentionally special for LLM tools: after the normal iteration limit, `tryAnswerNow` can append an answer-now instruction and disable function calling for one extra attempt. This test supplies exactly 250 nested tool-call replies followed by a text reply, so it exercises the boundary behavior.
- `agentSession.callTools` executes requested tools, records a `trajectory.SpanTool`, appends `genai.Part{FunctionResponse: ...}` to the request history, and emits duplicate-call warnings only when duplicate detection says the same call is repeating too much.
- `runner_test.go:testFlow` stores the LLM request log as JSON after a marshal/unmarshal normalization pass, and omits repeated configs unless the config changes from the previous request.

## Control Flow Represented by This Chunk

The parent `LLMAgent` calls the `researcher` tool. That tool runs a nested `LLMAgent` with prompt `"What do you think?"`. For each nested model response that contains a `researcher-tool` function call:

1. `parseResponse` extracts the `genai.FunctionCall`.
2. The model content containing that function call is appended to the nested request history.
3. `callTools` invokes the Go `NewFuncTool("researcher-tool", ...)` callback.
4. The empty struct result is serialized as an empty function response and appended to the next request.
5. The next `GenerateContent` call sends the full accumulated request history back to `sub-agent-model`.

This chunk is the serialized evidence for steps 2-5 over many iterations. The repeated reset to `Arg: 0` in later top-level entries is expected: each top-level JSON object is a fresh snapshot of the full request sent at that iteration, not a delta.

## State and Persistence Behavior

The fixture itself is persistent golden testdata. It is only regenerated when tests are run with the `-update` flag through `testFlow`, which writes `TestLLMToolMaxIters.llm.json` and the matching trajectory JSON.

Runtime state involved in the scenario is transient:

- the parent tool call passes `"Question": "What do you think?"`;
- `LLMTool.execute` stores that question under `AFLOW_LLMTOOL_PROMPT`;
- the nested agent stores its final text under `AFLOW_LLMTOOL_REPLY`;
- the tool prompt and reply keys are deleted after use so the parent state is not polluted;
- the nested request history lives in `agentSession.req` and is replayed into every `GenerateContent` request;
- `generateContentCached` may cache LLM calls under the `"llm"` cache namespace in real execution, keyed by model, config hash, request hash, candidate, and retry index.

The JSON chunk also captures the request-history persistence contract: every function call and every function response remains in the conversation sent to the model until an explicit compression or sliding-window feature changes history. This specific test path does not show compression or summary messages.

## Dependencies and Integration Points

The JSON schema mirrors `google.golang.org/genai` types, especially `GenerateContentConfig`, `Content`, `Part`, `FunctionCall`, and `FunctionResponse`.

Important local dependencies are:

- `runner_test.go` for golden request recording and comparison;
- `llm_tool_test.go` for the `TestLLMToolMaxIters` scenario and reply sequence;
- `llm_tool.go` for parent-tool-to-sub-agent bridging;
- `llm_agent.go` for iteration limits, request history accumulation, function-call parsing, and tool response insertion;
- `func_tool.go` and schema helpers for `NewFuncTool` declarations and typed argument conversion;
- trajectory recording, because the same test also compares `TestLLMToolMaxIters.trajectory.json`.

## Risks and Edge Cases

This fixture is intentionally very large because each request snapshot includes all prior nested tool calls. Small behavioral changes in request-history ordering, role assignment, empty tool-result serialization, config elision, or function-call id preservation can rewrite a large part of the golden file.

The max-iteration boundary is subtle. If `LLMAgent.chat` changes from allowing the `tryAnswerNow` extra attempt after `maxLLMIterations`, this test may either fail early with `agent reached max iterations limit (250)` or stop recording the final nested text reply. Conversely, raising `maxLLMIterations` would substantially increase fixture size.

The repeated calls use the same tool name and id but different `Arg` values. Duplicate-call detection must consider arguments, not only tool names, or this scenario would incorrectly inject duplicate warnings or fail before reaching the intended limit.

Because `researcher-tool` returns an empty struct, the golden responses have no meaningful payload. A change in JSON marshaling of empty structs, nil maps, or function response bodies could alter many entries without changing the high-level workflow result.

## Test Signals

The primary test signal is `go test` for `pkg/aflow`, specifically `TestLLMToolMaxIters`. Passing means the generated request log still matches this golden file and the workflow result remains `{"Reply": "YES"}`.

Useful invariants visible in this chunk:

- each nested continuation request includes prompt `"What do you think?"`;
- `functionCall` and `functionResponse` entries alternate;
- calls use `researcher-tool` with monotonically increasing `Arg` values within a single request snapshot;
- response entries preserve id `"id1"` and name `"researcher-tool"`;
- no duplicate-call warning text appears in this chunk;
- no `Config` field appears in these repeated entries because `runner_test.go` only stores the config when it changes.

These invariants make the chunk a regression detector for nested LLM tool history accumulation at the maximum iteration boundary.
