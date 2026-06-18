# subset-b-008137 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/agent/TestChatbotAgentExecutionPolicy.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/agent/TestChatbotAgentExecutionPolicy.java

Purpose: This test suite verifies the security boundary in `ChatbotAgent` after the first LLM call has produced a candidate tool-call JSON but before any `ToolExecutor` network/API work is allowed. It protects against prompt injection causing disallowed Recon API access, path traversal, prefix confusion, absolute URL exfiltration, and partial execution of mixed valid/invalid multi-endpoint requests.

Important APIs/types/functions: The class uses mocked `LLMClient` and `ToolExecutor`, `OzoneConfiguration`, `ChatbotConfigKeys.OZONE_RECON_CHATBOT_ENABLED`, `OZONE_RECON_CHATBOT_EXEC_REQUIRE_SAFE_SCOPE`, `OZONE_RECON_CHATBOT_MAX_TOOL_CALLS`, `ChatbotAgent.processQuery`, `LLMClient.LLMResponse`, and `ToolExecutor.ToolExecutionOutcome`. Mockito verification on `executeToolCallWithPolicy` is the central signal.

Control flow: `setUp` enables the chatbot and safe-scope enforcement, stubs the executor leniently, and constructs a `ChatbotAgent`. Each test configures the first LLM response as a raw JSON object. The agent parses that object, normalizes/validates endpoints, and either returns a direct rejection/fallback or proceeds to execution. These tests assert that disallowed endpoints never reach the executor and that most rejection paths require only one LLM call.

State and persistence behavior: There is no persistent state. Runtime state is limited to configuration-driven policy flags, parsed endpoint strings, parsed methods/parameters, and mocked invocation counts. The tests explicitly validate that blocked responses do not expose stack traces, internal package names, or chatbot credential config key fragments.

Dependencies and integration points: This suite anchors the integration between LLM output parsing, endpoint allowlist policy, path canonicalization, multi-tool batch validation, and the executor interface. It complements the parsing tests and endpoint tests by focusing on the Java-side policy layer that must remain authoritative even when the LLM emits malicious content.

Risks: Assertions mostly check non-execution and broad response text fragments, so they do not fully pin down exact user-facing rejection messages. The tests depend on the current allowlist semantics for `/api/v1/keys` boundary matching and canonical traversal handling. Multi-endpoint behavior is intentionally all-or-nothing; a future partial-execution policy would require deliberate test updates.

Test signals: Strong signals include `never()` calls to `executeToolCallWithPolicy` for `/api/v1/admin/delete`, external absolute URLs, `/api/v1/internal/secrets`, `/api/v1/keys2`, and traversal paths; `times(1)` LLM usage for direct rejection; and response-content checks for permitted-path wording without internal exception or config leakage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/agent/TestChatbotAgentExecutionPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/agent/TestChatbotAgentJsonExtraction.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/agent/TestChatbotAgentJsonExtraction.java

Purpose: This compact suite tests `ChatbotUtils.extractFirstJsonObject`, the raw-text preprocessing step used to recover a JSON object from LLM output before Jackson/tool-call parsing. It verifies robustness against prose, markdown fences, nested objects, braces inside string values, escaped quotes, truncation, null/empty inputs, arrays, Unicode, control characters, and large string values.

Important APIs/types/functions: The only production API under test is `ChatbotUtils.extractFirstJsonObject(String)`. The tests use JUnit `assertEquals`, `assertNull`, `assertNotNull`, and `assertTrue` to verify exact extracted substrings or graceful null returns.

Control flow: Each test passes one raw string to the extractor. Happy paths expect the complete first balanced `{...}` object to be returned unchanged. Prose and markdown wrapper tests expect surrounding text/fences to be ignored. Invalid input tests expect `null`. Multiple-object and array tests document that extraction starts at the first `{` and returns the first balanced object only.

State and persistence behavior: There is no mutable shared state or persistence. The behavior under test is a local scanning algorithm that must maintain brace depth, string-mode state, and escape handling without parsing full JSON.

Dependencies and integration points: This utility feeds `ChatbotAgent` tool-call routing. Its output determines whether the agent enters `SINGLE_ENDPOINT`, `MULTI_ENDPOINT`, `DOCUMENTATION_QUERY`, or fallback flow. Returning a syntactically complete but semantically unknown object is intentional; later parsing/routing handles missing or unknown `type` fields.

Risks: The extractor is not a full JSON validator; it only finds a balanced object. Arrays produce the first inner object instead of rejecting the array. The large-json test checks no crash but does not enforce timing thresholds. Unicode/control-character cases protect scanner stability, not downstream JSON parser acceptance.

Test signals: Exact string equality for simple, nested, multi-endpoint, prose-wrapped, fenced, escaped-quote, and string-brace examples; `null` for truncated/no-object/sentinel/prose-only inputs; and non-null bounded-object shape for control-character and 10,000-character string cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/agent/TestChatbotAgentJsonExtraction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/agent/TestChatbotAgentListKeysPolicy.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/agent/TestChatbotAgentListKeysPolicy.java

Purpose: This class verifies `ChatbotAgent` handling for the sensitive `/api/v1/keys/listKeys` endpoint. It ensures safe-scope validation rejects broad key scans unless the LLM provides a bucket-scoped `startPrefix`, verifies disabling safe-scope allows root scans, checks parameter pass-through, and confirms executor/LLM failures are wrapped in `ChatbotException`.

Important APIs/types/functions: The suite uses `ChatbotAgent.processQuery`, mocked `LLMClient.chatCompletion`, mocked `ToolExecutor.executeToolCallWithPolicy`, `ChatbotException`, `OzoneConfiguration`, and `ChatbotConfigKeys.OZONE_RECON_CHATBOT_EXEC_REQUIRE_SAFE_SCOPE`. `ArgumentCaptor<Map<String,String>>` validates exact executor parameters.

Control flow: `setUp` enables safe-scope and default executor success. Rejection tests return a `SINGLE_ENDPOINT` LLM JSON with absent, empty, root-only, or volume-only `startPrefix`; the agent must return a response without invoking the executor. Allowed tests return a bucket-scoped prefix and then a summary response, causing execution followed by a second LLM call. Exception tests inject `IOException` from the executor or runtime failure from the summarization call.

State and persistence behavior: There is no persistence. Runtime state includes the parsed parameters map, safe-scope boolean, max tool call count, and the two-stage LLM interaction. The disabled-safe-scope test constructs a second `ChatbotAgent` with a different config to prove policy is configuration controlled.

Dependencies and integration points: This suite binds LLM tool selection to Recon key-listing execution policy. It sits between general allowlist tests and `TestToolExecutorListKeys`, proving that the agent enforces bucket scoping before the executor handles pagination. It also validates that user/LLM filters such as `limit`, `replicationType`, and `keySize` survive routing.

Risks: The bucket-scope rule is tested syntactically as `/<volume>/<bucket>` and does not validate actual volume/bucket existence. Error wrapping assertions allow either execution or response-generation wording for summarization failure, which is resilient but less exact. Parameter values are strings, so type conversion is delegated elsewhere.

Test signals: No executor invocation for root/null/empty/volume-only prefixes; one executor invocation for `/vol1/bucket1`; execution allowed when `OZONE_RECON_CHATBOT_EXEC_REQUIRE_SAFE_SCOPE=false`; preserved `IOException` cause and message; preserved summarization runtime cause; and captured optional parameters exactly matching the LLM JSON.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/agent/TestChatbotAgentListKeysPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/agent/TestChatbotAgentToolCallParsing.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/agent/TestChatbotAgentToolCallParsing.java

Purpose: This suite tests `ChatbotAgent.processQuery` orchestration after the first LLM call: JSON extraction, tool-call type routing, executor invocation, second LLM summarization, fallback routing, max-tool-call capping, malformed output handling, input validation, and exception wrapping.

Important APIs/types/functions: Key elements are `ChatbotAgent`, `LLMClient.LLMResponse`, `LLMClient.LLMException`, `ToolExecutor.ToolExecutionOutcome`, `ChatbotException`, `ChatbotConfigKeys`, and Mockito verification for `chatCompletion` and `executeToolCallWithPolicy`. Canned JSON constants cover `SINGLE_ENDPOINT`, `MULTI_ENDPOINT`, and `DOCUMENTATION_QUERY`.

Control flow: `setUp` enables the chatbot with safe-scope and max five tool calls. Happy-path tests return a tool JSON, verify one executor call for single endpoint or two for multi-endpoint, and require a second LLM call for summarization. Documentation queries return an answer directly with no executor and no second LLM call. Unknown or malformed outputs trigger fallback, which uses a second LLM call but no executor. Exception tests verify initial LLM, executor, and summarization failures are surfaced as `ChatbotException`.

State and persistence behavior: There is no persistence. Runtime state is primarily the parsed tool-call model, the bounded list of multi-endpoint calls, empty-map substitution for null/wrong `parameters`, and invocation counts. Empty and null user queries are rejected before any LLM state is touched.

Dependencies and integration points: This is the main behavioral contract for the chatbot agent's LLM-to-Recon pipeline. It integrates `ChatbotUtils` extraction behavior, JSON field parsing, endpoint/method/parameter routing, the executor policy method, fallback prompting, and summarization. It also validates that empty endpoints are never sent to lower layers.

Risks: The multi-endpoint cap uses `atMost(5)`, so it verifies a ceiling but not exact truncation behavior. The tests do not inspect constructed prompts or response bodies beyond non-null/string fragments. Unknown type and missing fields rely on fallback text from the mocked LLM rather than exact internal fallback prompt shape.

Test signals: One executor plus two LLM calls for single endpoint; two executor calls plus two LLM calls for two endpoint JSON; direct documentation response with one LLM call; fallback paths for unknown type, missing type, truncated JSON, prose, sentinel, empty tool-call arrays, and empty endpoint; early `ChatbotException` for empty/null query; empty-map resilience for bad `parameters`; max five tool calls; and cause preservation for LLM/executor failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/agent/TestChatbotAgentToolCallParsing.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/agent/TestToolExecutorListKeys.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/agent/TestToolExecutorListKeys.java

Purpose: This suite verifies `ToolExecutor` handling of the paginated `listKeys` Recon API. It focuses on page aggregation, record/page counters, truncation when the configured page limit is reached, empty result handling, malformed prefix rejection, and propagation of HTTP/API `IOException`s.

Important APIs/types/functions: The tests use a spy of real `ToolExecutor`, `executeToolCallWithPolicy`, mocked `executeSingleCall`, `ToolExecutor.ToolExecutionOutcome`, Jackson `ObjectMapper`/`JsonNode`, and `ChatbotConfigKeys.OZONE_RECON_CHATBOT_EXEC_MAX_PAGES` plus `OZONE_RECON_CHATBOT_EXEC_PAGE_SIZE`.

Control flow: Setup constructs a real executor with max pages five and page size 200, then spies it so individual HTTP calls can be replaced with canned `JsonNode` pages. `testSinglePage` stops after a response without `lastKey`. `testMultiplePages` uses `lastKey` on page one to trigger a second call. `testMaxPagesLimit` returns an infinite page shape and expects termination at the caller-provided max. Error tests assert invalid `startPrefix` is rejected before any HTTP call and IO failures bubble up.

State and persistence behavior: There is no persistence. Runtime state includes the mutable request parameters passed between pages, aggregated `keys` array, records processed, pages fetched, and `truncated` marker in both the outcome and merged JSON body.

Dependencies and integration points: This class tests the execution engine used by the chatbot agent after safe-scope approval. It integrates Recon API response shape assumptions (`keys`, `lastKey`, `truncated`) with executor pagination policy and protects upper layers from unbounded listing.

Risks: Because `executeSingleCall` is mocked, URL construction and real HTTP behavior are not covered here. The tests do not inspect the `prevKey` or page parameter mutation, only call counts and merged output. Prefix validation duplicates some safe-scope intent at executor level and must stay aligned with the agent tests.

Test signals: Exact executor call counts of one, two, or three; `recordsProcessed`, `pagesFetched`, and `isTruncated` values; merged `keys` array lengths; `truncated=true` in capped output; `IllegalArgumentException` containing `requires 'startPrefix'` for missing/root prefix; and raw `IOException` message preservation for API failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/agent/TestToolExecutorListKeys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/api/TestChatbotEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/api/TestChatbotEndpoint.java

Purpose: This test suite validates the REST-level contract of `ChatbotEndpoint`, before and around agent execution. It covers input validation, successful and fallback responses, disabled feature behavior, generic error shielding, request timeout, executor queue saturation, singleton reuse, health reporting, model listing, and model-list failure handling.

Important APIs/types/functions: The class uses `ChatbotEndpoint.chat`, `health`, `getSupportedModels`, `shutdown`, `ChatbotEndpoint.ChatRequest`, `ChatbotEndpoint.ChatResponse`, `ChatbotAgent.processQuery`, `LLMClient.isAvailable`, `LLMClient.getSupportedModels`, `ChatbotException`, `Response`, and concurrency primitives `CountDownLatch`, `ExecutorService`, `Future`, `AtomicInteger`, and `AtomicReference`.

Control flow: `setUp` enables the chatbot, configures thread pool size, queue size, and request timeout, and constructs the endpoint with mocked agent/client. Validation tests call `chat` directly and inspect `Response`. Success tests stub the agent. Disabled tests create separate endpoint instances with feature toggle off. Timeout and queue tests construct short-timeout or small-queue endpoints and use blocking agent answers to force endpoint-level rejection or timeout paths.

State and persistence behavior: There is no persistence. Runtime state includes the endpoint's internal executor service, bounded queue, timeout configuration, enabled flag, and LLM client availability/model list. `tearDown` calls `shutdown` to release endpoint worker threads after each test.

Dependencies and integration points: This suite is the HTTP boundary for the chatbot feature. It integrates REST response mapping with agent exceptions, feature toggles, request admission control, asynchronous execution, health checks, and LLM model discovery. It confirms fallback text from the agent is a successful HTTP 200, not an error.

Risks: Concurrency tests use sleeps/latches and can be timing-sensitive, though timeouts are generous. Queue saturation asserts at least six 503 responses rather than an exact distribution because scheduling can vary. The endpoint is tested directly rather than through a Jersey container, so serialization annotations and network filters are outside scope.

Test signals: 400 with exact `Query cannot be empty`; 200 with `success=true` and response body for normal and fallback answers; 503 for disabled chat/models; 500 with generic error and no class/stack/rate-limit leak; 504 within two seconds for a 200 ms timeout; at least six queue-full 503s containing `too many requests`; five repeated calls routed to the same agent; health `enabled` and `llmClientAvailable` booleans; model list containing `gemini-2.5-flash`; and 500 for model provider exception.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/api/TestChatbotEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/llm/TestLangChain4jDispatcher.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/llm/TestLangChain4jDispatcher.java

Purpose: This suite tests `LangChain4jDispatcher` provider availability, supported-model discovery, validation, and provider routing without making real network calls. It verifies configured API keys control availability/model lists, unknown or unconfigured models are rejected, and explicit provider hints bypass model-list reverse lookup.

Important APIs/types/functions: The class uses `LangChain4jDispatcher.chatCompletion`, `isAvailable`, `getSupportedModels`, `LLMClient.ChatMessage`, `LLMClient.LLMException`, `CredentialHelper`, `OzoneConfiguration`, and chatbot provider/key config entries for Gemini, OpenAI, and Anthropic.

Control flow: Setup defaults provider to `gemini` and creates a dispatcher with no keys. Validation tests call `chatCompletion` with null/empty messages and expect `LLMException`. Availability/model tests mutate config keys and recreate the dispatcher. Routing tests either inspect `getSupportedModels` or call `chatCompletion` with missing keys and assert the resulting exception identifies the provider path or model recognition failure.

State and persistence behavior: No persistence is used. Runtime state is derived from configuration and `CredentialHelper` lookups. The dispatcher's supported model list changes based on which provider secrets are present.

Dependencies and integration points: This file anchors the chatbot LLM abstraction to provider-specific key configuration and model naming. It protects the `/api/v1/chatbot/models` endpoint contract indirectly by checking exposed model names and validates that a configured Gemini key does not accidentally route OpenAI model names to Gemini.

Risks: Tests avoid real LangChain4j clients and network calls, so request serialization, provider responses, token accounting, and actual model invocation are not covered. Model name assertions such as `gemini-2.5-flash`, `gpt-4.1`, and `claude-sonnet-4-6` are intentionally brittle compatibility signals and must be updated when supported lists change.

Test signals: `LLMException` for null/empty messages; `isAvailable=false` without keys and true with Gemini/OpenAI key; empty supported list without keys; provider-specific model names present with corresponding keys; unknown model errors mentioning `not recognised` and `GET /api/v1/chatbot/models`; OpenAI model rejected when only Gemini key exists; explicit `_provider=openai` and `anthropic:model` strings produce provider-specific missing-key errors rather than model-recognition errors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/llm/TestLangChain4jDispatcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/security/TestCredentialHelper.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/security/TestCredentialHelper.java

Purpose: This suite validates `CredentialHelper`, the chatbot secret resolver. It confirms secrets can be read from Hadoop credential provider JCEKS stores, plaintext configuration is used as fallback, missing values return an empty string/false availability, JCEKS values take priority over plaintext, and multiple chatbot provider keys can coexist in one credential store.

Important APIs/types/functions: The tests use `CredentialHelper.getSecret`, `hasSecret`, `OzoneConfiguration`, `CredentialProviderFactory.CREDENTIAL_PROVIDER_PATH`, `CredentialProvider.createCredentialEntry`, `flush`, JUnit `@TempDir`, and temporary JCEKS paths of the form `jceks://file...`.

Control flow: Each JCEKS test creates a temporary credential file path, sets it in the configuration, obtains a provider via Hadoop security APIs, writes one or more secret entries, flushes, and then constructs `CredentialHelper` to resolve them. Plaintext and missing-key tests use only config or empty config.

State and persistence behavior: Persistent state is the temporary JCEKS file under JUnit's temp directory. The helper reads credential provider entries before falling back to plain config. The tests verify no secret returns `""` rather than null and that `hasSecret` reflects non-empty resolution.

Dependencies and integration points: This is the credential source for `LangChain4jDispatcher` and chatbot provider availability. It integrates Recon chatbot config keys with Hadoop's credential provider mechanism, which is important for production deployments that should not store API keys in plaintext XML.

Risks: The JCEKS URI is built by string concatenation and assumes the local filesystem path format used by Hadoop credential providers. Tests do not cover malformed credential provider paths, provider initialization failures, or empty string secrets. Secret values are synthetic and not redacted in assertions because they are test-only.

Test signals: Exact returned secret from JCEKS; exact returned plaintext fallback; empty string and `hasSecret=false` for missing key; JCEKS overriding plaintext for the same key; and successful independent lookup of OpenAI and Gemini keys from one JCEKS store.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/chatbot/security/TestCredentialHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/common/ReconTestUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/common/ReconTestUtils.java

Purpose: This small test utility class centralizes creation of `SCMNodeDetails` for Recon-oriented tests. It supplies a deterministic Recon node id and datanode protocol server address.

Important APIs/types/functions: The exported API is `ReconTestUtils.getReconNodeDetails()`. It uses `SCMNodeDetails.Builder`, `setSCMNodeId`, `setDatanodeProtocolServerAddress`, and `InetSocketAddress.createUnresolved("127.0.0.1", 9888)`. The private constructor prevents instantiation.

Control flow: Calling `getReconNodeDetails` creates a new builder, sets `SCMNodeId` to `Recon`, sets the datanode protocol server address, and returns `builder.build()`.

State and persistence behavior: There is no persistence or shared mutable state. Each call returns a newly built value object. The address is unresolved to avoid DNS/network dependency during tests.

Dependencies and integration points: The helper is intended for Recon tests that need SCM node details without standing up a full SCM service. It integrates with HDDS SCM HA metadata types and gives tests a consistent Recon identity.

Risks: The fixed port `9888` and id `Recon` may conflict with tests that need multi-node uniqueness if reused blindly. The helper only sets the datanode protocol address, not the full matrix of SCM service endpoints.

Test signals: This is a helper rather than a test. Its correctness signal is deterministic construction of an `SCMNodeDetails` instance suitable for test injection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/common/ReconTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/fsck/TestContainerHealthStatus.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/fsck/TestContainerHealthStatus.java

Purpose: This suite verifies `ContainerHealthStatus`, the Recon/SCM health classifier for containers based on expected replication, actual replicas, replica states, node operational states, placement policy, and replica data checksums. It covers healthy, missing, under-replicated, over-replicated, mis-replicated, checksum mismatch, and decommission/maintenance behavior.

Important APIs/types/functions: The tests use `ContainerHealthStatus`, `ContainerInfo`, `ContainerReplica`, `ContainerReplica.ContainerReplicaBuilder`, `ContainerChecksums`, `ContainerID`, `PlacementPolicy.validateContainerPlacement`, `ContainerPlacementStatusDefault`, `RatisReplicationConfig`, `MockDatanodeDetails`, `ReconContainerMetadataManager`, `HddsProtos.NodeOperationalState`, and `ContainerReplicaProto.State`.

Control flow: `setup` mocks a closed RATIS THREE container with ID 123456 and a placement policy that is initially satisfied. Helper methods generate sets of replicas with desired container states and either matching or incrementing data checksums. Individual tests construct `ContainerHealthStatus` and query boolean predicates and deltas. Parameterized tests mutate one replica's datanode operational state to decommissioning/decommissioned/maintenance states and recompute status.

State and persistence behavior: There is no SQL or filesystem persistence. Runtime state is the mocked container metadata, a set of replica value objects, their datanode persisted operational state, and mocked placement validation. Some tests mutate the replica set in place by removing a replica, changing datanode state, and re-adding it.

Dependencies and integration points: This class protects the health semantics consumed by Recon fsck and `ReconReplicationManager`. It integrates SCM replication config, placement validation, node operational state semantics, and checksum comparison while using a mocked `ReconContainerMetadataManager`.

Risks: The replica mutation loops modify a set while iterating but break immediately after remove/add; this works here but is a fragile pattern. Placement is mocked, so real topology placement behavior is not covered. EC replication behavior is not exercised. Decommission versus maintenance semantics are intentionally precise and can break when SCM policy changes.

Test signals: Healthy status has `replicaDelta=0`, replica count three, and no missing/under/over/mis flags. Missing status has delta three and `isMissing=true`. One replica yields under-replicated delta two; four replicas yields over-replicated delta minus one. Extra `UNHEALTHY` replica does not make a properly replicated container unhealthy. Mismatched checksums set `areChecksumsMismatched=true`. Placement status requiring two racks makes `isMisReplicated=true` with delta one. Out-of-service node states clear over-replication and distinguish decommission under-replication from maintenance sufficient replication.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/fsck/TestContainerHealthStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/fsck/TestContainerHealthTask.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/fsck/TestContainerHealthTask.java

Purpose: This unit test verifies `ContainerHealthTask` execution wiring. It ensures the task obtains `ReconReplicationManager` from `ReconStorageContainerManagerFacade` and calls `processAll`, and that a failure from `processAll` is propagated rather than swallowed.

Important APIs/types/functions: It uses `ContainerHealthTask.runTask`, `ReconStorageContainerManagerFacade.getReplicationManager`, `ReconReplicationManager.processAll`, `ReconTaskConfig.setMissingContainerTaskInterval`, `ReconTaskStatusUpdaterManager.getTaskStatusUpdater`, and a mocked `ReconTaskStatusUpdater`.

Control flow: Each test mocks the Recon SCM facade and replication manager, returns the manager from `getReplicationManager`, constructs `ContainerHealthTask` with a two-second task interval and mocked task status updater manager, then calls `runTask`. The failure test stubs `processAll` to throw a `RuntimeException` and asserts the same message is seen by the caller.

State and persistence behavior: There is no persistence. Runtime state is mocked task configuration, updater lookup, and the replication manager invocation.

Dependencies and integration points: This is a scheduling/wiring guard for Recon's container health background task. It connects the task framework to the local Recon replication manager and task status updater infrastructure.

Risks: The test does not inspect task status updater side effects such as run timestamps or failure state, only the call to `processAll`. It also does not start a scheduler loop; `runTask` is invoked directly.

Test signals: `processAll` is invoked exactly once on success; when `processAll` throws `RuntimeException("processAll failed")`, `runTask` throws and preserves the message.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/fsck/TestContainerHealthTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/fsck/TestReconReplicationManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/fsck/TestReconReplicationManager.java

Purpose: This SQL-backed smoke and mapping suite verifies `ReconReplicationManager` construction, `processAll` execution, database writes for unhealthy container states, composite SCM state mapping to Recon base states, unsupported state skipping, idempotent no-container runs, and schema manager/DAO integration.

Important APIs/types/functions: The test extends `AbstractReconSqlDBTest` and uses `ReconReplicationManager`, `ReconReplicationManager.InitContext`, `ContainerHealthSchemaManager`, `UnhealthyContainersDao`, `ContainerSchemaDefinition.UnHealthyContainerStates`, `ContainerManager`, `ContainerInfo`, `ContainerReplica`, `ContainerHealthState`, `ReplicationManagerReport`, `ReplicationQueue`, `ContainerReplicaOp`, `SCMContext`, `NodeManager`, `PlacementPolicy`, `EventQueue`, and jOOQ-generated unhealthy-container POJOs/DAOs.

Control flow: `setUp` initializes a real Recon SQL DB, creates `ContainerHealthSchemaManager`, mocks SCM dependencies, configures the SCM context as leader and not in safe mode, and constructs a `ReconReplicationManager`. Tests set `containerManager.getContainers`, `getContainer`, and `getContainerReplicas`, then often replace `reconRM` with an anonymous subclass whose `processContainer` injects deterministic `ContainerHealthState` values into the report and container. After `processAll`, tests query the schema manager or DAO.

State and persistence behavior: Persistent state is the test Derby Recon SQL database created by `AbstractReconSqlDBTest`. `processAll` inserts unhealthy container rows keyed by container ID and state. The tests verify `EMPTY_MISSING`, `NEGATIVE_SIZE`, primary state rows, `REPLICA_MISMATCH`, and composite state expansion. A direct DAO insertion test confirms old records for containers not being processed persist across `processAll`.

Dependencies and integration points: This suite integrates Recon's local replication manager with SCM-style container iteration, health reports, SQL schema/DAO bindings, and `ContainerHealthSchemaManager` batch operations. It deliberately avoids RPC to SCM by mocking all SCM runtime collaborators and using a local manager.

Risks: Many tests override `processContainer`, so they validate database/report mapping rather than the full SCM health algorithm. Replica sets are mocks with only checksum behavior for mismatch detection. The no-container and DB smoke tests verify non-throwing behavior but not detailed cleanup. Unsupported state behavior depends on the allowed Recon enum set.

Test signals: Rows appear under `EMPTY_MISSING` for zero-key missing containers and `NEGATIVE_SIZE` for negative used bytes; one row each for `MISSING`, `UNDER_REPLICATED`, `OVER_REPLICATED`, `MIS_REPLICATED`, and `REPLICA_MISMATCH`; composite states map to counts of two missing, three under-replicated, and two over-replicated without empty-missing leakage; unsupported `UNHEALTHY` creates no rows; manager construction is non-null; repeated empty `processAll` leaves DAO count zero; directly inserted stale row survives; and schema manager batch delete/insert with empty lists throws no exception.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/fsck/TestReconReplicationManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/heatmap/HeatMapProviderDataResource.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/heatmap/HeatMapProviderDataResource.java

Purpose: This resource DTO encapsulates the `buckets` array from Solr/Ranger audit facet JSON for heatmap tests. It maps JSON property `buckets` to an array of `EntityMetaData` objects and protects the internal array with defensive copies.

Important APIs/types/functions: The class uses Jackson `@JsonProperty("buckets")`, `EntityMetaData[]`, `getMetaDataList`, `setMetaDataList`, and `Arrays.copyOfRange`.

Control flow: Jackson deserializes a `resources` JSON node into this type by calling the setter. Consumers call `getMetaDataList`, which returns a copied array when metadata exists or `null` otherwise. The setter copies the entire incoming array into the private field.

State and persistence behavior: The only state is the private `metaDataList` array. There is no persistence. The defensive-copy behavior prevents callers from mutating internal state via the returned array reference, though individual `EntityMetaData` objects remain shared.

Dependencies and integration points: It is used by `TestHeatMapInfo` to transform Solr facet responses into `List<EntityMetaData>` inputs for `HeatMapUtil.generateHeatMap`. It couples the test JSON shape to the Recon API type used by heatmap generation.

Risks: `setMetaDataList` does not handle null input and would throw `NullPointerException` if Jackson supplied null. Defensive copy is shallow, so metadata objects themselves are mutable if the type exposes mutators. The class lives under test sources but models an external JSON shape that must remain aligned with audit provider responses.

Test signals: No direct tests in this file. Indirect signals come from `TestHeatMapInfo`, where `JsonTestUtils.treeToValue` populates the DTO from `resources.buckets` and heatmap generation uses the returned metadata list.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/heatmap/HeatMapProviderDataResource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/heatmap/TestHeatMapInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/heatmap/TestHeatMapInfo.java

Purpose: This suite validates `HeatMapUtil.generateHeatMap` against representative Solr/Ranger audit facet JSON for key, volume, and bucket resources. It verifies that flat resource strings are converted into hierarchical `EntityReadAccessHeatMapResponse` trees with expected child counts, aggregate sizes, min/max access counts, paths, labels, and normalized colors.

Important APIs/types/functions: The tests use `ReconTestInjector`, `getTestReconOmMetadataManager`, `initializeNewOmMetadataManager`, `ReconOMMetadataManager`, `HeatMapUtil.generateHeatMap`, `HeatMapProviderDataResource`, `EntityMetaData`, `EntityReadAccessHeatMapResponse`, `JsonUtils.readTree`, `JsonTestUtils.treeToValue`, `OzoneStorageContainerManager`, `ReconStorageContainerManagerFacade`, and mocked OM/SCM service providers.

Control flow: `initializeInjector` builds a Recon test injector rooted at a temp directory with SQL DB, OM metadata manager, container DB, and SCM facade binding, then obtains `HeatMapUtil`. It also initializes a large `auditRespStr` containing key-resource facet buckets. `setUp` guards this initialization with an instance boolean. Each test parses a JSON string, navigates to `facets.resources`, deserializes it into `HeatMapProviderDataResource`, converts its metadata array to a list, calls `generateHeatMap`, and asserts the response tree.

State and persistence behavior: Persistent test state includes temporary OM DB directories, Recon SQL DB, and container DB created by `ReconTestInjector`, although the heatmap assertions primarily consume embedded JSON. Runtime state is the parsed metadata list and generated tree. The response tree carries aggregate `size`, `minAccessCount`, `maxAccessCount`, `label`, `path`, `children`, leaf `accessCount`, and normalized `color`.

Dependencies and integration points: This is the main integration test for heatmap generation from external audit facets into Recon API response types. It exercises Jackson JSON mapping, Recon dependency injection, OM metadata setup, SCM facade binding for datanode mapping availability, and hierarchical path construction for Ozone volume/bucket/key resources.

Risks: The key-resource JSON is very large and embedded inline, making the test brittle and hard to update. Assertions depend on exact ordering and color normalization values such as `0.442` and `0.058`. The `isSetupDone` flag is an instance field under JUnit's default per-method lifecycle, so it does not actually share setup across test instances unless lifecycle is changed. The tests parse static fixture JSON rather than calling a live audit provider.

Test signals: Key-resource heatmap has root label `root`, 12 children, size 25600, min access 2924, max access 155074, and selected child colors 0.0, 0.442, and 0.058. Volume-resource heatmap has two children, size 512, min 8590, max 19263, first child color 1.0, and root label `root`. Bucket-resource heatmap has two top-level volume children, first child color 0.0, and a nested path `/testnewvol2/fsobuck11`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/heatmap/TestHeatMapInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/heatmap/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/heatmap/package-info.java

Purpose: This package descriptor documents that `org.apache.hadoop.ozone.recon.heatmap` under test sources contains heatmap feature related test classes.

Important APIs/types/functions: It declares the package `org.apache.hadoop.ozone.recon.heatmap` and contains only a Javadoc package comment.

Control flow: There is no executable control flow.

State and persistence behavior: There is no state or persistence.

Dependencies and integration points: The descriptor groups test classes such as `TestHeatMapInfo` and `HeatMapProviderDataResource` in the Recon heatmap test namespace and can be picked up by Javadoc tooling.

Risks: No behavioral risk. The only maintenance risk is that the package comment may become stale if non-test helper classes or broader responsibilities are added to the package.

Test signals: None; this file is documentation-only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/heatmap/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/metrics/TestOzoneManagerSyncMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/metrics/TestOzoneManagerSyncMetrics.java

Purpose: This test verifies that `OzoneManagerSyncMetrics` maintains independent counters for snapshot requests, snapshot failures, delta failures, delta update totals, non-zero delta request counts, average delta updates, and sequence number lag.

Important APIs/types/functions: It uses `OzoneManagerSyncMetrics.create`, `unRegister`, `incrNumSnapshotRequests`, `incrNumSnapshotRequestsFailed`, `incrNumDeltaRequestsFailed`, `incrNumUpdatesInDeltaTotal`, `setSequenceNumberLag`, and the corresponding getters.

Control flow: The test creates a metrics instance, mutates several counters/gauges, asserts exact getter values, and unregisters in a `finally` block to avoid metrics system leakage.

State and persistence behavior: State is in-memory metrics counters and gauges registered with Hadoop metrics. There is no persistence. Cleanup through `unRegister` is important because metrics names are global-ish within the test JVM.

Dependencies and integration points: These metrics are consumed by Recon OM metadata sync monitoring. The test protects the behavior that delta failure increments its own counter and that adding seven updates creates one non-zero delta request with average seven.

Risks: It tests getters directly rather than emitted metrics records. It does not cover zero-update deltas or multiple increments. Metrics registration collisions can occur if `unRegister` is omitted, which the test avoids.

Test signals: Snapshot requests equals one, snapshot failures equals one, delta failures equals one, total delta updates equals seven, non-zero delta requests equals one, average updates per delta request equals `7.0f`, and sequence number lag equals eleven.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/metrics/TestOzoneManagerSyncMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/metrics/TestReconScmContainerSyncMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/metrics/TestReconScmContainerSyncMetrics.java

Purpose: This test verifies that `ReconScmContainerSyncMetrics` emits gauges only for container lifecycle states reconciled by the SCM container sync path: `OPEN`, `QUASI_CLOSED`, `CLOSED`, and `DELETED`. It also checks global sync status and duration gauges.

Important APIs/types/functions: The suite uses `ReconScmContainerSyncMetrics.create`, `unRegister`, `setContainerSyncDurationMs`, `setContainerCountDrift`, `setScmContainerSyncStatus`, `setScmContainerSyncDurationMs`, `MetricsAsserts.getMetrics`, `getIntGauge`, `getLongGauge`, `MetricsRecordBuilder`, and lifecycle constants `OPEN`, `QUASI_CLOSED`, `CLOSED`, `DELETED`, `CLOSING`, and `DELETING`.

Control flow: Setup registers a metrics instance and teardown unregisters it. The test sets durations and drifts for reconciled states and also sets values for non-reconciled `CLOSING`/`DELETING`. It obtains a metrics record builder and asserts present gauges for reconciled states while verifying the builder never received gauges for non-reconciled states.

State and persistence behavior: State is in-memory metrics values. There is no persistence. Unregistration avoids cross-test metrics conflicts.

Dependencies and integration points: These metrics surface Recon SCM container sync status and per-state drift/duration to Hadoop metrics consumers. The test locks down the public metric names such as `openContainerSyncDurationMs`, `quasiClosedContainerCountDrift`, and `scmContainerSyncStatus`.

Risks: The negative `verify(builder, never()).addGauge(...)` checks depend on metric builder mock behavior from `MetricsAsserts`. If new lifecycle states become reconciled, this test must change intentionally. It does not test metric reset behavior across sync cycles.

Test signals: Status gauge equals `SCM_CONTAINER_SYNC_STATUS_SUCCESS`; total sync duration equals 500; open/quasi-closed/closed/deleted durations equal 10/20/30/40; corresponding drift values equal 2/0/-3/4; and no gauges are emitted for closing/deleting duration or drift despite setters being called.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/metrics/TestReconScmContainerSyncMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/package-info.java

Purpose: This package descriptor documents the `org.apache.hadoop.ozone.recon` test package as containing Recon server tests.

Important APIs/types/functions: It contains only package-level Javadoc and the package declaration.

Control flow: There is no executable control flow.

State and persistence behavior: There is no state or persistence.

Dependencies and integration points: Javadoc/package tooling can use this descriptor for the root Recon test package. It provides a documentation anchor for tests and helpers under the Recon server namespace.

Risks: No runtime risk. The documentation is broad and may become underspecified as the package accumulates heterogeneous test utilities and suites.

Test signals: None; this file is documentation-only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/AbstractReconSqlDBTest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/AbstractReconSqlDBTest.java

Purpose: This base test class creates a fully initialized Recon SQL database for tests and exposes helper APIs for DAOs, schema definitions, jOOQ configuration, DSL context, connections, and Guice injector access. It standardizes Derby-backed schema setup for Recon persistence tests.

Important APIs/types/functions: Key methods include `createReconSchemaForTest`, `init`, `getReconSqlDBModules`, `createSchema`, `getInjector`, `getConnection`, `getDataSource`, `getDslContext`, `getConfiguration`, `getDao`, `getSchemaDefinition`, and nested `DerbyDataSourceConfigurationProvider`. It uses Guice modules `JooqPersistenceModule`, `ReconSchemaGenerationModule`, `ReconDaoBindingModule`, `ReconSchemaManager`, jOOQ `DSLContext`, and `DataSourceConfiguration`.

Control flow: Before each test, `createReconSchemaForTest` receives a JUnit temp directory, initializes a Derby datasource provider under `Config/derby_recon.db`, creates a Guice injector from Recon SQL modules, constructs a DSL context from the injected `DataSource`, and calls `ReconSchemaManager.createReconSchema`. Test subclasses then retrieve DAOs/schema definitions from the injector.

State and persistence behavior: Persistent state is an embedded Derby database under the per-test temp directory. The provider configures auto-commit, two max active connections, connection timeout, max age/idle age, and `SELECT 1` validation. `init` deletes and recreates the `Config` directory to isolate tests.

Dependencies and integration points: This class is the backbone for Recon SQL persistence tests, including schema-definition tests and `TestReconReplicationManager`. It integrates Spring file cleanup, Guice injection, jOOQ, generated DAOs, schema generation, and Derby datasource configuration.

Risks: `init` calls `fail()` without including the caught exception, which can obscure setup diagnostics. Connections returned by `getConnection` are not automatically closed by this base class. Derby and SQLite dialect differences require separate tests, but most subclasses inherit Derby only. The temp `Config` directory is deleted recursively, so callers must pass isolated temp paths.

Test signals: Subclasses rely on non-null injector/configuration/DSL/connection, successful schema creation, generated DAO availability, and working CRUD against the initialized schema.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/AbstractReconSqlDBTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/TestReconInternalSchemaDefinition.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/TestReconInternalSchemaDefinition.java

Purpose: This test validates the internal Recon task-status schema and generated DAO CRUD behavior for `RECON_TASK_STATUS`. It ensures the schema has the expected columns/types and that task status records can be created, read, updated, and deleted.

Important APIs/types/functions: The class extends `AbstractReconSqlDBTest` and uses `RECON_TASK_STATUS_TABLE_NAME`, JDBC `Connection`, `DatabaseMetaData`, `ResultSet`, SQL `Types`, `ReconTaskStatusDao`, and `ReconTaskStatus` POJO.

Control flow: `testSchemaCreated` reads database metadata for the task status table columns, builds actual `(name,type)` pairs, and compares them to the expected ordered list. `testReconTaskStatusCRUDOperations` verifies table presence, inserts two records, reads one by id, updates its sequence number, deletes the other, and verifies deletion.

State and persistence behavior: State is persisted in the per-test Derby Recon SQL DB created by the base class. The table stores task name, last updated timestamp, last updated sequence number, last task run status, and current-running flag.

Dependencies and integration points: This schema supports Recon background task bookkeeping and task status updater behavior. The test integrates generated jOOQ DAO classes with the schema produced by `ReconSchemaManager`.

Risks: Column order is asserted exactly, which is useful for compatibility but can be brittle if metadata ordering differs by DB dialect. The CRUD test leaves one updated record in the per-test DB, relying on temp DB isolation. It does not assert default values for status/running fields when omitted.

Test signals: Exactly five columns with expected SQL types; table metadata exists; inserted `HelloWorldTask` has timestamp and sequence 100; update changes sequence to 150; deleting `GoodbyeWorldTask` makes `findById` return null.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/TestReconInternalSchemaDefinition.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/TestReconWithDifferentSqlDBs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/TestReconWithDifferentSqlDBs.java

Purpose: This parameterized suite verifies that Recon schema setup and generated DAO bindings work with both Derby and SQLite datasource configurations. It is a cross-dialect smoke test for schema generation, Guice bindings, jOOQ configuration, DAO CRUD, and DSL operations.

Important APIs/types/functions: The test uses `AbstractReconSqlDBTest`, `DerbyDataSourceConfigurationProvider`, nested `SqliteDataSourceConfigurationProvider`, `DataSourceConfiguration`, `RECON_DAO_LIST`, `ReconTaskStatusDao`, `ReconTaskStatus`, jOOQ generated table `RECON_TASK_STATUS`, `SQLDialect.SQLITE`, Derby/SQLite driver constants, and JUnit `@TempDir` plus `@MethodSource`.

Control flow: `parametersSource` creates one Derby temp directory and one SQLite temp directory. `testSchemaSetup` constructs an `AbstractReconSqlDBTest` with the provider, manually invokes `createReconSchemaForTest`, asserts core objects and every DAO binding are non-null, inserts one task status record through the DAO, deletes rows through jOOQ DSL, and verifies the DAO sees zero records afterward.

State and persistence behavior: Persistent state is either embedded Derby at `derby_recon.db` or SQLite at `recon_sqlite.db` under temp directories. Both providers use auto-commit, two active connections, timeout/age settings, and `SELECT 1` validation.

Dependencies and integration points: This test guards Recon's SQL abstraction across supported local databases. It integrates datasource providers, schema generation, Guice DAO binding list, generated DAOs, and direct jOOQ DSL operations.

Risks: `@TempDir` is static, which can be sensitive to JUnit configuration. The test covers one DAO/table deeply and only non-null construction for the rest. It does not compare metadata column types across dialects. SQLite and Derby temp DBs share the same parent temp path but use distinct child directories.

Test signals: Injector, jOOQ configuration, DSL context, connection, and every DAO in `RECON_DAO_LIST` are non-null for both providers; inserting `ReconTaskStatus("TestTask", 1L, 2L, 1, 0)` yields one row; deleting through `RECON_TASK_STATUS` removes one row; DAO `findAll` returns zero after delete.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/TestReconWithDifferentSqlDBs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/TestSchemaVersionTableDefinition.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/TestSchemaVersionTableDefinition.java

Purpose: This suite verifies the Recon schema-version table definition and upgrade initialization semantics. It tests table columns, basic CRUD, fresh-install behavior, pre-upgrade cluster behavior where other tables exist but schema version does not, and upgraded-cluster behavior where an existing metadata layout version must be preserved.

Important APIs/types/functions: It extends `AbstractReconSqlDBTest` and uses `SCHEMA_VERSION_TABLE_NAME`, `SchemaVersionTableDefinition`, `ReconSchemaVersionTableManager`, `ReconLayoutVersionManager`, `ReconContext`, `GLOBAL_STATS_TABLE_NAME`, `UNHEALTHY_CONTAINERS_TABLE_NAME`, `SqlDbUtils.TABLE_EXISTS_CHECK`, `listAllTables`, jOOQ `DSLContext`, `SQLDataType`, `Timestamp`, JDBC metadata, and mocked `DataSource`.

Control flow: `testSchemaVersionTableCreation` checks metadata for `version_number` and `applied_on`. `testSchemaVersionCRUDOperations` drops all tables, creates only schema version table, inserts version 1, updates to 2, and deletes. Fresh install drops all tables, initializes schema with latest SLV 3, and expects layout manager current MLV 3. Pre-upgrade drops only schema version and ensures other tables exist, initializes, then expects current MLV -1. Upgraded-cluster creates other tables plus schema version, inserts MLV 2, initializes with latest SLV 3, and expects MLV remains 2.

State and persistence behavior: Persistent state is the per-test Derby DB. Tests intentionally drop and create tables to simulate installation and upgrade scenarios. Schema version rows store `version_number` and `applied_on`; the layout version manager reads current MLV from this table.

Dependencies and integration points: This is a key upgrade safety test connecting schema initialization with Recon's layout-version manager. It integrates table-existence checks, all-table listing, manual jOOQ DDL, schema-version manager, and upgrade-state inference from existing database tables.

Risks: Helper-created mock tables only have `id` and `data` columns, so they simulate presence rather than real schema. `assertEquals(true, tableExists)` is less idiomatic but clear. Dropping all tables inside a test relies on isolated DBs from the base class. The latest SLV value 3 is hard-coded in tests and must track production layout changes.

Test signals: Schema version table has exactly two columns with integer and timestamp types; CRUD changes version 1 to 2 and then leaves zero rows; fresh install creates table and sets MLV to 3; pre-upgraded cluster creates table and reports MLV -1; upgraded cluster preserves stored MLV 2 despite latest SLV 3.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/TestSchemaVersionTableDefinition.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/TestSqlSchemaSetup.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/TestSqlSchemaSetup.java

Purpose: This parameterized smoke test validates basic Recon SQL schema setup using the default Derby base class and confirms task status rows can be inserted with multiple `lastTaskRunStatus` values.

Important APIs/types/functions: It extends `AbstractReconSqlDBTest` and uses `RECON_DAO_LIST`, `ReconTaskStatusDao`, `ReconTaskStatus`, JUnit `@ParameterizedTest`, and `@ValueSource(ints = {0, 1, -1})`.

Control flow: For each status value, the inherited `@BeforeEach` creates the Recon schema. The test asserts injector, jOOQ configuration, DSL context, and connection are non-null, verifies every DAO binding in `RECON_DAO_LIST`, inserts one `ReconTaskStatus` with the parameterized status, and asserts one row exists.

State and persistence behavior: Persistent state is the per-test Derby DB from `AbstractReconSqlDBTest`. Each parameter invocation gets its own setup and inserts one task status row with status 0, 1, or -1.

Dependencies and integration points: This is a broad wiring smoke test for Recon SQL schema generation and DAO binding. It specifically guards task status support for success, failure, and sentinel/unknown status values.

Risks: It verifies availability of all DAOs but only exercises one DAO. It does not validate table definitions or clean up rows within an invocation, relying on isolated temp DB setup. Connection lifecycle is not explicitly closed in the test.

Test signals: Non-null injector/configuration/DSL/connection, non-null all DAO bindings, and exactly one task status row after insertion for each of `lastTaskRunStatus` 0, 1, and -1.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/TestSqlSchemaSetup.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/TestStatsSchemaDefinition.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/TestStatsSchemaDefinition.java

Purpose: This test validates the global stats schema and generated DAO CRUD behavior. It ensures `GLOBAL_STATS` has the expected columns and that `GlobalStatsDao` can insert, read, update, and delete statistic records with timestamps.

Important APIs/types/functions: The class extends `AbstractReconSqlDBTest` and uses `GLOBAL_STATS_TABLE_NAME`, JDBC `Connection`, `DatabaseMetaData`, `ResultSet`, SQL `Types`, `GlobalStatsDao`, `GlobalStats`, and `Timestamp`.

Control flow: `testIfStatsSchemaCreated` fetches metadata columns for the global stats table and compares ordered `(name,type)` pairs against `key`, `value`, and `last_updated_timestamp`. `testGlobalStatsCRUDOperations` verifies table presence, inserts two records, reads each by key, updates `key2` value and timestamp, then deletes `key1` and verifies it is gone.

State and persistence behavior: Persistent state is the per-test Derby Recon SQL DB. The global stats table stores stat key, long value, and last-updated timestamp. DAO operations mutate this table directly.

Dependencies and integration points: Global stats support Recon-wide counters and summaries. The test integrates `StatsSchemaDefinition` output from schema generation with jOOQ-generated `GlobalStatsDao` and POJO mappings.

Risks: Like other schema metadata tests, exact column ordering can be dialect-sensitive. Timestamp equality depends on Java/JDBC preserving millisecond precision for Derby in this setup. The test covers two records but not duplicate-key behavior or null constraints.

Test signals: Exactly three columns with expected SQL types; inserted `key1` has value 500 and exact timestamp; inserted `key2` has value 10 and timestamp plus one second; update changes `key2` to value 100 and later timestamp; deleting `key1` makes DAO lookup return null.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/TestStatsSchemaDefinition.java -->
