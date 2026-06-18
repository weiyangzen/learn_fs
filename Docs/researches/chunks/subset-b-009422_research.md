# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json lines 336306-354970

## Scope

This chunk covers a middle slice of the golden LLM request transcript for `TestLLMToolMaxIters`. The file is JSON testdata, not executable Go code. It records `genai.GenerateContent` requests emitted by the aflow test harness while a parent `LLMAgent` invokes an `LLMTool` named `researcher`, and that nested agent repeatedly invokes its own function tool named `researcher-tool`.

The requested range starts inside an already-running sub-agent request, immediately after a tool response for the previous visible call sequence and then continuing through `researcher-tool` calls with `Arg: 160`, `161`, and `162`. It then contains four complete visible `"Model": "sub-agent-model"` request objects and starts a fifth request object that continues into the next chunk. Within the exact line range there are 18,665 lines, 744 serialized `functionCall` entries, 744 serialized `functionResponse` entries, 5 `"Model"` entries, 5 `"Request"` entries, and 5 prompt text entries.

The visible `Arg` runs are:

- `160..162`, completing a request object that began before this chunk; the range also includes the preceding response for `Arg: 159`.
- `0..163`, `0..164`, `0..165`, and `0..166`, each in a complete visible sub-agent request-history object.
- `0..78`, beginning a request object that continues after this chunk; the matching response for `Arg: 78` is outside the requested range.

The range therefore documents the expanding request-history behavior of the max-iteration test, rather than a standalone logical scenario.

## Purpose

`TestLLMToolMaxIters.llm.json` is the golden request log used by `pkg/aflow` tests to detect regressions in how nested LLM agents build Gemini requests. The associated Go test, `TestLLMToolMaxIters` in `llm_tool_test.go`, constructs a parent `LLMAgent` whose mocked first reply calls an `LLMTool` named `researcher`. The nested sub-agent then calls `researcher-tool` once per LLM iteration for `maxLLMIterations` iterations before returning text, and the parent finally returns `"YES"`.

This chunk proves that, in the middle of that long nested conversation, aflow preserves the complete accumulated chat history for every subsequent sub-agent LLM request. Each request-history object includes:

- The sub-agent model name, `"sub-agent-model"`.
- The sub-agent prompt text, `"What do you think?"`.
- Repeated `functionCall` parts for `"researcher-tool"` with integer `Arg` values.
- A matching `functionResponse` part after each completed call.
- User-role serialized content for both prompt and tool-response messages, matching the test harness output.

The important behavioral signal is continuity. The transcript repeatedly restarts at `Arg: 0` because each JSON object is a full request sent to the model, not an incremental delta. Inside each object, the `Arg` values remain monotonic and the call/response pairs alternate in order.

## Important APIs, Types, And Data Shape

The JSON shape is produced by `testFlow` in `runner_test.go`. Its local `llmRequest` record stores each mocked `generateContent` call as:

- `Model`, a string such as `"sub-agent-model"`.
- Optional `Config`, present only when the generate-content config changes from the previous stored request.
- `Request`, a slice of serialized `*genai.Content`.

Most objects in this chunk omit `Config` because `testFlow` deep-copies and stores config only when it differs from the previous request. The tool declaration and sub-agent instruction are therefore inherited from earlier fixture records, not missing from the runtime request setup.

The runtime types represented by this data are:

- `LLMAgent`, whose `agentSession.chat` loop owns the repeated LLM request flow.
- `LLMTool`, which wraps a nested `LLMAgent` and exposes it as a callable tool to the parent agent.
- `Tool` / `NewFuncTool`, represented by the nested `"researcher-tool"` calls.
- `genai.Content` and `genai.Part`, serialized with `role`, `parts`, `text`, `functionCall`, and `functionResponse`.
- `genai.FunctionCall`, with `id: "id1"`, `name: "researcher-tool"`, and `args.Arg`.
- `genai.FunctionResponse`, with matching `id` and `name`; the response body is empty because the test tool returns `struct{}{}`.

There are no Go declarations in this JSON chunk itself. Its API value is as a stable serialized contract for request construction in the surrounding Go implementation.

## Control Flow Represented

The represented control flow is an unrolled nested-agent loop:

1. The parent agent has already called the `researcher` LLMTool in an earlier part of the fixture.
2. The nested `LLMTool` agent is running with prompt `"What do you think?"`.
3. On each nested LLM turn, the mocked model returns one `researcher-tool` function call with the next integer argument.
4. `agentSession.callTools` executes the Go test tool and appends a user-role `functionResponse` for the same call ID/name.
5. The next `generateContent` request sends the prompt plus all accumulated function calls and function responses so far.
6. The golden fixture records that whole next request, so each later request object is a larger prefix of the same logical sub-agent conversation.

The relevant implementation limit is `maxLLMIterations = 250` in `llm_agent.go`. `TestLLMToolMaxIters` builds mocked sub-agent replies with a loop over that constant, so the `Arg` values are an oracle for iteration order and count. This chunk covers the transition through request histories ending at logical arguments 163, 164, 165, and 166, then begins the request history for the following iterations.

The range starts and ends on chunk boundaries, not JSON-object boundaries. The opening lines complete a prior request object, and the closing lines stop after the `functionCall` for `Arg: 78` in a later request object, before that call's response appears in the next chunk.

## State And Persistence Behavior

The fixture itself is persistent repository testdata. It is compared by tests and regenerated only when the aflow test harness is run with the update flag. It has no runtime database writes, locks, caches, or side effects.

The runtime state captured by the fixture is the in-memory conversation history held by `agentSession.req`:

- The initial sub-agent prompt persists across all nested LLM calls.
- Each model function call is appended to the request history.
- Each tool result is appended as a `FunctionResponse` part using the same ID and tool name.
- The repeated request objects demonstrate that the nested agent does not reset history between tool calls.
- The surrounding `LLMTool` state handoff uses `AFLOW_LLMTOOL_PROMPT` and `AFLOW_LLMTOOL_REPLY`, but those keys are not directly serialized in this chunk.

The chunk also indirectly exercises the max-iteration safety behavior. The transcript exists because the nested agent is allowed to make many tool calls before final text is accepted. The whole-file reconciliation lane must combine later chunks to document the final `"Nothing."` sub-agent reply and parent `"YES"` reply.

## Dependencies And Integration Points

This fixture integrates with these aflow surfaces:

- `pkg/aflow/llm_tool_test.go`: `TestLLMToolMaxIters` defines the parent agent, nested `LLMTool`, `researcher-tool`, and the mocked reply sequence.
- `pkg/aflow/runner_test.go`: `testFlow` stubs `generateContent`, captures all requests, and compares them against `testdata/TestLLMToolMaxIters.llm.json`.
- `pkg/aflow/llm_agent.go`: defines `maxLLMIterations`, `agentSession.chat`, request-history append behavior, tool-call execution, response parsing, and the final max-iteration error path.
- `pkg/aflow/llm_tool.go`: provides the nested-agent wrapper and parent/sub-agent state handoff for `LLMTool`.
- `google.golang.org/genai`: supplies the request, content, part, function-call, function-response, and config types serialized into the fixture.

The paired `TestLLMToolMaxIters.trajectory.json` fixture validates span-level behavior for the same execution, while this `.llm.json` fixture validates exact model request payloads.

## Risks And Edge Cases

- The file is intentionally huge and repetitive. Manual edits can easily break JSON validity or golden equality through a single missing comma, bracket, response, or argument value.
- Chunk boundaries split JSON records. This requested range is not parseable as standalone JSON even though the full source file is valid.
- Counting every `Arg` occurrence in a large slice overcounts logical tool invocations because each request object repeats prior conversation history.
- The repeated call ID `"id1"` is expected. The mocked test replies reuse that ID for each nested tool call, so global uniqueness across the whole fixture is not a valid invariant here.
- The serialized role is `"user"` for function-call and function-response content because the test harness wraps mocked replies that way. Consumers should treat this as part of the current golden contract.
- `Config` omission in repeated records is intentional harness compression. Later request objects still depend on the same tool declarations and instruction established earlier.
- Future changes to `maxLLMIterations`, request-history trimming, sliding-window compression, Gemini JSON serialization, or empty-struct function response encoding will require coordinated fixture updates.
- The range closes after a `functionCall` whose matching `functionResponse` is outside this chunk. Any per-chunk validator must tolerate boundary-split pairs.

## Test Signals

The primary validation signal is `TestLLMToolMaxIters` passing with this golden fixture. Useful checks for this chunk are:

- The whole `TestLLMToolMaxIters.llm.json` file remains parseable JSON.
- The requested range contains 744 `functionCall` entries and 744 `functionResponse` entries, accounting for the opening and closing boundary splits.
- Complete visible request objects use `"Model": "sub-agent-model"` and prompt text `"What do you think?"`.
- Within each request-history object, `Arg` values increase monotonically.
- Completed tool calls have matching `functionResponse` entries with `id: "id1"` and `name: "researcher-tool"`.
- The paired trajectory fixture still shows nested `researcher-tool` spans and the eventual successful parent output when reconciled with the full file.

This chunk does not expose executable logic to unit test directly; its regression value is the exact serialized request history produced by the Go tests around `LLMAgent` and `LLMTool`.
