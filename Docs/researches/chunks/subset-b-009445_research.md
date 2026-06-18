# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json lines 765328-783952

## Scope

This chunk is a late interior slice of the golden LLM request transcript for `TestLLMToolMaxIters`. The source is serialized JSON testdata, not executable Go code. It records `llmRequest` snapshots captured by the aflow test harness while a parent `LLMAgent` calls an `LLMTool` named `researcher`, and that nested sub-agent repeatedly calls a normal function tool named `researcher-tool`.

The assigned range begins inside an already-open request at a `functionResponse` for `researcher-tool`, includes several full nested-agent request snapshots, and ends mid-object at the start of another `parts` entry. It is therefore not independently parseable as complete JSON; it must be interpreted as part of the full `TestLLMToolMaxIters.llm.json` array.

## Purpose

`TestLLMToolMaxIters` validates the bounded-iteration behavior of LLM tool execution. The Go test constructs model replies where the parent agent first calls the nested `researcher` tool with `Question: "What do you think?"`. The nested agent then receives synthetic `functionCall` replies for `researcher-tool` with integer `Arg` values generated from `0` up to `maxLLMIterations - 1`, before being forced to answer without more tool calls.

This chunk captures the end of the normal repeated-tool-call phase and the start of the forced-answer phase. It shows that each sub-agent request resends the full prompt/history, including earlier `functionCall` and `functionResponse` messages, and that after the iteration bound is reached the next request changes config to disable further function calling.

## Data Shape And APIs Represented

The JSON mirrors the local `llmRequest` struct in `runner_test.go`:

- `Model`: all complete request boundaries visible in this range are `"sub-agent-model"`.
- `Config`: omitted for repeated requests until line 781490, where the changed tool config is reserialized.
- `Request`: serialized `[]*genai.Content` history for the nested agent.
- `parts`: one-element message payloads containing prompt text, `functionCall`, or `functionResponse`.
- `functionCall`: uses `id: "id1"`, `name: "researcher-tool"`, and `args.Arg`.
- `functionResponse`: uses the same id and name, with no explicit response object because the registered Go tool returns `struct{}{}`.
- `toolConfig.functionCallingConfig.mode`: becomes `"NONE"` in the final complete request snapshot, matching the answer-now path that prevents additional tool calls.

The executable APIs exercised by this fixture are `LLMTool`, `LLMAgent`, `agentSession.chat`, `agentSession.tryAnswerNow`, typed function tools from `NewFuncTool`, and the golden request capture/comparison in `runner_test.go:testFlow`.

## Control Flow Captured In This Chunk

The runtime flow represented here is:

1. The parent agent has already called the `researcher` LLM tool.
2. The nested `researcher` session sends `GenerateContent` requests against `sub-agent-model`.
3. Each synthetic model reply asks for `researcher-tool` with the next `Arg` value.
4. The registered Go function tool returns an empty struct, producing a matching empty `functionResponse`.
5. The next LLM request appends the new call/response pair and resends the whole nested history.
6. After the normal iteration loop reaches the `maxLLMIterations` boundary, `tryAnswerNow` appends the best-effort-answer instruction and changes function calling mode to `NONE`.

Observed boundaries in this exact range:

- Leading partial request: starts before line 765328 and continues from the response before `Arg: 99` through later tool history, closing immediately before the request at line 769039.
- Complete request at line 769039: `Model: "sub-agent-model"` with prompt `"What do you think?"` and accumulated tool history restarting at `Arg: 0`.
- Complete request at line 775252: another full-history resend for the nested agent.
- Complete request at line 781490: includes a fresh `Config` block with the nested agent instruction, `temperature: 0.3`, the `researcher-tool` declaration/schema, and `toolConfig` mode `NONE`; this is the forced answer-now request.
- Trailing partial request: the range ends at line 783952 immediately after opening a new `parts` entry, so the following function call is outside this chunk.

## State And Persistence Behavior

This file is persistent golden state for the Go test suite. `runner_test.go:testFlow` stubs generation, records each request as `llmRequest`, normalizes the captured data through JSON marshal/unmarshal, and compares it against `testdata/TestLLMToolMaxIters.llm.json` unless tests are run with the update flag.

Runtime state visible in this fixture is append-only conversation history in `agentSession.req`. Tool calls and tool responses are preserved as prior `genai.Content` entries and sent again on every subsequent nested-agent request. The apparent restarts at `Arg: 0` are not execution restarts; they are full-history snapshots for later LLM turns. `LLMTool` bridges the parent tool call into nested-agent state via the prompt and later returns the nested reply to the parent as an `Answer`.

The transition at line 781490 is stateful: `tryAnswerNow` sets `answerNow`, mutates the generation config to disable function calling, and appends the instruction to answer with available information rather than calling more tools. This prevents the test from failing with `agent reached max iterations limit (250)` and lets the nested agent return `"Nothing."` after the max tool-call sequence.

## Dependencies And Integration Points

Important source-tree integration points:

- `sources/test-tools/syzkaller/pkg/aflow/llm_tool_test.go`: defines `TestLLMToolMaxIters`, the `researcher` `LLMTool`, the nested `researcher-tool`, and the synthetic reply sequence that issues `maxLLMIterations` tool calls.
- `sources/test-tools/syzkaller/pkg/aflow/llm_agent.go`: defines `maxLLMIterations = 250`, owns the chat loop, appends model and tool messages to request history, and implements `tryAnswerNow`.
- `sources/test-tools/syzkaller/pkg/aflow/llm_tool.go`: adapts a nested `LLMAgent` into a parent-callable tool and maps prompt/reply values through aflow state.
- `sources/test-tools/syzkaller/pkg/aflow/func_tool.go`: converts JSON argument maps into typed Go structs and converts empty struct results back into response maps.
- `sources/test-tools/syzkaller/pkg/aflow/runner_test.go`: provides the stubbed LLM, records requests, omits unchanged config from repeated request snapshots, and compares this golden file.
- `google.golang.org/genai`: supplies the serialized content, part, function-call, function-response, tool declaration, and generation-config structures.

## Risks And Maintenance Notes

This chunk is intentionally large and repetitive. Small changes in request-history retention, config elision, tool response serialization, function-calling configuration, schema generation, role assignment, or tool-call id handling can rewrite thousands of lines.

The repeated `id: "id1"` is synthetic and stable across many tool calls. Consumers should not infer uniqueness from this fixture. The meaningful ordering signal is the sequence of `Arg` values plus paired `functionCall`/`functionResponse` entries.

The chunk also demonstrates a scalability pressure point: because each request stores the entire accumulated conversation, late-turn snapshots duplicate almost all earlier tool history. That is useful for golden coverage but makes diffs and fixture size expensive when max-iteration behavior changes.

The boundaries are partial. The first visible `functionResponse` belongs to a call opened before the assigned range, and the final line is only the start of the next message. Whole-file conclusions should be merged with adjacent chunk research before deciding whether a sequence is complete.

## Test Signals

Useful signals in this range:

- 18,625 source lines.
- 3 visible `"Model": "sub-agent-model"` request boundaries.
- 1 visible `Config` block, reintroduced because the final request changes function-calling mode to `NONE`.
- 3 prompt entries containing `"What do you think?"`.
- 1 nested-agent instruction/config entry containing `"researcher instruction\nPrefer calling several tools at the same time to save round-trips.\n"`.
- 741 `functionCall` markers and 742 `functionResponse` markers; the asymmetry comes from starting on a response and ending mid-message.
- 742 visible `Arg` fields, with values spanning `0` through `248`; repeated counts come from full-history resends.
- No final `"Nothing."` sub-agent answer, parent `"YES"` answer, or max-iteration error text is inside this range.

This chunk should continue to pass when aflow preserves full nested-agent history, ordered tool call/response pairing, empty-result serialization, config elision for unchanged requests, and the `tryAnswerNow` transition after the `maxLLMIterations` tool-call phase.
