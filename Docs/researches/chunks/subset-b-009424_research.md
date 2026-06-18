# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json lines 373629-392289

## Purpose

This chunk is part of the golden LLM request log for `TestLLMToolMaxIters` in `pkg/aflow`. The file records the exact `GenerateContent` requests emitted by the aflow test harness and is compared against freshly generated requests by `testFlow`. This range covers a mid-to-late slice of the sub-agent conversation history while the test drives an `LLMTool` through many repeated nested tool calls.

The important behavior under test is not JSON parsing itself; it is that an `LLMTool` can make repeated calls to its own function tool up to the framework's `maxLLMIterations` limit and then still return a final answer to the parent agent. The fixture captures the expanding request history that is sent back to the sub-agent model on each iteration.

## Chunk Structure

The selected lines begin in the middle of a recorded `sub-agent-model` request. At line 373629 the request is already inside the `Request` array and continues a long alternating sequence:

- user-role `functionCall` parts for `researcher-tool`
- user-role `functionResponse` parts for the same call ID and tool name
- monotonically increasing `args.Arg` values

Within this line range, full top-level request objects begin at source lines 374314, 378652, 383015, 387403, and 391816. Each of those objects has:

- `"Model": "sub-agent-model"`
- `"Request"` starting with a text prompt part: `"What do you think?"`
- a repeated history of `researcher-tool` calls and responses

The range shows the fixture's accumulation pattern. Around these boundaries the top-level JSON request entries correspond to sub-agent request indices in the 140s through 150s, where the request lengths increase by two content entries per iteration: one function-call content and one function-response content. For example, adjacent entries around indices 140-152 have request lengths 279, 281, 283, and so on.

## Important APIs, Types, and Functions

The fixture is generated and consumed through the test harness in `sources/test-tools/syzkaller/pkg/aflow/runner_test.go`:

- `testFlow[Inputs, Outputs]` registers the flow, executes it, captures `GenerateContent` requests, normalizes them through JSON marshal/unmarshal, and compares them to `testdata/<TestName>.llm.json`.
- The captured request type has `Model`, optional `Config`, and `Request []*genai.Content`.
- The stubbed `generateContent` callback appends every request before returning the next scripted reply from `llmReplies`.

The test scenario is defined in `sources/test-tools/syzkaller/pkg/aflow/llm_tool_test.go`:

- `TestLLMToolMaxIters` creates a parent `LLMAgent` with an `LLMTool` named `researcher`.
- The nested `LLMTool` uses model `sub-agent-model` and exposes a `NewFuncTool` named `researcher-tool`.
- The scripted replies first make the parent call `researcher`, then make the sub-agent call `researcher-tool` once for every `i` in `range maxLLMIterations`, passing `{"Arg": i}`.
- After the repeated tool calls, the sub-agent returns `"Nothing."` and the parent returns `"YES"`.

The runtime code that gives this fixture meaning is in:

- `LLMTool` in `llm_tool.go`, which wraps a nested `LLMAgent`, maps the parent tool argument `Question` into temporary state key `AFLOW_LLMTOOL_PROMPT`, executes the nested agent, and returns `{"Answer": reply}`.
- `NewFuncTool` in `func_tool.go`, which declares JSON schemas for tool args/results and converts maps into typed Go structs before calling the function.
- `LLMAgent.chat` in `llm_agent.go`, which initializes request history with the prompt, sends repeated `GenerateContent` calls, parses function calls, appends model output and tool responses to history, and stops after final reply or `maxLLMIterations`.
- `maxLLMIterations = 250`, also in `llm_agent.go`, which bounds normal chat iterations.

## Control Flow Represented By This Chunk

The selected lines represent repeated iterations inside the nested `LLMTool` agent:

1. The parent agent has already invoked `researcher` with question text `"What do you think?"`.
2. `LLMTool.execute` has stored that question in context state and called the nested agent.
3. The nested agent request history starts with the prompt `"What do you think?"`.
4. On each sub-agent LLM response, the scripted model emits a `functionCall` to `researcher-tool` with `Arg` equal to the current iteration number.
5. `agentSession.callTools` executes `researcher-tool`, records a span, and appends a `functionResponse` content entry to `a.req`.
6. The next `GenerateContent` request sends the entire accumulated prompt, tool-call, and tool-response history back to `sub-agent-model`.

This chunk captures steps 4-6 repeated many times. It begins with call history already around `Arg: 145` from a previous top-level request and later includes new top-level sub-agent requests that restart their serialized `Request` array at `Arg: 0` and extend to increasingly high arguments. Near the chunk end, a new top-level request has started and reaches `Arg: 18` within the selected lines; that request continues beyond this chunk.

## State and Persistence Behavior

The JSON fixture is persisted golden test data, not production state. Its persistence role is to detect behavioral changes in the shape, order, or contents of generated LLM requests.

Runtime state represented by the fixture includes:

- `agentSession.req`: the in-memory conversation history. The fixture serializes snapshots of this slice as each `GenerateContent` request is made.
- Temporary LLMTool state keys: `AFLOW_LLMTOOL_PROMPT` is used to render the sub-agent prompt, and `AFLOW_LLMTOOL_REPLY` receives the sub-agent final answer.
- Tool result state is effectively empty for `researcher-tool`, because the function returns `struct{}{}`. In the golden JSON this appears as `functionResponse` parts with only `id` and `name`, without a meaningful response payload.
- Test normalization state: `testFlow` round-trips captured requests through JSON to stabilize types and schema representation before comparison.

No cache objects are serialized in this fixture, but production/test execution routes LLM calls through `generateContentCached`, which wraps actual generation in `CacheObject`. In this test the stub context records requests before replies are returned.

## Dependencies and Integration Points

This chunk depends on several external and internal contracts:

- `google.golang.org/genai` content shapes: `Content`, `Part`, `FunctionCall`, and `FunctionResponse` determine the serialized keys seen here.
- aflow tool declarations and schemas: `LLMTool.declaration` exposes parent tool schema with `Question`; `funcTool.declaration` exposes `researcher-tool` args using `toolArgs.Arg`.
- `osutil.WriteJSON` and `osutil.ReadJSON` define golden file read/write formatting.
- `trajectory` spans are generated in parallel as `.trajectory.json`; this `.llm.json` fixture checks request content, while the trajectory fixture checks agent/tool span behavior.
- The `-update` test flag in `runner_test.go` can regenerate this file, so any implementation change in request construction will require coordinated golden updates.

## Risks and Edge Cases

The primary risk covered by this fixture is an off-by-one or premature termination in the nested LLM loop. Since `TestLLMToolMaxIters` scripts exactly `maxLLMIterations` nested tool calls, changes to the `for iter := 0; iter < maxLLMIterations || a.tryAnswerNow(...)` condition, final-reply handling, or `LLMTool` answer-now behavior could change whether the sub-agent returns `"Nothing."` or fails with `agent reached max iterations limit (250)`.

The fixture is also sensitive to request-history ordering. `agentSession.chat` appends the model response content first, then appends function responses from `callTools`. Reordering these entries, changing their role, or including empty response maps differently would alter this chunk.

Because the selected range is deep inside a huge golden file, boundary chunks can start or end mid-object. This chunk starts inside an existing request and ends inside another request. Merge/reconciliation logic must treat chunk research as source-line scoped rather than assuming every chunk begins on a valid JSON object boundary.

Repeated empty `functionResponse` entries are intentional here. A future change that serializes empty `Response` maps, omits empty function responses, or changes zero-value handling in `genai.FunctionResponse` would create large fixture churn and could hide a real behavioral change in tool-response propagation.

The test also provides a signal about context growth. This fixture shows uncompressed, expanding request histories for many iterations. If compression, sliding-window behavior, duplicate-call detection, or answer-now prompts become active for this test, the request shape would diverge substantially.

## Test Signals

The direct test signal is `TestLLMToolMaxIters`, which expects final output `{"Reply": "YES"}` and compares the recorded request list against `sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json`.

Within this chunk, strong invariants include:

- model remains `sub-agent-model` for each top-level request object in the range
- request prompt remains `"What do you think?"`
- tool name remains `researcher-tool`
- function call ID remains `id1`
- `Arg` values advance by one within each serialized request history
- each function call is followed by a matching function response
- adjacent top-level sub-agent request histories grow by one call/response pair

If these invariants change, the golden comparison in `testFlow` should fail and point to either an intentional request-format update or a regression in nested tool iteration handling.
