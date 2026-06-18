# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json lines 690735-709385

## Scope

This chunk is an interior slice of the generated golden LLM request transcript for `TestLLMToolMaxIters`. The source file is JSON testdata, not executable Go code. It records the serialized `llmRequest` objects captured by `pkg/aflow/runner_test.go::testFlow` while a parent `LLMAgent` invokes an `LLMTool` named `researcher`, whose nested agent repeatedly calls the normal function tool `researcher-tool`.

The mapped range starts inside an already-open nested-agent request at the `Arg: 7` call and ends inside a later nested-agent request at the `Arg: 43` call. The chunk is therefore not independently parseable as a complete JSON document, but it is complete enough to describe the late-loop request-history behavior and the fixture signals for this portion of the max-iteration test.

## Purpose

`TestLLMToolMaxIters` validates that an LLM-backed tool can run a nested LLM/tool loop up to the `maxLLMIterations` bound while preserving conversation history and eventually returning to the parent agent. The test first has the root model call the `researcher` LLM tool with `Question: "What do you think?"`. The nested `"sub-agent-model"` then emits `maxLLMIterations` synthetic calls to `researcher-tool`, with integer `Arg` values generated from `0` through `249`, before the sub-agent replies `"Nothing."` and the root agent replies `"YES"`.

This chunk covers late pre-terminal snapshots of that nested loop. Each visible request snapshot resends the prompt plus all prior nested tool-call and tool-response turns from `Arg: 0` upward. The repetition is intentional: this fixture asserts the exact accumulated GenAI request history rather than an incremental delta protocol.

## Data Shape And APIs Represented

Each complete top-level request in the surrounding file mirrors the local `llmRequest` struct in `pkg/aflow/runner_test.go`:

- `Model`: complete request objects visible in this chunk use `"sub-agent-model"`, identifying the nested `LLMTool` agent rather than the root agent.
- `Config`: absent in this range because `testFlow` stores config only when it differs from the previous request.
- `Request`: a serialized `[]*genai.Content` conversation history passed to `generateContent`.

The visible `Request` entries are GenAI content objects with `role: "user"` and one part. The part variants in this range are the prompt text `"What do you think?"`, `functionCall` objects, and matching `functionResponse` objects. Every visible tool call uses `id: "id1"`, `name: "researcher-tool"`, and `args.Arg`; every response uses the same id and name, with no response payload because the Go tool returns `struct{}{}`.

The executable APIs exercised by this fixture are:

- `LLMTool.declaration`, `LLMTool.verify`, and `LLMTool.execute` in `pkg/aflow/llm_tool.go`, which expose a nested agent as a parent-callable function tool and bridge prompt/reply state through `AFLOW_LLMTOOL_PROMPT` and `AFLOW_LLMTOOL_REPLY`.
- `LLMAgent` and `agentSession.chat` in `pkg/aflow/llm_agent.go`, especially `maxLLMIterations = 250`, request-history accumulation, response parsing, and tool execution.
- `NewFuncTool` and `funcTool.execute` in `pkg/aflow/func_tool.go`, which convert model-supplied argument maps into the typed `toolArgs` struct and convert the empty result back to a response map.
- `testFlow` in `pkg/aflow/runner_test.go`, which stubs GenAI replies, records model/config/request triples, normalizes them through JSON, and compares them with this golden fixture.

## Control Flow Captured In This Chunk

The runtime sequence represented by the repeated JSON is:

1. The parent `LLMAgent` receives a model call to the `researcher` LLM tool.
2. `LLMTool.execute` stores the parent-supplied question in `ctx.state[AFLOW_LLMTOOL_PROMPT]` and runs its internal `LLMAgent`.
3. The nested agent sends a `GenerateContent` request beginning with `"What do you think?"` and the accumulated nested conversation history.
4. The synthetic model reply calls `researcher-tool` with the next integer `Arg`.
5. `agentSession.callTools` executes the registered Go `funcTool`, appends the model call and the corresponding `functionResponse`, and the next model request receives the full expanded history.

Observed request boundaries in this exact range:

- Leading partial request: begins before line 690735 and is visible from `Arg: 7` through `Arg: 234`; this is the tail of a snapshot that had already replayed earlier arguments before the chunk start.
- Complete request beginning at line 696433: uses `"Model": "sub-agent-model"`, contains the prompt at line 696438, and replays `Arg: 0` through `Arg: 235`.
- Complete request beginning at line 702346: uses `"Model": "sub-agent-model"`, contains the prompt at line 702351, and replays `Arg: 0` through `Arg: 236`.
- Trailing partial request beginning at line 708284: uses `"Model": "sub-agent-model"`, contains the prompt at line 708289, and is visible through `Arg: 43` before the chunk ends.

## State And Persistence Behavior

The JSON file is persistent golden state for the aflow test suite. `testFlow` captures every generated LLM request, deep-copies changed generation config, clones request slices to avoid later mutation, then marshals and unmarshals the recorded requests before comparing them with `testdata/TestLLMToolMaxIters.llm.json`. Running the Go test with `-update` can regenerate this file.

At runtime, the important persisted state is in memory:

- `agentSession.req` starts as the nested prompt content and grows append-only with each model function call and tool response.
- `LLMTool.execute` temporarily writes `AFLOW_LLMTOOL_PROMPT` into `ctx.state`, expects the nested reply in `AFLOW_LLMTOOL_REPLY`, then removes those bridge keys.
- `researcher-tool` is a typed `NewFuncTool` returning `struct{}{}`, so the fixture validates ordering, identity, argument conversion, and history retention more than response payload content.
- Each new request repeats history from `Arg: 0`, demonstrating full conversation replay rather than a sliding-window or compression path in this test segment.

This chunk also shows the storage cost of the full-history strategy: a few late iterations expand to 18,651 lines because each request snapshot repeats hundreds of prior tool turns.

## Dependencies And Integration Points

- `sources/test-tools/syzkaller/pkg/aflow/llm_tool_test.go`: defines `TestLLMToolMaxIters`, the `toolArgs{Arg int}` type, the parent `researcher` `LLMTool`, the nested `researcher-tool`, and the synthetic reply list generated for `maxLLMIterations`.
- `sources/test-tools/syzkaller/pkg/aflow/llm_agent.go`: defines `LLMAgent`, `agentSession`, `maxLLMIterations = 250`, the chat loop, max-iteration error path, request history, and tool-call handling.
- `sources/test-tools/syzkaller/pkg/aflow/llm_tool.go`: adapts `LLMTool` into a GenAI function declaration for the parent model and creates the internal agent prompt from `AFLOW_LLMTOOL_PROMPT`.
- `sources/test-tools/syzkaller/pkg/aflow/func_tool.go`: provides `NewFuncTool`, schema-backed declarations, state/argument conversion, and empty result conversion for the nested tool.
- `sources/test-tools/syzkaller/pkg/aflow/runner_test.go`: owns golden fixture capture and comparison for both `.llm.json` and `.trajectory.json`.
- `google.golang.org/genai`: supplies the serialized `Content`, `Part`, `FunctionCall`, `FunctionResponse`, and generation config types represented in this fixture.

## Risks And Maintenance Notes

This fixture region is intentionally repetitive and highly sensitive to small serialization or control-flow changes. Edits to `maxLLMIterations`, request-history retention, role assignment, empty `struct{}{}` result serialization, tool-call id handling, config elision, or `tryAnswerNow`/overflow behavior can rewrite large portions of this JSON.

The repeated `id1` value is synthetic test input from `llm_tool_test.go`, not evidence that production tool calls should reuse ids. Code that introduces stricter unique-id assumptions, duplicate-call filtering, or different loop detection semantics would need coordinated updates to this fixture.

The range begins and ends inside larger JSON structures, so local call/response counts are chunk-specific signals rather than full-file totals. Whole-file conclusions should be made by the later merge/reconciliation lane after adjacent chunks are combined.

## Test Signals

Signals measured in this exact line range:

- `functionCall` markers: 744.
- `functionResponse` markers: 744.
- `Arg` lines: 745.
- Prompt text entries `"What do you think?"`: 3.
- Complete visible `"Model": "sub-agent-model"` boundaries: 3.
- `Config` blocks: 0.
- Final text replies `"Nothing."` and `"YES"`: 0.

The one-extra `Arg` line relative to calls/responses comes from chunk boundaries cutting through JSON objects. The range starts after the `functionCall` marker for the visible `Arg: 7` object, while the final visible `Arg: 43` object starts near the end of the chunk.

Useful verification command for this chunk:

```sh
awk 'NR>=690735 && NR<=709385 { if ($0 ~ /"functionCall"/) calls++; if ($0 ~ /"functionResponse"/) responses++; if ($0 ~ /"Arg":/) args++; if ($0 ~ /"text": "What do you think\?"/) prompts++; if ($0 ~ /"Model": "sub-agent-model"/) submodels++; if ($0 ~ /"Config"/) configs++; if ($0 ~ /"Nothing\."/) nothing++; if ($0 ~ /"YES"/) yes++ } END { print calls+0, responses+0, args+0, prompts+0, submodels+0, configs+0, nothing+0, yes+0 }' sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json
```

Expected result for the current source is `744 744 745 3 3 0 0 0`.
