# subset-b-008122 Research

Grouped research for Recon chatbot, codec, fsck, heatmap, metrics, persistence, recovery, and SCM sync files. Each section preserves the source path and is delimited for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/agent/ToolExecutor.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/agent/ToolExecutor.java

Purpose: singleton executor for chatbot tool calls against Recon REST APIs. It normalizes endpoints, builds loopback HTTP URLs from `ozone.recon.http-address`, applies connect/read timeouts from chatbot config, and returns a structured `ToolExecutionOutcome`.

Important APIs/types/functions: `executeToolCallWithPolicy` is the public entry point; `executeListKeysWithPaging` implements bounded pagination for `/keys/listKeys`; `executeSingleCall` performs GET/POST via `HttpURLConnection`; `buildUrl` substitutes path placeholders and URL-encodes query values; `ToolExecutionOutcome` carries response body, record/page counts, truncation, cursor, and applied limits.

Control flow: non-`listKeys` requests make one HTTP call and estimate record count. `listKeys` requires non-root `startPrefix`, caps page size by requested `limit` and policy, loops on `lastKey`, aggregates `keys`, and annotates the merged JSON with truncation metadata.

State and persistence: no durable state; state is request-local. Configuration is captured at construction. Integration points are `ChatbotAgent`, `ChatbotUtils`, Recon REST resources, `OzoneConfiguration`, and `ReconConfigKeys`.

Risks: plain `HttpURLConnection` does not send SPNEGO credentials, so Kerberos-protected Recon APIs return 401 as documented in the source. Placeholder path values are not encoded when inserted into the path, unlike query parameters. Pagination only special-cases one endpoint suffix. Tests should cover URL construction, listKeys cursor termination/truncation, error stream handling, null parameter maps, and Kerberos/error status behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/agent/ToolExecutor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/agent/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/agent/package-info.java

Purpose: package-level Javadoc for Recon chatbot agent and tool execution classes. It documents that this package owns the agent-facing execution layer rather than REST endpoint or LLM-provider concerns.

Important APIs/types/functions: no runtime API; the only declaration is the `org.apache.hadoop.ozone.recon.chatbot.agent` package.

Control flow and state: none. Integration is documentation-level only, but it groups `ToolExecutor` and adjacent agent classes for Javadoc and package scanning.

Risks and test signals: compile/package-info validation is sufficient. Documentation should remain aligned with actual package responsibilities if future classes move agent planning, tool schema, or execution policy elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/agent/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/api/ChatbotEndpoint.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/api/ChatbotEndpoint.java

Purpose: JAX-RS singleton REST resource for `/chatbot`, exposing health, chat, and model-list APIs for the Recon chatbot.

Important APIs/types/functions: `health()` returns enabled and LLM availability flags; `chat(ChatRequest)` validates input, submits query processing to a bounded executor, and converts failures into HTTP responses; `getSupportedModels()` delegates to `LLMClient`; `shutdown()` tears down the executor; DTOs `ChatRequest` and `ChatResponse` are Jackson-friendly and ignore unknown fields.

Control flow: constructor reads pool and queue sizes from `ChatbotConfigKeys` and builds a fixed `ThreadPoolExecutor` backed by `ArrayBlockingQueue`. `chat` rejects disabled service and blank query, logs sanitized user/model/provider, submits `chatbotAgent.processQuery(query, model, provider)`, waits with configured request timeout, returns 200 on success, 503 on saturation/interruption, 504 on timeout, and 500 on execution failure.

State and persistence: no DB state; it owns an in-process executor. Dependencies are Guice/JAX-RS, `ChatbotAgent`, `LLMClient`, `OzoneConfiguration`, and chatbot config keys. Integration with Recon module wiring depends on the same enabled check used by controller installation.

Risks: `request` is dereferenced before null checking, so a null JSON body can throw. Blocking `Future#get` still occupies the request thread, though bounded by pool/queue. `Future.cancel(true)` relies on downstream interruption support. Tests should cover disabled mode, blank/null query, executor saturation, timeout, model errors, sanitized logging behavior, and lifecycle shutdown.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/api/ChatbotEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/api/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/api/package-info.java

Purpose: package-level Javadoc for REST API endpoints in the Recon chatbot module.

Important APIs/types/functions: no runtime types beyond declaring `org.apache.hadoop.ozone.recon.chatbot.api`; it documents ownership for resources such as `ChatbotEndpoint`.

Control flow, state, and persistence: none. Integration is with Javadoc/package discovery and source organization.

Risks and test signals: compile validation is enough. The package comment should be updated if non-REST support classes become the dominant contents.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/api/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/llm/LLMClient.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/llm/LLMClient.java

Purpose: provider-agnostic contract used by chatbot code to call LLM backends without depending on OpenAI, Gemini, Anthropic, or LangChain4j specifics.

Important APIs/types/functions: `chatCompletion(List<ChatMessage>, String, Map<String,Object>)`; `isAvailable()`; `getSupportedModels()`; DTO `ChatMessage`; DTO `LLMResponse` with content, model, token counts, metadata, and `getTotalTokens()`; checked `LLMException` with optional status code.

Control flow: this is an interface; implementations must normalize request and response behavior. The contract states API keys are resolved server-side via `CredentialHelper` and never provided per request.

State and persistence: no state. Dependencies are minimal Java collections plus documentation reference to credential helper. It integrates upward with `ChatbotAgent` and `ChatbotEndpoint`; `LangChain4jDispatcher` is the implementation in this subset.

Risks: nested DTO classes are immutable only for final fields but do not defensively copy metadata; callers can mutate passed metadata maps. Tests should assert implementation conformance: empty-message rejection, token accounting, metadata provider fields, supported model listing, and consistent exception wrapping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/llm/LLMClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/llm/LangChain4jDispatcher.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/llm/LangChain4jDispatcher.java

Purpose: `LLMClient` implementation that routes chatbot requests through LangChain4j models while hiding provider-specific builders from higher layers.

Important APIs/types/functions: constructor registers providers with configured secrets; `chatCompletion` resolves provider/model, translates messages, executes a LangChain4j `ChatLanguageModel`, and returns `LLMResponse`; `getSupportedModels` returns configured models for available providers; `buildOpenAiModel`, `buildGeminiModel`, and `buildAnthropicModel` create provider clients; `resolveKey`, `resolveProvider`, `translateMessages`, and `parseModelList` handle routing details.

Control flow: provider is chosen from `_provider`, `provider:model`, or model-list reverse lookup. `buildModel` caches `(provider,model)` instances in a `ConcurrentHashMap`; failures evict the cache key. Gemini is intentionally routed through the OpenAI-compatible endpoint to honor timeouts.

State and persistence: no durable state; in-memory supported model map and model cache. Dependencies include LangChain4j OpenAI/Anthropic models, `CredentialHelper`, and chatbot configuration keys. It integrates with `/chatbot/models`, endpoint health, and agent calls.

Risks: provider hints are trusted before checking that the provider is configured, so an unknown/unconfigured provider errors later. Concurrent first-use can build duplicate model instances. `parameters` is used only for `_provider`, not general generation controls. Tests should cover provider resolution precedence, missing secrets, model-cache eviction on failure, message role fallback, token usage null handling, configured base URLs, and supported-model list behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/llm/LangChain4jDispatcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/llm/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/llm/package-info.java

Purpose: package-level Javadoc for Recon chatbot LLM abstraction and dispatch classes.

Important APIs/types/functions: no runtime API; declares `org.apache.hadoop.ozone.recon.chatbot.llm`.

Control flow and state: none. Integration is documentation-level grouping for `LLMClient` and `LangChain4jDispatcher`.

Risks and test signals: compile/package-info validation is sufficient. Keep the comment accurate if provider-specific code moves into subpackages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/llm/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/package-info.java

Purpose: package-level Javadoc for Guice wiring and shared Recon chatbot types.

Important APIs/types/functions: no runtime members; declares `org.apache.hadoop.ozone.recon.chatbot`.

Control flow and state: none. Integration is source organization for chatbot config, module wiring, agent, endpoint, LLM, and security packages.

Risks and test signals: only compilation/Javadoc checks apply. The summary should be adjusted if the root package stops containing shared wiring or configuration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/security/CredentialHelper.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/security/CredentialHelper.java

Purpose: central singleton for resolving chatbot secrets from Hadoop credential providers, with plaintext configuration fallback for compatibility.

Important APIs/types/functions: `getSecret(String configKey)` reads `configuration.getPassword`, catches `IOException`, then falls back to `configuration.get`; `hasSecret` checks non-empty resolved values.

Control flow: JCEKS/Hadoop credential provider is attempted first. Empty or missing credential values fall through to plaintext config. Failures are warned and do not fail startup.

State and persistence: holds only injected `OzoneConfiguration`. It integrates with `LangChain4jDispatcher` provider registration and key resolution.

Risks: returned `String` copies secret material from `char[]`, making it harder to clear from memory. Fallback to plaintext can mask credential-provider misconfiguration. Logging includes config key names but not values. Tests should cover credential-provider success, provider IOException fallback, plaintext fallback, missing key empty result, and `hasSecret`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/security/CredentialHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/security/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/security/package-info.java

Purpose: package-level Javadoc for Recon chatbot security helpers.

Important APIs/types/functions: no runtime API; declares `org.apache.hadoop.ozone.recon.chatbot.security`.

Control flow and state: none. Integration is documentation-level grouping for classes such as `CredentialHelper`.

Risks and test signals: compile/Javadoc validation only. Update if the package expands beyond credential/secret helpers into authentication or authorization code.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/chatbot/security/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/codec/NSSummaryCodec.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/codec/NSSummaryCodec.java

Purpose: RocksDB `Codec<NSSummary>` for serializing and deserializing Recon namespace summary records.

Important APIs/types/functions: singleton `get()`; `toPersistedFormatImpl`; `fromPersistedFormatImpl`; `copyObject`; `readParentIdAndReplicatedSize`. It uses primitive codecs for int, short, long, and string fields.

Control flow: serialization writes file counts, size, fixed file-size-bucket length and contents, child directory IDs, directory-name bytes, parent ID, and replicated size. Deserialization reads in that order, then tolerates older persisted records by checking remaining bytes for parent ID and replicated size.

State and persistence: durable binary format for `NSSummary`; schema evolution is handled by optional trailing longs. Dependencies include `ReconConstants.NUM_OF_FILE_SIZE_BINS` and `NSSummary`.

Risks: uses Java `assert` for bucket-length and string-length checks, so production may not enforce corruption checks. `copyObject` reuses arrays/sets rather than deep-copying mutable collections. Tests should verify round-trip, backward compatibility with missing trailing fields, empty directory name, bucket count mismatches, and copy isolation expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/codec/NSSummaryCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/codec/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/codec/package-info.java

Purpose: package-level Javadoc for Recon DB table codecs.

Important APIs/types/functions: no runtime API; declares `org.apache.hadoop.ozone.recon.codec`.

Control flow and state: none. Integration is documentation-level grouping for codec classes used by Recon DB stores.

Risks and test signals: compile/Javadoc validation only. Keep aligned with actual codec contents when new persisted formats are added.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/codec/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/ContainerHealthStatus.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/ContainerHealthStatus.java

Purpose: value object that computes health, replication, placement, checksum, and key-count signals for a container and its replicas.

Important APIs/types/functions: constructor derives healthy replica sets, placement status, replica delta, key count, and `ContainerReplicaCount`; getters expose container ID/info, replication factor/count, missing/empty/deleted/over/under/mis-replicated checks, placement deltas/reasons, and checksum mismatch detection.

Control flow: unhealthy replicas are excluded from healthy sets; decommissioned/maintenance nodes are excluded from available replicas; placement is validated with healthy replicas. Ratis and EC containers instantiate different `ContainerReplicaCount` implementations using `ReplicationManagerConfiguration`.

State and persistence: no writes, but reads key count through `ReconContainerMetadataManager`. It integrates with placement policy, SCM container model, replica-count classes, and Recon metadata.

Risks: `getContainerKeyCount` wraps `IOException` as unchecked `RuntimeException`; `areChecksumsMismatched` compares `ContainerReplica::getChecksums`, while `ReconReplicationManager` uses data checksum. Tests should cover EC/Ratis differences, maintenance/decommission filtering, missing/empty logic, placement policy results, key-count failure, and checksum mismatch semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/ContainerHealthStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/ContainerHealthTask.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/ContainerHealthTask.java

Purpose: scheduled Recon SCM task that runs local container health analysis using Recon's `ReconReplicationManager`.

Important APIs/types/functions: `run()` loops with task lifecycle controls; `runTask()` casts SCM replication manager to `ReconReplicationManager` and invokes `processAll`; `stop()` unregisters metrics.

Control flow: each cycle records start time, calls `initializeAndRunTask`, sleeps for at least 60 seconds and otherwise `interval - elapsed`, exits on interruption, and logs other exceptions. `runTask` increments success/failure metrics and records runtime in a finally block.

State and persistence: durable DB writes are delegated to `ReconReplicationManager`. Task-local state includes interval and `ContainerHealthTaskMetrics`. Dependencies are `ReconScmTask`, `ReconStorageContainerManagerFacade`, `ReconTaskConfig`, and metrics.

Risks: hard cast assumes facade returns the Recon-specific replication manager. Repeated failures log but do not back off beyond normal loop sleep. Tests should cover success/failure metrics, sleep interval calculation, interruption, stop unregistering metrics, and integration with a mocked Recon replication manager.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/ContainerHealthTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/MissingContainerInfo.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/MissingContainerInfo.java

Purpose: API payload DTO describing one missing container for missing-container responses.

Important APIs/types/functions: constructor and getters for `containerId`, `missingSinceTimestamp`, `lastKnownPipelineId`, `lastKnownDatanodes`, and `keysInContainer`.

Control flow: none beyond object construction. State is immutable by absence of setters, but contained lists are not defensively copied.

State and persistence: no persistence; it represents data assembled from health tables, pipeline/datanode history, and key metadata. Dependency on `KeyMetadata` connects missing-container output to Recon namespace metadata.

Risks: external mutation of list references can alter response contents. Tests should validate JSON serialization shape, empty key/datanode lists, and null pipeline/list handling expected by API clients.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/MissingContainerInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/NoOpsContainerReplicaPendingOps.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/NoOpsContainerReplicaPendingOps.java

Purpose: no-op `ContainerReplicaPendingOps` implementation used by Recon's local replication manager so health checks can run without issuing or tracking replication commands.

Important APIs/types/functions: overrides `getPendingOps`, schedule add/delete, complete add/delete, and `getPendingOpCount`.

Control flow: all query methods return empty/zero/false and all scheduling methods do nothing. Constructor delegates clock/config to the superclass.

State and persistence: no stored operations, no DB writes. It integrates with `ReconReplicationManager` superclass construction and SCM replication health code.

Risks: correctness depends on SCM health-state determination continuing to ignore pending operations for read-only analysis. If upstream SCM changes health logic to depend on pending operations, Recon could report different health states. Tests should compare health classifications with and without pending ops and verify no command scheduling side effects.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/NoOpsContainerReplicaPendingOps.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/ReconReplicationManager.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/ReconReplicationManager.java

Purpose: Recon-specific extension of SCM `ReplicationManager` that runs read-only health checks over all containers and persists unhealthy states into Recon SQL tables.

Important APIs/types/functions: `InitContext` builder carries parent constructor dependencies; constructor injects `NoOpsContainerReplicaPendingOps`; `start()` is a no-op; `processAll()` performs the scan; `storeHealthStatesToDatabase` maps container health to rows; helpers create `UnhealthyContainerRecord`s for missing, under/over/mis-replicated, negative size, and replica mismatch states.

Control flow: `processAll` builds `ReconReplicationManagerReport`, gets all containers, calls inherited `processContainer(..., readOnly=true)` with a `MonitoringReplicationQueue`, checks data checksum mismatch, then stores results in chunks of 50,000 containers. Persistence loads existing `inStateSince`, deletes old health rows for touched containers, inserts new rows atomically, and logs unmapped SCM states.

State and persistence: writes `UNHEALTHY_CONTAINERS` through `ContainerHealthSchemaManager`; relies on mutable `ContainerInfo.healthState` set by inherited SCM processing. It integrates with container manager, placement policies, SCM context, node manager, health schema, and `ContainerHealthTask`.

Risks: inherited SCM behavior is a moving dependency; unmapped health states are skipped with warnings; `applyExistingInStateSince` is called after an earlier existing lookup causing duplicate reads; actual replica count uses all replicas, not only healthy/available replicas. Tests should cover each health-state mapping, `REPLICA_MISMATCH`, negative size deduplication, empty missing, chunked persistence, preservation of `inStateSince`, no command enqueueing, and unmapped state logging.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/ReconReplicationManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/ReconReplicationManagerReport.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/ReconReplicationManagerReport.java

Purpose: Recon extension of SCM `ReplicationManagerReport` that tracks all replica-checksum mismatch containers separately from SCM health states.

Important APIs/types/functions: constructor disables base sample-list allocation with `super(0)`; `addReplicaMismatchContainer`; `getReplicaMismatchContainers` returns an unmodifiable list.

Control flow: regular SCM counters remain in the superclass; Recon-specific `REPLICA_MISMATCH` IDs are accumulated in a separate list and later persisted by `ReconReplicationManager`.

State and persistence: in-memory scan report only; persistence occurs elsewhere. Integration is with `ReconReplicationManager.processAll`.

Risks: the list can grow to all containers with mismatches; unlike base samples it is intentionally unbounded. Tests should verify counters still work, mismatch list immutability, and empty/default report behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/ReconReplicationManagerReport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/ReconSafeModeMgrTask.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/ReconSafeModeMgrTask.java

Purpose: startup task that waits for Recon to observe enough SCM/container state before exiting Recon safe mode.

Important APIs/types/functions: constructor captures managers, wait threshold, and datanode heartbeat interval; `start()` loops until safe mode exits or threshold is exceeded; `tryReconExitSafeMode()` compares known containers against containers reported by all datanodes.

Control flow: initial check runs immediately. While still in safe mode and within threshold, the synchronized `start` method waits for one heartbeat interval, refreshes nodes/containers, and retries. If all containers are represented by datanode reports, safe mode is disabled; otherwise threshold expiry forces exit with a warning.

State and persistence: no durable writes except `ReconSafeModeManager.setInSafeMode(false)`. Dependencies are `ContainerManager`, `ReconNodeManager`, `ReconSafeModeManager`, task config, and heartbeat config.

Risks: compares only container counts, not exact identity coverage beyond the set size built from datanodes; initial node/container lists can be stale until refreshed. `wait` requires the synchronized method, which is present. Tests should cover no nodes, no containers, complete coverage, forced timeout exit, node-not-found logging, and interruption.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/ReconSafeModeMgrTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/package-info.java

Purpose: package-level Javadoc for Recon fsck/health-check related classes, though the current text says persistence interfaces.

Important APIs/types/functions: no runtime API; declares `org.apache.hadoop.ozone.recon.fsck`.

Control flow and state: none. Integration is documentation/source organization for container health, safe mode, and replication manager classes.

Risks and test signals: compile/Javadoc validation only. The comment appears stale or copied from persistence package docs; documentation should be corrected to avoid misleading generated Javadocs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/heatmap/HeatMapService.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/heatmap/HeatMapService.java

Purpose: abstract service contract for retrieving entity read-access heatmap data.

Important APIs/types/functions: single abstract `retrieveData(String path, String entityType, String startDate)` returning `EntityReadAccessHeatMapResponse`.

Control flow and state: none in this class. Implementations decide provider lookup, validation, and response construction.

State and persistence: no persistence. Integration point for APIs that need heatmap data without depending on `HeatMapServiceImpl`.

Risks and test signals: broad `throws Exception` pushes error handling to callers. Tests belong on concrete implementations and should validate contract behavior for missing providers and invalid paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/heatmap/HeatMapService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/heatmap/HeatMapServiceImpl.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/heatmap/HeatMapServiceImpl.java

Purpose: concrete heatmap service that loads a configured provider and converts provider metadata into API heatmap responses.

Important APIs/types/functions: constructor builds `HeatMapUtil` and calls `initializeProvider`; `retrieveData` normalizes leading slash and delegates to utility; `doHeatMapHealthCheck` delegates to provider or returns a non-loaded message.

Control flow: provider class name comes from `OZONE_RECON_HEATMAP_PROVIDER_KEY`; utility reflectively loads it; provider is initialized with Ozone config, OM metadata manager, namespace summary manager, and Recon SCM. Failed load/init logs and leaves provider null.

State and persistence: in-memory provider reference and utility; no direct writes. Integrates with pluggable `IHeatMapProvider`, Recon OM metadata, namespace summaries, and SCM.

Risks: provider load failures are swallowed into null provider and normal retrieval returns an empty response. Reflective loading uses default construction. `validatePath` strips only one leading OM key prefix. Tests should cover configured/missing/bad provider, init failure, path normalization, health check fallback, and empty provider response.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/heatmap/HeatMapServiceImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/heatmap/HeatMapUtil.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/heatmap/HeatMapUtil.java

Purpose: utility that loads heatmap providers and transforms flat entity access metadata into the nested root/volume/bucket/path tree consumed by the UI.

Important APIs/types/functions: `retrieveDataAndGenerateHeatMap`; `generateHeatMap`; `loadHeatMapProvider`; helpers for entity size lookup, bucket/volume insertion, min/max access counts, average access counts, color ratio calculation, and reflective provider loading.

Control flow: provider returns `EntityMetaData` rows. `generateHeatMap` initializes root min count from the first row, splits each path on `/`, looks up entity size through `EntityHandler.getDuResponse`, inserts or updates volume/bucket/prefix nodes, then computes aggregate sizes, min/max ranges, average access counts, and leaf color ratios.

State and persistence: no writes; reads DU/namespace data via `ReconNamespaceSummaryManager`, `ReconOMMetadataManager`, and Recon SCM. Provider loading uses `Class.forName(...).newInstance()`.

Risks: `generateHeatMap` assumes non-empty input; caller currently guards this. `getEntitySize` returns fallback `256L` on unresolved data, which can hide lookup problems. Color ratio divides by entity max count and uses truncation via floor. Reflection API is deprecated and requires no-arg constructor. Tests should cover empty/null metadata at public utility level, duplicate volumes/buckets, volume-only and bucket-only paths, size lookup failures, min/max/color math, and invalid provider class/type.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/heatmap/HeatMapUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/heatmap/IHeatMapProvider.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/heatmap/IHeatMapProvider.java

Purpose: plugin contract for heatmap data providers, allowing Recon to fetch read-access metadata from external systems such as Solr or other indexes.

Important APIs/types/functions: `retrieveData(path, entityType, startDate)` returns flat `EntityMetaData` rows; `init` receives Ozone config, OM metadata, namespace summary manager, and Recon SCM; default `getSolrAddress`; default `doHeatMapHealthCheck`.

Control flow: implementations are reflectively constructed by `HeatMapUtil` and initialized once by `HeatMapServiceImpl`; retrieval is called per request.

State and persistence: interface has no state; implementations may keep external client state. Integration points are heatmap service, Recon metadata managers, SCM, and health endpoints.

Risks: broad `throws Exception` and no explicit lifecycle/close method. Default health check returns healthy even for providers that do not override it. Tests for implementations should cover initialization, external connectivity, path/entity filtering, date handling, and health-check accuracy.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/heatmap/IHeatMapProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/heatmap/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/heatmap/package-info.java

Purpose: package-level Javadoc for Recon heatmap classes.

Important APIs/types/functions: no runtime API; declares `org.apache.hadoop.ozone.recon.heatmap`.

Control flow and state: none. Integration is source organization for service, provider, and utility classes.

Risks and test signals: compile/Javadoc validation only. The package comment should remain aligned if provider implementations move in or out of this package.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/heatmap/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/ContainerHealthTaskMetrics.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/ContainerHealthTaskMetrics.java

Purpose: Hadoop Metrics2 source for `ContainerHealthTask` runtime, success, and failure counters.

Important APIs/types/functions: static `create`; `unRegister`; `addRunTime`; `incrSuccess`; `incrFailure` (present after the read continuation); annotated `MutableRate` and `MutableCounterLong` fields.

Control flow: `create` registers a new metrics source named after the class with `DefaultMetricsSystem`; task code updates counters/rates during each run; `unRegister` removes the source.

State and persistence: in-memory metrics only. Integration with `ContainerHealthTask` and Hadoop Metrics2/Ozone metrics context.

Risks: duplicate registration can fail or replace depending on Metrics2 behavior if multiple task instances are created. Tests should cover counter/rate updates and unregister lifecycle; task tests should assert success/failure paths increment expected metrics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/ContainerHealthTaskMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/Metric.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/Metric.java

Purpose: simple immutable-ish wrapper for a metric response from `MetricsServiceProvider`.

Important APIs/types/functions: constructor accepts metadata map and sorted values; `getMetadata`; `getValues`.

Control flow: constructor copies values into a `TreeMap` to enforce sorted numeric timestamp/value ordering.

State and persistence: no persistence; metadata map reference is retained, values map is internally copied. Integration is with Recon metrics API/service responses.

Risks: metadata is not defensively copied and values getter returns the mutable `TreeMap` as `SortedMap`, allowing caller mutation. Tests should cover ordering, empty values, metadata preservation, and mutability expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/Metric.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/OzoneManagerSyncMetrics.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/OzoneManagerSyncMetrics.java

Purpose: Metrics2 source for Recon synchronization with Ozone Manager metadata.

Important APIs/types/functions: static `create`; `unRegister`; increment methods for snapshot/delta request failures and totals; `incrNumUpdatesInDeltaTotal`; sequence-number lag setter/getter; test getters.

Control flow: delta update increments both total updates and non-zero delta request count, then recomputes average updates per non-zero request. Snapshot and failure counters are straightforward increments.

State and persistence: in-memory metrics; no durable writes. Integrates with OM sync tasks and Hadoop Metrics2.

Risks: average only accounts for non-zero delta requests by design; zero-update requests are not counted in denominator. Metrics fields are injected by Metrics2 annotations after registration. Tests should cover average calculation, sequence lag, failure counters, unregister, and zero-update semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/OzoneManagerSyncMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/ReconScmContainerSyncMetrics.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/ReconScmContainerSyncMetrics.java

Purpose: custom Metrics2 source for SCM container sync status, total duration, per-state sync duration, and per-state count drift.

Important APIs/types/functions: static `create`; `unRegister`; setters/getters for overall status/duration and state gauges; `getMetrics` snapshots gauges; status constants for in-progress/success/failure.

Control flow: constructor initializes gauges and metric names for OPEN, QUASI_CLOSED, CLOSED, and DELETED states. Metric names are generated from enum names via Guava `CaseFormat`. Unknown states passed to setters are ignored.

State and persistence: in-memory atomic gauges; no DB writes. Integrates with SCM container sync tasks and Metrics2 collector.

Risks: only selected lifecycle states are exported; other states silently return zero/ignore updates. Tests should cover metric-name generation, collector output, ignored states, concurrency through atomic values, and unregister lifecycle.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/ReconScmContainerSyncMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/ReconSyncMetrics.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/ReconSyncMetrics.java

Purpose: Metrics2 source for OM delta sync and full snapshot sync operations.

Important APIs/types/functions: static `create`; `unRegister`; update/increment methods for delta fetch duration/success/failures/data size, delta apply duration/failures, full DB request latency/fetch count, snapshot size/download success/failure; getters for tests.

Control flow: sync code calls counters/rates at relevant fetch, apply, and snapshot stages. Rates use `MutableRate`, counters use `MutableCounterLong`.

State and persistence: in-memory metrics only. Integrates with Recon OM sync code and Metrics2.

Risks: no success counter for delta apply, only failures and duration. Metrics fields rely on registration for initialization. Tests should validate all increments/rates, snapshot counters, and lifecycle unregister.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/ReconSyncMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/ReconTaskControllerMetrics.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/ReconTaskControllerMetrics.java

Purpose: Metrics2 source for Recon task controller queue behavior and system-wide reprocess outcomes.

Important APIs/types/functions: static `create`; `unRegister`; setters/incrementers for queue size, buffered/dropped/processed events, checkpoint/execution/stage DB failures, successful reprocesses, and submitted reprocess events; test getters.

Control flow: task controller updates gauges/counters as queue events and reprocess phases occur. Metrics are annotation-backed.

State and persistence: in-memory metrics; no DB writes. Integrates with Recon task controller and Metrics2.

Risks: event count semantics must match producer code because this class does no validation. Tests should verify increments by arbitrary counts, queue gauge update, failure category counters, and unregister lifecycle.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/ReconTaskControllerMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/ReconTaskMetrics.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/ReconTaskMetrics.java

Purpose: dynamic per-task Metrics2 source for delta processing and reprocess timings/failures.

Important APIs/types/functions: static `create`; `unRegister`; increment/update methods for task delta success/failure/duration and task reprocess failure/duration; getters; `getMetrics`; `sanitizeTaskName`.

Control flow: metric objects are lazily created in concurrent maps per task name using a `MetricsRegistry`. `getMetrics` snapshots the static task counter and all dynamic counters/rates.

State and persistence: in-memory concurrent maps of metric objects; no DB writes. Integrates with Recon task framework and Metrics2.

Risks: `numTasksTracked` is declared but not incremented when new task metrics are created, so it may not reflect unique tasks. Sanitization can collide different task names. Tests should cover lazy creation, name sanitization/collisions, metric snapshots, concurrency, and expected value for `numTasksTracked`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/ReconTaskMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/ReconTaskStatusMetrics.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/ReconTaskStatusMetrics.java

Purpose: Metrics2 source that exposes rows from the persistent `ReconTaskStatus` SQL table as metrics.

Important APIs/types/functions: injected `ReconTaskStatusDao`; `register`; `unregister`; `getMetrics`.

Control flow: each metrics collection calls `findAll()`, emits one record per task with a `type` tag, `lastUpdatedTimestamp` gauge, and `lastUpdatedSeqNumber` counter.

State and persistence: reads persistent SQL task status; no writes. Integrates with jOOQ generated DAO, Guice injection, and Metrics2.

Risks: metrics collection can hit the database on scrape path; DAO failures are not caught here. Using a counter for sequence number represents a point-in-time value, not a monotonically incremented metric source. Tests should cover empty table, multiple rows, tag values, register/unregister, and DAO exception behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/ReconTaskStatusMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/package-info.java

Purpose: package-level Javadoc for Recon metrics classes.

Important APIs/types/functions: no runtime API; declares `org.apache.hadoop.ozone.recon.metrics`.

Control flow and state: none. Integration is documentation/source organization for Metrics2 sources and metric DTOs.

Risks and test signals: compile/Javadoc validation only. Comment is accurate for the package.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/package-info.java

Purpose: package-level Javadoc for the Recon application entry point and related root-level classes.

Important APIs/types/functions: no runtime API; declares `org.apache.hadoop.ozone.recon`.

Control flow and state: none. Integration is root package documentation for Recon service code.

Risks and test signals: compile/Javadoc validation only. Keep updated if root package responsibilities change.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/ContainerHealthSchemaManager.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/ContainerHealthSchemaManager.java

Purpose: SQL/jOOQ manager for the `UNHEALTHY_CONTAINERS` table used by container health scanning and APIs.

Important APIs/types/functions: `insertUnhealthyContainerRecords`; `batchDeleteSCMStatesForContainers`; `replaceUnhealthyContainerRecordsAtomically`; `getExistingInStateSinceByContainerIds`; `applyExistingInStateSince`; `getUnhealthyContainersSummary`; `getUnhealthyContainers`; `getUnhealthyContainersCount`; `getUnhealthyContainersCursor`; nested `UnhealthyContainerRecord`, `ContainerStateKey`, and `UnhealthyContainersSummary`.

Control flow: inserts are batched in chunks of 1000. Deletes and existing-state lookups chunk container IDs by `MAX_IN_CLAUSE_CHUNK_SIZE` to avoid Derby generated-bytecode limits. Atomic replace runs delete and insert in one jOOQ transaction. Query methods support forward/reverse pagination, count capping, and lazy cursor streaming with configured fetch size.

State and persistence: owns all SQL operations for unhealthy container records and preserves `inStateSince` for unchanged `(containerId,state)` pairs. Depends on `ContainerSchemaDefinition`, jOOQ generated table classes, `OzoneConfiguration`, and Recon server fetch-size config.

Risks: `applyExistingInStateSince` performs its own lookup, so callers that already fetched existing values may duplicate DB work. Cursor callers must close returned cursors. Count method requires non-null state. Tests should cover Derby chunking, atomic rollback, state preservation, each allowed state deletion, pagination direction, cursor fetch size, capped counts, summaries, and DB exception fallbacks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/ContainerHealthSchemaManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/ContainerHistory.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/ContainerHistory.java

Purpose: serializable POJO representing historical container replica presence on a datanode.

Important APIs/types/functions: full constructor; default constructor for Jackson; getters/setters for container ID, datanode UUID/host, first/last seen time, last BCS ID getter, state, and data checksum.

Control flow: none beyond property storage.

State and persistence: intended for serialization/deserialization into Recon persistence or API payloads. It carries historical state but no persistence logic itself.

Risks: `lastBcsId` has a getter but no setter, which can limit Jackson or manual mutation after default construction. No validation of timestamps, state, or checksum. Tests should cover Jackson round-trip, constructor values, default-constructor deserialization, and missing setter behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/ContainerHistory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/DataSourceConfiguration.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/DataSourceConfiguration.java

Purpose: abstraction for database connection and jOOQ dialect settings used by Recon persistence wiring.

Important APIs/types/functions: getters for driver class, JDBC URL, username/password, autocommit flag, connection timeout, SQL dialect, pool size, max connection/idle age, connection test statement, and idle test period.

Control flow and state: interface only; implementations supply config values to datasource providers and `JooqPersistenceModule`.

State and persistence: configuration-level integration with BoneCP, Derby/SQLite providers, and jOOQ. No direct persistence operations.

Risks: password exposed as `String`; SQL dialect is stringly typed and later converted with `SQLDialect.valueOf`. Tests should validate implementations provide compatible dialect/URL/driver and sensible pooling values for embedded vs external DBs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/DataSourceConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/DefaultDataSourceProvider.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/DefaultDataSourceProvider.java

Purpose: Guice provider that creates the Recon SQL `DataSource` based on configured JDBC URL.

Important APIs/types/functions: injected `DataSourceConfiguration`; `get()` chooses Derby provider, SQLite provider, or a BoneCP pooled datasource.

Control flow: JDBC URLs containing `derby` delegate to `DerbyDataSourceProvider`; containing `sqlite` delegate to `SqliteDataSourceProvider`; all others configure BoneCP with driver, URL, credentials, autocommit, timeouts, pool size, age limits, idle test period, and test statement.

State and persistence: creates connection pools or embedded datasources; no queries itself. Integrates with `JooqPersistenceModule` and SQL schema classes.

Risks: substring URL detection can misclassify unusual URLs. Embedded DBs bypass pooling by design. Credentials are set directly on BoneCP. Tests should cover URL routing, BoneCP property mapping, Derby/SQLite native providers, and bad driver/URL behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/DefaultDataSourceProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/DerbyDataSourceProvider.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/DerbyDataSourceProvider.java

Purpose: provider for embedded Derby `DataSource` used by Recon persistence.

Important APIs/types/functions: constructor takes `DataSourceConfiguration`; `get()` creates the Derby database/schema then returns `EmbeddedDataSource`.

Control flow: obtains JDBC URL, calls `createNewDerbyDatabase(jdbcUrl, RECON_SCHEMA_NAME)`, logs creation errors, strips `jdbc:derby:` prefix to set database name, and sets user to Recon schema name.

State and persistence: may create Derby database/schema as a side effect. Integrates with generated jOOQ schema name and SQL DB utility.

Risks: creation exceptions are logged but do not stop datasource creation, so later failures may be delayed. It ignores password/autocommit/pool settings. Tests should cover URL conversion, schema creation invocation/failure, datasource user, and invalid path behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/DerbyDataSourceProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/JooqPersistenceModule.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/JooqPersistenceModule.java

Purpose: Guice module that wires Recon SQL persistence, jOOQ configuration, datasource transactions, and `@Transactional` interception.

Important APIs/types/functions: `configure`; provider method `getConfiguration`; provider method `provideDataSourceTransactionManager`; nested `SpringConnectionProvider`.

Control flow: binds `DataSource` to `DefaultDataSourceProvider` singleton; installs `TransactionalMethodInterceptor` for methods/classes annotated with Spring `@Transactional`; disables jOOQ logo; builds `DefaultConfiguration` with datasource, Spring-aware connection provider, and configured SQL dialect; exposes `DataSourceTransactionManager`.

State and persistence: creates the core persistence wiring used by jOOQ DAOs/schema managers. Integration with Spring transaction utilities ensures jOOQ uses transaction-bound connections.

Risks: `SQLDialect.valueOf` fails on invalid config. Provider method calls `provider.get()` directly and can create datasource before Guice singleton caching expectations if misused. Tests should cover module injection, transactional interception, dialect selection, and transaction-bound acquire/release.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/JooqPersistenceModule.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/SqliteDataSourceProvider.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/SqliteDataSourceProvider.java

Purpose: provider for native SQLite `DataSource`, avoiding connection pooling for the embedded default database case.

Important APIs/types/functions: constructor takes `DataSourceConfiguration`; `get()` creates `SQLiteDataSource` and sets configured JDBC URL.

Control flow: no branching; direct datasource creation.

State and persistence: creates datasource only; no queries. Integrates with `DefaultDataSourceProvider` URL routing.

Risks: ignores username/password/pool/autocommit settings, consistent with embedded SQLite but important if URL points to nonstandard setup. Tests should verify URL propagation and compatibility with default Recon SQLite configuration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/SqliteDataSourceProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/TransactionalMethodInterceptor.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/TransactionalMethodInterceptor.java

Purpose: AOP Alliance method interceptor that implements Spring-managed transactions for Guice-bound Recon persistence methods.

Important APIs/types/functions: constructor receives provider for `DataSourceTransactionManager`; `invoke(MethodInvocation)`.

Control flow: obtains a transaction with default definition, proceeds with invocation, commits only if this call opened a new transaction, ignores `UnexpectedRollbackException` during commit, rolls back new transactions on `Exception`, and rethrows.

State and persistence: no direct persistence; controls transaction boundaries for datasource/jOOQ operations. Integrates with `JooqPersistenceModule` interceptors.

Risks: catches only `Exception`, not `Error`; unchecked `RuntimeException` is covered, but serious throwables may skip rollback. Ignoring `UnexpectedRollbackException` can hide transaction failures. Tests should cover nested transactions, commit/rollback, checked/runtime exceptions, unexpected rollback handling, and transaction manager provider behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/TransactionalMethodInterceptor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/package-info.java

Purpose: package-level Javadoc for Recon SQL DB persistence interfaces and wiring.

Important APIs/types/functions: no runtime API; declares `org.apache.hadoop.ozone.recon.persistence`.

Control flow and state: none. Integration is documentation/source organization for datasource providers, jOOQ module, transaction interceptor, and schema managers.

Risks and test signals: compile/Javadoc validation only. Comment is accurate but broad.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/recovery/ReconOMMetadataManager.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/recovery/ReconOMMetadataManager.java

Purpose: Recon extension of OM metadata manager for managing the local OM snapshot DB and providing Recon-specific listing/basic-key APIs.

Important APIs/types/functions: `updateOmDB`; `getLastSequenceNumberFromDB`; `isOmTablesInitialized`; volume and bucket listing/existence methods; `getOzoneConfiguration`; `getKeyTableBasic`; `createCheckpointReconMetadataManager`.

Control flow and state: interface only; implementation manages DB store refresh and direct table iteration. Extends `OMMetadataManager`, so callers can use normal OM metadata APIs plus Recon-specific snapshot lifecycle operations.

State and persistence: represents Recon's local RocksDB snapshot of OM metadata. Integrates with `DBCheckpoint`, `Table`, `BucketLayout`, OM helper types, and Recon API basic key info.

Risks: broad interface mixes lifecycle, listing, and factory behavior. Tests should target implementation behavior for snapshot replacement, sequence number, table initialization, and listing pagination.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/recovery/ReconOMMetadataManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/recovery/ReconOmMetadataManagerImpl.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/recovery/ReconOmMetadataManagerImpl.java

Purpose: Recon implementation of OM metadata manager backed by local OM snapshot RocksDB stores.

Important APIs/types/functions: constructors; `createCheckpointReconMetadataManager`; `start`; `updateOmDB`; `getLastSequenceNumberFromDB`; `isOmTablesInitialized`; `getKeyTableBasic`; `listVolumes`; `volumeExists`; `listBucketsUnderVolume`; `getOzoneConfiguration`; private `initializeNewRdbStore` and `listAllBuckets`.

Control flow: `start` locates last known OM snapshot and initializes a DB store. `updateOmDB` deletes the old DB directory, initializes the new store, and closes the previous store if replaced. Listing methods iterate tables directly, not through OM cache, handling null tables with empty results. Bucket listing supports all-bucket mode, volume existence checks, start-bucket skipping, prefix seek, and max limits.

State and persistence: owns current `DBStore` inherited from `OmMetadataManagerImpl`, `omTablesInitialized`, config, and `ReconUtils`. Reads RocksDB metadata snapshots and may delete old snapshot directories. Integrates with OM DB definitions, table codecs, Recon snapshot directory config, and namespace/Recon APIs.

Risks: `initializeNewRdbStore` catches `IOException` internally and does not rethrow, so `updateOmDB` may silently leave no initialized store after logging. Deleting the old DB before successful initialization can lose last good local snapshot. `getLastSequenceNumberFromDB` casts store to `RDBStore`. Tests should cover startup without snapshot, checkpoint factory path validation, update failure, old-store close/delete ordering, list pagination, null tables, FSO/basic key table selection, and sequence-number IOException.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/recovery/ReconOmMetadataManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/recovery/package-info.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/recovery/package-info.java

Purpose: package-level Javadoc for OM snapshot recovery and checkpoint handling classes.

Important APIs/types/functions: no runtime API; declares `org.apache.hadoop.ozone.recon.recovery`.

Control flow and state: none. Integration is source organization for `ReconOMMetadataManager` and its implementation.

Risks and test signals: compile/Javadoc validation only. Comment accurately reflects the package.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/recovery/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ContainerReplicaHistory.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ContainerReplicaHistory.java

Purpose: tracks first/last observed times and replica metadata for a container replica on one datanode.

Important APIs/types/functions: constructor; getters/setters for BCS ID, last seen time, state, checksums; `getDataChecksum`; `fromProto`; `toProto`.

Control flow: null checksums are normalized to `ContainerChecksums.unknown()`. Proto conversion maps datanode UUID, times, BCS ID, state, and data checksum.

State and persistence: used as persisted/container-history value data via proto wrappers; it records observation history but does not guarantee continuous replica presence. Integrates with `DatanodeID`, `ContainerChecksums`, and protobuf `ContainerReplicaHistoryProto`.

Risks: first seen time and datanode ID are final and cannot be corrected after construction. Proto only persists data checksum, not richer checksum object fields if added later. Tests should cover null checksums, proto round-trip, last-seen updates, state changes, and unknown checksum behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ContainerReplicaHistory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ContainerReplicaHistoryList.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ContainerReplicaHistoryList.java

Purpose: persisted wrapper for a list of `ContainerReplicaHistory` records.

Important APIs/types/functions: static `getCodec`; constructor copies input list; `asList` returns unmodifiable view; `getList` returns mutable backing list; `fromProto`; `toProto`.

Control flow: `DelegatedCodec` wraps `Proto2Codec` for `ContainerReplicaHistoryListProto`; proto conversion maps each item through `ContainerReplicaHistory`.

State and persistence: durable codec for Recon DB table definitions storing replica history. Integrates with HDDS DB codec framework and protobuf types.

Risks: `getList` exposes mutable list, while `asList` is read-only; callers must choose carefully. Constructor does not null-check input. Tests should cover codec round-trip, list copy semantics, mutability via `getList`, unmodifiable `asList`, empty list, and null input behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ContainerReplicaHistoryList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/PipelineSyncTask.java -->
## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/PipelineSyncTask.java

Purpose: background Recon SCM task that syncs pipeline state from SCM and reconciles operational state for dead nodes.

Important APIs/types/functions: constructor; `run`; `runTask`; private `syncOperationalStateOnDeadNodes`.

Control flow: `run` loops while task can run, calls `initializeAndRunTask`, sleeps configured interval, and records failure status on throwable. `runTask` takes a fair write lock, fetches pipelines from SCM, initializes Recon pipeline manager, syncs dead-node operational state, logs duration, and marks status success. Dead-node sync fetches Recon dead nodes, gets SCM nodes, filters matching datanodes, warns if SCM does not report DEAD, and updates Recon node operational state from SCM.

State and persistence: modifies in-memory Recon pipeline/node manager state and task status; persistence depends on those managers/updaters. Dependencies are `StorageContainerServiceProvider`, `ReconPipelineManager`, `ReconNodeManager`, `ReconTaskConfig`, and task status updater.

Risks: any throwable exits the loop rather than continuing after one failed iteration. Uses write lock though no read path appears in this class. Matching relies on `DatanodeDetails.equals`. Tests should cover pipeline initialization, dead-node operational updates, SCM state mismatch warning, exceptions from SCM/node manager, status updater success/failure, interruption, and lock release.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/PipelineSyncTask.java -->
