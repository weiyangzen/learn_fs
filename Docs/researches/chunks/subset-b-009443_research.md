# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json lines 728034-746679

## Scope

This chunk is an interior slice of the golden LLM request transcript for `TestLLMToolMaxIters`. The source file is serialized JSON testdata, not executable Go. The assigned range starts inside an already-open nested-agent `Request` history and ends inside another request's `functionResponse`, so this chunk is not independently parseable as a complete JSON document.

The visible transcript belongs to the `"sub-agent-model"` used by an `LLMTool` named `researcher`. That nested agent repeatedly receives synthetic `functionCall` parts for `researcher-tool`, executes the local function tool, appends matching `functionResponse` parts, and resends the full accumulated history on each subsequent model call.

## Purpose

`TestLLMToolMaxIters` validates the boundary behavior of an LLM-backed tool when its nested agent runs through `maxLLMIterations` tool-calling rounds. The parent agent first calls the `researcher` tool with `Question: "What do you think?"`. The nested agent then receives one synthetic `researcher-tool` call per iteration, with `Arg` values generated from `0` through `maxLLMIterations - 1`, before eventually returning `"Nothing."` to the parent and the parent returning `"YES"`.

This exact range documents the late-loop full-history replay immediately before the final few iterations. The leading partial request contains retained history for `Arg: 71` through `Arg: 240`. Two complete request snapshots then replay history from `Arg: 0` through `Arg: 241` and from `Arg: 0` through `Arg: 242`. The trailing partial request begins another full-history replay and reaches visible `Arg: 89` before the chunk ends.

## Data Shape And APIs Represented

The serialized objects mirror the local `llmRequest` struct in `sources/test-tools/syzkaller/pkg/aflow/runner_test.go`:

- `Model`: all request boundaries visible in this range use `"sub-agent-model"`, the model configured on the nested `LLMTool`.
- `Request`: a `[]*genai.Content` conversation history passed to `GenerateContent`.
- `parts`: each visible content entry has one part, either prompt text, a `functionCall`, or a `functionResponse`.
- `functionCall`: tool calls use `id: "id1"`, `name: "researcher-tool"`, and integer `args.Arg`.
- `functionResponse`: responses use the same id and tool name; no response payload is serialized because the Go callback returns `struct{}{}`.
- `role`: all visible content entries use `"user"`, matching the test stub's synthetic candidate role and the role used for tool responses.

The executable APIs exercised by this fixture are `LLMTool.declaration`, `LLMTool.execute`, and `LLMTool.verify`; `LLMAgent.executeOne`, `agentSession.chat`, `agentSession.callTools`, and `LLMAgent.parseResponse`; typed tool wrapping through `NewFuncTool`; request capture in `testFlow`; and Gemini structures from `google.golang.org/genai`.

## Control Flow Captured In This Chunk

The runtime sequence represented here is:

1. The parent model calls `researcher`, causing `LLMTool.execute` to convert the parent tool arguments into `llmToolArgs`.
2. `LLMTool.execute` stores the question in `ctx.state[AFLOW_LLMTOOL_PROMPT]` and runs the nested `LLMAgent`.
3. `LLMTool.verify` has configured that nested agent with prompt template `{{.AFLOW_LLMTOOL_PROMPT}}`, reply key `AFLOW_LLMTOOL_REPLY`, model `"sub-agent-model"`, and tool `researcher-tool`.
4. `agentSession.chat` sends `GenerateContent` with the prompt `"What do you think?"` plus all retained prior function calls and responses.
5. The test stub returns the next synthetic `functionCall` for `researcher-tool`.
6. `agentSession.callTools` executes the registered `NewFuncTool` callback, records a tool span, and appends a matching `functionResponse` to the next request history.

Observed boundaries in lines 728034-746679:

- Leading partial request: begins before the assigned range; visible complete call/response pairs run from `Arg: 71` through `Arg: 240`.
- Request beginning at line 732286: prompt at line 732291, then full retained history from `Arg: 0` through `Arg: 241`; it ends before the next request boundary.
- Request beginning at line 738349: prompt at line 738354, then full retained history from `Arg: 0` through `Arg: 242`; it ends before the next request boundary.
- Trailing partial request beginning at line 744437: prompt at line 744442, then visible retained history from `Arg: 0` through `Arg: 89`; the chunk ends inside the response for `Arg: 89`.

The apparent resets from high `Arg` values back to `0` are not execution resets. They show that each captured `GenerateContent` request contains the complete nested-agent history as of that model call.

## State And Persistence Behavior

This file is persistent golden test state. `runner_test.go:testFlow` records every model request, stores a config only when it changes from the prior request, clones the request slice, JSON-normalizes captured data through marshal/unmarshal, and compares the result against `testdata/TestLLMToolMaxIters.llm.json`.

The runtime state visible in this chunk is append-only nested-agent conversation history:

- `agentSession.req` starts with the nested prompt content and grows by appending the model's function-call content and the tool-response content for each iteration.
- `LLMTool.execute` uses `ctx.state` as a temporary bridge: `AFLOW_LLMTOOL_PROMPT` feeds the nested prompt, and `AFLOW_LLMTOOL_REPLY` later carries the nested final reply back to the parent tool response.
- `researcher-tool` returns `struct{}{}`, so each response object mainly preserves call id, tool name, ordering, and the absence of unexpected payload fields.
- No `Config` block appears in this slice, which is consistent with `testFlow` eliding unchanged generation configs for repeated nested-agent calls.
- No sliding-window summary, compression retry, input-overflow handling, final text reply, or parent-agent return appears in this chunk.

Because each late request repeats hundreds of earlier entries, this range also demonstrates the quadratic growth of the golden transcript when request history is fully retained.

## Dependencies And Integration Points

Primary integration points:

- `sources/test-tools/syzkaller/pkg/aflow/llm_tool_test.go`: defines `TestLLMToolMaxIters`, constructs the parent `LLMAgent`, creates the `researcher` `LLMTool`, registers `researcher-tool`, generates `maxLLMIterations` synthetic function-call replies, and expects final output `Reply: "YES"`.
- `sources/test-tools/syzkaller/pkg/aflow/llm_tool.go`: adapts a nested `LLMAgent` into a parent-callable function tool and bridges question/answer values through `ctx.state`.
- `sources/test-tools/syzkaller/pkg/aflow/llm_agent.go`: owns the model-call loop, `maxLLMIterations = 250`, response parsing, full-history request maintenance, tool execution, duplicate-call detection, context compression hooks, overflow handling, and max-iteration error path.
- `sources/test-tools/syzkaller/pkg/aflow/func_tool.go`: provides `NewFuncTool`, argument conversion, state conversion, callback execution, and result conversion for the synthetic `researcher-tool`.
- `sources/test-tools/syzkaller/pkg/aflow/runner_test.go`: supplies the synthetic `GenerateContent` stub and compares this `.llm.json` fixture with captured requests.
- `sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.trajectory.json`: companion trajectory fixture for the same execution, recording spans rather than raw LLM requests.
- `google.golang.org/genai`: provides `GenerateContentConfig`, `Content`, `Part`, `FunctionCall`, `FunctionResponse`, and response structures serialized into this golden data.

## Risks And Maintenance Notes

This fixture region is repetitive but sensitive. Small changes to role assignment, function-call id preservation, argument serialization, empty `struct{}{}` response conversion, tool-response ordering, history retention, config elision, or `maxLLMIterations` will rewrite thousands of lines around this chunk.

The repeated `id: "id1"` is intentional synthetic input from the test. The current duplicate-call guard is still expected to accept these calls because `Arg` changes across iterations. A stricter id-uniqueness requirement, or duplicate detection keyed too narrowly on id/name instead of tool arguments, would conflict with this fixture.

The chunk boundaries cut through JSON structures. Reconciliation should combine this document with adjacent chunk reports before drawing whole-file conclusions about JSON syntax, the final `Arg: 249` call, the nested `"Nothing."` reply, the parent `"YES"` reply, or the absence of a max-iteration failure in the complete test.

## Test Signals

Concrete signals observed in lines 728034-746679:

- 18,646 source lines and about 262,119 bytes of fixture text.
- 3 visible `"Model": "sub-agent-model"` request boundaries.
- 3 visible prompt text entries with `"What do you think?"`.
- 745 `functionCall` markers and 744 `functionResponse` markers.
- 745 visible `Arg` fields.
- 1,488 visible `"name": "researcher-tool"` lines.
- 1,489 visible `"id": "id1"` lines.
- 0 visible `Config` blocks.
- 0 visible final text replies, parent answers, API errors, or max-iteration error messages.
- Visible argument runs: `71-240`, `0-241`, `0-242`, and `0-89`.

This chunk should remain stable while aflow preserves full nested-agent request history, deterministic call/response ordering, empty-result serialization for `struct{}{}`, argument-sensitive duplicate handling, and the current `maxLLMIterations` semantics.
