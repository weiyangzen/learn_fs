# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json lines 616134-634789

## Scope

This chunk is an interior slice of the golden LLM request transcript for `TestLLMToolMaxIters`. The source is JSON testdata, not executable Go code. It records serialized `llmRequest` objects captured by the aflow test harness while a parent `LLMAgent` calls an `LLMTool` named `researcher`, whose nested sub-agent repeatedly invokes the normal function tool `researcher-tool`.

The assigned range starts inside the first visible request snapshot, immediately after the `Arg: 215` `functionCall` object and before its matching response. It then includes four visible `sub-agent-model` request boundaries, of which three begin inside the chunk, and ends inside the fourth visible request snapshot after the `Arg: 69` call but before its matching response. The range is therefore not independently parseable JSON; its research value is in the repeated request-history pattern it contributes to the full fixture.

## Purpose

`TestLLMToolMaxIters` validates the max-iteration behavior of an LLM-backed tool. The parent agent receives a synthetic model reply that calls the LLM tool `researcher` with `Question: "What do you think?"`. The nested sub-agent then receives synthetic replies that call `researcher-tool` once for every value in `range maxLLMIterations`, where `maxLLMIterations` is `250`. After those tool rounds, the nested agent replies with `"Nothing."`, and the parent agent returns the final structured output `Reply: "YES"`.

This chunk verifies the late part of the repeated nested-tool loop. It shows accumulated history snapshots where each new nested-agent request resends the prompt plus every prior `researcher-tool` call/response from `Arg: 0` upward. In this exact slice, the first partial snapshot continues through `Arg: 220`; the complete snapshots that start at lines 621839 and 627427 continue through `Arg: 221` and `Arg: 223`; and the trailing partial snapshot starts at line 633039 and reaches the open `Arg: 69` call at the chunk end.

## Data Shape And APIs Represented

The JSON mirrors the `llmRequest` struct built in `runner_test.go:testFlow`:

- `Model`: visible request objects in this range use `"sub-agent-model"`, the model configured on the `LLMTool`.
- `Request`: a slice of `genai.Content` messages representing the nested agent conversation history at the moment of each model call.
- `parts`: each content entry contains one text, `functionCall`, or `functionResponse` part.
- `functionCall`: tool-call parts use `id: "id1"`, `name: "researcher-tool"`, and an integer `args.Arg`.
- `functionResponse`: response parts use the same `id` and `name`; there is no payload because the Go callback returns `struct{}{}`.

The executable APIs and types exercised by this fixture are defined outside the JSON: `LLMTool` in `llm_tool.go`, `LLMAgent` and `agentSession` in `llm_agent.go`, typed tool construction through `NewFuncTool`, and golden request capture/comparison in `runner_test.go`.

## Control Flow Captured In This Chunk

The represented runtime flow is:

1. `LLMTool.execute` converts parent tool args into `llmToolArgs` and stores the question in `ctx.state[AFLOW_LLMTOOL_PROMPT]`.
2. `LLMTool.verify` has already constructed an internal `LLMAgent` whose prompt template reads that state key and whose reply is written to `AFLOW_LLMTOOL_REPLY`.
3. The nested agent sends a `GenerateContent` request to `"sub-agent-model"` with prompt text `"What do you think?"` and all retained prior tool messages.
4. The synthetic model reply requests `researcher-tool` with the next `Arg`.
5. aflow executes the registered Go tool, appends a matching `functionResponse`, and sends another full-history request.

Observed line boundaries in this range:

- leading partial snapshot: the range begins at line 616134 inside the `Arg: 215` call entry, includes the response for `Arg: 215`, complete pairs for `Arg: 216` through `Arg: 220`, and closes just before the request beginning at line 621839;
- complete request beginning at line 621839: prompt plus call/response history from `Arg: 0` through `Arg: 221`;
- complete request beginning at line 627427: prompt plus call/response history from `Arg: 0` through `Arg: 223`;
- trailing partial request beginning at line 633039: prompt plus complete pairs through `Arg: 68`, then the `Arg: 69` call whose response starts after the assigned range.

## State And Persistence Behavior

This file is persistent golden test state. The test harness records requests during execution, JSON round-trips them to normalize Go values, and compares them to `testdata/TestLLMToolMaxIters.llm.json` unless the `-update` flag rewrites the fixture.

Runtime state represented here is append-only nested-agent conversation state. `agentSession.req` retains the prompt and every prior model/tool interaction for this test because neither sliding-window summarization nor token compression is enabled in the fixture. Each later request object therefore repeats a larger history instead of recording only a delta. `LLMTool.execute` temporarily uses `ctx.state` to bridge the parent tool question into the nested agent and then deletes the prompt/reply bridge keys after use.

The repeated snapshots expose the expected growth pattern: request size increases as the sub-agent approaches `maxLLMIterations`, with no persisted response body beyond tool identity/order because `researcher-tool` returns an empty struct.

## Dependencies And Integration Points

Primary integration points:

- `sources/test-tools/syzkaller/pkg/aflow/llm_tool_test.go`: defines `TestLLMToolMaxIters`, constructs the parent `LLMAgent`, configures the `researcher` `LLMTool`, registers `researcher-tool`, and creates synthetic `genai.Part` replies for `range maxLLMIterations`.
- `sources/test-tools/syzkaller/pkg/aflow/llm_agent.go`: defines `LLMAgent`, `agentSession`, the tool-call loop, tool history tracking, answer handling, and the `maxLLMIterations = 250` guard.
- `sources/test-tools/syzkaller/pkg/aflow/llm_tool.go`: adapts an `LLMAgent` into a tool declaration with `llmToolArgs` and `llmToolResults`, and bridges prompt/reply through `AFLOW_LLMTOOL_PROMPT` and `AFLOW_LLMTOOL_REPLY`.
- `sources/test-tools/syzkaller/pkg/aflow/runner_test.go`: captures `GenerateContent` calls, stores `Model`, optional `Config`, and `Request`, and compares the result against this `.llm.json` file.
- `sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.trajectory.json`: companion golden trajectory for the same test execution.
- `google.golang.org/genai`: provides the serialized `Content`, `Part`, `FunctionCall`, `FunctionResponse`, and generation config structures.

## Risks And Maintenance Notes

This chunk is mechanically repetitive but sensitive to small behavior changes. Any change to history retention, request role assignment, function-call id generation, empty response serialization, config elision, or the order in which tool calls and responses are appended will rewrite many lines of the golden fixture.

The repeated `id1` value is intentional in the synthetic replies used by the test. Code that starts requiring globally unique function-call IDs, or loop detection that keys too narrowly on name/id without considering args and sequence, would conflict with this fixture. The fixture also documents the current full-history resend strategy, which has quadratic golden-file growth; if summarization or compression becomes enabled for this path, this part of the fixture should change substantially.

Because the assigned lines start and end inside JSON objects, merge/reconciliation must combine this note with neighboring chunk reports before treating the whole file as a complete parseable transcript.

## Test Signals

Concrete signals in this line range:

- 4 visible `"Model": "sub-agent-model"` markers.
- 4 prompt text entries with `"What do you think?"`.
- 744 `functionCall` markers and 744 `functionResponse` markers.
- All visible tool events target `"researcher-tool"` and use `id: "id1"`.
- No `Config` block appears in this interior range, consistent with `runner_test.go` eliding repeated configs after the previous request.
- No final nested `"Nothing."` reply, parent `"YES"` reply, or max-iteration error appears in this chunk.

The fixture should continue to pass when aflow preserves full nested history, deterministic tool-call ordering, empty-struct response serialization, and the current `maxLLMIterations` behavior. It should fail through `TestLLMToolMaxIters` when any of those serialized request expectations drift.
