# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json lines 354971-373628

## Scope

This chunk is an interior slice of the golden LLM request transcript for `TestLLMToolMaxIters`. The source is JSON testdata, not executable Go code. It records serialized `llmRequest` entries captured by the aflow test harness while a parent `LLMAgent` invokes an `LLMTool` named `researcher`, whose nested sub-agent repeatedly calls `researcher-tool`.

The assigned range begins inside the closing of the request-history entry for `Arg: 78`, includes the matching function response for that prior call, spans three complete new `sub-agent-model` request objects, and ends inside the function response entry for `Arg: 144` in a later request snapshot. The chunk is therefore not independently parseable JSON; its value is as part of the larger golden fixture.

## Purpose

`TestLLMToolMaxIters` validates the max-iteration behavior of an LLM-backed tool. The parent agent first calls the LLM tool `researcher` with `Question: "What do you think?"`. The nested agent then calls its own normal function tool, `researcher-tool`, once per generated model response up to `maxLLMIterations`, before returning text to the parent. The parent then returns the final structured output `Reply: "YES"`.

This chunk verifies deterministic request-history accumulation deep in that loop. Each later `sub-agent-model` request replays the complete nested prompt and all prior `researcher-tool` calls/responses from `Arg: 0` upward. The visible request snapshots cover the point where accumulated tool-call histories grow through arguments `167`, `168`, `169`, and `170`, followed by the beginning of the next snapshot through `Arg: 144`.

## Data Shape And APIs Represented

The JSON mirrors the local `llmRequest` shape compared by `runner_test.go:testFlow`:

- `Model`: visible complete and partial top-level entries in this range use `"sub-agent-model"`.
- `Request`: a serialized slice of `genai.Content` messages for the nested agent.
- `parts`: a one-element array containing either a `functionCall`, a `functionResponse`, or, at request starts, prompt text.
- `functionCall`: carries `id: "id1"`, `name: "researcher-tool"`, and `args.Arg`.
- `functionResponse`: carries `id: "id1"` and `name: "researcher-tool"`; no payload appears because the Go tool returns `struct{}{}`.

The executable APIs exercised by the fixture are defined outside this JSON: `LLMTool` in `llm_tool.go`, `LLMAgent` and `agentSession.chat` in `llm_agent.go`, typed tool creation through `NewFuncTool`, and request capture/comparison in `runner_test.go`.

## Control Flow Captured In This Chunk

The represented runtime flow is:

1. `LLMTool.execute` receives the parent tool call and injects the question into the nested agent prompt.
2. The nested agent sends a `GenerateContent` request with prompt `"What do you think?"` plus accumulated history.
3. The model reply requests `researcher-tool` with a numeric `Arg`.
4. aflow executes the registered Go tool and appends a matching `functionResponse`.
5. The next LLM request includes the entire history again, so each top-level request object is a full snapshot rather than a delta.

Observed boundaries in this exact line range:

- leading partial request: starts before the chunk, includes the response for the previously opened `Arg: 78`, then complete call/response pairs for `Arg: 79` through `Arg: 167`, and ends at line 357210;
- complete request beginning at line 357211: prompt plus `Arg: 0` through `Arg: 168`;
- complete request beginning at line 361449: prompt plus `Arg: 0` through `Arg: 169`;
- complete request beginning at line 365712: prompt plus `Arg: 0` through `Arg: 170`;
- trailing partial request beginning at line 370000: prompt plus complete pairs through `Arg: 143`, then the `Arg: 144` call and the beginning of its response at the chunk end.

## State And Persistence Behavior

The fixture is persistent golden state for tests. It is generated when the harness runs with its update path and otherwise acts as the expected output compared against freshly captured requests.

Runtime state represented here is append-only nested-agent conversation history:

- `agentSession.req` grows after every model response and tool response.
- `LLMTool.execute` temporarily stores the tool question in `ctx.state[AFLOW_LLMTOOL_PROMPT]`.
- `LLMTool.verify` constructs an internal `LLMAgent` that writes its answer to `AFLOW_LLMTOOL_REPLY`.
- `researcher-tool` returns an empty struct, so the persisted response blocks validate identity and order rather than data content.
- Repeated request snapshots intentionally restart at `Arg: 0` because every new LLM round resends full history.

This chunk shows the quadratic growth pressure of the current history strategy: later request objects include hundreds of repeated call/response entries.

## Dependencies And Integration Points

Primary integration points:

- `sources/test-tools/syzkaller/pkg/aflow/llm_tool_test.go`: defines `TestLLMToolMaxIters`, creates the `researcher` LLM tool and nested `researcher-tool`, and appends synthetic replies for `range maxLLMIterations`.
- `sources/test-tools/syzkaller/pkg/aflow/llm_agent.go`: defines `maxLLMIterations = 250`, the chat loop, tool-call handling, retry/answer-now behavior, and the max-iteration error path.
- `sources/test-tools/syzkaller/pkg/aflow/llm_tool.go`: adapts an `LLMAgent` into a function-like tool for the parent model and bridges prompt/reply through `ctx.state`.
- `sources/test-tools/syzkaller/pkg/aflow/runner_test.go`: captures generated LLM requests, JSON-normalizes them, and compares them with this `.llm.json` fixture.
- `sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.trajectory.json`: companion golden span trace for the same execution.
- `google.golang.org/genai`: supplies the request, content, function call, function response, and config structures serialized here.

## Risks And Maintenance Notes

This region is highly repetitive, so small behavioral changes can produce large golden diffs. Changes to message role assignment, function-call id generation, empty function-response serialization, config elision, or request-history retention will rewrite many lines.

The repeated use of `id1` is intentional in the synthetic reply stream. If runtime code starts requiring unique ids per call, or if duplicate-call detection keys too strongly on id/name without considering args and position, this fixture would expose that mismatch.

The chunk starts and ends inside JSON structures. Merge tooling and human review should reconcile it with adjacent chunks before drawing whole-file conclusions. The local marker counts are asymmetric: this range contains 744 `functionCall` markers and 745 `functionResponse` markers because it starts after the `Arg: 78` call marker but includes that call's response marker.

## Test Signals

Useful signals observed in this range:

- 4 visible `"Model": "sub-agent-model"` boundaries, of which 3 complete inside the chunk.
- 4 prompt text entries with `"What do you think?"`.
- 744 `functionCall` markers and 745 `functionResponse` markers.
- No `Config` block in this interior range, indicating unchanged config elision.
- All visible tool events target `"researcher-tool"` with id `"id1"`.
- No final `"Nothing."` sub-agent reply, parent `"YES"` reply, or max-iteration error appears in this chunk.

The chunk should continue to pass when the aflow request builder preserves full nested history, call/response ordering, and the current max-iteration semantics. It should fail loudly through `TestLLMToolMaxIters` if those serialized requests drift.
