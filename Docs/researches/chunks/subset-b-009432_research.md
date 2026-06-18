# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json lines 522882-541532

## Scope

This chunk is an interior slice of the golden LLM request transcript for `TestLLMToolMaxIters`. The source is JSON testdata, not executable Go code. It records serialized `llmRequest` entries captured by the aflow test harness while a parent `LLMAgent` invokes an `LLMTool` named `researcher`, whose nested sub-agent repeatedly calls `researcher-tool`.

The assigned range begins inside a request-history entry at the call for `Arg: 98`, includes that matching function response, spans several complete `sub-agent-model` request snapshots, and ends inside a later request snapshot at the call/response pair for `Arg: 19`. The chunk is therefore not independently parseable JSON; it is meaningful as part of the larger golden fixture.

## Purpose

`TestLLMToolMaxIters` validates the maximum-iteration behavior of an LLM-backed tool. The parent model first calls the `researcher` LLM tool with `Question: "What do you think?"`. The nested sub-agent then repeatedly asks to execute its own function tool, `researcher-tool`, using monotonically increasing integer arguments until the test's synthetic reply stream reaches the configured iteration limit. After the tool-call loop, the sub-agent returns `"Nothing."`, and the parent returns the final `"YES"` reply.

This chunk verifies deterministic request-history accumulation in the middle of that long loop. Every new `sub-agent-model` request repeats the nested prompt and all prior `researcher-tool` call/response history from `Arg: 0` upward. The visible snapshots here cover the transition from an earlier request ending around `Arg: 203`, through full snapshots ending at `Arg: 204`, `Arg: 205`, and `Arg: 206`, into the next snapshot beginning again at `Arg: 0` and reaching `Arg: 19` by the chunk end.

## Data Shape And APIs Represented

The JSON mirrors the local `llmRequest` shape compared by `runner_test.go:testFlow`:

- `Model`: complete request objects in this range use `"sub-agent-model"`.
- `Request`: a serialized slice of `genai.Content` messages for the nested agent.
- `parts`: a one-element array containing either prompt text, a `functionCall`, or a `functionResponse`.
- `functionCall`: carries `id: "id1"`, `name: "researcher-tool"`, and `args.Arg`.
- `functionResponse`: carries `id: "id1"` and `name: "researcher-tool"`; no response payload is visible because the Go tool returns `struct{}{}`.

The executable APIs exercised by the fixture are defined outside this JSON: `LLMTool` in `llm_tool.go`, `LLMAgent` and `agentSession.chat` in `llm_agent.go`, typed function-tool creation through `NewFuncTool`, and request capture/comparison in `runner_test.go`.

## Control Flow Captured In This Chunk

The represented runtime flow is:

1. `LLMTool.execute` receives the parent tool call, converts the incoming map into `llmToolArgs`, and stores the question in `ctx.state[AFLOW_LLMTOOL_PROMPT]`.
2. The nested agent sends a `GenerateContent` request with prompt `"What do you think?"` plus accumulated conversation history.
3. The mocked model reply requests `researcher-tool` with a numeric `Arg`.
4. `agentSession.callTools` executes the registered Go tool and appends a matching `functionResponse` part.
5. The next LLM request includes the entire prompt plus all previous calls and responses, so each top-level request object is a full snapshot rather than a delta.

Observed boundaries in this exact line range:

- leading partial request: starts before the chunk, includes call/response pairs from `Arg: 98` through `Arg: 203`, and closes before line 525530;
- complete request beginning at line 525530: prompt plus `Arg: 0` through `Arg: 204`;
- complete request beginning at line 530668: prompt plus `Arg: 0` through `Arg: 205`;
- complete request beginning at line 535831: prompt plus `Arg: 0` through `Arg: 206`;
- trailing partial request beginning at line 541019: prompt plus `Arg: 0` through the visible `Arg: 19` pair at the chunk end.

## State And Persistence Behavior

The fixture is persistent golden state for tests. It is regenerated only through the test harness update path and otherwise acts as the expected serialized request output compared against freshly captured execution.

Runtime state represented here is append-only nested-agent conversation history:

- `agentSession.req` grows after every model response and every tool-response message.
- `LLMTool.execute` temporarily stores the tool question in `ctx.state[AFLOW_LLMTOOL_PROMPT]` and deletes it after the nested agent returns.
- `LLMTool.verify` constructs an internal `LLMAgent` whose `Reply` key is `AFLOW_LLMTOOL_REPLY`.
- `researcher-tool` returns an empty struct, so the persisted response blocks validate identity, ordering, and history retention rather than result data.
- Repeated request snapshots intentionally restart at `Arg: 0` because each new LLM round resends the full conversation history.

This chunk makes the history-growth cost visible: later request objects contain hundreds of duplicated call/response entries. That behavior is expected for this golden file and is part of the max-iteration test signal.

## Dependencies And Integration Points

Primary integration points:

- `sources/test-tools/syzkaller/pkg/aflow/llm_tool_test.go`: defines `TestLLMToolMaxIters`, creates the parent-visible `researcher` LLM tool, registers nested `researcher-tool`, and appends synthetic function-call replies in a loop over `maxLLMIterations`.
- `sources/test-tools/syzkaller/pkg/aflow/llm_tool.go`: adapts an `LLMAgent` into a function-like tool and bridges prompt/reply through `ctx.state`.
- `sources/test-tools/syzkaller/pkg/aflow/llm_agent.go`: owns `agentSession.chat`, tool execution via `callTools`, duplicate-call tracking, context handling, and the final `agent reached max iterations limit` guard.
- `sources/test-tools/syzkaller/pkg/aflow/runner_test.go`: captures generated LLM requests, JSON-normalizes them with a marshal/unmarshal round trip, and compares them against this `.llm.json` fixture.
- `sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.trajectory.json`: companion golden trajectory for the same execution.
- `google.golang.org/genai`: supplies the serialized request, content, function call, function response, config, and text part types.

## Risks And Maintenance Notes

This region is highly repetitive, so small behavioral changes can produce very large golden diffs. Changes to request-history retention, role assignment, function-call id generation, empty response serialization, config elision, JSON schema normalization, or nested-agent prompt handling will rewrite many lines.

The repeated use of `id1` is intentional in the synthetic reply stream. Duplicate-call detection should not flag these calls as an infinite loop because the arguments differ across iterations. A change that keys too heavily on tool name or id without considering `args.Arg` would likely surface through this fixture.

The chunk starts and ends inside JSON structures. Merge/reconciliation tooling should combine it with adjacent chunks before drawing whole-file conclusions. Local marker counts are balanced in this slice, but the first and last structures are only partial relative to the whole JSON array.

## Test Signals

Useful signals observed in this range:

- 4 visible `"Model": "sub-agent-model"` request boundaries.
- 4 prompt text entries with `"What do you think?"`.
- 744 `functionCall` markers and 744 `functionResponse` markers.
- 744 visible `Arg` values, with resets at new request snapshots after `203`, `204`, `205`, and `206`.
- All visible tool events target `"researcher-tool"` with id `"id1"`.
- No `Config` block appears in this interior range, indicating unchanged config elision after the first request for the model/config pair.
- No final `"Nothing."` sub-agent reply, parent `"YES"` reply, or max-iteration error appears in this chunk.

The chunk should continue to pass when aflow preserves full nested request history, call/response ordering, empty-struct response serialization, and current max-iteration semantics. It should fail through `TestLLMToolMaxIters` if any of those serialized request expectations drift.
