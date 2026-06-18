# Research Group: subset-b-009447

This grouped report covers aflow LLM and loop test fixtures under `sources/test-tools/syzkaller/pkg/aflow/testdata`. The files are JSON fixtures consumed by Go tests in `llm_agent_test.go`, `llm_tool_test.go`, `loop_test.go`, `func_tool_test.go`, and `flow_test.go`. `.llm.json` files persist expected mocked Gemini `GenerateContent` request/config histories. `.trajectory.json` files persist expected `trajectory.Span` execution logs.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.trajectory.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.trajectory.json

## Purpose
This large trajectory fixture is the expected execution trace for `TestLLMToolMaxIters` in `llm_tool_test.go`. It proves that an `LLMTool` sub-agent can perform exactly `maxLLMIterations` internal tool loops before returning to the parent `LLMAgent`, and that the framework still finishes with the parent reply `YES`.

## Important APIs, Types, and Functions
The fixture serializes `trajectory.Span` objects from `pkg/aflow/trajectory`. It exercises `LLMAgent`, `LLMTool`, `Tool`, `NewFuncTool`, and the `maxLLMIterations` constant in `llm_agent.go`. The sub-agent tool declaration is `researcher-tool` with integer argument `Arg`; the parent-visible tool is `researcher` with `Question` input and `Answer` output.

## Control Flow
The JSON array has 1014 spans: 2 flow spans, 6 parent-agent spans, 506 LLM spans, and 500 tool spans. The sequence starts with flow `test`, parent agent `smarty`, a parent LLM call that invokes `researcher`, then a nested agent named `researcher`. The nested agent alternates LLM/tool spans for `researcher-tool` 250 times. After the final sub-agent LLM reply `Nothing.`, control returns through the `researcher` tool result and the parent agent replies `YES`.

## State and Persistence
This file is static golden data. It persists deterministic span sequence numbers, nesting levels, model names, instructions, prompts, tool args/results, and final flow results. It does not mutate runtime state itself, but guards state propagation through `ctx.state` for `LLMTool`, especially the temporary `AFLOW_LLMTOOL_PROMPT` and `AFLOW_LLMTOOL_REPLY` variables.

## Dependencies and Integration Points
The fixture integrates with the aflow test harness that records trajectories and compares them against `testdata`. It depends on the generated span schema staying compatible with `trajectory.Span`, and on the test's fake LLM reply list matching the expected number of iterations.

## Risks
Because the file is large and sequence-sensitive, small changes to retry or span-recording behavior can produce broad diffs. A regression in max-iteration enforcement could either truncate before the sub-agent result or allow unbounded loops. Changes to tool nesting, span names, or LLMTool state cleanup would break this fixture.

## Test Signals
Successful comparison signals that nested LLM tools can reach the configured iteration ceiling, record 250 internal tool calls, return `Answer: Nothing.`, and let the parent flow finish with `Reply: YES` without span errors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMToolMaxIters.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestNestedDoWhileOutput.trajectory.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestNestedDoWhileOutput.trajectory.json

## Purpose
This trajectory is the golden trace for `TestNestedDoWhileOutput` in `loop_test.go`. It verifies that a variable produced inside an inner `DoWhile` loop remains visible to a later action in the containing outer loop body.

## Important APIs, Types, and Functions
The fixture records `DoWhile.execute`, `DoWhile.loop`, `Pipeline`, and `NewFuncAction` behavior through `trajectory.Span`. It specifically covers loop variable discovery in `DoWhile.verify`, where loop-body outputs are collected and zero-initialized before execution.

## Control Flow
The file has 14 spans: 2 flow, 4 loop, 4 iteration, and 4 action spans. The outer loop runs one iteration. Inside it, the inner loop runs one iteration and `inner-action` returns `InnerContinue: ""` and `Leaked: "val"`. After the inner loop finishes, `outer-consumer` receives `Leaked` and returns `Continue: ""`, ending the outer loop.

## State and Persistence
The fixture persists the expected state handoff in span results: `Leaked` is produced by `inner-action` and then consumed by `outer-consumer`. It is a static golden file, but it protects runtime `ctx.state` behavior for nested loop variables.

## Dependencies and Integration Points
It integrates with the loop verification and execution machinery in `loop.go` and the test harness trajectory comparison. It also indirectly depends on reflect-based output type collection and map-backed workflow state.

## Risks
The main risk is incorrectly scoping loop variables so inner-loop outputs are cleared before outer actions can use them. Changes to loop variable initialization or nested loop verification could cause a missing input panic or a test failure in `outer-consumer`.

## Test Signals
The expected signal is a clean trajectory with no errors and final flow results `{}`. The visible result chain includes `Leaked: "val"` from `inner-action` and `Continue: ""` from `outer-consumer`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestNestedDoWhileOutput.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestNestedDoWhileVarLeak.trajectory.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestNestedDoWhileVarLeak.trajectory.json

## Purpose
This trajectory is the golden trace for `TestNestedDoWhileVarLeak` in `loop_test.go`. It verifies that variables created inside a nested loop do not cause a duplicate-definition panic when the outer loop re-enters for another iteration.

## Important APIs, Types, and Functions
It covers `DoWhile.verify`, `DoWhile.loop`, `Pipeline`, and `NewFuncAction`. The key implementation point is `DoWhile.loop` resetting known loop variables to zero values at the start of loop execution while allowing redefinition for nested loops.

## Control Flow
The file has 28 spans: 2 flow, 6 loop, 8 iteration, and 12 action spans. The outer loop runs two iterations. Each outer iteration calls `outer-action`, then an inner one-iteration loop with `inner-action` producing `Leaked: "val"` and `consumer-action` consuming it. The first outer iteration returns `Continue: "yes"` and the second returns `Continue: ""`.

## State and Persistence
The persisted span results show `Continue`, `InnerContinue`, and `Leaked` across both outer iterations. The fixture protects the map-backed workflow state from retaining nested loop output metadata in a way that would conflict on the second pass.

## Dependencies and Integration Points
It integrates with reflect-based loop variable typing, nested `Pipeline` execution, and trajectory span nesting. The test harness expects all action, loop, and iteration spans in deterministic order.

## Risks
If nested loop outputs are treated as globally new outputs on every outer iteration, execution can fail on re-entry. If they are over-cleared, `consumer-action` may not see `Leaked`. Either behavior would show up as missing spans or non-empty span errors.

## Test Signals
The expected signal is a no-error trace with two outer iteration names, repeated `inner-action`/`consumer-action` spans, and final flow results `{}`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestNestedDoWhileVarLeak.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestNilToolArg.llm.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestNilToolArg.llm.json

## Purpose
This LLM request fixture backs `TestNilToolArg` in `llm_agent_test.go`. It captures how an `LLMAgent` declares and replays a function tool whose argument is a nullable pointer field.

## Important APIs, Types, and Functions
The fixture records mocked `genai.GenerateContent` inputs produced by `LLMAgent.execute`, `NewFuncTool`, schema generation, and function response handling. The tool is `swiss-knife`; its `Optional` parameter schema has type `["null","integer"]` and is listed as required.

## Control Flow
The array has 2 requests. The first request contains the model config, system instruction with rendered `{{.toolSwissKnife}}`, and a `swiss-knife` function declaration. The second request replays the prompt, a model function call with `"Optional": null`, and a function response reporting `missing argument "Optional"`.

## State and Persistence
The file persists exact model request state, including system instruction text, tool schema, thinking level `HIGH`, and conversation history. It is a golden fixture, not runtime storage. Its important state signal is the distinction between a JSON null value and argument conversion semantics.

## Dependencies and Integration Points
It integrates with `google.golang.org/genai`, aflow schema generation, text/template rendering for tool placeholders, and `convertFromMap` argument conversion. The matching trajectory file records the execution-side error.

## Risks
Nullable pointer arguments are easy to regress: a schema may allow null while the converter treats null as missing. This fixture captures that current behavior. Any intentional fix for nil pointer handling must update both request and trajectory goldens.

## Test Signals
The test signal is the exact two-request history and the error response `missing argument "Optional"` after a null tool call.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestNilToolArg.llm.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestNilToolArg.trajectory.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestNilToolArg.trajectory.json

## Purpose
This trajectory is the execution-side golden for `TestNilToolArg`. It verifies how the agent records a nullable tool argument call and the resulting conversion error before still producing the final reply `Result`.

## Important APIs, Types, and Functions
It serializes `trajectory.Span` values for `LLMAgent`, LLM spans, and a `NewFuncTool` tool span named `swiss-knife`. The relevant code paths are tool argument conversion, `BadCallError` style feedback, and final reply extraction into the `Reply` field.

## Control Flow
The file has 10 spans: 2 flow, 2 agent, 4 LLM, and 2 tool spans. The agent first asks the LLM, receives a `swiss-knife` call with `Optional: null`, records a tool span error `missing argument "Optional"`, sends the error back to the model, and then records final reply `Result`.

## State and Persistence
The fixture persists the final flow result `{"Result":"Result"}` and the intermediate tool error. It protects state behavior where a failed tool call does not prevent the agent from continuing the conversation and setting the reply variable.

## Dependencies and Integration Points
It is paired with `TestNilToolArg.llm.json` and depends on the same genai function call format. It also integrates with trajectory span finishing, including error propagation on the tool span without failing the whole flow.

## Risks
A converter change could make null accepted, which would remove the error span. A stricter agent loop could treat the tool error as fatal, preventing the final reply. Either change must be intentional and reflected in both goldens.

## Test Signals
Expected signals are the tool error `missing argument "Optional"`, final agent reply `Result`, and final flow results containing `Result`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestNilToolArg.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestOnlyStructuredOutputs.llm.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestOnlyStructuredOutputs.llm.json

## Purpose
This fixture backs `TestOnlyStructuredOutputs`. It records the initial model request for an agent that has structured outputs only and no text `Reply` field.

## Important APIs, Types, and Functions
It exercises `LLMOutputs`, the synthetic `set-results` tool, `llmOutputsInstruction`, and schema generation for a `Result int` output. It uses `LLMAgent` without a reply variable.

## Control Flow
The JSON array contains 1 request. The request includes the system instruction `Instruction` plus the set-results requirement, a single function declaration named `set-results`, and the initial user prompt. The mocked model response in the test is a `set-results` call with `Result: 42`.

## State and Persistence
The file persists request config, not execution state. It establishes that structured output agents still run as text-capable model calls with a function tool and that final state is expected to come from tool results rather than a model text reply.

## Dependencies and Integration Points
It integrates with the genai tool declaration schema, aflow output registration, and final result extraction in `LLMAgent.execute`. The corresponding trajectory records that no final reply text is required.

## Risks
If agent verification starts requiring `Reply` even when `Outputs` is set, this fixture fails. If set-results schema generation changes, the golden request changes.

## Test Signals
The important signal is a single request declaring only `set-results` with required integer `Result`, thinking level `HIGH`, and no tool responses yet.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestOnlyStructuredOutputs.llm.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestOnlyStructuredOutputs.trajectory.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestOnlyStructuredOutputs.trajectory.json

## Purpose
This trajectory is the execution golden for `TestOnlyStructuredOutputs`. It proves that a pure structured-output agent can complete without producing text.

## Important APIs, Types, and Functions
It records spans for `LLMAgent`, the synthetic `set-results` tool from `LLMOutputs`, and final flow result collection. The central state field is `outputs map[string]any` inside the agent session.

## Control Flow
The file has 8 spans: 2 flow, 2 agent, 2 LLM, and 2 tool spans. The model calls `set-results`, the tool returns `Result: 42`, the agent finishes without a reply string, and the flow exports `Result: 42`.

## State and Persistence
The span results persist `Result: 42` at the tool, agent, and flow levels. This protects the behavior that `Outputs` can satisfy final workflow outputs independently from `Reply`.

## Dependencies and Integration Points
It is paired with the `.llm.json` request fixture and depends on `trajectory.Span.Results` serialization for tool and flow outputs. It also depends on the synthetic set-results tool being treated like a normal tool span.

## Risks
A regression could require a text reply, drop structured outputs when no reply exists, or fail to record set-results as a tool span. All would change this trajectory.

## Test Signals
Expected signals are no span errors, no final reply text, and final results `{"Result":42}`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestOnlyStructuredOutputs.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestOutputOverflow.llm.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestOutputOverflow.llm.json

## Purpose
This request fixture backs `TestOutputOverflow`. It captures how the agent lowers Gemini thinking levels after `FinishReasonMaxTokens` responses and resets thinking when the conversation advances.

## Important APIs, Types, and Functions
It exercises `LLMAgent.execute`, output overflow handling, genai `thinkingConfig`, `LLMOutputs`, and the synthetic `set-results` tool. The expected thinking sequence is `HIGH, MEDIUM, LOW, MINIMAL, HIGH, MEDIUM, LOW, MINIMAL`.

## Control Flow
The array has 8 requests. The first four are repeated initial prompt attempts with progressively reduced thinking. After a successful `set-results` call with `Output: 42`, the next four requests include that tool call/response in history and again step through the thinking levels until minimal thinking also overflows.

## State and Persistence
This fixture persists model config state across retries: system instruction, set-results schema, request history length, and thinking level. It does not store final workflow state, but it records when retry attempts reuse or extend conversation history.

## Dependencies and Integration Points
It integrates with genai finish reasons, aflow retry policy, and request construction. The trajectory file records the visible span-level errors `MAX_TOKENS`.

## Risks
Overflow recovery is sensitive to retry count and history management. A change that fails to lower thinking could keep overflowing; a change that fails to reset after a successful response would send later requests with too little reasoning budget.

## Test Signals
Expected signals are exactly 8 requests, the thinking level descent repeated twice, and preserved set-results history in the second half.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestOutputOverflow.llm.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestOutputOverflow.trajectory.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestOutputOverflow.trajectory.json

## Purpose
This trajectory is the execution golden for `TestOutputOverflow`. It verifies that output overflow is surfaced as span errors while the agent can still accept structured results before a later terminal overflow.

## Important APIs, Types, and Functions
It records `LLMAgent` spans, LLM spans with error values, and the `set-results` tool span. Relevant implementation areas are `parseLLMError` style response handling, finish-reason processing, and agent retry control.

## Control Flow
The file has 10 spans: 2 flow, 2 agent, 4 LLM, and 2 tool spans. Three initial LLM attempts finish with `MAX_TOKENS`, then the model calls `set-results` and the tool records `Output: 42`. A later invocation again overflows enough for the overall final expected error value to be `MAX_TOKENS`.

## State and Persistence
The trajectory persists `Output: 42` as an intermediate result and `MAX_TOKENS` errors on LLM spans. It protects the distinction between recoverable overflow attempts and final failure behavior.

## Dependencies and Integration Points
It is paired with `TestOutputOverflow.llm.json` and depends on genai finish reason string serialization. It also integrates with final result comparison in the test harness, where the expected test output is the max-token error string.

## Risks
Changing overflow span recording, retry limits, or set-results retention could make the trajectory misleading. The main behavioral risk is either losing successful structured output after retries or masking a final overflow as success.

## Test Signals
Expected signals are three recorded `MAX_TOKENS` errors, one `set-results` tool result `Output: 42`, and a final agent/flow error path matching `MAX_TOKENS`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestOutputOverflow.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestSetResultsToolIsNotLast.llm.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestSetResultsToolIsNotLast.llm.json

## Purpose
This request fixture backs `TestSetResultsToolIsNotLast`. It verifies that `set-results` can be called before another tool and still be retained as the final structured output once the agent later produces a reply.

## Important APIs, Types, and Functions
It exercises `LLMOutputs`, `NewFuncTool`, set-results handling inside `LLMAgent`, and request history construction for multiple tools. Declared tools are `tool` and `set-results`.

## Control Flow
The array has 3 requests. The initial request declares both tools. The second request includes a `set-results` call and response with `Result: 42`. The third request keeps that history and adds a later `tool` function call/response before the final text reply `Done` in the test reply sequence.

## State and Persistence
The file persists conversation history showing that structured outputs remain in history even when not the last tool call. It protects agent session state that stores accepted set-results output until the final reply completes the agent.

## Dependencies and Integration Points
It integrates with genai function response history, set-results output storage, and normal tool execution. The paired trajectory confirms final workflow outputs include both `Reply` and `Result`.

## Risks
If set-results is only accepted as the last tool call, the agent would incorrectly ask for results again. If later tool calls clear `session.outputs`, the final `Result` would be lost.

## Test Signals
Expected signals are request lengths 1, 3, and 5; tool declarations for `tool` and `set-results`; and preserved `Result: 42` history before the later `tool` call.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestSetResultsToolIsNotLast.llm.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestSetResultsToolIsNotLast.trajectory.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestSetResultsToolIsNotLast.trajectory.json

## Purpose
This trajectory is the execution golden for `TestSetResultsToolIsNotLast`. It proves that a structured output captured by `set-results` survives a subsequent normal tool invocation and final text reply.

## Important APIs, Types, and Functions
It records spans for `LLMAgent`, the synthetic `set-results` tool, and a normal `tool` created by `NewFuncTool`. It validates session output retention and final state export.

## Control Flow
The file has 14 spans: 2 flow, 2 agent, 6 LLM, and 4 tool spans. The agent receives `set-results`, executes it, receives and executes `tool`, then receives final reply `Done`. The final flow result includes both `Reply: Done` and `Result: 42`.

## State and Persistence
The fixture persists intermediate `Result: 42`, empty normal tool result, final reply, and combined flow results. It protects `agentSession.outputs` from being overwritten or cleared by unrelated tool calls.

## Dependencies and Integration Points
It pairs with the request fixture and depends on deterministic trajectory nesting and ordering for mixed tool types. It also depends on `LLMAgent.Outputs` and `Reply` coexisting.

## Risks
A regression in output lifetime can drop `Result`. A regression in finalization can require set-results to be last, causing additional missing-output prompts and trajectory drift.

## Test Signals
Expected signals are no errors, tool spans for both `set-results` and `tool`, final reply `Done`, and final results `{"Reply":"Done","Result":42}`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestSetResultsToolIsNotLast.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestSummaryWindow.llm.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestSummaryWindow.llm.json

## Purpose
This request fixture backs `TestSummaryWindow`. It captures sliding-window summarization behavior when an agent keeps only a limited number of historical messages and asks the model to attach summaries before old context is dropped.

## Important APIs, Types, and Functions
It exercises private `LLMAgent.summaryWindow`, `slidingWindowInstruction`, request trimming, function tool history, and `NewFuncTool` declaration for `tick`. The tool has `Seq` input and `ResFoo` output.

## Control Flow
The array has 8 requests. The first declares `tick`; later requests alternate `tick` calls and responses. When the window threshold is reached, the request includes `slidingWindowInstruction` appended to a user message. Subsequent requests preserve a model summary text such as `summary 3` while older calls are trimmed.

## State and Persistence
The fixture persists exact conversation slices after windowing: request lengths alternate between compact 3-message windows and 4-message summary-producing windows. It protects `summaryMessage` tracking inside `agentSession`.

## Dependencies and Integration Points
It integrates with genai content roles, tool call/function response serialization, and trajectory recording. The paired trajectory confirms repeated tool execution and final reply.

## Risks
Sliding-window logic can drop useful tool output too early, duplicate summaries, or fail to request a summary before trimming. Those changes would appear as request history length or instruction placement differences.

## Test Signals
Expected signals are 8 requests, repeated `tick` calls, inserted `slidingWindowInstruction`, summaries in model messages, and final completion after request sequence exceeds 6.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestSummaryWindow.llm.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestSummaryWindow.trajectory.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestSummaryWindow.trajectory.json

## Purpose
This trajectory is the execution golden for `TestSummaryWindow`. It verifies that sliding-window summarization preserves forward progress across many tool calls and ends with reply `Done`.

## Important APIs, Types, and Functions
It records `LLMAgent` LLM spans and `tick` tool spans. The key implementation state is `agentSession.req` plus `summaryMessage`, with `summaryWindow` deciding when to ask for model summary text.

## Control Flow
The file has 34 spans: 2 flow, 2 agent, 16 LLM, and 14 tool spans. Seven `tick` tool executions return `ResFoo: 123`. The model eventually stops calling tools and returns text `Done`.

## State and Persistence
The trajectory persists repeated tool outputs and final flow result `{"Reply":"Done"}`. It does not show every trimmed request message directly; that role belongs to the `.llm.json` fixture. Together they protect both runtime spans and request history.

## Dependencies and Integration Points
It pairs with `TestSummaryWindow.llm.json` and depends on deterministic fake time and span sequencing. It also integrates with tool result serialization and final reply extraction.

## Risks
If summary-window trimming breaks tool history or summary insertion, the agent may loop, lose context, or fail to finish. Span counts and final reply provide broad regression coverage.

## Test Signals
Expected signals are 7 successful `tick` results, no errors, and final reply/result `Done`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestSummaryWindow.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestTokenCompression.llm.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestTokenCompression.llm.json

## Purpose
This request fixture backs `TestTokenCompression`. It captures token-threshold based context compression, where the agent calls a cheaper compressor prompt and resumes with only the anchor prompt plus summary.

## Important APIs, Types, and Functions
It exercises private `LLMAgent.compressTokens`, `compressContext`, compressor instruction construction, `GoodBalancedModel` style compressor behavior, and normal `tick` tool declaration. It also records usage-triggered transition from full history to compressed history.

## Control Flow
The array has 4 requests. The agent first calls `tick`, then calls `tick` again after prompt token count grows. The third request is a compressor-model request containing system instructions wrapped in `<system_instructions>` and the prior tool history. The fourth request resumes the main model with two messages: original prompt and `Here is the summary... compressed summary`.

## State and Persistence
The file persists exact compression request content, temperature `0.1` for the compressor, and the truncated post-compression request. It protects the anchor-plus-summary invariant asserted by the Go test.

## Dependencies and Integration Points
It integrates with genai usage metadata from mocked responses, request history construction, and the trajectory that records a `smarty-compressor` LLM span. It also interacts with duplicate-tool-call detection because compression resets history in related tests.

## Risks
Compression can accidentally duplicate system instructions, lose the original prompt, retain too much old history, or summarize with tools enabled. This fixture checks that the compressor has no tools and that resumed main history is compact.

## Test Signals
Expected signals are 4 requests, a compressor request with the memory-compressor instruction, and a final main request containing only the prompt plus formatted summary.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestTokenCompression.llm.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestTokenCompression.trajectory.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestTokenCompression.trajectory.json

## Purpose
This trajectory is the execution golden for `TestTokenCompression`. It proves that context compression is recorded as an LLM span and the main agent continues to final reply `Done`.

## Important APIs, Types, and Functions
It records spans for agent `smarty`, compressor LLM name `smarty-compressor`, and `tick` tool executions. The relevant state is token accounting from `GenerateContentResponse.UsageMetadata` and the compressed summary reply.

## Control Flow
The file has 16 spans: 2 flow, 2 agent, 8 LLM, and 4 tool spans. Two `tick` calls occur, token growth triggers a compressor LLM span with reply `compressed summary`, and the main agent resumes and returns `Done`.

## State and Persistence
The fixture persists `ResFoo: 123` tool results, compressor reply text, and final flow result `{"Reply":"Done"}`. It protects the execution trace around the request-history truncation captured in the `.llm.json` file.

## Dependencies and Integration Points
It pairs with the LLM request fixture and depends on genai usage metadata being interpreted consistently. It also integrates with trajectory naming for compressor spans.

## Risks
If compression is not recorded, if the compressor reply is treated as the final answer, or if the main request cannot resume from summary, this trajectory will drift or fail.

## Test Signals
Expected signals are the `smarty-compressor` LLM reply `compressed summary`, two successful `tick` tool results, and final reply `Done`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestTokenCompression.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestTokenCompressionResetsHistory.llm.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestTokenCompressionResetsHistory.llm.json

## Purpose
This request fixture backs `TestTokenCompressionResetsHistory`. It verifies that after compression the agent can make another identical `tick` tool call without duplicate-call detection blocking it.

## Important APIs, Types, and Functions
It covers `LLMAgent.compressTokens`, `agentSession.toolHistory`, `recordAndCheckDuplicate`, compressor request construction, and `NewFuncTool` for `tick`.

## Control Flow
The array has 6 requests. Before compression, the history accumulates three identical `tick` calls. A compressor request summarizes that history. The resumed main request contains only prompt plus summary, and the final request records a fourth `tick` call/response after compression.

## State and Persistence
The fixture persists both request-history truncation and the reset duplicate-call context. The post-compression history lacks the prior three tool call records, which is the key state behavior under test.

## Dependencies and Integration Points
It integrates with token usage metadata in mocked responses, compressor prompting, and duplicate loop detection constants in `llm_agent.go`. The paired trajectory counts four successful `tick` executions.

## Risks
If compression leaves `toolHistory` intact, the fourth identical call would be rejected as a loop. If compression drops too much, the resumed request may lose the summary or prompt anchor.

## Test Signals
Expected signals are 6 requests, compressor invocation after three ticks, resumed two-message history, and a later accepted `id4` tick call.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestTokenCompressionResetsHistory.llm.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestTokenCompressionResetsHistory.trajectory.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestTokenCompressionResetsHistory.trajectory.json

## Purpose
This trajectory is the execution golden for `TestTokenCompressionResetsHistory`. It proves that compression resets duplicate tool-call history while preserving agent progress.

## Important APIs, Types, and Functions
It records `LLMAgent` spans, compressor LLM span `smarty-compressor`, and repeated `tick` tool spans. The most important implementation state is `agentSession.toolHistory`, which must be cleared when context is compressed.

## Control Flow
The file has 24 spans: 2 flow, 2 agent, 12 LLM, and 8 tool spans. Four `tick` executions return `ResFoo: 123`. Compression occurs after the third tick and records reply `compressed summary`; the fourth identical tick is then allowed and the agent returns `Done`.

## State and Persistence
The fixture persists all four successful tool results and final `Reply: Done`. It guards against loop-detection state leaking across compression.

## Dependencies and Integration Points
It pairs with the request fixture and depends on both genai usage metadata and trajectory span naming. It also integrates with `defaultLoopDetectionLimit`, where repeated identical calls are otherwise bounded.

## Risks
The main risk is false-positive loop detection after compression. A secondary risk is clearing too much state, such as losing accepted tool results needed in the summary.

## Test Signals
Expected signals are four `tick` tool results, one compressor reply `compressed summary`, no duplicate-call error, and final flow result `{"Reply":"Done"}`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestTokenCompressionResetsHistory.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolErrors.llm.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolErrors.llm.json

## Purpose
This request fixture backs `TestToolErrors` in `func_tool_test.go`. It records how tool errors are returned to the model as function responses.

## Important APIs, Types, and Functions
It exercises `NewFuncTool`, `BadCallError`, normal Go errors from tool execution, genai function responses, and the `faulty` tool schema with boolean `CallError`.

## Control Flow
The array has 2 requests. The first declares tool `faulty`. The second request includes a `faulty` function call with `CallError: true` and a function response containing error text `you are wrong`. The next mocked reply in the Go test makes a hard-error call that is represented in the trajectory.

## State and Persistence
This file persists request history after a recoverable bad-call error. It does not include the later terminal hard error request because the test stops when the hard error fails the flow.

## Dependencies and Integration Points
It integrates with function response encoding, tool schema generation, and the agent loop that allows the model to correct bad calls. The trajectory captures the later hard error and final failure text.

## Risks
If all tool errors become fatal, this fixture would have no second request. If bad-call errors are not returned to the model, correction workflows break.

## Test Signals
Expected signals are the `faulty` declaration, one function call with `CallError: true`, and a function response error `you are wrong`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolErrors.llm.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolErrors.trajectory.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolErrors.trajectory.json

## Purpose
This trajectory is the execution golden for `TestToolErrors`. It distinguishes recoverable bad-call feedback from terminal hard tool failure.

## Important APIs, Types, and Functions
It records `LLMAgent`, LLM spans, and tool spans for `faulty`. It covers `BadCallError`, ordinary `error`, tool execution result/error recording, and final flow error propagation.

## Control Flow
The file has 12 spans: 2 flow, 2 agent, 4 LLM, and 4 tool spans. The first tool call errors with `you are wrong`, which is returned to the model. The second call uses `CallError: false`, the tool returns `hard error`, and the agent/flow finish with `tool faulty failed: error: hard error args: map[CallError:false]`.

## State and Persistence
The fixture persists both tool error spans and the propagated terminal error. It protects the state transition from recoverable model feedback to fatal workflow error.

## Dependencies and Integration Points
It pairs with the LLM request fixture and depends on error string formatting in tool wrappers. It also integrates with trajectory error fields on tool, agent, and flow spans.

## Risks
Changing error formatting can break golden comparisons. More importantly, conflating `BadCallError` with hard errors would either stop too early or continue after a real failure.

## Test Signals
Expected signals are tool error `you are wrong`, later `hard error`, and final flow error text naming tool `faulty` and its args.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolErrors.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolInPrompt.llm.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolInPrompt.llm.json

## Purpose
This request fixture backs `TestToolInPrompt`. It verifies that tool template placeholders can be rendered in both the agent instruction and prompt before the request is sent.

## Important APIs, Types, and Functions
It exercises `LLMAgent.Instruction`, `LLMAgent.Prompt`, the template helper that exposes tools as `.toolSwissKnife`, and `NewFuncTool` declaration for `swiss-knife`.

## Control Flow
The array contains 1 request. The system instruction is rendered as `Use swiss-knife` plus the multiple-tools hint. The prompt is rendered as `Please call swiss-knife now.` The tool declaration is still included, although the mocked model replies with text directly.

## State and Persistence
The file persists rendered prompt/config state and verifies there are no unresolved template markers. It does not persist execution state beyond the outbound request.

## Dependencies and Integration Points
It integrates with aflow template rendering, tool-name normalization for template variables, and genai request construction. The trajectory confirms the agent can finish without actually using the prompted tool.

## Risks
A template helper regression could leave `{{.toolSwissKnife}}` unresolved or render the wrong tool name. This would degrade prompts and potentially confuse model tool calls.

## Test Signals
Expected signals are one request, rendered text containing `swiss-knife`, a valid `swiss-knife` tool declaration, and no function call history.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolInPrompt.llm.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolInPrompt.trajectory.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolInPrompt.trajectory.json

## Purpose
This trajectory is the execution golden for `TestToolInPrompt`. It verifies that an agent with rendered tool references in prompt/instruction can complete with a plain text reply.

## Important APIs, Types, and Functions
It records `LLMAgent` and LLM spans, but no tool span, because the mocked model does not call `swiss-knife`. It still depends on `NewFuncTool` verification and template rendering during agent setup.

## Control Flow
The file has 6 spans: 2 flow, 2 agent, and 2 LLM spans. The agent sends its request, receives reply `Ignored`, records that reply, and the flow exports `Ignored`.

## State and Persistence
The trajectory persists final agent reply and flow result `{"Ignored":"Ignored"}`. It protects the behavior that declaring a tool and mentioning it in prompt text does not force its execution.

## Dependencies and Integration Points
It pairs with the LLM request fixture and integrates with final reply extraction. The absence of tool spans is meaningful and should remain stable unless the mocked replies change.

## Risks
If the framework starts enforcing tool use based on prompt text, this test would fail. If template rendering breaks earlier, the paired `.llm.json` catches it before trajectory comparison.

## Test Signals
Expected signals are no errors, no tool spans, final reply `Ignored`, and final flow result `Ignored`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolInPrompt.trajectory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolMisbehavior.llm.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolMisbehavior.llm.json

## Purpose
This request fixture backs `TestToolMisbehavior` in `flow_test.go`. It captures a robust agent loop that handles several malformed model tool calls, missing structured outputs, duplicate set-results calls, and an empty final reply before eventual success.

## Important APIs, Types, and Functions
It exercises `LLMAgent`, `LLMOutputs`, `NewFuncTool`, set-results validation, tool existence checks, argument conversion, function response error generation, and missing-reply/missing-output prompts. Declared tools are `tool1`, `tool2`, and `set-results`.

## Control Flow
The array has 5 requests. The first declares tools. The second records a batch of six model calls: a valid `tool1`, invalid `tool2` string arg, missing `tool2` arg, `tool2` with extra arg but valid required value, nonexistent `tool3`, and wrong `set-results` arg. The third adds a final text reply `I am done` and a missing set-results correction prompt. The fourth adds two successful `set-results` calls. The fifth adds an empty reply marker and a missing-reply correction prompt.

## State and Persistence
The file persists rich conversation history with error function responses: wrong type, missing argument, nonexistent tool, and missing `AdditionalOutput`. It also persists correction prompts that keep the agent in the loop until both structured output and final reply are valid.

## Dependencies and Integration Points
It integrates with genai multi-part tool calls, schema conversion, output storage, and agent finalization. It is one of the broadest fixtures for defensive model-tool integration behavior.

## Risks
The main risks are accepting malformed outputs, stopping after an invalid final reply, or losing the later accepted `AdditionalOutput: 2` when multiple set-results calls appear. Error text stability is also important for golden comparisons.

## Test Signals
Expected signals include all four error response classes, retention of successful tool results, missing-output and missing-reply correction prompts, and final history that precedes the model reply `Finally done`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolMisbehavior.llm.json -->
