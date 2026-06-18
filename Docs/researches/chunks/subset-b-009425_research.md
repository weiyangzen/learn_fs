# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json lines 392290-410946

## Scope

This chunk covers lines 392290-410946 of `sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json`. The source is a large golden JSON fixture, not executable Go code. It stores serialized LLM requests captured by the aflow test harness for `TestLLMToolMaxIters`, where a parent `LLMAgent` calls an `LLMTool` named `researcher`, and that nested agent repeatedly calls its own function tool named `researcher-tool`.

The requested range is an interior slice of the full fixture. It begins inside an existing nested sub-agent request history, immediately after a `functionResponse`, and then continues with a visible `researcher-tool` call at `Arg: 19`. It contains four `"Model": "sub-agent-model"` request records and stops inside the fourth visible request after the matching response for `Arg: 48`; the next `Arg: 49` call begins just after the range. The slice is therefore source-valid only as part of the complete JSON file, not as a standalone JSON document.

Within the exact range there are 18,657 lines, 744 `functionCall` markers, 745 `functionResponse` markers, 4 `"Model"` entries, 4 `"Request"` entries, 0 `"Config"` entries, and 4 prompt entries for `"What do you think?"`. The extra response count comes from the range starting with a response whose corresponding call is in the previous chunk.

The visible `Arg` runs are:

- `19..176`, completing a request object that began before this chunk.
- `0..177`, a complete visible sub-agent request-history object.
- `0..178`, another complete visible sub-agent request-history object.
- `0..179`, another complete visible sub-agent request-history object.
- `0..48`, the beginning of the next request object, with the `Arg: 49` call outside this chunk.

## Purpose

`TestLLMToolMaxIters.llm.json` is persistent golden testdata for `pkg/aflow`. It pins the exact `genai.GenerateContent` request payloads emitted by `runner_test.go:testFlow` while running `llm_tool_test.go:TestLLMToolMaxIters`.

The associated Go test builds a root `LLMAgent` whose first mocked model reply calls the `researcher` LLM tool with question `"What do you think?"`. `LLMTool` then runs a nested `LLMAgent` on `"sub-agent-model"`. That sub-agent calls `researcher-tool` once for every `i` in `range maxLLMIterations`, using args `{ "Arg": i }`, then returns text `"Nothing."`; the parent agent finally returns `"YES"`.

This chunk documents a late-middle section of that nested tool loop. Its primary value is validating request-history persistence: every later sub-agent request repeats the original prompt and all prior nested tool calls and responses, then adds the next model-requested call. The repeated restarts at `Arg: 0` are expected because each top-level JSON record stores a full outbound request snapshot rather than only the newly appended conversation turn.

## Important APIs, Types, And Data Shape

The fixture entries are produced by the local `llmRequest` type inside `runner_test.go:testFlow`:

- `Model`: the resolved model string, here `"sub-agent-model"` for all visible request records.
- `Config`: optional `*genai.GenerateContentConfig`; absent in this chunk because `testFlow` stores it only when it differs from the previous recorded request.
- `Request`: the accumulated `[]*genai.Content` request history sent to `generateContent`.

The repeated JSON elements in this slice map to these runtime constructs:

- `LLMAgent`: owns `agentSession.chat`, the request history slice, model calls, reply parsing, and max-iteration guard.
- `LLMTool`: exposes a nested `LLMAgent` as a parent-agent function tool named `researcher`.
- `Tool` and `NewFuncTool`: define the nested `researcher-tool` callback used by the sub-agent.
- `genai.Content` and `genai.Part`: serialized as `role`, `parts`, `text`, `functionCall`, and `functionResponse`.
- `genai.FunctionCall`: serialized with `id: "id1"`, `name: "researcher-tool"`, and integer `args.Arg`.
- `genai.FunctionResponse`: serialized with the same `id` and `name`; no response body is visible because the test tool returns `struct{}{}`.

No tool declaration appears in this slice. That is not a missing field; the unchanged sub-agent config and tool declaration were recorded earlier in the fixture and omitted from repeated request records by the test harness's config-compression rule.

## Control Flow Represented

The represented runtime flow is an unrolled nested-agent chat loop:

1. A parent model has already requested the `researcher` LLM tool before this range.
2. `LLMTool.execute` has stored the parent question in `ctx.state` under `AFLOW_LLMTOOL_PROMPT` and started its internal agent.
3. The nested agent sends `generateContent` requests to `"sub-agent-model"` with prompt `"What do you think?"`.
4. The mocked sub-agent model reply contains one `researcher-tool` `FunctionCall` for the next integer `Arg`.
5. `agentSession.chat` appends the model content to `a.req`.
6. `agentSession.callTools` invokes the Go `NewFuncTool("researcher-tool", ...)` callback and appends a matching `FunctionResponse` content item.
7. The next LLM iteration sends the whole accumulated `a.req` slice back to the model.
8. `testFlow` records that whole request before returning the next scripted reply.

`maxLLMIterations` is 250 in `llm_agent.go`. The test intentionally appends 250 nested `researcher-tool` replies before the final `"Nothing."` text reply, so these `Arg` values serve as an oracle for ordering and iteration-count behavior. This chunk covers request histories around logical endings 176, 177, 178, and 179, then begins the next request history through `Arg: 48`.

The chunk boundaries matter. The opening response belongs to a call serialized in the previous chunk. The closing line includes a complete response for `Arg: 48`, while the following `Arg: 49` call starts outside the requested range. Per-chunk validation must not require every edge pair to be self-contained.

## State And Persistence Behavior

The file itself is durable repository state. `testFlow` compares captured requests against `testdata/TestLLMToolMaxIters.llm.json`, or rewrites the fixture only when the test suite runs with `-update`. The chunk does not perform runtime I/O, cache writes, network calls, or database updates by itself.

The runtime state encoded here is the nested `agentSession.req` conversation history:

- The initial prompt remains the first content item in every visible sub-agent request.
- Each model function call is appended as a content item.
- Each tool execution result is appended as a corresponding `functionResponse`.
- The nested agent preserves all prior calls and responses rather than resetting history after each tool invocation.
- The serialized request history grows by one call/response pair per successful tool iteration.

`LLMTool` also uses `ctx.state` for parent/sub-agent handoff via `AFLOW_LLMTOOL_PROMPT` and `AFLOW_LLMTOOL_REPLY`, but those keys are not directly serialized in this JSON chunk. The empty function responses reflect the nested tool implementation returning `struct{}{}` with no meaningful payload.

## Dependencies And Integration Points

This chunk is tied to these source-tree components:

- `sources/test-tools/syzkaller/pkg/aflow/llm_tool_test.go`: defines `TestLLMToolMaxIters`, the `toolArgs` struct with `Arg int`, the `researcher` LLM tool, and the nested `researcher-tool` callback.
- `sources/test-tools/syzkaller/pkg/aflow/runner_test.go`: defines `testFlow`, the mocked `generateContent` callback, request capture, JSON round-trip normalization, and golden-file comparison.
- `sources/test-tools/syzkaller/pkg/aflow/llm_agent.go`: defines `maxLLMIterations`, `agentSession.chat`, `parseResponse`, `callTools`, request-history append behavior, context compression hooks, and final max-iteration error handling.
- `sources/test-tools/syzkaller/pkg/aflow/llm_tool.go`: defines `LLMTool`, its Gemini function declaration, and the state handoff used to run a nested agent as a tool.
- `sources/test-tools/syzkaller/pkg/aflow/func_tool.go`: provides the function-tool adapter that turns the Go callback result into a function response map.
- `google.golang.org/genai`: provides the concrete request, response, content, part, function-call, function-response, and config types serialized into this fixture.

The paired `TestLLMToolMaxIters.trajectory.json` fixture validates the span-level execution view for the same test. This `.llm.json` file validates exact model request payload shape and request-history accumulation.

## Risks And Edge Cases

- The fixture is very large and repetitive. A small manual edit to one comma, brace, call id, tool name, or integer argument can invalidate the JSON or break golden equality.
- This line range is not standalone JSON. It begins and ends inside larger request-history structures.
- Counting `Arg` fields in the chunk overcounts unique logical tool executions because later request snapshots replay earlier history.
- The call id `"id1"` is intentionally reused by the mocked replies. Unique call IDs across the entire fixture are not a valid invariant for this test.
- All visible nested tool calls and responses use role `"user"` because `testFlow` wraps scripted replies in a `genai.Content` with `RoleUser`. That role assignment is part of the current golden contract.
- Missing `Config` entries in this chunk are intentional. Config and tool declarations are unchanged from earlier recorded requests.
- Changes to `maxLLMIterations`, request-history trimming, context compression thresholds, empty-struct JSON serialization, Gemini SDK field names, or function-call response formatting will cascade through many lines of this fixture.
- The range includes one more `functionResponse` than `functionCall` because of the opening boundary. A chunk-local checker should account for boundary-split pairs instead of flagging this as an error.

## Test Signals

The direct validation signal is the aflow Go test using this golden file:

- `TestLLMToolMaxIters` should pass when generated requests match `testdata/TestLLMToolMaxIters.llm.json`.
- The full JSON file should remain parseable as a top-level request array.
- The requested range should contain 744 `functionCall` markers and 745 `functionResponse` markers because of the leading split response.
- The visible request records should use `"Model": "sub-agent-model"` and preserve the prompt text `"What do you think?"`.
- Within each complete visible request object, `Arg` values should increase monotonically from `0` to the request's current end.
- Completed visible calls should have matching `functionResponse` records with `id: "id1"` and `name: "researcher-tool"`.
- The companion trajectory fixture should still show nested `researcher-tool` spans and the eventual successful parent output when reconciled with the full source file.

This chunk does not expose independently executable logic. Its regression value is as part of the exact serialized request transcript for the `LLMAgent` and `LLMTool` max-iteration scenario.
