# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json lines 317647-336305

## Scope And Purpose

This chunk is a non-standalone slice of the oversized golden LLM request fixture for `TestLLMToolMaxIters`. The source is serialized JSON test data, not executable implementation code. It records `GenerateContent` requests captured by the aflow test harness while a parent `LLMAgent` invokes an `LLMTool` sub-agent and that sub-agent repeatedly calls its own function tool.

The assigned line range starts inside an existing sub-agent request history at the visible `Arg: 57` call and ends inside a later request at the visible `Arg: 160` call. Within this window there are 4 visible `Model: "sub-agent-model"` request starts, no `Config` blocks, 744 complete `functionCall` entries, 744 complete `functionResponse` entries, and 745 visible `Arg` fields because the first `Arg` is exposed at the chunk boundary without its enclosing `functionCall` line. Visible argument values span `0` through `161`, with repeated values caused by consecutive request snapshots replaying accumulated history.

## Fixture Structure In This Chunk

The complete request objects visible in this chunk all target `sub-agent-model`. Each request is an accumulated nested-agent chat history with this repeated shape:

- an initial user text prompt, `What do you think?`;
- a user-role `functionCall` part for `researcher-tool`;
- call id `id1`;
- integer argument `args.Arg`;
- a following user-role `functionResponse` part with matching id and name;
- no explicit response payload, matching the nested Go tool returning `struct{}{}`.

The four visible request starts are at lines 320195, 324208, 328246, and 332309. They are separate model requests, not duplicate copies of a single request. Each later request includes the full prior prompt/call/response history and appends one additional tool turn before being sent back to the stubbed model.

Because the chunk boundaries cut through JSON objects, the opening and closing fragments should be interpreted with adjacent chunks. The opening fragment is the tail of a previous request that already reached `Arg: 56`; this chunk begins with the next visible call at `Arg: 57`. The closing fragment shows a later request after `Arg: 159` has received a matching response and `Arg: 160` has begun.

## Producer Test And Important APIs

The producer is `TestLLMToolMaxIters` in `sources/test-tools/syzkaller/pkg/aflow/llm_tool_test.go`. The test builds a scripted LLM reply sequence where the parent agent first calls the `researcher` LLM tool, then the sub-agent calls `researcher-tool` once for every value in `range maxLLMIterations`, and finally the sub-agent returns `Nothing.` before the parent returns `YES`.

The fixture is consumed by `testFlow` in `sources/test-tools/syzkaller/pkg/aflow/runner_test.go`. That helper stubs `generateContent`, records each request as `{Model, Config, Request}`, omits repeated configs unless they changed from the previous request, round-trips through JSON for normalization, and compares the result to `testdata/TestLLMToolMaxIters.llm.json`.

Key aflow APIs represented here include:

- `LLMAgent.config`, which builds the GenAI config, system instruction, prompt, tool declarations, and tool map;
- `agentSession.chat`, which owns the iterative model/tool loop and enforces `maxLLMIterations = 250`;
- `LLMAgent.parseResponse`, which separates text, thoughts, and function calls from the model response;
- `agentSession.callTools`, which executes `researcher-tool` and appends matching `FunctionResponse` parts to the next request;
- `NewFuncTool`, which defines the nested typed tool with argument struct field `Arg int`.

## Control Flow Represented

This chunk represents the long middle of the nested-agent tool loop. The parent-facing `researcher` tool has already been invoked before this line range. The sub-agent is repeatedly sent the same accumulated conversation history, the model asks for one more `researcher-tool` call, aflow executes the local function tool, and the tool response becomes part of the next request.

The control-flow cycle encoded by each call/response pair is:

1. `agentSession.chat` sends the current `Request` to `sub-agent-model`.
2. The stubbed model reply contains a `FunctionCall` for `researcher-tool`.
3. `parseResponse` returns that call to the chat loop.
4. `callTools` executes the local Go callback with the integer `Arg`.
5. The empty `struct{}{}` result is serialized as a `functionResponse` envelope with id/name only.
6. The expanded request history is sent on the next iteration.

The request starts in this chunk correspond to later iterations whose histories end around `Arg: 157`, `Arg: 158`, `Arg: 159`, and then a partial history reaching `Arg: 160` before the chunk ends. The values reset to `0` at each new request because every request snapshot contains the complete nested-agent history from the beginning of that sub-agent conversation.

## State And Persistence Behavior

The runtime state represented by this fixture is transient, but the JSON file persists the expected request transcript for regression testing.

Important state behind this slice includes:

- `agentSession.req`, the growing request-history slice serialized into every visible `Request`;
- `agentSession.toolHistory`, used by duplicate-call detection while allowing this test's distinct `Arg` values to proceed;
- `ctx.state` entries used by `LLMTool` to pass the parent question into the nested agent and later return the nested reply;
- the `requests []llmRequest` golden log in `runner_test.go`, which stores model name, optional config, and cloned request content.

No durable cache, database, or external side effect is encoded by the repeated `researcher-tool` calls in this chunk. The nested tool callback returns an empty struct and does not mutate state. The durable signal is the exact shape of request-history accumulation, role assignment, call ids, tool names, and empty response serialization.

## Dependencies And Integration Points

The JSON shape follows `google.golang.org/genai` data structures: `GenerateContentConfig`, `Content`, `Part`, `FunctionCall`, and `FunctionResponse`. It is also sensitive to aflow schema and map-conversion behavior because typed Go tool arguments and results become JSON request/response parts.

Integration points covered by this chunk are:

- nested `LLMAgent` execution through `LLMTool`;
- GenAI function-calling request serialization;
- function tool execution for `researcher-tool`;
- test harness config de-duplication, shown by absent `Config` blocks in these repeated sub-agent requests;
- golden request comparison in `runner_test.go`;
- trajectory generation indirectly, because each model request and each tool call also emits spans in `TestLLMToolMaxIters.trajectory.json`.

## Risks And Maintenance Notes

The main risk is fixture size and brittleness. This test intentionally records full accumulated histories for a long max-iteration scenario, so a small change to request append order, role names, function response payload omission, or JSON normalization can create large golden-file churn.

This slice is also easy to misread because it begins and ends mid-object. Chunk-level tooling must not require standalone JSON validity, and file-level reconciliation should use adjacent chunks to recover the parent request, nested tool schema/config, and final text replies.

Request growth is a real behavioral concern outside the test. The same full-history pattern can approach model input limits in real LLMTool runs; `agentSession.chat` has overflow and compression handling elsewhere, but this fixture primarily validates max-iteration request accumulation rather than compression.

Duplicate-call handling is another maintenance sensitivity. The repeated tool name is intentional here, and calls remain distinct because `Arg` changes. A future duplicate detector that keys only on tool name would break this scenario.

## Test Signals

Strong regression signals visible in this chunk are:

- every complete visible `functionCall` has an immediately matching `functionResponse` for `id1` and `researcher-tool`;
- visible request snapshots restart from `Arg: 0` after each new `sub-agent-model` request and grow by one tool turn per iteration;
- no repeated `Config` appears, confirming the runner stores config only when it changes;
- all visible function-call and function-response content items use role `user`;
- empty tool results remain omitted from the serialized `functionResponse` body;
- the sub-agent loop continues well past `Arg: 150`, exercising the high-iteration path toward the `maxLLMIterations` boundary.

The final `Nothing.` and `YES` replies are outside this chunk. This range therefore validates the long middle of nested tool-call persistence, not the terminal handoff back to the parent agent.
