# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json lines 261651-280316

## Scope

This chunk is a partial slice of the oversized golden LLM request fixture for `TestLLMToolMaxIters`. The source is JSON test data, not executable code. It records serialized calls sent to the stubbed GenAI client while the `aflow` LLM tool harness replays a main agent invoking an `LLMTool` sub-agent, and the sub-agent repeatedly invokes its own function tool.

The chunk starts in the middle of one `Request` history at `Arg: 90` and ends in the middle of another request after the `Arg: 103` response. Within the assigned window there are 5 visible `Model: "sub-agent-model"` request objects, 5 prompt text entries (`"What do you think?"`), 744 `functionCall` entries, and 744 matching `functionResponse` entries. The repeated tool name is `researcher-tool`, the call id is consistently `id1`, and every entry has `role: "user"`.

## Purpose

The fixture supports the max-iteration regression test for `LLMTool`. In `llm_tool_test.go`, `TestLLMToolMaxIters` constructs a sequence where the main agent calls the `researcher` LLM tool once, then the sub-agent calls `researcher-tool` `maxLLMIterations` times before returning `"Nothing."`, after which the main agent returns `"YES"`. `runner_test.go` records every request passed to the stubbed model and compares it against `testdata/TestLLMToolMaxIters.llm.json`.

This chunk covers the middle of that generated growth pattern. It demonstrates that each subsequent sub-agent model request contains the original prompt and the complete conversation history accumulated so far: alternating `functionCall` and `functionResponse` messages for each previous tool invocation.

## Data Shape And Important Fields

- Top-level elements in this chunk are objects with `Model`, optional `Config` outside this slice, and `Request`.
- `Model` is always `"sub-agent-model"` for the complete request objects visible here.
- Each `Request` starts with a user text part containing `"What do you think?"`.
- Tool call entries use:
  - `parts[0].functionCall.id = "id1"`
  - `parts[0].functionCall.name = "researcher-tool"`
  - `parts[0].functionCall.args.Arg = <integer>`
- Tool response entries use:
  - `parts[0].functionResponse.id = "id1"`
  - `parts[0].functionResponse.name = "researcher-tool"`
  - no explicit `response` body, matching the Go tool returning an empty `struct{}`
- Every call is followed by its corresponding response before the next call appears.

## Control Flow Represented

The serialized histories in the chunk correspond to repeated iterations of `agentSession.chat` in `llm_agent.go`. The engine:

1. Sends the current `Request` history to the model.
2. Receives a `FunctionCall` for `researcher-tool`.
3. Appends that model response to the request history.
4. Executes the local function tool.
5. Appends a `FunctionResponse` to the request history.
6. Sends the expanded history on the next model call.

The visible request object starts and lengths are:

- Prior object fragment before line 263000: visible `Arg` range 90-143 from a request that began before this chunk.
- Object starting line 263000: `Arg` range 0-144, 145 calls.
- Object starting line 266638: `Arg` range 0-145, 146 calls.
- Object starting line 270301: `Arg` range 0-146, 147 calls.
- Object starting line 273989: `Arg` range 0-147, 148 calls.
- Object starting line 277702: `Arg` range 0-103 visible before the chunk ends.

The increasing upper bound shows golden serialization of the request history immediately before successive later tool calls. Because `maxLLMIterations` is 250, this chunk is not the terminal max-iteration boundary; it is one segment of the complete oversized fixture.

## State And Persistence Behavior

The file persists deterministic golden state for test comparison. Runtime state is held by the test harness in memory as `requests []llmRequest`, then marshaled through JSON and compared to this file. The fixture itself has no mutable state, cache keys, or side effects, but it encodes important persisted expectations:

- full request history is preserved across repeated sub-agent tool calls;
- empty struct tool results serialize as a `functionResponse` with id and name only;
- the same tool call id (`id1`) is reused in this generated scenario;
- integer `Arg` values remain stable after the runner's marshal/unmarshal normalization.

Any change to request compaction, role assignment, tool-response serialization, or iteration accounting can cause this chunk's golden data to change.

## Dependencies And Integration Points

- Consumed by `runner_test.go`, which compares actual stubbed model requests against `testdata/TestLLMToolMaxIters.llm.json`.
- Produced by `TestLLMToolMaxIters` in `llm_tool_test.go` when run with `-update`.
- Relies on GenAI request/response structures from `google.golang.org/genai`.
- The repeated local tool is created by `NewFuncTool("researcher-tool", ...)` and returns `struct{}{}`.
- The outer tool is an `LLMTool` named `researcher` using `Model: "sub-agent-model"` and `TaskType: FormalReasoningTask`.
- The hard cap comes from `maxLLMIterations = 250` in `llm_agent.go`; the chat loop returns `agent reached max iterations limit (250)` if the model never terminates.

## Risks And Maintenance Notes

- The fixture is huge and highly repetitive. Manual edits are risky because one missing or extra call/response pair will desynchronize all later golden requests.
- This chunk begins and ends mid-object, so chunk-level readers must not infer whole-file validity from the opening or closing braces in this slice.
- If `maxLLMIterations`, `callTools`, role handling, JSON formatting, or request-history compression changes, this fixture may need regeneration rather than hand patching.
- The fixture intentionally captures large repeated histories; tests that compare it may be expensive in memory and diff output size.
- Because the sub-agent's tool returns an empty struct, adding fields to that response type or changing empty-response omission would alter every `functionResponse` here.

## Test Signals

The strongest test signal in this chunk is structural regularity: every visible `functionCall` for `researcher-tool` has exactly one immediately following `functionResponse` with the same id/name, and request snapshots reset to `Arg: 0` after each new `Model: "sub-agent-model"` object. The increasing visible upper bounds (`144`, `145`, `146`, `147`, then a later partial `103`) align with sequential model calls as the sub-agent approaches the max-iteration scenario.

The expected final result for the whole test remains outside this chunk: the sub-agent eventually returns `"Nothing."`, and the main agent returns `"YES"`. This chunk therefore primarily validates the long middle of the tool-call loop and request-history persistence, not the final answer handoff.
