# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json lines 186963-205637

## Scope

This chunk covers a middle slice of the golden LLM request transcript for `TestLLMToolMaxIters`. The file is JSON testdata, not executable Go code. It records the `genai.GenerateContent` requests produced by the aflow test harness while a parent `LLMAgent` invokes an `LLMTool` named `researcher`, and that nested agent repeatedly invokes its own function tool named `researcher-tool`.

The requested range starts inside one already-running sub-agent request, at a `researcher-tool` call with `Arg: 29`, and ends inside another sub-agent request after the matching response for `Arg: 25`. Within the range there are 18,675 lines, 6 complete `"Model": "sub-agent-model"` request objects, 744 serialized `functionCall` entries, 744 matching `functionResponse` entries, and 6 prompt text entries. The visible `Arg` runs are:

- `29..121`, continuing a request object that began in the previous chunk.
- `0..122`, `0..123`, `0..124`, `0..125`, and `0..126`, each in a complete visible sub-agent request object.
- `0..25`, beginning a request object that continues into the next chunk.

The range therefore captures the expanding request-history behavior of the max-iteration test, rather than a standalone logical scenario.

## Purpose

`TestLLMToolMaxIters.llm.json` is the golden request log used by `pkg/aflow` tests to detect regressions in how nested LLM agents build Gemini requests. The associated Go test constructs replies where the main agent first calls an `LLMTool` named `researcher`. The nested `LLMTool` agent then calls `researcher-tool` `maxLLMIterations` times before returning text, and finally the parent agent returns `"YES"`.

This chunk specifically proves that the nested `LLMTool` request history grows monotonically and preserves every prior tool call/response pair as new sub-agent LLM calls are made. Each repeated request includes:

- The sub-agent model name, `"sub-agent-model"`.
- The sub-agent prompt text, `"What do you think?"`.
- A sequence of `functionCall` parts for `"researcher-tool"` with integer `Arg` values.
- A matching `functionResponse` part after each call.
- User-role content entries for both prompt and tool-response messages, matching the test harness serialization.

The important behavioral signal is that reaching the normal `maxLLMIterations` boundary is represented by many successive LLM requests and matching tool responses, not by a dropped context, malformed tool response, or premature final text.

## Important APIs, Types, And Data Shape

The JSON shape is produced by the aflow unit-test harness in `runner_test.go`, which records each mocked `generateContent` call as an object containing `Model`, optional `Config`, and `Request`. `Config` is omitted from repeated requests when it matches the previous request configuration; this explains why most complete objects in this chunk show only `"Model"` and `"Request"` even though the initial request in the file includes the full sub-agent function declaration.

The relevant runtime types represented by this data are:

- `LLMAgent`, whose `chat` loop stores the active request history in `agentSession.req` and appends model responses plus tool responses on every iteration.
- `LLMTool`, which wraps a nested `LLMAgent` and exposes it as a parent-agent function declaration. The parent passes the `Question` argument through the temporary `AFLOW_LLMTOOL_PROMPT` state key.
- `Tool` / `NewFuncTool`, represented here by the nested `"researcher-tool"` declaration and call records.
- `genai.Content` and `genai.Part`, serialized as JSON objects with `role`, `parts`, `text`, `functionCall`, and `functionResponse`.
- `genai.FunctionCall`, with repeated `id: "id1"`, `name: "researcher-tool"`, and `args.Arg`.
- `genai.FunctionResponse`, with matching `id` and `name`, and an omitted or empty response body because the test tool returns `struct{}{}`.

There are no user-defined Go functions or structs declared in this JSON chunk. The API value of the chunk is as a stable serialized contract for the Go code that builds LLM requests.

## Control Flow Represented

The represented control flow is an unrolled transcript of repeated nested-agent tool use:

1. The parent agent has already called the `researcher` LLMTool in an earlier part of the fixture.
2. The `LLMTool.execute` path has created a nested `LLMAgent` request whose initial user prompt is `"What do you think?"`.
3. On each nested LLM turn, the mocked model returns one `researcher-tool` function call with the next integer argument.
4. `agentSession.callTools` executes the Go test tool and appends a user-role `functionResponse` for that same call ID/name.
5. The next `generateContent` request contains the prompt and all accumulated call/response pairs so far.
6. The fixture records each subsequent request object, so each object is a larger prefix of the same logical sub-agent conversation.

The chunk boundary is important. It does not start on a top-level JSON object boundary; it begins in the middle of a request history where arguments `0..28` were already present in the previous chunk. It also does not end on a logical completion boundary; the next chunk is needed to finish the visible request object and the later final text reply.

Because the mocked replies are generated by a loop over `maxLLMIterations` in the Go test, the monotonically increasing `Arg` values are a test oracle for iteration count and ordering. Any missing response, wrong role, reordered argument, or unexpected final reply inside this range would indicate a request-construction or tool-execution regression.

## State And Persistence Behavior

The JSON fixture itself is persistent repository testdata. It is compared by tests and regenerated only when the test harness is run with the update flag. It has no runtime state, database writes, caches, locks, or side effects.

The runtime state captured by the fixture is the in-memory LLM conversation history:

- `agentSession.req` persists the prompt, model function calls, and user tool responses across nested-agent iterations.
- Tool results are appended as `FunctionResponse` parts using the same call ID and tool name returned by the model.
- `LLMTool.execute` temporarily stores the nested prompt in `ctx.state[AFLOW_LLMTOOL_PROMPT]` and later reads `ctx.state[AFLOW_LLMTOOL_REPLY]`, but those state keys are not directly serialized here.
- The repeated request objects demonstrate that aflow does not reset the nested agent history on every tool call; it sends the accumulated transcript back to the model.

The chunk also indirectly exercises the `maxLLMIterations` safety boundary. The large transcript exists because the nested agent is allowed to make many tool calls before returning. The report for the whole file must combine neighboring chunks to determine where the final `Nothing.` and parent `YES` replies appear.

## Dependencies And Integration Points

This fixture integrates with several aflow test and implementation surfaces:

- `pkg/aflow/llm_tool_test.go`, especially `TestLLMToolMaxIters`, defines the parent agent, nested `LLMTool`, `researcher-tool`, and the reply sequence with `Arg` values generated from `range maxLLMIterations`.
- `pkg/aflow/runner_test.go` provides `testFlow`, the mocked `generateContent` callback, and golden-file comparison against `testdata/TestLLMToolMaxIters.llm.json`.
- `pkg/aflow/llm_tool.go` defines the nested-agent wrapper, the `Question`/`Answer` schemas, and state handoff between parent and nested agents.
- `pkg/aflow/llm_agent.go` defines `maxLLMIterations`, the `chat` loop, request history append logic, `callTools`, duplicate-call tracking, and response parsing.
- The external `google.golang.org/genai` package defines the serialized request types and function-call/function-response schema used by the fixture.

The fixture is also linked to `TestLLMToolMaxIters.trajectory.json`, which records the high-level span trajectory for the same test. This `.llm.json` file focuses on the exact model requests, while the trajectory file validates execution spans and results.

## Risks And Edge Cases

- The file is very large and intentionally repetitive. Manual edits are high risk because a single missing comma, unmatched bracket, lost tool response, or incorrect `Arg` value can invalidate the JSON or break the golden comparison.
- Chunk boundaries split JSON object boundaries. Research or tooling that samples only the first and last lines can misinterpret the range as malformed, even though the full file is valid JSON.
- The repeated call ID `"id1"` is expected in this fixture because each mocked model function-call part uses that ID. A validator that assumes globally unique call IDs across the entire transcript would flag a false positive.
- The fixture uses role `"user"` for serialized function-call and function-response contents as produced by the test harness. This is part of the golden contract, even if it looks counterintuitive compared with a model/user chat transcript.
- Because `Config` is deduplicated by the test harness when unchanged, later request objects omit the function declaration and system instruction. Consumers must understand this golden-file compression rather than treating missing config as missing tool setup.
- The `Arg` runs reset at each new sub-agent request-history object because the fixture records successive full requests, not only incremental deltas. Counting every `Arg` occurrence in the file will overcount logical tool invocations unless request-object boundaries are considered.
- Any change to `maxLLMIterations`, Gemini request serialization, tool-response body omission, schema generation, or request-history trimming will require coordinated fixture updates.
- The test stresses a large context. Future changes to compression, sliding-window behavior, answer-now behavior, or loop-detection policy may intentionally change this fixture, but accidental history loss would be visible in this range as shortened or missing call/response sequences.

## Test Signals

The primary validation signal is running the aflow Go tests that compare this fixture against freshly generated requests. Useful checks include:

- `TestLLMToolMaxIters` should pass with the existing `TestLLMToolMaxIters.llm.json` golden file.
- The JSON should remain parseable as a whole file, even though this chunk alone starts and ends mid-object.
- The request sequence should preserve alternating `functionCall` and `functionResponse` parts for `"researcher-tool"` with matching `id: "id1"`.
- Within each request-history object, `Arg` values should be monotonically increasing from the visible start value to that object's end.
- Complete visible request objects in this chunk should use `"Model": "sub-agent-model"` and prompt text `"What do you think?"`.
- The associated trajectory golden should still show the nested tool calls and eventual successful parent output `Reply: "YES"` when reconciled with the full fixture.

This chunk does not contain executable logic to unit test directly; its value is regression coverage for the LLM request serialization produced by the surrounding Go tests.
