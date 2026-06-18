# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json lines 485570-504225

## Scope

This chunk is an interior slice of the golden LLM request transcript for `TestLLMToolMaxIters`. The source is JSON testdata rather than executable Go code, and the assigned range is not independently parseable JSON: it starts inside the closing of a `functionCall` entry for `Arg: 9`, includes that call's matching response, spans two complete later `sub-agent-model` request snapshots, and ends after the response for `Arg: 159` in the next snapshot.

The range is part of the expected request list compared by the aflow test harness. It records how the nested `LLMTool` agent repeatedly calls a normal function tool named `researcher-tool` while the request history grows.

## Purpose

`TestLLMToolMaxIters` validates the behavior of an LLM-backed tool near the `maxLLMIterations` path. A parent `LLMAgent` calls the `researcher` `LLMTool` with `Question: "What do you think?"`. The nested agent then receives the question as its prompt and repeatedly asks to call `researcher-tool` with increasing integer `Arg` values. After the configured synthetic tool-call sequence completes, the nested agent returns `"Nothing."`, and the parent returns the final workflow output `Reply: "YES"`.

This chunk verifies the deterministic middle of that nested loop. It is especially valuable because every new model request replays the full nested conversation history, so later request objects contain hundreds of repeated `functionCall` and `functionResponse` messages.

## Data Shape And APIs Represented

The serialized objects follow the local `llmRequest` shape from `runner_test.go:testFlow`:

- `Model`: the visible full request boundaries in this range are all `"sub-agent-model"`.
- `Request`: a slice of `genai.Content` values representing the nested agent's current conversation history.
- `parts`: each message has one part in this chunk.
- `text`: request starts contain the prompt text `"What do you think?"`.
- `functionCall`: model-produced calls use `id: "id1"`, `name: "researcher-tool"`, and `args.Arg`.
- `functionResponse`: tool results use the same `id` and `name`, with no response payload because the Go tool returns `struct{}{}`.
- `role`: all visible content entries use `"user"`, matching how the test stub constructs synthetic model replies.

The executable APIs exercised by this fixture are `LLMTool` in `llm_tool.go`, `LLMAgent` and `agentSession.chat` in `llm_agent.go`, `NewFuncTool` in `func_tool.go`, and golden request capture/comparison in `runner_test.go`.

## Control Flow Captured In This Chunk

The runtime flow represented here is:

1. The parent model calls the `researcher` LLM tool.
2. `LLMTool.execute` stores the parent-supplied question in `ctx.state[AFLOW_LLMTOOL_PROMPT]` and runs the nested agent.
3. The nested agent sends `GenerateContent` requests to `"sub-agent-model"` with the original prompt plus accumulated history.
4. The stub model returns a `functionCall` for `researcher-tool`.
5. aflow executes the registered `NewFuncTool` callback and appends a matching `functionResponse`.
6. The next nested request includes the complete history again, not just the latest delta.

Observed boundaries in this exact line range:

- leading partial request: the range begins inside the already-open `Arg: 9` call object, includes the `Arg: 9` response, then complete call/response pairs for `Arg: 10` through `Arg: 196`, and closes the request at line 490260;
- complete request at lines 490264-495224: prompt plus complete call/response pairs for `Arg: 0` through `Arg: 197`;
- complete request at lines 495227-500212: prompt plus complete call/response pairs for `Arg: 0` through `Arg: 198`;
- trailing partial request beginning at line 500215: prompt plus complete call/response pairs for `Arg: 0` through `Arg: 159`, ending just before the next `Arg: 160` call marker.

## State And Persistence Behavior

This file is persistent golden test state. During normal tests, freshly captured request JSON is round-tripped through marshal/unmarshal and compared against `testdata/TestLLMToolMaxIters.llm.json`. When the test is run with the update flag, the fixture can be regenerated from the current behavior.

Runtime state represented by the chunk is append-only nested-agent conversation state:

- `agentSession.req` starts with the nested prompt and grows after each model tool-call reply and each tool response.
- `LLMTool.execute` bridges parent and child agent state through `AFLOW_LLMTOOL_PROMPT` and `AFLOW_LLMTOOL_REPLY`.
- `researcher-tool` receives typed args with `Arg int` and returns an empty struct, so the fixture validates ordering, identity, and serialization shape rather than tool result data.
- The repeated request snapshots intentionally restart at `Arg: 0`, because every LLM round resends the full conversation history.

This region also demonstrates the quadratic-size characteristic of full-history request persistence: each successive request repeats almost the entire previous request and adds one more call/response pair.

## Dependencies And Integration Points

Primary integration points:

- `sources/test-tools/syzkaller/pkg/aflow/llm_tool_test.go`: defines `TestLLMToolMaxIters`, creates the `researcher` nested LLM tool, appends `maxLLMIterations` synthetic `researcher-tool` replies, and expects final output `Reply: "YES"`.
- `sources/test-tools/syzkaller/pkg/aflow/llm_tool.go`: exposes a nested `LLMAgent` as a tool, converts the parent tool args/result shape, and uses state keys to pass prompt/reply across the nested execution.
- `sources/test-tools/syzkaller/pkg/aflow/llm_agent.go`: owns `maxLLMIterations = 250`, the `agentSession.chat` loop, request-history appending, tool execution, final-reply checks, and answer-now behavior for LLM tools.
- `sources/test-tools/syzkaller/pkg/aflow/func_tool.go`: provides `NewFuncTool`, typed argument conversion, and result conversion for `researcher-tool`.
- `sources/test-tools/syzkaller/pkg/aflow/runner_test.go`: stubs `GenerateContent`, records `llmRequest{Model, Config, Request}`, elides repeated config unless changed, and compares against this `.llm.json` fixture.
- `sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.trajectory.json`: companion golden trace for the same workflow execution.
- `google.golang.org/genai`: supplies `GenerateContentConfig`, `Content`, `Part`, `FunctionCall`, `FunctionResponse`, and text part types serialized into the fixture.

## Risks And Maintenance Notes

This area is highly repetitive, so small semantic changes produce large fixture diffs. Changes to request-history retention, role assignment, config-elision behavior, function-call id generation, empty response serialization, schema conversion, or tool-call ordering would rewrite many lines.

The repeated `id1` is intentional in the synthetic reply list for this test. Code that begins enforcing unique function-call ids across a session would need this fixture and test adjusted together.

Because the chunk starts and ends inside JSON structures, marker counts are asymmetric and should be reconciled with adjacent chunks before drawing whole-file conclusions. The line range includes an extra response marker for the partially visible `Arg: 9` call and stops after `Arg: 159` before the next `Arg: 160` call marker.

## Test Signals

Concrete signals in this chunk:

- 3 visible `"Model": "sub-agent-model"` request starts.
- 3 prompt text entries with `"What do you think?"`.
- 744 `functionCall` markers and 745 `functionResponse` markers.
- Visible `Arg` values range from `0` through `198`.
- The leading partial segment completes the request ending at `Arg: 196`.
- The two complete snapshots end at `Arg: 197` and `Arg: 198`.
- The trailing partial snapshot contains complete call/response pairs through `Arg: 159`.
- No `Config` block appears in this interior slice, consistent with `runner_test.go` only storing config when it changes.
- No final nested `"Nothing."`, parent `"YES"`, or max-iteration error appears in this chunk.

The associated test should continue to pass when aflow preserves full nested-history replay, stable tool-call/response ordering, empty-struct response serialization, and the current `maxLLMIterations` control flow.
