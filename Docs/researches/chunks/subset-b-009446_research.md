# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json lines 783953-787905

## Scope

This chunk is the final slice of the golden LLM request transcript for `TestLLMToolMaxIters`. The source is serialized JSON testdata rather than executable Go. The assigned range starts in the middle of a nested-agent request history, completes the final repeated `researcher-tool` call/response sequence through `Arg: 249`, records the max-iteration best-effort prompt, and then captures the next parent-agent model request after the nested `LLMTool` returns.

Because the range opens inside an already-started JSON object, it is not independently parseable. It does, however, include the final file close, so it provides the terminal state of the fixture.

## Purpose

`TestLLMToolMaxIters` exercises an LLM-backed tool that delegates a parent tool call to a nested `LLMAgent`. The nested agent repeatedly calls its own tool, `researcher-tool`, until the iteration cap is reached. This chunk records the boundary behavior at the cap:

- The nested request history retains call/response pairs for `researcher-tool` with visible `Arg` values `96` through `249`.
- After the `Arg: 249` response, the agent appends an instruction asking for a best-effort answer without more tool calls.
- The next captured request switches back to parent model `"model"` and includes a `researcher` function response with `Answer: "Nothing."`.

The fixture therefore verifies that the max-iteration path does not fail immediately. Instead, it asks the nested model to produce a final answer from accumulated information, maps that result into the parent tool response, and allows the parent agent to continue.

## Data Shape And APIs Represented

The JSON mirrors captured `GenerateContent` inputs from the aflow test harness:

- `Model`: the leading partial request is the tail of a repeated nested-agent call using the previously configured nested model; the final complete request uses `"model"`, the parent agent model.
- `Config`: reappears on the final parent request because the model/config changed. It includes the parent system instruction, temperature `0.3`, a `researcher` function declaration, text response modality, and `thinkingConfig` with `includeThoughts: true` and `thinkingLevel: "HIGH"`.
- `Request`: an ordered conversation history represented as content entries with `parts`.
- `functionCall`: nested calls use `id: "id1"`, name `researcher-tool`, and numeric `args.Arg`; the parent request preserves the earlier call to `researcher` with `id: "id0"` and `Question: "What do you think?"`.
- `functionResponse`: nested responses echo `id1` and `researcher-tool` with no payload, reflecting the empty `struct{}{}` result of the synthetic local tool; the parent response echoes `id0`, name `researcher`, and payload `Answer: "Nothing."`.
- `role`: all visible content entries use `"user"`, consistent with the serialized Gemini `genai.Content` objects used by the test.

The executable APIs represented by this fixture include `LLMTool.declaration`, `LLMTool.execute`, `LLMTool.verify`, `LLMAgent.executeOne`, `agentSession.chat`, `agentSession.callTools`, `LLMAgent.parseResponse`, typed function-tool wrapping through `NewFuncTool`, and request capture/comparison in the `testFlow` harness.

## Control Flow Captured In This Chunk

The visible flow is:

1. The chunk begins inside the nested agent's accumulated request, with a `researcher-tool` call for `Arg: 96`.
2. For each integer through `Arg: 249`, the transcript alternates a `functionCall` content entry and a matching `functionResponse` content entry.
3. After the response for `Arg: 249`, the nested session appends the text instruction: `Provide a best-effort answer... without calling any more tools!`
4. The nested model's eventual text answer is not itself represented as a request object, but the following parent request shows its result after `LLMTool.execute` bridges the nested reply into the parent tool response.
5. The final captured request returns to the parent agent. Its history contains the original prompt, the parent `researcher` tool call with `Question: "What do you think?"`, and the `researcher` function response containing `Answer: "Nothing."`.

This confirms that the transcript is an append-only request log: model responses are visible indirectly when they become part of the next request history as function calls, function responses, or final bridged data.

## State And Persistence Behavior

This file is persistent golden state for a test, and this chunk records two state transitions.

Nested-agent session state grows monotonically. The request history keeps every prior tool call and response, so late iterations are large and repetitive. The visible `Arg: 96-249` range is only the tail of a larger retained request that began before this chunk.

Max-iteration recovery is represented by appending a regular text content entry to the same nested request history. That text asks the model to answer with the information already gathered and forbids further tool calls. This is the behavioral signal that the loop reached `maxLLMIterations` and moved into a best-effort final-answer attempt.

Parent-tool bridge state is visible in the final request. `LLMTool.execute` has taken the nested answer and returned it to the parent as the `researcher` function response payload. The parent request then persists that response in its own history so the parent model can produce the final output.

The fixture itself is maintained by the test harness as JSON-normalized request state. Any change in serialization, model config elision, role assignment, retained history, response conversion, or loop limit will rewrite this terminal region.

## Dependencies And Integration Points

Primary integration points for interpreting this chunk:

- `sources/test-tools/syzkaller/pkg/aflow/llm_tool_test.go`: defines `TestLLMToolMaxIters`, builds the parent agent, registers the nested `researcher` `LLMTool`, supplies synthetic model behavior, and expects the overall parent reply after the tool returns.
- `sources/test-tools/syzkaller/pkg/aflow/llm_tool.go`: adapts a nested `LLMAgent` into a parent-callable tool and maps question/reply values through aflow state keys.
- `sources/test-tools/syzkaller/pkg/aflow/llm_agent.go`: owns the iteration loop, full-history request accumulation, tool-call handling, max-iteration handling, response parsing, and retry/final-answer behavior.
- `sources/test-tools/syzkaller/pkg/aflow/func_tool.go`: wraps the synthetic `researcher-tool` callback and converts its empty result into a Gemini function response.
- `sources/test-tools/syzkaller/pkg/aflow/runner_test.go`: captures `GenerateContent` requests into `.llm.json`, elides repeated configs, normalizes JSON, and compares the captured transcript with this fixture.
- `sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.trajectory.json`: companion fixture that records the same run as execution spans rather than raw LLM requests.
- `google.golang.org/genai`: supplies the content, part, function-call, function-response, config, and schema types serialized here.

## Risks And Maintenance Notes

This range is highly sensitive to loop-boundary semantics. Changing `maxLLMIterations`, changing whether the cap is inclusive/exclusive, or replacing the best-effort prompt with an error path would alter the visible `Arg: 249` terminus and the post-loop text entry.

The repeated nested call id `id1` is intentional fixture input. The agent must still distinguish calls by the combination of tool name and arguments, or at least avoid rejecting this generated sequence solely because the id repeats. A duplicate-call guard keyed too narrowly on id would break this test.

The empty nested `functionResponse` objects are also meaningful. Adding a payload for `struct{}{}`, omitting empty responses, or changing response field ordering would churn this large golden file.

The final parent request shows a config block because execution returns from nested model context to parent model context. Changes to config-delta elision, function declaration schema generation, thinking config defaults, or parent model naming will surface here even when runtime behavior is otherwise unchanged.

## Test Signals

Concrete signals in lines 783953-787905:

- 3,952 source lines and about 56,083 bytes of fixture text.
- Visible nested `researcher-tool` argument range: `96-249`.
- Final nested tool call visible: `Arg: 249`, followed by its matching `functionResponse`.
- Max-iteration recovery prompt is present immediately after the final nested response.
- Final request boundary uses parent `Model: "model"` with a full `Config` block.
- Parent function declaration exposes `researcher` with required `Question` input and required `Answer` response schemas.
- Parent request contains the original text prompt, the `researcher` `functionCall` with `Question: "What do you think?"`, and the `researcher` `functionResponse` with `Answer: "Nothing."`.
- The file closes after this parent request, so the later parent text reply is represented as the test harness response rather than another captured request.

This chunk should remain stable while aflow preserves append-only request histories, the current `maxLLMIterations` boundary, best-effort recovery at the cap, nested-to-parent `LLMTool` answer bridging, and deterministic Gemini request serialization.
