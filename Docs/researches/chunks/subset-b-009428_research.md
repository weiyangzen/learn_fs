# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json lines 448262-466916

## Scope

This chunk covers lines 448262-466916 of `sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json`. The source is generated golden JSON testdata, not executable Go code. It stores serialized LLM request snapshots captured by the aflow test harness while `TestLLMToolMaxIters` exercises a parent `LLMAgent` calling an `LLMTool` named `researcher`, whose nested sub-agent repeatedly calls a function tool named `researcher-tool`.

The requested range is an interior slice of a much larger JSON array. It starts inside the `args` object for a visible `researcher-tool` call with `Arg: 61`, contains several complete and partial nested request histories, and ends on the `Arg: 43` line of a trailing `functionCall` whose remaining fields and matching response continue after this chunk. The range is therefore not standalone parseable JSON; it is meaningful as part of the complete fixture.

Within this exact line range there are 18,655 source lines, 744 `functionCall` markers, 744 `functionResponse` markers, 4 `"Model": "sub-agent-model"` records, 4 `"Request"` records, 0 `"Config"` records, and 4 prompt text entries for `"What do you think?"`.

The visible `Arg` runs are:

- `61..188`, finishing a request object that began before this chunk.
- `0..189`, a complete visible sub-agent request-history object.
- `0..190`, another complete visible sub-agent request-history object.
- `0..191`, another complete visible sub-agent request-history object.
- `0..43`, the beginning of the next request object; the chunk ends before the rest of the `Arg: 43` call.

## Purpose

`TestLLMToolMaxIters.llm.json` is the durable request-log oracle for `pkg/aflow`'s `TestLLMToolMaxIters`. The Go test builds a root `LLMAgent` whose first mocked model reply calls the `researcher` LLM tool with `Question: "What do you think?"`. `LLMTool` then runs an internal `LLMAgent` on `"sub-agent-model"`. That nested agent calls `researcher-tool` once for every value in `range maxLLMIterations`, then returns text `"Nothing."`; the parent model finally returns `"YES"`.

This chunk documents a late-middle part of the nested tool loop. Its primary behavioral signal is request-history persistence. Each new sub-agent LLM request resends the original prompt plus all prior nested `functionCall` and `functionResponse` entries, so later fixture records repeatedly restart at `Arg: 0` rather than storing only the newest delta.

The visible calls around `Arg: 189`, `190`, and `191` show that the nested agent is still below the `maxLLMIterations = 250` guard and continues to accept tool calls before the final text reply appears in a later chunk.

## Important APIs, Types, And Data Shape

The JSON shape corresponds to the local `llmRequest` type in `runner_test.go:testFlow`:

- `Model`: the model passed to the stubbed `generateContent`; all visible request records in this range use `"sub-agent-model"`.
- `Config`: optional `*genai.GenerateContentConfig`; absent in this chunk because `testFlow` records config only when it changes from the previous captured request.
- `Request`: the accumulated `[]*genai.Content` conversation history sent to the model.

The repeated JSON elements map to these runtime constructs:

- `LLMAgent` and `agentSession.chat` own the model-call loop, request history, tool execution, reply parsing, and max-iteration guard.
- `LLMTool` adapts a nested `LLMAgent` into a parent-agent function tool named `researcher`.
- `NewFuncTool` creates the nested `researcher-tool` callback used by `TestLLMToolMaxIters`.
- `genai.Content` and `genai.Part` serialize as `role`, `parts`, `text`, `functionCall`, and `functionResponse`.
- `genai.FunctionCall` is represented with `id: "id1"`, `name: "researcher-tool"`, and `args.Arg`.
- `genai.FunctionResponse` is represented with the same `id` and `name`; there is no response payload because the test callback returns `struct{}{}`.

No tool declaration or system instruction appears in this slice. That is expected: the sub-agent config was recorded earlier in the fixture, and unchanged config is omitted from subsequent `llmRequest` records by the golden-file harness.

## Control Flow Represented

The runtime flow encoded by this range is:

1. The parent agent has already invoked the `researcher` LLM tool before this line range.
2. `LLMTool.execute` has stored the parent question in `ctx.state[AFLOW_LLMTOOL_PROMPT]` and started its internal agent with prompt `"What do you think?"`.
3. The nested agent sends a `generateContent` request to `"sub-agent-model"` using its accumulated `agentSession.req` history.
4. The mocked model response requests one `researcher-tool` call with the next integer `Arg`.
5. `agentSession.callTools` invokes the Go callback and appends a matching `functionResponse`.
6. The next LLM request resends the entire accumulated history, including all earlier calls and responses.
7. `runner_test.go:testFlow` captures that outbound request and later compares it with this `.llm.json` fixture.

The exact chunk boundaries are important. The opening line is already inside the `Arg: 61` call of a request object that began earlier. The next complete visible request histories end at `Arg: 189`, `Arg: 190`, and `Arg: 191`. The final visible request begins at line 465824 and reaches only the `Arg: 43` value before the chunk ends, so its call record is split across chunks.

## State And Persistence Behavior

The fixture itself is persistent repository testdata. It is compared during test execution and regenerated only when the aflow test suite is run with its `-update` path. This JSON chunk performs no runtime I/O, cache mutation, locking, or database work on its own.

The runtime state captured here is the nested agent's append-only conversation history:

- The initial prompt remains present at the start of every visible nested request record.
- Each model-requested tool call is appended as a content part.
- Each Go tool result is appended as a corresponding `functionResponse`.
- The nested agent does not reset history between tool calls.
- The repeated full-history snapshots make the fixture grow quadratically in this max-iteration scenario.

`LLMTool` also uses workflow state for parent/sub-agent handoff: `AFLOW_LLMTOOL_PROMPT` carries the parent question into the nested agent, and `AFLOW_LLMTOOL_REPLY` carries the nested final answer back to `LLMTool.execute`. Those state keys are not serialized directly in this chunk, but the prompt text and nested model records are downstream evidence of that handoff.

## Dependencies And Integration Points

This chunk is tied to these source-tree components:

- `sources/test-tools/syzkaller/pkg/aflow/llm_tool_test.go`: defines `TestLLMToolMaxIters`, the `toolArgs` struct with `Arg int`, the `researcher` LLM tool, and the nested `researcher-tool` callback returning `struct{}{}`.
- `sources/test-tools/syzkaller/pkg/aflow/llm_agent.go`: defines `maxLLMIterations = 250`, `agentSession.chat`, request-history handling, tool-call execution, answer-now handling, and the max-iteration failure path.
- `sources/test-tools/syzkaller/pkg/aflow/llm_tool.go`: defines `LLMTool`, its Gemini function declaration, nested-agent verification, and `ctx.state` prompt/reply bridge.
- `sources/test-tools/syzkaller/pkg/aflow/func_tool.go`: adapts typed Go callbacks into aflow `Tool` implementations and supplies the empty response body seen here.
- `sources/test-tools/syzkaller/pkg/aflow/runner_test.go`: defines `testFlow`, stubs `generateContent`, records `llmRequest` snapshots, JSON-normalizes them, and compares them with `testdata/TestLLMToolMaxIters.llm.json`.
- `google.golang.org/genai`: supplies the request, config, content, part, function-call, and function-response types serialized by the fixture.

The companion `sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.trajectory.json` validates span-level execution for the same scenario, while this `.llm.json` fixture validates exact model request payloads and history growth.

## Risks And Edge Cases

- The line range is not standalone JSON because it starts inside a call argument and ends before a trailing call is complete.
- Chunk-local call/response counts happen to balance at 744 each, but this does not mean all visible edge pairs are self-contained. Both the opening and closing boundaries split structures.
- Counting `Arg` occurrences in this range overcounts unique runtime tool executions because complete request records replay the same historical calls from `Arg: 0`.
- The repeated function-call ID `"id1"` is intentional in the mocked replies. Global call-ID uniqueness is not an invariant for this test fixture.
- Role values are serialized as `"user"` for model reply and tool-response content because `testFlow` wraps scripted replies in user-role `genai.Content`.
- Missing `Config` blocks are intentional harness compression, not a missing tool declaration.
- Changes to `maxLLMIterations`, request-history retention, context compression, Gemini SDK JSON field names, function-response encoding for `struct{}{}`, or tool-call ID handling will create large golden diffs across this repetitive region.
- Manual edits in this file are high risk: a single missed comma, brace, tool name, or `Arg` value can invalidate the full fixture or break equality with captured requests.

## Test Signals

Primary validation comes from `TestLLMToolMaxIters` passing against the full golden file. Useful signals for this chunk are:

- The complete `TestLLMToolMaxIters.llm.json` file remains parseable as a top-level JSON array.
- Lines 448262-466916 contain 744 `functionCall` markers and 744 `functionResponse` markers.
- All visible request records use `"Model": "sub-agent-model"` and include prompt text `"What do you think?"`.
- Complete visible request histories restart at `Arg: 0` and increase monotonically through `Arg: 189`, `190`, and `191`.
- Completed visible tool calls have matching `functionResponse` entries with `id: "id1"` and `name: "researcher-tool"`.
- No final nested `"Nothing."` reply, parent `"YES"` reply, or max-iteration error appears in this chunk; those whole-file outcomes must be reconciled from later lines and the companion trajectory fixture.

This chunk does not expose an independently executable unit. Its regression value is preserving the exact serialized request transcript for aflow's nested `LLMAgent` and `LLMTool` max-iteration behavior.
