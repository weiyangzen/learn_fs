# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json lines 746680-765327

## Scope

This chunk is an interior slice of the golden LLM request transcript for `TestLLMToolMaxIters`. The source file is serialized JSON testdata, not executable Go. The assigned range begins inside an already-open nested-agent request history and ends inside another replayed request, so it is not independently parseable as a complete JSON document.

The visible data belongs to the nested `"sub-agent-model"` used by an `LLMTool` named `researcher`. It records repeated `researcher-tool` function-call/function-response pairs while the nested agent approaches the `maxLLMIterations` boundary.

## Purpose

`TestLLMToolMaxIters` verifies that an LLM-backed tool can perform exactly `maxLLMIterations` nested LLM iterations without being rejected one iteration too early. The parent agent calls the `researcher` LLM tool with `Question: "What do you think?"`. The nested agent then repeatedly asks to call its own `researcher-tool` with incrementing integer `Arg` values, receives empty successful tool responses, eventually replies `"Nothing."`, and lets the parent continue to its final `"YES"` reply.

This chunk documents the late-loop replay region around arguments 90 through 245. It shows the accumulated nested-agent conversation being resent in full on every model call, rather than only the newest tool result. The apparent repetition and resets to `Arg: 0` are therefore expected request-history snapshots, not a runtime restart.

## Data Shape And APIs Represented

The serialized objects mirror the local `llmRequest` shape in `sources/test-tools/syzkaller/pkg/aflow/runner_test.go`:

- `Model`: visible request boundaries use `"sub-agent-model"` for the nested `LLMTool` agent.
- `Request`: an ordered `[]*genai.Content` conversation history passed to `GenerateContent`.
- `parts`: each content entry contains one part, either prompt text, a `functionCall`, or a `functionResponse`.
- `functionCall`: calls use `id: "id1"`, `name: "researcher-tool"`, and integer `args.Arg`.
- `functionResponse`: responses use the same id and name, with no visible response payload because the Go callback returns `struct{}{}`.
- `role`: visible request entries use `"user"`, matching the test stub's synthetic candidate role and the role used for tool responses.

The executable APIs exercised by this fixture include `LLMTool.declaration`, `LLMTool.execute`, `LLMTool.verify`, `LLMAgent.executeOne`, `agentSession.chat`, `agentSession.callTools`, `LLMAgent.parseResponse`, `LLMAgent.generateContent`, typed tool wrapping via `NewFuncTool`, and golden request capture through `testFlow`.

## Control Flow Captured In This Chunk

The runtime sequence represented here is:

1. The parent model has already called the `researcher` tool.
2. `LLMTool.execute` has converted the parent tool arguments into `llmToolArgs`, stored the question in `ctx.state[AFLOW_LLMTOOL_PROMPT]`, and started the nested `LLMAgent`.
3. The nested agent's prompt is rendered from `{{.AFLOW_LLMTOOL_PROMPT}}`, producing `"What do you think?"`.
4. Each nested `GenerateContent` call receives the prompt plus all prior `researcher-tool` calls and responses.
5. The stubbed LLM returns the next synthetic `functionCall`.
6. `agentSession.callTools` executes the registered `NewFuncTool` callback, appends a matching `functionResponse`, and the next model request replays the longer history.

Observed boundaries in lines 746680-765327:

- Leading partial request: the request started before the chunk; visible complete pairs run from `Arg: 90` through `Arg: 243`.
- Request starting at line 750550: full visible replay with prompt `"What do you think?"`, then `Arg: 0` through `Arg: 244`.
- Request starting at line 756688: full visible replay with prompt, then `Arg: 0` through `Arg: 245`.
- Trailing partial request starting at line 762851: full visible replay begins again with prompt and reaches visible `Arg: 98` before the chunk ends.

The jump from `Arg: 243` to a new request starting at `Arg: 0` is the critical fixture signal. It confirms `agentSession.req` persists all earlier messages and is cloned into each golden `GenerateContent` request.

## State And Persistence Behavior

This file is persistent golden test state. `runner_test.go:testFlow` captures each model call, elides unchanged `Config` blocks, stores cloned request slices, JSON-normalizes captured values through a marshal/unmarshal round trip, and compares them to `testdata/TestLLMToolMaxIters.llm.json` unless the test is run with `-update`.

Runtime state visible in the chunk is append-only conversation state:

- `agentSession.req` starts with the nested prompt and grows by appending one model function-call content and one tool-response content per iteration.
- `LLMTool.execute` bridges data through `ctx.state`: `AFLOW_LLMTOOL_PROMPT` supplies the nested prompt, and `AFLOW_LLMTOOL_REPLY` receives the nested final answer in later chunks.
- The `researcher-tool` callback returns `struct{}{}`, so response records are intentionally empty except for id/name metadata.
- The repeated `id: "id1"` is intentional synthetic test input. Duplicate-call detection should not treat these calls as identical because the `Arg` value changes each time.
- No `Config` object is visible in this range, which is consistent with golden capture storing configs only when they differ from the previous captured request.

No durable application state is updated by the fixture itself. Its persistence role is to lock down request serialization, iteration behavior, role assignment, function-call id/name preservation, argument conversion, and empty result serialization for the Go test.

## Dependencies And Integration Points

Key source integration points:

- `sources/test-tools/syzkaller/pkg/aflow/llm_tool_test.go`: defines `TestLLMToolMaxIters`, creates the parent `LLMAgent`, constructs the nested `LLMTool`, registers `researcher-tool`, generates synthetic replies for `range maxLLMIterations`, and expects final output `Reply: "YES"`.
- `sources/test-tools/syzkaller/pkg/aflow/llm_tool.go`: adapts a nested `LLMAgent` into a parent-callable function tool and uses `ctx.state` keys `AFLOW_LLMTOOL_PROMPT` and `AFLOW_LLMTOOL_REPLY`.
- `sources/test-tools/syzkaller/pkg/aflow/llm_agent.go`: owns `maxLLMIterations = 250`, the model-call loop, full conversation history, tool execution, duplicate-call checking, final-reply validation, input-overflow handling, and `tryAnswerNow` behavior for LLM tools.
- `sources/test-tools/syzkaller/pkg/aflow/func_tool.go`: implements `NewFuncTool`, schema declarations, state conversion, argument conversion, callback invocation, and result-to-map conversion for the synthetic nested tool.
- `sources/test-tools/syzkaller/pkg/aflow/runner_test.go`: provides the synthetic `GenerateContent` stub and golden `.llm.json` comparison.
- `sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.trajectory.json`: companion golden trajectory for the same execution, recording flow/agent/LLM/tool spans rather than raw request bodies.
- `google.golang.org/genai`: supplies the serialized `GenerateContentConfig`, `Content`, `Part`, `FunctionCall`, and `FunctionResponse` structures.

## Risks And Maintenance Notes

This region is mechanically repetitive but highly sensitive. Changes to any of the following will rewrite large portions of this chunk:

- `maxLLMIterations` value or loop condition in `agentSession.chat`.
- Whether the full history or a summarized/sliding-window history is sent for this test.
- Tool response role, function-call id preservation, tool name spelling, or empty `struct{}{}` serialization.
- Golden capture behavior for unchanged configs.
- Argument schema or JSON field naming for `toolArgs.Arg`.
- Duplicate-call logic if it starts rejecting repeated ids even when arguments differ.

The chunk boundaries are partial JSON boundaries. Whole-file synthesis must merge adjacent chunk reports before making conclusions about JSON validity, the final `Arg: 249` call, the forced best-effort answer path, the nested final `"Nothing."` reply, or the parent final `"YES"` reply. This range alone shows no input-overflow error, no final text answer, and no max-iteration error.

## Test Signals

Concrete signals observed in lines 746680-765327:

- 18,648 source lines and about 262,124 bytes of fixture text.
- 3 visible `"Model": "sub-agent-model"` request boundaries, plus one leading request that began before the chunk.
- 3 visible prompt text entries containing `"What do you think?"`.
- 744 `functionCall` markers, 744 `functionResponse` markers, and 744 visible `Arg` fields.
- 0 visible `Config` blocks.
- Visible argument runs: `90-243`, `0-244`, `0-245`, and `0-98`.
- All visible tool calls and responses use `id: "id1"` and `name: "researcher-tool"`.
- No visible parent-agent request boundary, final text response, `Answer` payload, API error, or `"agent reached max iterations limit"` error.

Useful regression checks for this chunk are exact golden comparison of `TestLLMToolMaxIters.llm.json`, trajectory comparison against `TestLLMToolMaxIters.trajectory.json`, and targeted tests that confirm a nested `LLMTool` may consume exactly 250 tool-calling iterations before producing its final reply.
