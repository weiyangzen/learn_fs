# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json lines 130916-149599

## Scope

This chunk is an interior slice of the golden LLM request transcript for `TestLLMToolMaxIters` in `pkg/aflow`. The source file is testdata, not executable code. It serializes captured `GenerateContent` requests from the `testFlow` harness so the aflow tests can compare future request construction against a stable fixture.

The mapped range covers lines 130916-149599 of `TestLLMToolMaxIters.llm.json`. It starts in the middle of one nested sub-agent request history, includes seven complete new top-level request objects for `"sub-agent-model"`, and ends inside the next request history. The chunk belongs to the long repeated-tool-call region where the nested agent's request history grows on every iteration.

## Purpose

`TestLLMToolMaxIters` verifies that an `LLMTool` implemented by a nested `LLMAgent` can execute its own tool calls all the way to the `maxLLMIterations` boundary and still return control to the parent agent. The parent model calls the `researcher` LLM tool with the question `"What do you think?"`; the sub-agent model then repeatedly calls the nested function tool `researcher-tool` with integer `Arg` values before eventually producing `"Nothing."`, after which the parent model returns `"YES"`.

This specific chunk validates the middle of that accumulated sub-agent conversation. Its main signal is not a new schema shape, but the persistence of the complete prompt plus prior `functionCall` and `functionResponse` messages across many `sub-agent-model` requests.

## Data Shape And APIs Represented

The JSON objects in this file mirror the local `llmRequest` records captured by `runner_test.go:testFlow`:

- `Model` identifies the model passed to the stubbed LLM client. In this chunk every visible top-level boundary is `"sub-agent-model"`.
- `Config` is absent in this range. Earlier requests carry the GenAI generation config, but `testFlow` elides repeated configs when they are unchanged.
- `Request` is the serialized slice of `genai.Content` messages sent for that call.

The content parts visible in this chunk are:

- `text` with `"What do you think?"`, the prompt injected into the sub-agent by `LLMTool.execute`.
- `functionCall` with id `"id1"`, name `"researcher-tool"`, and args object `{"Arg": <int>}`.
- `functionResponse` with id `"id1"` and name `"researcher-tool"`. The response has no payload because the Go callback returns `struct{}{}`, whose response schema is an empty object.

The fixture is produced by `llm_tool_test.go:TestLLMToolMaxIters`, where `toolArgs` is `struct { Arg int }` and `NewFuncTool("researcher-tool", ...)` declares the nested function tool. The broader implementation also exercises `LLMTool.declaration`, `LLMTool.execute`, `LLMTool.verify`, `LLMAgent.chat`, `agentSession.callTools`, and the GenAI types `Content`, `Part`, `FunctionCall`, and `FunctionResponse`.

## Control Flow Captured In This Chunk

The chunk opens after a previous `functionCall` and begins with its matching `functionResponse`, then continues through calls with visible `Arg` values from `28` through `101` before the first top-level request boundary inside the range. After that, each new `sub-agent-model` object restarts its `Request` array from the prompt and replays the whole accumulated conversation from `Arg: 0`.

Observed request-history segments in this exact line range are:

- leading partial segment: 74 call args, first `28`, last `101`;
- complete request at line 132779: 103 call args, first `0`, last `102`;
- complete request at line 135367: 104 call args, first `0`, last `103`;
- complete request at line 137980: 105 call args, first `0`, last `104`;
- complete request at line 140618: 106 call args, first `0`, last `105`;
- complete request at line 143281: 107 call args, first `0`, last `106`;
- complete request at line 145969: 108 call args, first `0`, last `107`;
- trailing partial request beginning at line 148682: visible call args from `0` through `36`.

Within each request snapshot, the sequence is stable:

1. prompt content is sent as a user message;
2. the model's prior `researcher-tool` call is represented as a `functionCall` part;
3. aflow's tool execution appends a matching `functionResponse` part;
4. the next request sends the full accumulated history back to `sub-agent-model`.

This repeated restart from `Arg: 0` is expected because each top-level JSON entry is a full request snapshot, not a delta.

## State And Persistence Behavior

The JSON file itself has no runtime state transitions, but it records important state contracts in the aflow runner:

- `LLMTool.execute` stores the parent tool question in `ctx.state[AFLOW_LLMTOOL_PROMPT]` before running the nested agent.
- `LLMTool.verify` creates an internal `LLMAgent` whose prompt is `{{.AFLOW_LLMTOOL_PROMPT}}` and whose reply is written to `AFLOW_LLMTOOL_REPLY`.
- The nested `agentSession.req` persists and grows for the lifetime of the sub-agent call.
- Tool call ids remain stable as `"id1"` throughout this synthetic max-iteration transcript.
- Empty Go tool results are persisted as function responses with only `id` and `name`.
- The golden `.llm.json` file is persistent test state and is rewritten only by the test harness update path.

Because each next LLM request carries all previous nested tool messages, the fixture grows quadratically with the number of tool iterations. This chunk is part of that growth curve around accumulated calls `102` through `108`.

## Dependencies And Integration Points

Primary integration points:

- `sources/test-tools/syzkaller/pkg/aflow/llm_tool_test.go`: constructs `TestLLMToolMaxIters`, builds the reply stream, and defines the `researcher-tool` callback.
- `sources/test-tools/syzkaller/pkg/aflow/llm_tool.go`: bridges a parent function tool call into a nested `LLMAgent` via `AFLOW_LLMTOOL_PROMPT` and `AFLOW_LLMTOOL_REPLY`.
- `sources/test-tools/syzkaller/pkg/aflow/llm_agent.go`: owns `maxLLMIterations`, the chat loop, function-call parsing, request-history accumulation, and the final answer-now behavior.
- `sources/test-tools/syzkaller/pkg/aflow/runner_test.go`: captures `llmRequest` records, normalizes them through JSON, elides unchanged configs, and compares them to this golden file.
- `sources/test-tools/syzkaller/pkg/aflow/func_tool.go` and schema helpers: define the typed function-tool declaration used by the nested sub-agent.
- `sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.trajectory.json`: validates the trajectory/span view of the same nested tool execution.
- `google.golang.org/genai`: supplies the model request, content, function call, and function response structures serialized into this fixture.

## Risks And Maintenance Notes

This chunk is fragile by design. Changes to request ordering, role assignment, function-call id generation, empty response serialization, config equality/elision, or tool schema generation can rewrite many lines even if the high-level workflow still returns `"YES"`.

The repeated `"id1"` id is intentional in the synthetic replies. If future code assigns unique ids per nested tool call, this fixture and adjacent chunks will change at large scale. Duplicate-call handling must also continue to account for arguments; otherwise repeated calls to the same tool name and id with different `Arg` values could be misclassified.

The line range starts and ends inside JSON structures. Chunk-local counts are useful for guard verification, but final file-level conclusions must be reconciled with neighboring chunks.

The fixture size is tied directly to `maxLLMIterations = 250` and to the current behavior of replaying the entire conversation history. Lowering the iteration limit, adding history compression, or changing the answer-now boundary path would materially alter this range.

## Test Signals

Exact signals observed in this line range:

- 7 visible top-level `"Model": "sub-agent-model"` request boundaries.
- 744 `functionCall` entries and 744 matching `functionResponse` entries.
- 7 prompt text entries with `"What do you think?"`.
- 0 `Config` blocks, confirming unchanged config elision in this interior region.
- All visible calls target `"researcher-tool"` with id `"id1"`.
- No final text response, parent-agent response, error, or duplicate-call warning appears in this chunk.

Useful verification command:

```sh
awk 'NR>=130916 && NR<=149599 { if ($0 ~ /functionCall/) calls++; if ($0 ~ /functionResponse/) responses++; if ($0 ~ /"Model"/) models++; if ($0 ~ /"text": "What do you think\\?"/) prompts++; if ($0 ~ /"Config"/) configs++ } END { print calls, responses, models, prompts, configs }' sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.llm.json
```

Expected result for the current source is:

```text
744 744 7 7 0
```
