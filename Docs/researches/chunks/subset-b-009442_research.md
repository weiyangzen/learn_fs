# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json lines 709386-728033

## Scope

This chunk is an interior slice of the golden LLM request transcript for `TestLLMToolMaxIters`. The source is serialized JSON testdata, not executable Go. It records `llmRequest` objects captured by the aflow test harness while a parent `LLMAgent` invokes an `LLMTool` named `researcher`, whose nested sub-agent repeatedly calls the function tool `researcher-tool`.

The assigned range starts inside an already-open `sub-agent-model` request at the `functionResponse` for the previous chunk's `Arg: 43` call, then continues through the visible `Arg: 44` and later call/response history. It contains three complete top-level request objects that begin at lines 714247, 720235, and 726248, and ends just after the `functionResponse` for `Arg: 70` in the final visible request snapshot. Because both boundaries cut through larger JSON structures, this chunk is not independently parseable as a full JSON document.

## Purpose

`TestLLMToolMaxIters` validates that an LLM-backed tool can execute a nested LLM conversation up to `maxLLMIterations` without losing or corrupting request history. The Go test first has the parent model call the `researcher` LLM tool with `Question: "What do you think?"`. The nested agent then receives synthetic model replies that call `researcher-tool` once for each integer in `range maxLLMIterations`, where `maxLLMIterations` is `250`. After those nested tool rounds, the sub-agent returns `"Nothing."` and the parent agent returns structured output `Reply: "YES"`.

This exact chunk covers late-loop full-history resend behavior. The leading partial request continues retained history from `Arg: 43` through `Arg: 237`; the complete requests that start inside the range carry prompt-plus-history snapshots through `Arg: 238` and `Arg: 239`; the final complete request starts over at the beginning of a new full-history snapshot and reaches `Arg: 70` before the range ends. The apparent resets to `Arg: 0` are expected: each `GenerateContent` request serializes the whole nested conversation history accumulated so far, not just the delta for the next tool call.

## Data Shape And APIs Represented

The JSON mirrors the `llmRequest` struct local to `sources/test-tools/syzkaller/pkg/aflow/runner_test.go:testFlow`:

- `Model`: every complete request object visible in this range uses `"sub-agent-model"`, the model configured on the nested `LLMTool`.
- `Request`: serialized `[]*genai.Content` conversation history passed to `GenerateContent`.
- `parts`: one-element content payloads containing prompt text, a `functionCall`, or a `functionResponse`.
- `functionCall`: tool-call parts use `id: "id1"`, `name: "researcher-tool"`, and integer `args.Arg` values.
- `functionResponse`: response parts use the same `id` and `name`; no payload is serialized because the registered Go callback returns `struct{}{}`.
- `role`: visible prompt, call, and response content is stored with `"role": "user"`, matching the test stub's synthetic response content and aflow's generated tool-response messages.

The executable APIs exercised by this fixture are `LLMTool` and its `llmToolArgs`/`llmToolResults` bridge, `LLMAgent` and `agentSession.chat`, typed tool construction through `NewFuncTool`, request capture in `testFlow`, and Gemini content structures from `google.golang.org/genai`.

## Control Flow Captured In This Chunk

The represented runtime flow is:

1. The parent `LLMAgent` has already received a synthetic `FunctionCall` for the `researcher` LLM tool.
2. `LLMTool.execute` converts the parent tool args into `llmToolArgs`, stores the question in `ctx.state[AFLOW_LLMTOOL_PROMPT]`, and executes its internal nested `LLMAgent`.
3. `LLMTool.verify` has built that nested agent with `Prompt: "{{.AFLOW_LLMTOOL_PROMPT}}"`, `Reply: "AFLOW_LLMTOOL_REPLY"`, model `"sub-agent-model"`, and the nested `researcher-tool`.
4. `agentSession.chat` sends `GenerateContent` with prompt text `"What do you think?"` plus retained tool-call history.
5. The test stub returns a synthetic `functionCall` for `researcher-tool` with the next `Arg` value.
6. `agentSession.callTools` executes the registered function tool, appends a matching `functionResponse`, and the next request resends the expanded history.

Observed boundaries in this range:

- Leading partial request: the range begins at line 709386 inside the response for `Arg: 43`, then includes complete pairs from `Arg: 44` through `Arg: 237`.
- Complete request beginning at line 714247: prompt plus retained pairs from `Arg: 0` through `Arg: 238`.
- Complete request beginning at line 720235: prompt plus retained pairs from `Arg: 0` through `Arg: 239`.
- Complete request beginning at line 726248: prompt plus retained pairs from `Arg: 0` through `Arg: 70`; the next `Arg: 71` call begins after the assigned range.

## State And Persistence Behavior

This file is persistent golden test state. `runner_test.go:testFlow` captures each `GenerateContent` call as `{Model, Config, Request}`, deep-copies config only when it differs from the previous request, clones the request slice, JSON-normalizes captured values through marshal/unmarshal, and compares the result with `testdata/TestLLMToolMaxIters.llm.json` unless the test is run with update behavior.

Runtime state represented by the chunk is append-only nested-agent conversation history:

- `agentSession.req` starts with the nested prompt content and grows by appending each model tool-call content and each generated tool-response content.
- `LLMTool.execute` uses `ctx.state` as a temporary bridge for `AFLOW_LLMTOOL_PROMPT` and `AFLOW_LLMTOOL_REPLY`, deleting the prompt after execution and deleting the reply after extracting it.
- `researcher-tool` returns `struct{}{}`, so the serialized responses mainly validate identity, ordering, and absence of unexpected result payloads.
- No sliding-window summary, context compression, answer-now retry, or token-overflow path is visible in this chunk; the request history is fully retained and repeatedly resent.

The chunk also demonstrates the quadratic fixture-growth cost of full-history golden data: adding only a few model iterations generates thousands of repeated JSON lines because every later request includes all prior tool events.

## Dependencies And Integration Points

Primary integration points:

- `sources/test-tools/syzkaller/pkg/aflow/llm_tool_test.go`: defines `TestLLMToolMaxIters`, constructs the parent `LLMAgent`, configures the `researcher` `LLMTool`, registers `researcher-tool`, generates synthetic `genai.Part` function calls for `range maxLLMIterations`, and expects final `Reply: "YES"`.
- `sources/test-tools/syzkaller/pkg/aflow/llm_agent.go`: defines `LLMAgent`, `agentSession`, `maxLLMIterations = 250`, the model-call loop, final-reply handling, tool execution, duplicate-call tracking, context-compression hooks, and max-iteration failure path.
- `sources/test-tools/syzkaller/pkg/aflow/llm_tool.go`: adapts an `LLMAgent` into a parent-callable tool and bridges question/answer values through `ctx.state`.
- `sources/test-tools/syzkaller/pkg/aflow/func_tool.go`: provides `NewFuncTool`, argument conversion, callback execution, and result conversion for the nested `researcher-tool`.
- `sources/test-tools/syzkaller/pkg/aflow/runner_test.go`: supplies the synthetic model stub, captures `llmRequest` objects, elides unchanged configs, and performs golden-file comparison.
- `sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.trajectory.json`: companion trajectory fixture for the same logical flow.
- `google.golang.org/genai`: provides `Content`, `Part`, `FunctionCall`, `FunctionResponse`, `GenerateContentConfig`, and response structures serialized into this JSON.

## Risks And Maintenance Notes

This chunk is mechanically repetitive but sensitive to small behavioral changes. Any change to request-history retention, content role assignment, function-call ID handling, empty-response serialization, config elision, or the order in which model responses and tool responses are appended will rewrite this region of the fixture.

The repeated `id: "id1"` value is intentional synthetic test input. aflow duplicate-loop detection must consider the changing argument map and sequence rather than keying only on call id or tool name; otherwise this max-iteration fixture would look like a repeated identical call. Conversely, if a future implementation requires globally unique function-call IDs, this golden data will need to change.

The assigned line range starts and ends inside JSON structures. Merge/reconciliation should combine this chunk with neighboring reports before making whole-file conclusions about the final `"Nothing."` sub-agent reply, the parent `"YES"` reply, or whether the overall test reaches the max-iteration guard.

## Test Signals

Concrete signals observed in this range:

- 18,648 fixture lines.
- 3 complete top-level request objects begin inside the assigned range.
- 3 visible `"Model": "sub-agent-model"` markers.
- 3 visible prompt text entries with `"What do you think?"`.
- 744 `functionCall` markers and 745 `functionResponse` markers; the extra response is from the leading partial boundary at the response for `Arg: 43`.
- 744 visible `Arg` fields, with visible values ranging from `0` through `239`.
- Visible local sequence resets occur at lines 714263, 720251, and 726264, each corresponding to a new full-history request snapshot.
- All visible tool events target `"researcher-tool"` and use `id: "id1"`.
- No `Config` block appears in this interior range, consistent with `testFlow` eliding unchanged generation config after earlier requests.
- No final text reply, parent answer, API error, token-overflow recovery, or max-iteration failure text appears in this chunk.

This chunk should continue to pass when aflow preserves full nested request history, deterministic tool-call ordering, empty-struct response serialization, argument-sensitive duplicate detection, and current `maxLLMIterations` semantics.
