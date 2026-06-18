# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json lines 429606-448261

## Scope

This chunk covers lines 429606-448261 of `sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json`. The source is a golden JSON fixture for `pkg/aflow`, not executable code. It stores serialized `genai.GenerateContent` request snapshots captured while `TestLLMToolMaxIters` drives an `LLMTool` named `researcher` whose nested agent repeatedly calls `researcher-tool`.

The requested range is an interior slice of the complete JSON file. It starts inside a sub-agent request-history object at a visible `researcher-tool` call with `Arg: 63`. It then includes complete top-level request objects beginning at lines 432658, 437321, 442009, and 446722, all for `"Model": "sub-agent-model"`. The chunk ends at line 448261 inside the next `functionCall` object, after the call id has appeared but before the `args` block and `Arg: 61` line. The range is therefore not standalone JSON and must be interpreted as part of the full fixture.

Within this exact line window there are 745 `functionCall` markers, 744 `functionResponse` markers, 744 visible `Arg` fields, 4 `"Model"` entries, 4 `"Request"` entries, and 4 visible prompt entries for `"What do you think?"`. The extra call marker is the unfinished call at the closing boundary.

The visible argument runs are:

- `63..184`, completing a request object that began before the chunk.
- `0..185`, a complete visible sub-agent request-history object.
- `0..186`, another complete visible sub-agent request-history object.
- `0..187`, another complete visible sub-agent request-history object.
- `0..60`, the beginning of the next request-history object, with the `Arg: 61` call continuing just after the chunk.

## Purpose

`TestLLMToolMaxIters.llm.json` persists the exact LLM request transcript expected by `llm_tool_test.go:TestLLMToolMaxIters`. The associated test builds a parent `LLMAgent` whose first mocked model response calls the `researcher` LLM-backed tool with question `"What do you think?"`. That tool runs a nested `LLMAgent` on `"sub-agent-model"` and gives it a simple function tool named `researcher-tool`.

The test scripts the nested model to call `researcher-tool` once for every `i` in `range maxLLMIterations`, passing `{ "Arg": i }`, then return text `"Nothing."`. The parent model finally returns `"YES"`. This chunk documents late-middle request snapshots from that nested loop, where the important behavior is the growing request history: every later outbound request repeats the prompt and all prior function-call/function-response pairs before adding the next call.

## Important APIs, Types, And Data Shape

The JSON records map to `google.golang.org/genai` request structures captured by the aflow test harness:

- `Model`: the model name sent to the generation layer, here `"sub-agent-model"` for every visible top-level record.
- `Request`: the accumulated `[]*genai.Content` conversation history sent to `generateContent`.
- `parts[].text`: the original nested prompt, `"What do you think?"`.
- `parts[].functionCall`: a model-requested call to `researcher-tool`, with `id: "id1"` and integer argument `Arg`.
- `parts[].functionResponse`: the framework's reply after executing `researcher-tool`, also using `id: "id1"` and `name: "researcher-tool"`.

The Go constructs behind the fixture are:

- `LLMTool` in `llm_tool.go`, which exposes a nested `LLMAgent` as a parent-agent function tool.
- `llmToolArgs` and `llmToolResults`, which define the parent-facing `Question` and `Answer` schema for `researcher`.
- `LLMAgent` and `agentSession.chat` in `llm_agent.go`, which maintain `a.req`, parse model replies, call tools, append tool responses, and enforce `maxLLMIterations`.
- `NewFuncTool` in the test setup, which adapts the Go callback for `researcher-tool`; the callback returns `struct{}{}`, so responses serialize without a payload body in this chunk.
- `genai.Content`, `genai.Part`, `genai.FunctionCall`, and `genai.FunctionResponse`, whose field names determine the golden JSON shape.

No `Config` or tool declaration appears in this slice. Those are present earlier in the full fixture and are omitted from these repeated records because the test harness only records changed config values.

## Control Flow Represented

The represented control flow is an unrolled portion of the nested agent chat loop:

1. The parent agent has already called the `researcher` LLM tool.
2. `LLMTool.execute` has converted the parent call args, stored the question in context state under `AFLOW_LLMTOOL_PROMPT`, and invoked its internal agent.
3. The nested agent sends `"What do you think?"` plus accumulated history to `"sub-agent-model"`.
4. The scripted nested model emits one `functionCall` to `researcher-tool` for the next `Arg` value.
5. `agentSession.chat` appends that model content to the request history.
6. `agentSession.callTools` executes the Go `researcher-tool` callback and appends a matching `functionResponse`.
7. The next iteration sends the full expanded history back to the model.

This chunk sits around sub-agent request histories that end at `Arg` 184, 185, 186, and 187, then begins the next request through `Arg: 60`. The repeated restart at `Arg: 0` in each visible top-level request is expected because each JSON record is a full request snapshot, not a delta.

`maxLLMIterations` is 250 in `llm_agent.go`. The fixture's many repeated tool calls are the oracle that the nested LLM tool can consume the full allowed iteration budget and then still return a final answer instead of failing early with the max-iteration error.

## State And Persistence Behavior

The durable state is the golden fixture itself. `runner_test.go:testFlow` captures generated requests, normalizes them through JSON, and compares them with `testdata/TestLLMToolMaxIters.llm.json`; the file is rewritten only when the test suite is run in update mode.

Runtime state represented in this chunk is primarily `agentSession.req`:

- The first content item remains the prompt `"What do you think?"`.
- Each model function call is retained as a user-role content item.
- Each tool result is retained as a following user-role `functionResponse`.
- The history grows by one call/response pair per successful nested tool iteration.
- Empty tool results remain represented by the presence of a `functionResponse`, even though no response object is visible.

`LLMTool` also uses `ctx.state` keys `AFLOW_LLMTOOL_PROMPT` and `AFLOW_LLMTOOL_REPLY` for handoff between the parent tool call and nested agent reply. Those keys are implementation state and are not serialized directly in this chunk.

## Dependencies And Integration Points

This chunk integrates with these source-tree components:

- `sources/test-tools/syzkaller/pkg/aflow/llm_tool_test.go`: defines `TestLLMToolMaxIters`, constructs the parent agent, the `researcher` `LLMTool`, the nested `researcher-tool`, and the scripted replies.
- `sources/test-tools/syzkaller/pkg/aflow/llm_tool.go`: implements `LLMTool.declaration`, `LLMTool.execute`, and `LLMTool.verify`.
- `sources/test-tools/syzkaller/pkg/aflow/llm_agent.go`: defines `maxLLMIterations = 250`, the chat loop, request-history append behavior, tool-call processing, final reply validation, and the max-iteration failure path.
- `sources/test-tools/syzkaller/pkg/aflow/runner_test.go`: records model requests and performs golden-file comparison for `.llm.json` fixtures.
- `sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.trajectory.json`: companion golden data for span-level execution of the same scenario.
- `google.golang.org/genai`: external SDK types whose JSON representation is pinned here.

## Risks And Edge Cases

- The selected lines are not a complete JSON document. The range starts inside one request object and ends inside an unfinished `functionCall`.
- The closing boundary produces one more `functionCall` marker than visible `Arg` or `functionResponse` entries. A chunk-local checker should not treat that as a missing response in the full fixture.
- Counting `Arg` values in this chunk does not equal unique runtime tool executions, because each request snapshot repeats earlier history.
- The call id `"id1"` is intentionally reused by the scripted mock replies. Global uniqueness of call ids is not an invariant for this test.
- All visible calls and responses have role `"user"` because of how the test harness serializes scripted content. Changing role assignment would create large golden diffs.
- Empty `functionResponse` bodies are intentional because the test tool returns `struct{}{}`.
- Any change to `maxLLMIterations`, request-history retention, function response serialization, Gemini SDK field names, or `LLMTool` prompt/reply state handling would cascade across this large fixture.

## Test Signals

The main validation signal is `TestLLMToolMaxIters`: generated request snapshots must match this `.llm.json` file, the final workflow output must be `{ "Reply": "YES" }`, and the companion trajectory fixture should continue to show nested `researcher-tool` spans.

Useful invariants in this chunk are:

- Visible top-level request records use `"Model": "sub-agent-model"`.
- Each complete visible request begins with prompt text `"What do you think?"`.
- Tool calls use `name: "researcher-tool"` and `id: "id1"`.
- Within each complete request snapshot, `Arg` values increase monotonically from `0` to the current terminal argument.
- Completed visible function calls are followed by matching `functionResponse` parts.
- Adjacent complete request snapshots grow by one additional call/response pair.

This chunk's regression value is request-transcript fidelity for the `LLMAgent`/`LLMTool` max-iteration scenario, not standalone executable behavior.
