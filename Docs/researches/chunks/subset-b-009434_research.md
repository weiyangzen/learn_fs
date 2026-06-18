# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json lines 560185-578836

## Scope

This chunk is an interior slice of the golden LLM request transcript for `TestLLMToolMaxIters`. The file is JSON testdata rather than executable Go code, and this assigned line range is not independently parseable JSON because it begins inside a prior request's function-response/call history and ends inside the next request's partially opened `functionResponse` object.

The visible data records repeated nested-agent requests to `"sub-agent-model"` while an `LLMTool` named `researcher` runs its own `LLMAgent` and repeatedly invokes a function tool named `researcher-tool`. This range finishes one already-started request snapshot, contains three complete subsequent snapshots, and begins a fifth snapshot.

## Purpose

`TestLLMToolMaxIters` verifies that an LLM-backed tool can execute through a long nested tool-call sequence bounded by `maxLLMIterations`. The parent agent receives a synthetic model reply that calls the `researcher` LLM tool with `Question: "What do you think?"`. The sub-agent then receives synthetic replies that call `researcher-tool` once per model round for `range maxLLMIterations`, where `maxLLMIterations` is `250`. After those tool calls, the sub-agent returns `"Nothing."`, then the parent returns `"YES"`.

This chunk validates late-loop request-history accumulation. Each new `"sub-agent-model"` request snapshot starts with the prompt text `"What do you think?"`, then replays all prior `researcher-tool` `functionCall`/`functionResponse` pairs from `Arg: 0` upward. The apparent resets from high `Arg` values back to `0` are request-boundary resets in the serialized golden transcript, not runtime counter resets.

## Data Shape And APIs Represented

The serialized objects mirror the `llmRequest` struct local to `runner_test.go:testFlow`:

- `Model`: every complete request boundary in this chunk uses `"sub-agent-model"`.
- `Request`: a slice of `genai.Content` objects representing the nested agent's prompt and accumulated tool history.
- `parts`: normally contains one prompt, `functionCall`, or `functionResponse` part.
- `functionCall`: uses `id: "id1"`, `name: "researcher-tool"`, and `args.Arg` with an integer loop counter.
- `functionResponse`: uses the same `id` and tool name with no response payload, matching the Go function tool's `struct{}{}` return.
- `role`: all visible entries use `"user"`, because the test harness wraps synthetic response parts as `genai.RoleUser`.

The executable APIs exercised by this fixture are outside the JSON shard:

- `LLMTool` exposes the nested agent as the parent model's `researcher` tool.
- `LLMAgent` and `agentSession.chat` own the model-call loop, request history, tool execution, max-iteration limit, and final-reply validation.
- `NewFuncTool` registers `researcher-tool` with typed args containing `Arg int`.
- `testFlow` stubs `GenerateContent`, records every request passed to the model, normalizes captured data through JSON marshal/unmarshal, and compares it with this `.llm.json` golden file.
- `google.golang.org/genai` supplies the serialized content, part, function-call, function-response, config, and model request structures.

## Control Flow Captured In This Chunk

The runtime sequence represented here is:

1. The parent `LLMAgent` calls the `researcher` `LLMTool`.
2. `LLMTool.execute` passes the question into the nested agent prompt.
3. The nested agent starts each model request with `"What do you think?"`.
4. For each synthetic model reply, `agentSession.chat` appends the model's `researcher-tool` `functionCall`, executes the tool, and appends the matching empty `functionResponse`.
5. The next `GenerateContent` call receives the full prompt plus all previously appended call/response content.
6. `testFlow` captures full request snapshots, so the golden fixture grows quadratically as the long iteration test advances.

Observed boundaries in this exact line range:

- Leading partial request: lines 560185-562020 show the tail of a request snapshot with complete visible `Arg: 138` through `Arg: 210` call/response pairs.
- Complete request beginning at line 562021: prompt text at the start of the `Request`, then `Arg: 0` through `Arg: 211`, ending before line 567334.
- Complete request beginning at line 567334: prompt text, then `Arg: 0` through `Arg: 212`, ending before line 572672.
- Complete request beginning at line 572672: prompt text, then `Arg: 0` through `Arg: 213`, ending before line 578035.
- Trailing partial request beginning at line 578035: prompt text and complete visible `Arg: 0` through `Arg: 31` function calls; the chunk ends immediately after opening the following `functionResponse` object.

No final text reply, parent-agent result, `Answer` object, or max-iteration error is visible in this range.

## State And Persistence Behavior

This JSON is persistent golden state for the aflow test suite. It is updated only through the test harness's `-update` path and is otherwise used as the expected request transcript for `TestLLMToolMaxIters`.

Runtime state represented in the chunk is append-only nested-agent conversation history:

- `agentSession.req` starts with the prompt and grows by appending model tool-call content and tool-response content after every model round.
- `LLMTool.execute` bridges the parent question and nested reply through context state keys; the visible prompt text is the serialized effect of that bridge.
- `researcher-tool` returns `struct{}{}`, so response entries preserve call ordering and identity but carry no body.
- `Config` is omitted in this range because `testFlow` only stores config when it changes from the previous request.
- Repeated `id: "id1"` values are fixture input from `llm_tool_test.go`, not evidence of production unique-ID generation.

The chunk is a direct example of the current full-history replay design. Late in the max-iteration test, adjacent model requests resend hundreds of previously recorded tool events.

## Dependencies And Integration Points

Important source integrations:

- `sources/test-tools/syzkaller/pkg/aflow/llm_tool_test.go`: defines `TestLLMToolMaxIters`, constructs the parent `LLMAgent`, registers the `researcher` `LLMTool`, builds synthetic replies with `maxLLMIterations` calls to `researcher-tool`, and expects final output `Reply: "YES"`.
- `sources/test-tools/syzkaller/pkg/aflow/llm_agent.go`: defines `maxLLMIterations = 250` and implements the chat loop that appends responses, calls tools, handles token overflow via `tryAnswerNow`, and returns a max-iteration error if no final answer is reached.
- `sources/test-tools/syzkaller/pkg/aflow/llm_tool.go`: adapts nested `LLMAgent` execution into a function-callable tool for the parent agent.
- `sources/test-tools/syzkaller/pkg/aflow/func_tool.go`: provides the typed function-tool wrapper used for `researcher-tool`.
- `sources/test-tools/syzkaller/pkg/aflow/runner_test.go`: captures the model requests and compares them against `testdata/TestLLMToolMaxIters.llm.json`.
- `sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.trajectory.json`: companion golden trajectory for spans from the same execution.

External dependency sensitivity is mainly through `google.golang.org/genai`: changes to content roles, part serialization, function-call encoding, empty function responses, or config omission would rewrite this fixture.

## Risks And Maintenance Notes

This fixture region is intentionally repetitive and therefore fragile to broad golden-file churn. Small changes to history append order, request snapshot strategy, function-call IDs, message roles, empty struct response encoding, or config-copy elision can alter thousands of lines.

Because this assigned range starts and ends inside JSON structures, local syntax validation is not meaningful. Whole-file validation and final interpretation must happen after adjacent chunks are merged.

The range does not cover the exact max-iteration boundary or final parent reply. Its signal is late-loop history retention: snapshots ending at `Arg: 210`, `211`, `212`, and `213`, followed by the beginning of the next snapshot.

## Test Signals

Concrete signals in lines 560185-578836:

- 18,652 source lines.
- 4 visible `"Model": "sub-agent-model"` boundaries.
- 4 visible `"Request"` boundaries.
- 4 visible prompt entries for `"What do you think?"`.
- 744 visible `functionCall` markers.
- 744 visible `functionResponse` markers.
- 744 visible complete `Arg` lines.
- 1,488 visible `"name": "researcher-tool"` lines.
- 1,488 visible `"id": "id1"` lines.
- 0 visible `Config` blocks.
- Argument runs by visible block: `138-210`, `0-211`, `0-212`, `0-213`, and `0-31`.

The test should continue to pass when the nested agent preserves prompt and tool history, appends call/response entries in the current order, and records full model requests. It should fail if request construction switches to deltas, changes role serialization, changes empty response serialization, or alters the `LLMTool` max-iteration/history behavior.
