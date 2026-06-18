# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json lines 634790-653437

## Scope

This chunk is an interior slice of the golden LLM request transcript for `TestLLMToolMaxIters`. The source is serialized JSON testdata, not executable Go code. It records `llmRequest` objects captured by the aflow test harness while a parent `LLMAgent` invokes an `LLMTool` named `researcher`, whose nested sub-agent repeatedly calls a normal function tool named `researcher-tool`.

The assigned range starts inside an already-open `sub-agent-model` request, at the stored `functionResponse` that follows tool call `Arg: 69`. It then includes all remaining call/response pairs through `Arg: 224`, two complete subsequent `sub-agent-model` request snapshots, and the beginning of the next snapshot through the `functionResponse` for `Arg: 135`. Because it begins and ends inside larger JSON structures, this chunk is not independently parseable as a full JSON document.

## Purpose

`TestLLMToolMaxIters` validates that an LLM-backed tool can run a nested LLM conversation up to the `maxLLMIterations` bound without corrupting request history. The Go test constructs synthetic model replies where the parent agent first calls the `researcher` LLM tool with `Question: "What do you think?"`. The nested agent then receives one generated `functionCall` for `researcher-tool` per iteration, with integer `Arg` values from `0` up to the loop limit, before eventually returning text to the parent.

This chunk verifies the middle-to-late history growth of that nested agent. Each `sub-agent-model` request snapshot resends the initial prompt plus all prior tool calls and tool responses from `Arg: 0` upward. The visible repetition is intentional: the fixture asserts full conversation-history accumulation, not just incremental deltas.

## Data Shape And APIs Represented

The JSON mirrors the local `llmRequest` struct in `runner_test.go`:

- `Model`: complete request objects visible in this chunk use `"sub-agent-model"`.
- `Request`: serialized `[]*genai.Content` history for the nested agent.
- `parts`: one-element message payloads containing prompt text, `functionCall`, or `functionResponse`.
- `functionCall`: uses `id: "id1"`, `name: "researcher-tool"`, and `args.Arg`.
- `functionResponse`: uses the same id and name, with no explicit response payload because the registered Go tool returns `struct{}{}`.

The executable APIs exercised by this fixture are `LLMTool` in `llm_tool.go`, `LLMAgent` and `agentSession.chat` in `llm_agent.go`, typed function-tool construction through `NewFuncTool`, and golden request capture/comparison in `runner_test.go:testFlow`.

## Control Flow Captured In This Chunk

The runtime flow represented here is:

1. `LLMTool.execute` receives a parent model tool call and writes the question into `ctx.state[AFLOW_LLMTOOL_PROMPT]`.
2. `LLMTool.verify` has adapted the tool into an internal `LLMAgent` whose prompt template reads that state key.
3. The nested agent sends a `GenerateContent` request containing `"What do you think?"` and accumulated history.
4. The model reply asks to call `researcher-tool` with the next `Arg` value.
5. `agentSession.callTools` executes the registered Go `funcTool`, appends a matching `functionResponse`, and the next LLM request resends the entire expanded history.

Observed boundaries in this exact range:

- Leading partial request: starts before line 634790, includes the response for `Arg: 69`, complete call/response pairs for `Arg: 70` through `Arg: 224`, and closes at line 638676.
- Complete request beginning at line 638678: prompt plus accumulated pairs from `Arg: 0` through `Arg: 225`.
- Complete request beginning at line 644341: prompt plus accumulated pairs from `Arg: 0` through `Arg: 226`.
- Trailing partial request beginning at line 650029: prompt plus accumulated pairs through the response for `Arg: 135`; the next `Arg: 136` call begins immediately after this chunk.

## State And Persistence Behavior

This file is persistent golden state for the test suite. `runner_test.go:testFlow` captures generated requests, normalizes them through JSON marshal/unmarshal, and compares them against `testdata/TestLLMToolMaxIters.llm.json` unless the test is run with the update flag.

The runtime state visible through the fixture is append-only nested-agent conversation history:

- `agentSession.req` grows by appending each model response and each tool-response content block.
- `LLMTool.execute` temporarily stores the sub-agent prompt in `ctx.state` and later expects the nested reply in `AFLOW_LLMTOOL_REPLY`.
- `researcher-tool` returns an empty struct, so the serialized responses primarily validate call identity, ordering, and history retention.
- The repeated restart at `Arg: 0` in each snapshot is expected because each request is a full history resend.

The chunk illustrates the storage and diff-size cost of this history strategy: a small number of additional iterations produce thousands of repeated JSON lines.

## Dependencies And Integration Points

Important source-tree integration points:

- `sources/test-tools/syzkaller/pkg/aflow/llm_tool_test.go`: defines `TestLLMToolMaxIters`, creates the `researcher` LLM tool, registers `researcher-tool`, and appends `maxLLMIterations` synthetic tool-call replies.
- `sources/test-tools/syzkaller/pkg/aflow/llm_agent.go`: defines `maxLLMIterations = 250`, owns the chat loop, sends `GenerateContent` requests, appends tool results to history, and returns the max-iteration error if the loop cannot finish.
- `sources/test-tools/syzkaller/pkg/aflow/llm_tool.go`: adapts a nested `LLMAgent` into a parent-callable tool and bridges prompt/reply values through `ctx.state`.
- `sources/test-tools/syzkaller/pkg/aflow/func_tool.go`: converts model-supplied argument maps into typed Go structs, executes tool functions, and converts results back to response maps.
- `sources/test-tools/syzkaller/pkg/aflow/runner_test.go`: stubs Gemini generation, records every request, elides repeated config when unchanged, and compares this fixture with fresh output.
- `google.golang.org/genai`: supplies the content, part, function-call, function-response, and generation-config structures serialized in the fixture.

## Risks And Maintenance Notes

This region is intentionally repetitive, so small runtime changes create very large golden diffs. Changes to conversation-history retention, message role assignment, config elision, function-response serialization, empty-struct result handling, or tool-call id generation would rewrite this chunk.

The fixed `id1` value across many calls is synthetic test input. Duplicate-call detection must not treat this fixture as a loop merely because the id and tool name repeat; the arguments and ordered history are part of the intended behavior. Conversely, if future code requires unique tool-call ids per invocation, this golden file will need coordinated test updates.

The chunk boundaries are partial. The leading `functionResponse` belongs to a call before the assigned range, and the final visible response is followed by more history outside the range. Merge/reconciliation should combine this with adjacent chunks before drawing whole-file conclusions.

## Test Signals

Useful signals in this range:

- 18,648 lines and about 262 KB of fixture text.
- 3 visible `"Model": "sub-agent-model"` boundaries that begin inside the chunk, plus the tail of one request that began earlier.
- 3 visible prompt entries with `"What do you think?"`.
- 744 `functionCall` markers and 745 `functionResponse` markers; the asymmetry comes from starting at the response after `Arg: 69`.
- No `Config` block appears in this interior range, matching the harness behavior of recording config only when it changes from the previous request.
- All visible tool events target `researcher-tool` with `id: "id1"`.
- No final `"Nothing."` sub-agent answer, parent `"YES"` answer, or max-iteration error appears in this chunk.

The chunk should continue to pass when aflow preserves full nested request history, ordered tool call/response pairing, empty-tool-result serialization, and the current `maxLLMIterations` semantics.
