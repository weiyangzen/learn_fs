# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json lines 504226-522881

## Scope

This chunk is a 262 KiB interior slice of the golden LLM request transcript for `TestLLMToolMaxIters`. The file is JSON testdata rather than executable Go code, and this range is not independently parseable JSON because it starts inside a `Request` array entry and ends inside the next request's `functionCall` object. Its research value is as one ordered shard of the larger fixture that the aflow test harness compares against captured model requests.

The visible data records repeated nested-agent requests to `"sub-agent-model"` while an `LLMTool` named `researcher` runs its own `LLMAgent` and repeatedly invokes a function tool named `researcher-tool`. This slice finishes one request-history snapshot, contains three complete subsequent snapshots, and begins a fifth snapshot.

## Purpose

`TestLLMToolMaxIters` exercises the maximum-iteration behavior of an LLM-backed tool. The parent agent receives a synthetic model reply that calls the `researcher` LLM tool with `Question: "What do you think?"`. The sub-agent then receives synthetic replies that call `researcher-tool` once per model round for `range maxLLMIterations`, where `maxLLMIterations` is 250. After those tool calls, the sub-agent returns `"Nothing."`, then the parent returns `"YES"`.

This chunk validates that the nested agent preserves and resends the accumulated conversation history late in that tool-call loop. Each new `"sub-agent-model"` request snapshot starts with the prompt text `"What do you think?"`, then replays all prior `researcher-tool` `functionCall`/`functionResponse` pairs from `Arg: 0` upward. The repeated snapshots are intentional: `runner_test.go:testFlow` stores the full request slice passed to `GenerateContent`, not only the incremental delta.

## Data Shape And APIs Represented

The serialized objects mirror the local `llmRequest` struct inside `runner_test.go:testFlow`:

- `Model`: every complete request boundary in this chunk uses `"sub-agent-model"`.
- `Request`: a slice of `genai.Content` objects representing the nested agent's prompt and tool history.
- `parts`: a one-element array containing either prompt text, `functionCall`, or `functionResponse`.
- `functionCall`: uses `id: "id1"`, `name: "researcher-tool"`, and `args.Arg` with an integer counter.
- `functionResponse`: uses the same `id` and tool name but no payload, matching the Go tool's `struct{}{}` result.
- `role`: all visible entries use `"user"`, including function calls and responses, because the test's synthetic `GenerateContentResponse` builds candidate content with `genai.RoleUser`.

The executable APIs exercised by the fixture are outside this JSON shard:

- `LLMTool.declaration`, `LLMTool.execute`, and `LLMTool.verify` in `llm_tool.go`.
- `LLMAgent.executeOne`, `agentSession.chat`, `agentSession.tryAnswerNow`, `agentSession.callTools`, and response parsing in `llm_agent.go`.
- `NewFuncTool` from `func_tool.go`, used by `llm_tool_test.go` to register `researcher-tool`.
- `testFlow` in `runner_test.go`, which stubs `GenerateContent`, records requests, normalizes them through JSON marshal/unmarshal, and compares this `.llm.json` file.
- `google.golang.org/genai` request, content, part, function call, function response, and config types.

## Control Flow Captured In This Chunk

The runtime sequence represented here is:

1. `LLMTool.execute` converts the parent tool-call args, stores the parent question in `ctx.state[AFLOW_LLMTOOL_PROMPT]`, and runs the nested `LLMAgent`.
2. The nested agent starts with a single prompt content, `"What do you think?"`.
3. For each synthetic model reply, `agentSession.chat` records the model's `functionCall`, executes `researcher-tool`, and appends a matching `functionResponse`.
4. The next `GenerateContent` call receives the full prompt plus all previously appended call/response content.
5. `testFlow` captures each request before consuming the next synthetic reply, so the golden file grows quadratically as the iteration count increases.

Observed boundaries in this exact line range:

- Leading partial request: lines 504226-505206 contain complete call/response pairs for `Arg: 160` through `Arg: 199`, completing a request snapshot that started in the prior chunk.
- Complete request beginning at line 505228: prompt text at line 505233, then `Arg: 0` through `Arg: 200`, ending before line 510266.
- Complete request beginning at line 510266: prompt text at line 510271, then `Arg: 0` through `Arg: 201`, ending before line 515329.
- Complete request beginning at line 515329: prompt text at line 515334, then `Arg: 0` through `Arg: 202`, ending before line 520417.
- Trailing partial request beginning at line 520417: prompt text at line 520422 and complete call/response pairs for `Arg: 0` through `Arg: 97`; the chunk ends at line 522881 inside the `functionCall` for `Arg: 98`.

No final text reply, parent-agent request, `Answer` payload, or max-iteration error is visible in this range.

## State And Persistence Behavior

This JSON is persistent golden state for the aflow test suite. It is updated only through the test harness's `-update` path and is otherwise used as the expected request transcript for `TestLLMToolMaxIters`.

Runtime state represented in the chunk is append-only nested-agent conversation history:

- `agentSession.req` is the main in-memory state visible here. It starts with the prompt and grows by appending model tool-call content and tool-response content after every model round.
- `LLMTool.execute` uses `ctx.state[AFLOW_LLMTOOL_PROMPT]` to pass the parent question into the nested prompt and later reads `ctx.state[AFLOW_LLMTOOL_REPLY]` for the nested reply. Those state keys are not serialized directly in this chunk, but the prompt text is their visible effect.
- `researcher-tool` returns `struct{}{}`, so response blocks preserve order and identity but carry no JSON response body.
- The fixture stores full request snapshots. Resetting `Arg` from a high value back to `0` at each `"Model"` boundary is expected and indicates a new request replaying history rather than a loop counter reset in execution.
- `testFlow` deep-copies changed configs and request slices before storing them. No `Config` blocks are visible in this interior range, which means the effective nested-agent configuration did not change at these request boundaries.

The chunk is a concrete example of the history-retention cost of the current design. Late in the `maxLLMIterations` loop, adjacent requests repeat hundreds of prior tool events.

## Dependencies And Integration Points

Important source integrations:

- `sources/test-tools/syzkaller/pkg/aflow/llm_tool_test.go`: defines `TestLLMToolMaxIters`, constructs the parent `LLMAgent`, registers the `researcher` `LLMTool`, builds the synthetic reply stream with `maxLLMIterations` calls to `researcher-tool`, and expects final output `Reply: "YES"`.
- `sources/test-tools/syzkaller/pkg/aflow/llm_tool.go`: adapts an `LLMAgent` into a tool exposed to the parent model and bridges question/reply through `ctx.state`.
- `sources/test-tools/syzkaller/pkg/aflow/llm_agent.go`: owns the chat loop, `maxLLMIterations = 250`, input-token overflow handling, `tryAnswerNow`, tool execution, final-reply validation, and history compression/sliding behavior.
- `sources/test-tools/syzkaller/pkg/aflow/func_tool.go`: provides typed function-tool wrappers used to expose `researcher-tool`.
- `sources/test-tools/syzkaller/pkg/aflow/runner_test.go`: captures and compares the serialized requests in this `.llm.json` fixture.
- `sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.trajectory.json`: companion golden trajectory for the same execution, covering spans rather than raw LLM requests.

External dependency sensitivity is mainly through `google.golang.org/genai`: changes to `Content`, `Part`, `FunctionCall`, `FunctionResponse`, role serialization, or empty response serialization would rewrite this fixture.

## Risks And Maintenance Notes

This fixture region is intentionally repetitive and therefore fragile to broad golden-file churn. Small changes to history append order, message roles, function-call IDs, config-elision behavior, or empty struct response encoding will alter thousands of lines.

The repeated `id: "id1"` across many `researcher-tool` calls is part of the synthetic test setup, not evidence of unique-call-id generation. Code changes that enforce unique function-call IDs or correlate responses only by ID would need corresponding test updates and may invalidate this scenario.

Because this chunk starts and ends inside JSON structures, tools must merge it with adjacent chunks before drawing whole-file conclusions or validating JSON syntax. Local marker asymmetry is expected: the range includes a trailing `functionCall` marker for `Arg: 98` without its `Arg` line or response, and it begins at the start of a complete `functionCall` for `Arg: 160`.

The range does not cover the actual max-iteration edge or final reply. Its signal is late-loop request-history accumulation through snapshots ending at `Arg: 199`, `200`, `201`, and `202`, plus the beginning of the next snapshot.

## Test Signals

Concrete signals in lines 504226-522881:

- 18,656 source lines, about 262,140 bytes.
- 4 visible `"Model": "sub-agent-model"` boundaries.
- 4 visible prompt text entries with `"What do you think?"`.
- 745 `functionCall` markers and 744 `functionResponse` markers.
- 744 complete `Arg` lines in the assigned range.
- 1,488 visible `"name": "researcher-tool"` lines.
- 1,489 visible `"id": "id1"` lines.
- 0 visible `Config` lines.
- 0 visible final `Reply` or text-return markers.
- Argument runs by visible block: `160-199`, `0-200`, `0-201`, `0-202`, and `0-97`, with the next `Arg: 98` call opened at the chunk end.

The test should continue to pass when `LLMTool` preserves nested-agent prompts, `agentSession.chat` appends tool calls and responses in the current order, and `testFlow` captures complete request histories. It should fail loudly if model request construction switches to deltas, alters roles, changes empty response serialization, or changes max-iteration/history behavior.
