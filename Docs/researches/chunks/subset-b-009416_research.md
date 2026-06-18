# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json lines 224310-242982

## Scope

This chunk is an 18,673-line slice from the golden LLM request ledger for `TestLLMToolMaxIters`. The file is not production code; it is structured test data consumed by `pkg/aflow` tests. The mapped range begins in the middle of one recorded `sub-agent-model` request, at the `researcher-tool` call with `Arg: 120`, and ends in the next recorded request after `Arg: 54`. The slice therefore documents a rolling request-history window rather than a complete standalone JSON document.

## Purpose

`TestLLMToolMaxIters` verifies that an `LLMTool` sub-agent can repeatedly call its own function tool up to the hard LLM iteration limit and still return control to the parent agent. In the test source, `maxLLMIterations` is `250`, and the mocked model reply sequence appends `researcher-tool` function calls for every `i` in `range maxLLMIterations`, followed by a text reply `"Nothing."` from the sub-agent and `"YES"` from the parent.

This chunk captures the late-middle portion of the sub-agent request ledger, around the point where each newly recorded `GenerateContent` call contains a longer replay of previous function call/response pairs. It acts as a regression signal for the exact Gemini `genai.Content` history that `agentSession.chat` sends after each tool execution.

## Data Shape And Important API Types

The records in this range are JSON encodings of the `llmRequest` struct defined in `runner_test.go`:

- `Model`: here always `"sub-agent-model"` in this range.
- `Config`: omitted after the initial request when unchanged, because the test recorder only stores config changes.
- `Request`: an ordered slice of `*genai.Content`.

Each `Request` starts with a user text part:

- `text: "What do you think?"`
- `role: "user"`

Then it alternates between:

- `functionCall` parts using `id: "id1"`, `name: "researcher-tool"`, and integer `args.Arg`.
- `functionResponse` parts using the same `id` and tool name, with no explicit response payload because the Go tool returns `struct{}{}`.

The fixture uses the `google.golang.org/genai` request schema. Function calls are represented as model content parts, and tool completions are represented as response parts appended to the next request history.

## Chunk-Specific Control Flow

The first visible request in this chunk is already near the end of a long sub-agent history. It continues calls:

- `Arg: 120` through `Arg: 132`, each immediately followed by a matching `functionResponse`.

That request closes, then the next `sub-agent-model` request begins from scratch with the original prompt and replays the tool history from:

- `Arg: 0` through `Arg: 133`.

Subsequent recorded requests in this range repeat the same pattern:

- one more prior call/response pair is included near the end of each request;
- the request closes;
- a new `Request` begins with `"What do you think?"`;
- the tool-call replay restarts at `Arg: 0`.

By the end of the selected lines, the chunk has passed through the request that includes `Arg: 137` and has entered the next request, which is replaying from `Arg: 0` and reaches `Arg: 54` before the range ends. The observed transition points in the full file around this chunk show the growing tail:

- request ending at `Arg: 132`;
- next ending at `Arg: 133`;
- next ending at `Arg: 134`;
- next ending at `Arg: 135`;
- next ending at `Arg: 136`;
- next ending at `Arg: 137`.

This matches `agentSession.chat`: after each LLM response containing a function call, the agent appends the response content to `a.req`, executes the tool through `callTools`, appends the function response, and sends the full accumulated `a.req` to the next `GenerateContent` call.

## State And Persistence Behavior

There is no runtime state mutation stored in this JSON itself. The persistence here is golden-test persistence:

- `testFlow` records every mocked LLM request into `testdata/TestLLMToolMaxIters.llm.json`.
- On normal test runs, actual requests are compared against this file.
- With the `-update` flag, the fixture can be regenerated.

The relevant runtime state is carried by `LLMTool.execute` and the nested `LLMAgent`:

- The parent tool call passes `Question: "What do you think?"`.
- `LLMTool.execute` stores that prompt in `ctx.state["AFLOW_LLMTOOL_PROMPT"]`.
- The nested agent renders that state into its prompt and runs with `Reply` bound to `AFLOW_LLMTOOL_REPLY`.
- The inner `researcher-tool` receives only its decoded `Arg`; it returns an empty struct, producing empty function-response objects in this fixture.

The repeated request histories are also a persistence signal: the sub-agent session carries previous `genai.Content` entries forward between iterations. This chunk is useful for detecting accidental truncation, misordered append behavior, wrong roles, missing tool responses, or unexpected response bodies.

## Dependencies And Integration Points

This fixture integrates with:

- `llm_tool_test.go`: constructs `TestLLMToolMaxIters`, `LLMTool`, the nested `researcher-tool`, and the mocked reply sequence.
- `llm_agent.go`: defines `maxLLMIterations = 250` and drives the loop in `agentSession.chat`.
- `llm_tool.go`: adapts an `LLMTool` into a nested `LLMAgent`, passes the question via `ctx.state`, and extracts the nested reply.
- `runner_test.go`: captures `GenerateContent` requests and compares them with `.llm.json` golden data.
- `TestLLMToolMaxIters.trajectory.json`: companion golden trace that records spans for the parent agent, nested agent, LLM calls, and each `researcher-tool` execution.
- `google.golang.org/genai`: supplies `GenerateContentConfig`, `Content`, `Part`, `FunctionCall`, and function response structures.

Because `Config` is omitted through this region, the chunk depends on prior records for the effective sub-agent config: model `"sub-agent-model"`, formal-reasoning temperature, high thinking config, and the `researcher-tool` declaration with integer `Arg`.

## Risks And Maintenance Notes

- The range is not valid standalone JSON. It begins and ends inside nested arrays/objects. Chunk readers must preserve file-line context and avoid treating this slice as a separately parseable fixture.
- The fixture is very large because every successive LLM request repeats all prior tool calls and responses. Small changes to history retention, role naming, response serialization, function-call IDs, config elision, or max-iteration behavior can rewrite huge sections of the file.
- All visible function calls use the same `id: "id1"`. That is intentional for this mocked reply sequence, but any future uniqueness requirement in the genai integration would invalidate this golden file.
- Empty `functionResponse` payloads are expected because `researcher-tool` returns `struct{}{}`. If serialization starts emitting explicit empty response objects, this region will change while behavior may still be semantically equivalent.
- The test is sensitive to `maxLLMIterations`. Raising or lowering the constant changes the number of mocked sub-agent calls, the fixture size, and the expected max-iteration boundary.
- The request roles in stored model replies are `"user"` because the test stub wraps mocked `genai.Part` replies with `RoleUser`. That can look odd for model-returned function calls, but it is the established golden behavior for these tests.

## Test Signals

The main signal from this chunk is that no max-iteration error occurs before the sub-agent has made the allowed number of tool calls. In this selected region, the fixture shows successful continuation through high `Arg` values and repeated reconstruction of full request history. A regression would typically appear as:

- a missing `functionResponse` after a `functionCall`;
- an incorrect `Arg` sequence or skipped call;
- premature final text before the max-iteration sequence is complete;
- an unexpected `Config` block in unchanged sub-agent requests;
- a changed model name, role, tool name, or function-call ID;
- a shorter history indicating unintended compression or truncation in this no-overflow path.

The companion trajectory fixture provides the execution-level cross-check: each tool call should have matching start and finish spans with empty results, nested under the `researcher` sub-agent.
