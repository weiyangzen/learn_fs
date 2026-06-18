# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json lines 578837-597487

## Scope

This chunk is an interior slice of the golden LLM request transcript for `TestLLMToolMaxIters`. The source is JSON testdata, not executable Go code. It records serialized `llmRequest` entries captured by the aflow test harness while a parent `LLMAgent` invokes an `LLMTool` named `researcher`, whose nested sub-agent repeatedly calls `researcher-tool`.

The assigned range starts inside a previously opened `sub-agent-model` request snapshot, immediately after the `Arg: 31` tool call and at its matching `functionResponse`. It then includes the remainder of that request through `Arg: 214`, three later top-level request boundaries, two complete request snapshots through `Arg: 215` and `Arg: 216`, and the beginning of the next request through the opening of another `functionCall` after `Arg: 127`. The chunk is therefore not independently parseable JSON; it is meaningful as part of the larger golden fixture.

## Purpose

`TestLLMToolMaxIters` validates max-iteration handling for an LLM-backed tool. The parent agent first calls the `researcher` LLM tool with `Question: "What do you think?"`. The nested agent then calls its ordinary function tool, `researcher-tool`, once per generated model response for `maxLLMIterations` iterations before returning text to the parent. The parent finally returns the structured output `Reply: "YES"`.

This range exercises the late middle of that nested loop, where the serialized request history is already large. It verifies that every subsequent `GenerateContent` request to `"sub-agent-model"` resends the complete nested prompt and the full accumulated call/response history from `Arg: 0` upward, rather than only a delta. The repeated argument ranges are expected because every stored request object is a full snapshot of `agentSession.req` at that point in the loop.

## Data Shape And APIs Represented

The JSON mirrors the `llmRequest` structure built in `runner_test.go:testFlow`:

- `Model`: all visible complete top-level objects in this chunk use `"sub-agent-model"`.
- `Request`: a serialized slice of `genai.Content` messages for the nested agent.
- `parts`: one-element arrays containing prompt text, a `functionCall`, or a `functionResponse`.
- `functionCall`: uses `id: "id1"`, `name: "researcher-tool"`, and integer `args.Arg`.
- `functionResponse`: uses the same `id` and `name`; response payload is absent because the registered Go tool returns `struct{}{}`.

The executable APIs represented by this data are `LLMAgent` and `agentSession.chat` in `llm_agent.go`, `LLMTool` as the parent-facing tool adapter, typed tool construction via `NewFuncTool`, and the `google.golang.org/genai` content/function-call schema serialized by the test harness.

## Control Flow Captured In This Chunk

Runtime flow represented here:

1. The parent model has already called the `researcher` LLM tool.
2. The nested agent prompt is `"What do you think?"`.
3. Each model reply requests one `researcher-tool` invocation with the next integer `Arg`.
4. `agentSession.callTools` executes the registered Go tool and appends a matching `functionResponse`.
5. The next nested LLM request includes the original prompt plus all prior model tool calls and tool responses.

Observed boundaries in this exact line range:

- leading partial request: its top-level object begins before the chunk at line 578034; the chunk starts at the response for the already opened `Arg: 31`, then includes calls/responses for `Arg: 32` through `Arg: 214`;
- complete request beginning at line 583422: prompt plus `Arg: 0` through `Arg: 215`;
- complete request beginning at line 588835: prompt plus `Arg: 0` through `Arg: 216`;
- trailing request beginning at line 594273: prompt plus complete pairs through `Arg: 127`, then the chunk ends at the opening of the next `functionCall` before its `Arg` value is visible.

`maxLLMIterations` is defined as `250` in `llm_agent.go`, and `llm_tool_test.go` builds synthetic replies with `for i := range maxLLMIterations`. This chunk does not show the final `"Nothing."` nested reply or the parent `"YES"` reply; those occur later in the full fixture.

## State And Persistence Behavior

This file is persistent golden state for `TestLLMToolMaxIters`. In normal test runs, freshly captured request snapshots are JSON-normalized and compared against this fixture. With the harness update flag, `runner_test.go` rewrites the golden file from the actual execution.

Runtime state represented here is append-only nested-agent conversation history:

- `agentSession.req` starts with the nested prompt and grows by appending each model `functionCall` content and each tool-response content.
- The `researcher-tool` result is an empty struct, so the persisted function-response entries validate ordering, id/name association, and empty-result serialization.
- `runner_test.go` stores `Config` only when it changes from the previous LLM call. No `Config` object appears in this interior range, which indicates config elision rather than missing configuration.
- Request snapshots repeatedly restart at `Arg: 0` because each new model call receives full history.

The chunk is a concrete example of the quadratic fixture growth caused by full-history persistence: late iterations contain hundreds of repeated call/response entries in each stored request.

## Dependencies And Integration Points

Primary integration points:

- `sources/test-tools/syzkaller/pkg/aflow/llm_tool_test.go`: defines `TestLLMToolMaxIters`, the `researcher` LLM tool, the nested `researcher-tool`, and the synthetic reply stream.
- `sources/test-tools/syzkaller/pkg/aflow/llm_agent.go`: defines `maxLLMIterations = 250`, the chat loop, tool-call handling, token overflow answer-now handling, and the max-iteration error path.
- `sources/test-tools/syzkaller/pkg/aflow/llm_tool.go`: adapts a nested `LLMAgent` into a parent-callable tool and bridges question/reply through aflow state.
- `sources/test-tools/syzkaller/pkg/aflow/runner_test.go`: captures requests, omits repeated configs, marshals/unmarshals for stable comparison, and compares against this `.llm.json` fixture.
- `sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.trajectory.json`: companion golden span trace for the same execution.
- `google.golang.org/genai`: provides `GenerateContentConfig`, `Content`, `Part`, `FunctionCall`, and `FunctionResponse` structures serialized here.

## Risks And Maintenance Notes

This region is highly repetitive, so small behavior changes can produce very large golden diffs. Changes to message roles, request-history retention, empty response encoding, config elision, function-call id handling, or the max-iteration constant will rewrite many lines.

The repeated `id1` value is intentional in the synthetic test replies. Duplicate-call detection must account for arguments and history semantics, not treat this fixture as proof that call ids are globally unique. The absence of function-response payloads is also intentional because `researcher-tool` returns `struct{}{}`.

The line range begins and ends inside JSON objects. Merge/reconciliation tooling should combine this with adjacent chunks before making whole-file conclusions. In this chunk, marker counts are balanced only because the leading unmatched call is paired by its response and the trailing opened call is not yet paired inside the range.

## Test Signals

Useful signals observed in this range:

- 3 visible `"Model": "sub-agent-model"` top-level boundaries inside the chunk, plus a leading partial object that began before the range.
- 3 prompt text entries with `"What do you think?"`; the leading partial object's prompt is outside this chunk.
- 745 `functionCall` markers and 745 `functionResponse` markers.
- 744 visible `Arg` values: `32` through `214`, then `0` through `215`, `0` through `216`, and `0` through `127`.
- No `Config` block appears in this interior range.
- All visible tool events target `"researcher-tool"` with id `"id1"`.
- No final sub-agent text, parent final reply, or max-iteration error appears in this chunk.

The fixture should continue to pass while aflow preserves full nested-agent history, call/response ordering, empty tool-response serialization, and the current `maxLLMIterations` loop semantics.
