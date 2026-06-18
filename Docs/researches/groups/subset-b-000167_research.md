# subset-b-000167 Research

Grouped research for the listed Moby client, proxy, daemon, and contrib files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/service_create_test.go -->
# sources/cloud-native/moby/client/service_create_test.go

## Purpose
Tests the Docker API client service-create path, including daemon errors, transport failures, successful response decoding, platform selection, and digest-pinning behavior.

## APIs, Types, And Functions
The file defines `TestServiceCreateError`, `TestServiceCreateConnectionError`, `TestServiceCreate`, `TestServiceCreateCompatiblePlatforms`, and `TestServiceCreateDigestPinning`. It exercises `Client.ServiceCreate` with `swarm.ServiceSpec`, registry auth options, `registrytypes.DistributionInspect`, OCI platform descriptors, and digest references.

## Control Flow, State, And Integration
Tests create mock HTTP clients, assert `POST /services/create`, optionally mock `GET /distribution/...`, encode JSON responses, and compare returned service IDs and warning lists. State is only test-local HTTP request/response data, but it models the daemon API contract and registry distribution resolution step.

## Risks And Test Signals
Important signals are correct errdefs propagation, connection error handling, JSON request shape, compatible-platform query behavior, and digest pinning when an image tag resolves to a content digest. Regressions would affect swarm service creation and image resolution in client callers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/service_create_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/service_inspect.go -->
# sources/cloud-native/moby/client/service_inspect.go

## Purpose
Implements service inspection for the Docker API client, returning a typed swarm service plus raw response metadata for a single service identifier.

## APIs, Types, And Functions
`ServiceInspectOptions` carries `InsertDefaults`; `ServiceInspectResult` wraps `swarm.Service` and raw JSON bytes; `Client.ServiceInspect` is the public method. It depends on `trimID`, `cli.get`, `ensureReaderClosed`, JSON decoding, and `swarm.Service`.

## Control Flow, State, And Integration
The method validates and trims the service ID, conditionally sets `insertDefaults=1`, sends `GET /services/{id}`, reads the entire response into the result body, then unmarshals it into the service value. It persists no client state and uses request query parameters as the only mutation surface.

## Risks And Test Signals
Risk centers on empty or malformed IDs, response-body lifetime, and preserving raw JSON for callers that need fields beyond the typed struct. Integration points are the daemon service inspect endpoint, API query encoding, and swarm type evolution.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/service_inspect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/service_inspect_test.go -->
# sources/cloud-native/moby/client/service_inspect_test.go

## Purpose
Verifies the service inspect client contract for daemon errors, not-found errors, invalid input, and successful response decoding.

## APIs, Types, And Functions
The tests are `TestServiceInspectError`, `TestServiceInspectServiceNotFound`, `TestServiceInspectWithEmptyID`, and `TestServiceInspect`. They use mock HTTP handlers, `cerrdefs.IsNotFound`, `InvalidParameter`, `swarm.Service`, and assert helpers.

## Control Flow, State, And Integration
Mock clients expect `GET /services/service_id`, return status codes or a JSON service object, and assert the client returns the matching service ID. The empty-ID case checks local validation before a daemon call. All state is contained in the mock server and decoded response object.

## Risks And Test Signals
The tests catch path regressions, wrong method selection, failure to classify 404 responses, lost invalid-parameter validation, and JSON decode breaks. They are a unit-level signal for swarm service inspect consumers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/service_inspect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/service_list.go -->
# sources/cloud-native/moby/client/service_list.go

## Purpose
Implements listing swarm services through the Docker API client with optional filters and service status reporting.

## APIs, Types, And Functions
`ServiceListOptions` exposes `Filters` and `Status`; `ServiceListResult` carries `[]swarm.Service`; `Client.ServiceList` performs the request. It depends on `Filters.updateURLValues`, `cli.get`, JSON decoding, and swarm API types.

## Control Flow, State, And Integration
The method builds query values from filters, adds `status=1` when requested, calls `GET /services`, decodes the response array, and closes the response reader. It has no persistence beyond the returned slice.

## Risks And Test Signals
Key risks are omitted filters, incorrect status query encoding, decode errors, and API type drift. The integration point is the daemon service-list endpoint used by swarm orchestration tools and CLI list commands.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/service_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/service_list_test.go -->
# sources/cloud-native/moby/client/service_list_test.go

## Purpose
Tests service list error propagation and successful decoding from the daemon mock endpoint.

## APIs, Types, And Functions
The file defines `TestServiceListError` and `TestServiceList`. It uses `Client.ServiceList`, `ServiceListOptions`, `swarm.Service`, mock HTTP status responses, and gotest assertions.

## Control Flow, State, And Integration
The error test returns a server failure from `GET /services` and expects an unknown errdefs classification. The success test writes a JSON array with one service and compares the decoded ID. Test state is limited to the mock response body and request assertions.

## Risks And Test Signals
Signals include method/path correctness, daemon error mapping, and JSON array decoding. Missing coverage around filters and `Status` means query-building regressions there would need additional tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/service_list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/service_logs.go -->
# sources/cloud-native/moby/client/service_logs.go

## Purpose
Implements streaming log retrieval for swarm services, returning an `io.ReadCloser` that closes automatically when the supplied context is canceled.

## APIs, Types, And Functions
`ServiceLogsOptions` includes stdout/stderr selection, `Since`, `Until`, timestamps, follow, tail, and details flags. `ServiceLogsResult` is an `io.ReadCloser`; `Client.ServiceLogs` validates IDs, builds query parameters, and wraps the response body in `newCancelReadCloser`.

## Control Flow, State, And Integration
The function trims the service ID, translates boolean options into `1` query values, parses `Since` with `timestamp.GetTimestamp`, suppresses `tail` for empty or `all`, then sends `GET /services/{id}/logs`. The stream is live daemon state and remains caller-owned until closed or context cancellation fires.

## Risks And Test Signals
Risks include stream leaks, invalid timestamp handling, mismatched service-log query semantics, and inconsistent behavior with task/container logs. Integration points are the swarm logs endpoint and Docker's multiplexed log stream conventions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/service_logs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/service_logs_example_test.go -->
# sources/cloud-native/moby/client/service_logs_example_test.go

## Purpose
Provides public example documentation for consuming service logs from the Go client.

## APIs, Types, And Functions
`ExampleClient_ServiceLogs` demonstrates `client.NewClientWithOpts`, `Client.ServiceLogs`, `ServiceLogsOptions`, context timeouts, and copying the returned stream to standard output with `io.Copy`.

## Control Flow, State, And Integration
The example creates a context, requests logs for a named service, handles the returned `io.ReadCloser`, defers close, and streams bytes to `os.Stdout`. It is documentation-oriented and does not persist state, but it shows the intended resource-management pattern for callers.

## Risks And Test Signals
The signal is compile-time example validity and API ergonomics. It highlights the need for callers to close streams and manage cancellation; failures would indicate changed constructor names, option fields, or result type behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/service_logs_example_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/service_logs_test.go -->
# sources/cloud-native/moby/client/service_logs_test.go

## Purpose
Tests service log request construction, option encoding, response streaming, and error propagation.

## APIs, Types, And Functions
The tests are `TestServiceLogsError` and `TestServiceLogs`. They exercise `Client.ServiceLogs`, `ServiceLogsOptions`, mock `GET /services/service_id/logs`, and the returned read closer.

## Control Flow, State, And Integration
The error case returns a daemon failure and expects an errdefs unknown error. The success case checks request method, path, and query values for stdout/stderr, follow, timestamps, details, since, and tail, then reads the response body from the returned stream.

## Risks And Test Signals
Signals cover query compatibility and streaming response lifetime. Remaining risks include context-cancel behavior and `tail=all` suppression, which are primarily covered by implementation review rather than these tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/service_logs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/service_remove.go -->
# sources/cloud-native/moby/client/service_remove.go

## Purpose
Implements swarm service removal through the Docker API client.

## APIs, Types, And Functions
`ServiceRemoveOptions` is currently empty, `ServiceRemoveResult` is an empty result wrapper, and `Client.ServiceRemove` performs the operation. The method depends on `trimID` and `cli.delete`.

## Control Flow, State, And Integration
The method validates and normalizes the service ID, then sends `DELETE /services/{id}` without a request body or query parameters. No local client state is persisted; all state mutation occurs in the daemon's swarm service store.

## Risks And Test Signals
Risks are mostly API-contract mistakes: accepting empty IDs, wrong HTTP verb, or wrong path. Integration is direct with the daemon service delete endpoint, where successful calls delete swarm state and related task scheduling intent.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/service_remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/service_remove_test.go -->
# sources/cloud-native/moby/client/service_remove_test.go

## Purpose
Verifies service removal behavior for daemon failures, not-found errors, and successful deletion.

## APIs, Types, And Functions
The file defines `TestServiceRemoveError`, `TestServiceRemoveNotFoundError`, and `TestServiceRemove`. It uses `Client.ServiceRemove`, `ServiceRemoveOptions`, mock `DELETE /services/service_id`, and errdefs assertions.

## Control Flow, State, And Integration
Mock handlers assert the request method and path, then return server error, 404, or success. The tests validate classification of daemon errors and that a successful delete returns nil error and an empty result.

## Risks And Test Signals
The test signal protects the removal endpoint contract. It does not deeply test ID validation, but it catches path, method, and error mapping regressions that would break swarm service cleanup callers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/service_remove_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/service_update.go -->
# sources/cloud-native/moby/client/service_update.go

## Purpose
Implements swarm service updates, including versioned optimistic concurrency, registry auth metadata, and rollback control.

## APIs, Types, And Functions
`ServiceUpdateOptions` carries `EncodedRegistryAuth`, `RegistryAuthFrom`, `Rollback`, and `QueryRegistry`; `ServiceUpdateResult` carries `Warnings`; `Client.ServiceUpdate` posts a `swarm.ServiceSpec`. It uses API headers such as `X-Registry-Auth`, query values for version/auth/rollback, and `cli.post`.

## Control Flow, State, And Integration
The method trims the service ID, sets `version`, registry auth source, and rollback query parameters, attaches encoded registry auth as a header when present, posts to `/services/{id}/update`, and decodes daemon warnings. It mutates daemon swarm service state, not local client state.

## Risks And Test Signals
Risks include missing version query values causing update conflicts, auth header regressions, rollback semantics drifting, and warning decode failures. Integration is with swarm managers and registry credential resolution.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/service_update.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/service_update_test.go -->
# sources/cloud-native/moby/client/service_update_test.go

## Purpose
Tests service update error propagation, connection failure handling, request method/path, query encoding, and response warning decoding.

## APIs, Types, And Functions
The tests are `TestServiceUpdateError`, `TestServiceUpdateConnectionError`, and `TestServiceUpdate`. They exercise `Client.ServiceUpdate`, `ServiceUpdateOptions`, `swarm.Version`, `swarm.ServiceSpec`, and mock `POST /services/service_id/update`.

## Control Flow, State, And Integration
The tests configure server responses, assert `version`, `registryAuthFrom`, and rollback-related request behavior where applicable, and decode returned warnings. State is test-local but mirrors the daemon update endpoint.

## Risks And Test Signals
Signals include transport failure classification, daemon error mapping, and warning preservation. The file is a contract test for API clients that rely on versioned service updates.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/service_update_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/swarm_get_unlock_key.go -->
# sources/cloud-native/moby/client/swarm_get_unlock_key.go

## Purpose
Implements retrieval of the swarm manager unlock key from the daemon.

## APIs, Types, And Functions
`SwarmGetUnlockKeyResult` wraps `swarm.UnlockKeyResponse`; `Client.SwarmGetUnlockKey` performs `GET /swarm/unlockkey`, decodes JSON, and closes the response reader.

## Control Flow, State, And Integration
The method sends a simple GET request without query parameters, decodes the unlock-key payload into swarm API types, and returns it. It does not persist local state, but it exposes sensitive cluster unlock material from daemon state.

## Risks And Test Signals
Risk centers on error handling and safe treatment of sensitive data by callers. Integration is with swarm autolock functionality and manager recovery workflows.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/swarm_get_unlock_key.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/swarm_get_unlock_key_test.go -->
# sources/cloud-native/moby/client/swarm_get_unlock_key_test.go

## Purpose
Tests unlock-key retrieval for server errors and successful JSON decoding.

## APIs, Types, And Functions
The file defines `TestSwarmGetUnlockKeyError` and `TestSwarmGetUnlockKey`, using `Client.SwarmGetUnlockKey`, `swarm.UnlockKeyResponse`, mock `GET /swarm/unlockkey`, and errdefs assertions.

## Control Flow, State, And Integration
Mock handlers assert method and path, then return either an error status or an unlock-key response body. The success test checks the decoded unlock key value.

## Risks And Test Signals
Signals protect endpoint path, HTTP method, error mapping, and JSON shape. The test does not validate secrecy handling, which remains caller and logging policy responsibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/swarm_get_unlock_key_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/swarm_init.go -->
# sources/cloud-native/moby/client/swarm_init.go

## Purpose
Implements swarm initialization, converting client options into daemon `swarm.InitRequest` payloads and returning the new node ID.

## APIs, Types, And Functions
`SwarmInitOptions` embeds `swarm.InitRequest`; `SwarmInitResult` contains the daemon response string; `Client.SwarmInit` performs the request. It depends on JSON decode and swarm types, including `net/netip` fields in init configuration.

## Control Flow, State, And Integration
The method posts the supplied init request to `/swarm/init`, decodes the daemon response as a string node ID, and closes the response body. It initializes persistent swarm cluster state in the daemon.

## Risks And Test Signals
Risks include request-shape drift with swarm API types, decode errors for the string response, and daemon-side irreversible cluster initialization. Integration is with swarm manager bootstrap and network address configuration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/swarm_init.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/swarm_init_test.go -->
# sources/cloud-native/moby/client/swarm_init_test.go

## Purpose
Tests swarm initialization error propagation and successful node-ID decoding.

## APIs, Types, And Functions
The tests are `TestSwarmInitError` and `TestSwarmInit`. They call `Client.SwarmInit`, provide `SwarmInitOptions`, use mock `POST /swarm/init`, and check errdefs classification and response content.

## Control Flow, State, And Integration
Handlers assert method and path, return either a server error or JSON-encoded node ID, and the client result is compared. Test state is isolated to the mock HTTP exchange.

## Risks And Test Signals
Signals cover basic endpoint contract and response decoding. More complex init request validation remains a daemon-side concern rather than a client unit test.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/swarm_init_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/swarm_inspect.go -->
# sources/cloud-native/moby/client/swarm_inspect.go

## Purpose
Implements swarm cluster inspection through the Docker API client.

## APIs, Types, And Functions
`SwarmInspectOptions` is currently empty; `SwarmInspectResult` wraps `swarm.Swarm`; `Client.SwarmInspect` requests and decodes the current swarm object.

## Control Flow, State, And Integration
The method sends `GET /swarm`, decodes the response into `swarm.Swarm`, closes the reader, and returns the typed result. It reads daemon cluster state but does not mutate client state.

## Risks And Test Signals
Risks are endpoint drift, JSON decode failures as swarm fields evolve, and callers assuming fields are always present. Integration is with swarm manager metadata, Raft configuration, and node join-token state exposed by the daemon.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/swarm_inspect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/swarm_inspect_test.go -->
# sources/cloud-native/moby/client/swarm_inspect_test.go

## Purpose
Tests swarm inspection for daemon error handling and successful typed decoding.

## APIs, Types, And Functions
`TestSwarmInspectError` and `TestSwarmInspect` exercise `Client.SwarmInspect`, `SwarmInspectOptions`, mock `GET /swarm`, `swarm.Swarm`, and errdefs assertions.

## Control Flow, State, And Integration
The mock server verifies method and path, then returns a failure or a JSON object with a swarm ID. The client result is compared to ensure response decoding preserves the ID.

## Risks And Test Signals
Signals protect the basic inspect API contract. The test does not cover all swarm fields, so schema field regressions outside ID would need broader fixture coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/swarm_inspect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/swarm_join.go -->
# sources/cloud-native/moby/client/swarm_join.go

## Purpose
Implements joining an existing swarm with a daemon-side join request.

## APIs, Types, And Functions
`SwarmJoinOptions` embeds `swarm.JoinRequest`; `SwarmJoinResult` is an empty result wrapper; `Client.SwarmJoin` posts the join request to the daemon.

## Control Flow, State, And Integration
The method sends `POST /swarm/join` with the requested advertise address, remote addresses, listen address, and join token embedded in the API type. The daemon persists membership and node identity if successful; the client stores nothing.

## Risks And Test Signals
Risks include request serialization drift and failure to surface daemon errors for invalid tokens or unreachable managers. Integration is with swarm node bootstrap and cluster membership state.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/swarm_join.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/swarm_join_test.go -->
# sources/cloud-native/moby/client/swarm_join_test.go

## Purpose
Tests swarm join error propagation and successful call behavior.

## APIs, Types, And Functions
The file defines `TestSwarmJoinError` and `TestSwarmJoin`, using `Client.SwarmJoin`, `SwarmJoinOptions`, mock `POST /swarm/join`, and errdefs assertions.

## Control Flow, State, And Integration
Handlers assert the HTTP method and path, then return a daemon error or success. The client should return an error in the failure case and nil error with an empty result in the success case.

## Risks And Test Signals
Signals cover endpoint contract and daemon error propagation. The file does not inspect the full request body, so detailed join option serialization relies on the shared request machinery and swarm type tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/swarm_join_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/swarm_leave.go -->
# sources/cloud-native/moby/client/swarm_leave.go

## Purpose
Implements leaving a swarm, optionally forcing removal when the daemon is a manager.

## APIs, Types, And Functions
`SwarmLeaveOptions` contains `Force`; `SwarmLeaveResult` is empty; `Client.SwarmLeave` posts to the daemon with a `force` query value when requested.

## Control Flow, State, And Integration
The method builds `force=1` only for forced leave and sends `POST /swarm/leave`. Successful calls mutate daemon swarm membership and may remove cluster participation state.

## Risks And Test Signals
Risks include accidentally omitting the force flag or using the wrong HTTP method. Integration is with node demotion/leave workflows and daemon swarm state cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/swarm_leave.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/swarm_leave_test.go -->
# sources/cloud-native/moby/client/swarm_leave_test.go

## Purpose
Tests swarm leave error handling and force query encoding.

## APIs, Types, And Functions
`TestSwarmLeaveError` and `TestSwarmLeave` exercise `Client.SwarmLeave`, `SwarmLeaveOptions`, mock `POST /swarm/leave`, and errdefs assertions.

## Control Flow, State, And Integration
The success test asserts the request method, path, and force query value when `Force` is true. The error test returns a daemon failure and expects an unknown errdefs classification.

## Risks And Test Signals
Signals catch query encoding and endpoint regressions. The test models client behavior only; daemon cleanup correctness is covered elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/swarm_leave_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/swarm_unlock.go -->
# sources/cloud-native/moby/client/swarm_unlock.go

## Purpose
Implements unlocking an autolocked swarm manager by submitting the unlock key to the daemon.

## APIs, Types, And Functions
`SwarmUnlockOptions` embeds `swarm.UnlockRequest`; `SwarmUnlockResult` is empty; `Client.SwarmUnlock` posts to `/swarm/unlock`.

## Control Flow, State, And Integration
The method serializes the unlock request, posts it to the daemon, and returns any daemon error. It stores no local state, while successful calls unlock persisted manager state and encrypted Raft material.

## Risks And Test Signals
Risks include improper propagation of sensitive unlock keys and weak error classification for rejected keys. Integration is with swarm autolock and manager recovery paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/swarm_unlock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/swarm_unlock_test.go -->
# sources/cloud-native/moby/client/swarm_unlock_test.go

## Purpose
Tests swarm unlock endpoint method/path and daemon error propagation.

## APIs, Types, And Functions
The tests are `TestSwarmUnlockError` and `TestSwarmUnlock`, using `Client.SwarmUnlock`, `SwarmUnlockOptions`, mock `POST /swarm/unlock`, and errdefs assertions.

## Control Flow, State, And Integration
The mock server checks method and path, returns either a server error or success, and the test asserts the client error result. Sensitive key contents are not inspected in this unit.

## Risks And Test Signals
Signals protect the basic unlock client contract. Remaining risk is body serialization and secret logging policy, which requires broader review outside this focused endpoint test.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/swarm_unlock_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/swarm_update.go -->
# sources/cloud-native/moby/client/swarm_update.go

## Purpose
Implements swarm cluster updates with versioned concurrency and optional token/unlock-key rotation flags.

## APIs, Types, And Functions
`SwarmUpdateOptions` embeds `swarm.Spec` and contains `RotateWorkerToken`, `RotateManagerToken`, `RotateManagerUnlockKey`, and `Version`. `SwarmUpdateResult` is empty; `Client.SwarmUpdate` posts to `/swarm/update`.

## Control Flow, State, And Integration
The method encodes version and rotation booleans into query values, posts the swarm spec, and returns daemon errors. Successful calls mutate cluster-level Raft configuration, token state, and potentially unlock-key material.

## Risks And Test Signals
Risks include missing version values, inverted rotation flags, and daemon API drift around swarm spec serialization. Integration is with manager control-plane state and security token rotation workflows.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/swarm_update.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/swarm_update_test.go -->
# sources/cloud-native/moby/client/swarm_update_test.go

## Purpose
Tests swarm update error handling and successful endpoint invocation.

## APIs, Types, And Functions
`TestSwarmUpdateError` and `TestSwarmUpdate` exercise `Client.SwarmUpdate`, `SwarmUpdateOptions`, mock `POST /swarm/update`, and errdefs classification.

## Control Flow, State, And Integration
The mock server validates request method and path, then returns failure or success. The tests assert that daemon failures surface and successful updates return nil errors.

## Risks And Test Signals
The file protects the endpoint contract but gives limited coverage to query parameters for version and rotation flags. Those fields remain the main client-side risk surface.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/swarm_update_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/system_disk_usage.go -->
# sources/cloud-native/moby/client/system_disk_usage.go

## Purpose
Implements `Client.DiskUsage`, normalizing daemon disk-usage responses into a richer client result across current and legacy API versions.

## APIs, Types, And Functions
Important types are `DiskUsageOptions`, `DiskUsageResult`, `ContainersDiskUsage`, `ImagesDiskUsage`, `VolumesDiskUsage`, `BuildCacheDiskUsage`, and `legacyDiskUsage`. Conversion helpers include `diskUsageResultFromLegacyAPI`, `imageDiskUsageFromLegacyAPI`, `containerDiskUsageFromLegacyAPI`, `buildCacheDiskUsageFromLegacyAPI`, and `volumeDiskUsageFromLegacyAPI`.

## Control Flow, State, And Integration
The method builds `type=` query entries for requested object classes and `verbose=1` when needed, calls `GET /system/df`, and selects decode behavior based on `cli.version < 1.52`. Current responses expose object-specific usage structs; legacy responses are converted by computing totals, active counts, and reclaimable bytes from item lists.

## Risks And Test Signals
Risks include API-version branching, reclaimable calculations, omitted verbose item clones, negative image container counts, shared build-cache sizing, and volume usage data being nil. Integration is with daemon system accounting, image/container/volume/build API types, and CLI disk-usage displays.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/system_disk_usage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/system_disk_usage_test.go -->
# sources/cloud-native/moby/client/system_disk_usage_test.go

## Purpose
Tests disk-usage request errors, option query construction, current response decoding, legacy conversion, and image reclaimable calculations.

## APIs, Types, And Functions
The tests include `TestDiskUsageError`, `TestDiskUsage`, `TestDiskUsageWithOptions`, `TestLegacyDiskUsage`, and `TestImageDiskUsageFromLegacyAPI`. They use system, image, container, volume, and build-cache API fixtures.

## Control Flow, State, And Integration
Mock handlers validate `GET /system/df`, query type selections, and verbose flag behavior. Fixtures exercise current `system.DiskUsage` decoding and legacy response conversion for counts, totals, active objects, and reclaimable space.

## Risks And Test Signals
Signals are strong around version compatibility and accounting math. The tests catch regressions in legacy behavior that could otherwise silently skew CLI or API consumers' disk cleanup recommendations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/system_disk_usage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/system_events.go -->
# sources/cloud-native/moby/client/system_events.go

## Purpose
Implements streaming daemon events with timestamp/filter query construction and content-type aware JSON stream decoding.

## APIs, Types, And Functions
`EventsListOptions` contains `Since`, `Until`, and `Filters`; `EventsResult` exposes message and error channels; `Client.Events` starts the stream. `buildEventsQueryParams` parses timestamps using `timestamp.GetTimestamp` and applies filters.

## Control Flow, State, And Integration
`Events` creates channels, starts a goroutine, builds query parameters, sets Accept headers for JSON lines, NDJSON, and JSON sequence, calls `GET /events`, and decodes messages until decoder error or context cancellation. The returned stream reflects live daemon event state and requires caller cancellation.

## Risks And Test Signals
Risks include goroutine leaks, blocked message consumers, incorrect timestamp reference times, content-type mismatch, and EOF/error channel semantics. Integration points are daemon event streaming and filter encoding shared by many Docker clients.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/system_events.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/system_events_test.go -->
# sources/cloud-native/moby/client/system_events_test.go

## Purpose
Tests event-stream option errors, daemon error propagation, request construction, and streaming decode behavior.

## APIs, Types, And Functions
The tests are `TestEventsErrorInOptions`, `TestEventsErrorFromServer`, and `TestEvents`. They use `Client.Events`, `EventsListOptions`, filters, `events.Message`, JSON encoding, and channel assertions.

## Control Flow, State, And Integration
Tests force timestamp parse errors before HTTP, mock server errors from `/events`, and emit JSON event messages for the streaming path. They read from returned message and error channels to verify startup and decode behavior.

## Risks And Test Signals
Signals include early option validation, method/path correctness, filter/timestamp query output, and stream channel semantics. Context cancellation and alternate event content types remain important integration risks.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/system_events_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/system_info.go -->
# sources/cloud-native/moby/client/system_info.go

## Purpose
Implements retrieval of daemon system information.

## APIs, Types, And Functions
`InfoOptions` is currently empty; `SystemInfoResult` embeds `system.Info`; `Client.Info` sends the request and decodes the result.

## Control Flow, State, And Integration
The method creates an empty query, calls `GET /info`, decodes JSON into `system.Info`, and closes the response body. It reads daemon runtime state including drivers, resources, plugins, security options, and discovered devices.

## Risks And Test Signals
Risks are schema drift, invalid JSON handling, and callers depending on optional fields. Integration is broad because `/info` feeds diagnostics, CLI display, and capability detection.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/system_info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/system_info_test.go -->
# sources/cloud-native/moby/client/system_info_test.go

## Purpose
Tests system info error handling, invalid JSON handling, basic decode behavior, and discovered-device fields.

## APIs, Types, And Functions
The tests include `TestInfoServerError`, `TestInfoInvalidResponseJSONError`, `TestInfo`, and `TestInfoWithDiscoveredDevices`. They exercise `Client.Info`, `InfoOptions`, and `system.Info`.

## Control Flow, State, And Integration
Mock handlers validate `GET /info`, return server failures, malformed JSON, or structured info responses. The tests assert expected errors and decoded fields, including newer discovered-device data.

## Risks And Test Signals
Signals cover response decode robustness and schema additions. Since `/info` is a large structure, tests sample important fields rather than exhaustively verifying every daemon capability.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/system_info_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/task_inspect.go -->
# sources/cloud-native/moby/client/task_inspect.go

## Purpose
Implements inspection of a single swarm task through the Docker API client.

## APIs, Types, And Functions
`TaskInspectOptions` is empty; `TaskInspectResult` wraps `swarm.Task`; `Client.TaskInspect` validates the task ID and decodes the daemon response.

## Control Flow, State, And Integration
The method trims the task ID, calls `GET /tasks/{id}`, decodes JSON into a task object, and closes the response reader. It reads scheduler task state without mutating local or daemon state.

## Risks And Test Signals
Risks include empty ID handling, endpoint path drift, and swarm task schema evolution. Integration is with swarm scheduler state, service diagnostics, and task-level log/status workflows.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/task_inspect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/task_inspect_test.go -->
# sources/cloud-native/moby/client/task_inspect_test.go

## Purpose
Tests swarm task inspection for daemon errors, empty IDs, and successful JSON decoding.

## APIs, Types, And Functions
The tests are `TestTaskInspectError`, `TestTaskInspectWithEmptyID`, and `TestTaskInspect`. They use `Client.TaskInspect`, `TaskInspectOptions`, mock `GET /tasks/task_id`, `swarm.Task`, and errdefs assertions.

## Control Flow, State, And Integration
The empty-ID test checks local validation. Other tests assert request method/path and return either a server failure or a JSON task with an ID to decode.

## Risks And Test Signals
Signals protect endpoint and validation behavior. Coverage is intentionally narrow and does not exhaustively check all task fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/task_inspect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/task_list.go -->
# sources/cloud-native/moby/client/task_list.go

## Purpose
Implements listing swarm tasks with optional filter query parameters.

## APIs, Types, And Functions
`TaskListOptions` contains `Filters`; `TaskListResult` contains `[]swarm.Task`; `Client.TaskList` performs the list request. It depends on filter URL encoding and JSON decoding.

## Control Flow, State, And Integration
The method applies filters to query values, calls `GET /tasks`, decodes the response array, and closes the body. It reads daemon scheduler state and persists nothing locally.

## Risks And Test Signals
Risks include filter encoding bugs and schema drift in `swarm.Task`. Integration points are service/task status views and swarm scheduling diagnostics.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/task_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/task_list_test.go -->
# sources/cloud-native/moby/client/task_list_test.go

## Purpose
Tests task list daemon error handling and successful task array decoding.

## APIs, Types, And Functions
`TestTaskListError` and `TestTaskList` call `Client.TaskList`, pass `TaskListOptions`, use mock `GET /tasks`, and compare `swarm.Task` results.

## Control Flow, State, And Integration
The mock server returns a failure for the error path and a JSON array for the success path. Tests assert method/path correctness and decoded task IDs.

## Risks And Test Signals
The file catches endpoint and decode regressions. Filter query coverage is limited, leaving filter-specific behavior dependent on shared filter helpers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/task_list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/task_logs.go -->
# sources/cloud-native/moby/client/task_logs.go

## Purpose
Implements streaming log retrieval for a single swarm task.

## APIs, Types, And Functions
`TaskLogsOptions` mirrors service log flags; `TaskLogsResult` is an `io.ReadCloser`; `Client.TaskLogs` sends `GET /tasks/{id}/logs` and wraps the response in `newCancelReadCloser`.

## Control Flow, State, And Integration
The method builds stdout/stderr, since, timestamps, details, follow, and tail query values, parses `Since`, sends the GET request, and returns a cancel-aware stream. Unlike service logs, it always sets `tail` from the option value.

## Risks And Test Signals
Risks include missing task ID validation, inconsistent `Until` handling despite the option field, stream leaks, and log query drift relative to service/container logs. Integration is with daemon task log endpoints and live log consumers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/task_logs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/utils.go -->
# sources/cloud-native/moby/client/utils.go

## Purpose
Provides shared client helpers for invalid-parameter errors, ID trimming, API-version parsing, platform encoding, and context-cancelable response readers.

## APIs, Types, And Functions
Important items are `emptyIDError`, `InvalidParameter`, `trimID`, `parseAPIVersion`, `parseMajorMinor`, `encodePlatforms`, `encodePlatform`, `cancelReadCloser`, `newCancelReadCloser`, `Read`, and `Close`.

## Control Flow, State, And Integration
`trimID` rejects empty identifiers and trims `sha256:` prefixes to 64 hex characters. Platform helpers JSON-encode OCI platform slices for query/header use. `cancelReadCloser` starts a goroutine that closes the underlying reader on context cancellation and serializes reads/closes with a mutex.

## Risks And Test Signals
Risks include data races around stream close, overly aggressive ID trimming, and platform JSON compatibility. These helpers are integrated across many endpoint methods, so small regressions have broad client impact.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/utils_test.go -->
# sources/cloud-native/moby/client/utils_test.go

## Purpose
Tests platform JSON encoding and race safety for cancelable read closers.

## APIs, Types, And Functions
`TestEncodePlatforms` checks `encodePlatforms` with OCI platform values. `TestNewCancelReadCloserRace` exercises `newCancelReadCloser` with concurrent cancellation, reading, and closing behavior.

## Control Flow, State, And Integration
The platform test compares JSON output. The race test uses contexts and readers to ensure cancel-triggered close does not race or panic while reads are active. State is limited to test-local readers and goroutines.

## Risks And Test Signals
Signals are important because `newCancelReadCloser` protects log and stream APIs from goroutine leaks and data races. Running tests with `-race` would increase confidence in the concurrency path.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/version.go -->
# sources/cloud-native/moby/client/version.go

## Purpose
Implements daemon version retrieval and typed decoding of version, API, platform, component, and runtime metadata.

## APIs, Types, And Functions
`ServerVersionOptions` is empty; `ServerVersionResult` embeds `system.Version`; `PlatformInfo` describes platform names; `Client.ServerVersion` performs `GET /version` and decodes the result.

## Control Flow, State, And Integration
The method sends a simple GET request, decodes JSON into `system.Version`, and returns it. It reads daemon build/runtime state and does not modify client fields itself.

## Risks And Test Signals
Risks include schema drift for components/runtimes, invalid JSON, and callers using server version for feature gates. Integration is central to API negotiation, diagnostics, and CLI version output.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/volume_create.go -->
# sources/cloud-native/moby/client/volume_create.go

## Purpose
Implements Docker volume creation through the API client.

## APIs, Types, And Functions
`VolumeCreateOptions` embeds `volume.CreateOptions`; `VolumeCreateResult` embeds `volume.Volume`; `Client.VolumeCreate` posts to `/volumes/create` and decodes the created volume.

## Control Flow, State, And Integration
The method serializes the create options, sends `POST /volumes/create`, decodes the daemon response into a volume object, and closes the response. Successful calls create persistent daemon volume metadata and possibly driver-backed storage.

## Risks And Test Signals
Risks include request body drift for driver/options/labels and response decode failures. Integration is with volume drivers, daemon volume store, and container mount workflows.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/volume_create.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/volume_create_test.go -->
# sources/cloud-native/moby/client/volume_create_test.go

## Purpose
Tests volume create error propagation and successful response decoding.

## APIs, Types, And Functions
The tests are `TestVolumeCreateError` and `TestVolumeCreate`, using `Client.VolumeCreate`, `VolumeCreateOptions`, mock `POST /volumes/create`, and `volume.Volume`.

## Control Flow, State, And Integration
Mock handlers assert method/path, return a daemon error or JSON volume object, and the client result is compared by volume name. State is mock-server scoped.

## Risks And Test Signals
Signals cover endpoint contract and result decoding. The tests do not inspect full request bodies, so option serialization has only indirect coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/volume_create_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/volume_inspect.go -->
# sources/cloud-native/moby/client/volume_inspect.go

## Purpose
Implements inspection of a Docker volume by name or ID.

## APIs, Types, And Functions
`VolumeInspectOptions` is empty; `VolumeInspectResult` embeds `volume.Volume`; `Client.VolumeInspect` validates the ID/name, sends the request, and decodes the result.

## Control Flow, State, And Integration
The method trims and validates the volume identifier, calls `GET /volumes/{id}`, decodes JSON into the volume type, and closes the response. It reads daemon volume metadata and driver usage data.

## Risks And Test Signals
Risks include rejecting valid names if ID trimming is wrong, not-found classification, and volume schema drift. Integration is with volume drivers and mount planning code.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/volume_inspect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/volume_inspect_test.go -->
# sources/cloud-native/moby/client/volume_inspect_test.go

## Purpose
Tests volume inspect daemon errors, not-found handling, empty ID validation, and successful decode.

## APIs, Types, And Functions
The tests include `TestVolumeInspectError`, `TestVolumeInspectNotFound`, `TestVolumeInspectWithEmptyID`, and `TestVolumeInspect`. They use `Client.VolumeInspect`, `volume.Volume`, and errdefs assertions.

## Control Flow, State, And Integration
Mock handlers assert `GET /volumes/volume_id`, return status codes or a JSON volume, and the client validates decoded name fields. Empty ID validation occurs before HTTP.

## Risks And Test Signals
Signals protect validation, path construction, error classification, and response decoding. Broader driver-specific fields are not exhaustively tested.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/volume_inspect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/volume_list.go -->
# sources/cloud-native/moby/client/volume_list.go

## Purpose
Implements Docker volume listing with optional filters.

## APIs, Types, And Functions
`VolumeListOptions` contains `Filters`; `VolumeListResult` wraps `volume.ListResponse`; `Client.VolumeList` performs the request and decode.

## Control Flow, State, And Integration
The method applies filters to URL values, sends `GET /volumes`, decodes the list response, and closes the response body. It reads daemon volume store state without mutating it.

## Risks And Test Signals
Risks include filter query encoding, schema drift in warnings or volume entries, and nil list fields. Integration is with CLI volume listing, pruning decisions, and driver metadata display.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/volume_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/volume_list_test.go -->
# sources/cloud-native/moby/client/volume_list_test.go

## Purpose
Tests volume list error propagation and successful list response decoding.

## APIs, Types, And Functions
`TestVolumeListError` and `TestVolumeList` exercise `Client.VolumeList`, `VolumeListOptions`, mock `GET /volumes`, and `volume.ListResponse`.

## Control Flow, State, And Integration
The mock server returns a daemon error or JSON list containing a named volume. Tests assert request method/path and decoded volume count/name.

## Risks And Test Signals
Signals cover endpoint and decode basics. Filter-specific coverage is limited, leaving shared filter helper behavior as the main guard for filtered volume lists.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/volume_list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/volume_prune.go -->
# sources/cloud-native/moby/client/volume_prune.go

## Purpose
Implements pruning unused Docker volumes and decoding reclaimed-space results.

## APIs, Types, And Functions
`VolumePruneOptions` contains `Filters`; `VolumePruneResult` embeds `volume.PruneReport`; `Client.VolumePrune` posts to `/volumes/prune`. It uses errdefs to preserve daemon error classes around unsupported or failed prune operations.

## Control Flow, State, And Integration
The method applies filters to query values, sends `POST /volumes/prune`, decodes the prune report, and closes the reader. Successful calls delete persistent daemon volume data that is not referenced.

## Risks And Test Signals
Risks are destructive behavior through wrong filters, error class loss, and decode issues for deleted-volume lists or space reclaimed. Integration is with daemon volume reference tracking and CLI cleanup commands.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/volume_prune.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/volume_prune_test.go -->
# sources/cloud-native/moby/client/volume_prune_test.go

## Purpose
Tests volume prune success and error variants, including errdefs classification and decoded prune reports.

## APIs, Types, And Functions
`TestVolumePrune` uses table-driven mock responses for `Client.VolumePrune`, `VolumePruneOptions`, mock `POST /volumes/prune`, and `volume.PruneReport`.

## Control Flow, State, And Integration
Test cases configure status codes and JSON bodies, assert the request method/path, and compare deleted volume names plus reclaimed space. State is local to each table case.

## Risks And Test Signals
Signals are valuable because prune is destructive. The test checks response mapping but does not execute real daemon volume reference accounting.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/volume_prune_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/volume_remove.go -->
# sources/cloud-native/moby/client/volume_remove.go

## Purpose
Implements removal of a named Docker volume with optional force behavior.

## APIs, Types, And Functions
`VolumeRemoveOptions` contains `Force`; `VolumeRemoveResult` is empty; `Client.VolumeRemove` validates the identifier and sends the delete request.

## Control Flow, State, And Integration
The method trims the volume ID/name, sets `force=1` when requested, and sends `DELETE /volumes/{id}`. Successful daemon calls delete volume metadata and possibly storage managed by a volume driver.

## Risks And Test Signals
Risks include destructive removal from wrong path construction, missing force query, and invalid ID handling. Integration is with volume drivers and daemon reference checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/volume_remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/volume_remove_test.go -->
# sources/cloud-native/moby/client/volume_remove_test.go

## Purpose
Tests volume removal server errors, connection errors, method/path correctness, and force query encoding.

## APIs, Types, And Functions
The tests are `TestVolumeRemoveError`, `TestVolumeRemoveConnectionError`, and `TestVolumeRemove`. They use `Client.VolumeRemove`, `VolumeRemoveOptions`, mock `DELETE /volumes/volume_id`, and errdefs assertions.

## Control Flow, State, And Integration
Mock handlers assert method, path, and query values, then return status codes. The connection test uses a client pointing to an unreachable server to verify transport error behavior.

## Risks And Test Signals
Signals protect a destructive endpoint from method/path/query regressions. The tests do not cover driver-specific daemon side effects.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/volume_remove_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/volume_update.go -->
# sources/cloud-native/moby/client/volume_update.go

## Purpose
Implements update of cluster-scoped volume metadata using versioned swarm object semantics.

## APIs, Types, And Functions
`VolumeUpdateOptions` contains `Version` and `Spec`; `VolumeUpdateResult` is empty; `Client.VolumeUpdate` sends a `PUT` request. It uses `swarm.Version` and `volume.UpdateVolumeOptions`.

## Control Flow, State, And Integration
The method trims the volume name, sets `version` in query parameters, and sends `PUT /volumes/{name}` with the update spec. Successful calls mutate daemon or swarm volume metadata.

## Risks And Test Signals
Risks include missing optimistic-concurrency version, wrong method, and update spec drift. Integration is with swarm-aware volume drivers and daemon volume metadata storage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/volume_update.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/volume_update_test.go -->
# sources/cloud-native/moby/client/volume_update_test.go

## Purpose
Tests volume update daemon errors and successful request construction.

## APIs, Types, And Functions
`TestVolumeUpdateError` and `TestVolumeUpdate` exercise `Client.VolumeUpdate`, `VolumeUpdateOptions`, `swarm.Version`, and mock `PUT /volumes/test1`.

## Control Flow, State, And Integration
Mock handlers assert method, path, and version query encoding, then return server failure or success. The tests verify error classification and nil success behavior.

## Risks And Test Signals
Signals cover the versioned update endpoint contract. Request-body field coverage is limited, so schema drift in update options would need additional tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/volume_update_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/cmd/docker-proxy/main_linux.go -->
# sources/cloud-native/moby/cmd/docker-proxy/main_linux.go

## Purpose
Provides the Linux `docker-proxy` entrypoint that maps host ports to container ports for TCP, UDP, and SCTP traffic.

## APIs, Types, And Functions
Key items are `ProxyConfig`, `main`, `newProxy`, `parseFlags`, and `handleStopSignals`. It uses inherited file descriptors `parentPipeFd` and `listenSockFd`, `net` listeners, SCTP support, Rootless/userland proxy protocol flags, and version printing via `dockerversion`.

## Control Flow, State, And Integration
`main` marks inherited descriptors close-on-exec, parses flags, builds the appropriate proxy, reports startup status to the parent pipe, installs signal handling, and blocks in `Proxy.Run`. `newProxy` either reuses an inherited listener or opens a host listener, configures UDP packet-info control messages, and constructs backend addresses.

## Risks And Test Signals
Risks include inherited descriptor misuse, wrong IP family selection, UDP source-address handling, SCTP availability, and startup reporting deadlocks. Integration is with dockerd's port publishing path and Linux socket behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/cmd/docker-proxy/main_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/cmd/docker-proxy/network_proxy_linux_test.go -->
# sources/cloud-native/moby/cmd/docker-proxy/network_proxy_linux_test.go

## Purpose
Provides integration-style tests for docker-proxy networking across TCP, UDP, SCTP, IPv4, IPv6, dual-stack, listener inheritance, and backend error recovery.

## APIs, Types, And Functions
The file defines `EchoServer`, `EchoServerOptions`, `StreamEchoServer`, `UDPEchoServer`, listener helpers, `testProxyAt`, protocol helpers, and tests such as `TestTCP4Proxy`, `TestTCP4ProxyHalfClose`, `TestUDPWriteError`, and SCTP IPv4/IPv6 cases.

## Control Flow, State, And Integration
Tests start local echo backends, build proxy configs with either inherited sockets or host ports, run proxies in goroutines, connect clients, send test buffers, and compare echoed data. SCTP listener setup uses low-level `unix` syscalls to create inheritable descriptors.

## Risks And Test Signals
Signals cover real socket behavior, half-close propagation, UDP ICMP write-error recovery, dual-stack routing, and SCTP proxying. Risks include host SCTP support, fixed "hopefully free" ports, timing, and platform/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/cmd/docker-proxy/network_proxy_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/cmd/docker-proxy/proxy_linux.go -->
# sources/cloud-native/moby/cmd/docker-proxy/proxy_linux.go

## Purpose
Defines shared Linux docker-proxy protocol abstractions.

## APIs, Types, And Functions
`ipVersion` is a string-like protocol suffix type with IPv4 and IPv6 values. `Proxy` is the common interface implemented by TCP, UDP, and SCTP proxies, with `Run` and `Close` methods.

## Control Flow, State, And Integration
This file has no runtime flow of its own; it establishes compile-time contracts used by `main_linux.go` and protocol-specific proxy implementations. State is held by concrete proxy structs in other files.

## Risks And Test Signals
Risks are low but central: changing the interface breaks all protocol implementations. Integration signals come from docker-proxy tests that instantiate concrete proxies through the shared interface.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/cmd/docker-proxy/proxy_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/cmd/docker-proxy/sctp_proxy_linux.go -->
# sources/cloud-native/moby/cmd/docker-proxy/sctp_proxy_linux.go

## Purpose
Implements SCTP forwarding for docker-proxy.

## APIs, Types, And Functions
`SCTPProxy` stores frontend listener and backend address. `NewSCTPProxy`, `clientLoop`, `Run`, and `Close` implement the `Proxy` interface using `github.com/ishidawataru/sctp`.

## Control Flow, State, And Integration
`Run` accepts SCTP clients and starts `clientLoop` goroutines. Each client loop dials the backend, wraps SCTP connections to preserve send/receive info, then runs bidirectional `io.Copy` brokers until either side finishes or the proxy closes.

## Risks And Test Signals
Risks include SCTP kernel/module availability, connection close semantics, goroutine cleanup, and error handling when backend dial fails. Integration is with published SCTP ports and the shared docker-proxy lifecycle.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/cmd/docker-proxy/sctp_proxy_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/cmd/docker-proxy/tcp_proxy_linux.go -->
# sources/cloud-native/moby/cmd/docker-proxy/tcp_proxy_linux.go

## Purpose
Implements TCP forwarding for docker-proxy.

## APIs, Types, And Functions
`TCPProxy` stores frontend and backend TCP addresses. `NewTCPProxy`, `clientLoop`, `Run`, and `Close` implement the shared `Proxy` interface.

## Control Flow, State, And Integration
`Run` accepts TCP connections and starts a client goroutine per connection. `clientLoop` dials the backend and starts two `io.Copy` brokers, using `CloseRead` and `CloseWrite` to support half-close semantics before closing both ends.

## Risks And Test Signals
Risks include stalled goroutines, improper half-close behavior, backend dial failures, and listener close races. Integration is with Docker host-port publishing and TCP socket behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/cmd/docker-proxy/tcp_proxy_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/cmd/docker-proxy/udp_proxy_linux.go -->
# sources/cloud-native/moby/cmd/docker-proxy/udp_proxy_linux.go

## Purpose
Implements UDP forwarding for docker-proxy with per-client connection tracking and source-address preservation.

## APIs, Types, And Functions
Important types are `connTrackKey`, `connTrackMap`, `connTrackEntry`, and `UDPProxy`. Key functions are `newConnTrackKey`, `newConnTrackEntry`, `lastWrite`, `NewUDPProxy`, `replyLoop`, `Run`, `readDestFromCmsg`, and `Close`.

## Control Flow, State, And Integration
`Run` reads datagrams and packet-info control messages from the frontend listener. It creates a backend UDP connection per client address, stores it in `connTrackTable`, starts `replyLoop`, and writes incoming datagrams to the backend. Replies are sent back with control messages so the source address matches the host address the client targeted.

## Risks And Test Signals
Risks include conntrack leaks, lock ordering, ICMP port-unreachable retry behavior, packet-info parsing compatibility, timeout cleanup, and IPv4/IPv6 differences. Integration is with Linux UDP socket control messages and Docker port publishing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/cmd/docker-proxy/udp_proxy_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/cmd/docker-proxy/udp_proxy_linux_test.go -->
# sources/cloud-native/moby/cmd/docker-proxy/udp_proxy_linux_test.go

## Purpose
Tests that one-sided UDP traffic keeps conntrack entries alive while clients continue sending even if the backend does not reply.

## APIs, Types, And Functions
`TestUDPOneSided` exercises `NewUDPProxy`, `UDPProxy.Run`, `UDPProxy.Close`, `connTrackTimeout`, and UDP client/backend sockets.

## Control Flow, State, And Integration
The test creates a UDP proxy, sends repeated datagrams without backend replies, and checks connection tracking behavior across timeout windows. State under test is the proxy's `connTrackTable` and `lastW` timestamps.

## Risks And Test Signals
This catches premature conntrack garbage collection for write-only UDP flows. Timing sensitivity is the main risk, but the signal is important for UDP protocols that receive delayed or no replies.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/cmd/docker-proxy/udp_proxy_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/cmd/dockerd/main.go -->
# sources/cloud-native/moby/cmd/dockerd/main.go

## Purpose
Provides the main executable entrypoint for `dockerd`.

## APIs, Types, And Functions
The file defines `main`, using `reexec.Init`, terminal setup via `term.StdStreams`, signal-aware context setup, and `command.NewDaemonCli().Start`.

## Control Flow, State, And Integration
Startup first lets reexec subcommands run and return. The normal path creates a cancellable context tied to interrupt/SIGTERM, initializes standard streams, constructs the daemon CLI, starts dockerd, and exits nonzero on error.

## Risks And Test Signals
Risks include signal handling regressions, reexec behavior changes, stream setup errors, and failure to propagate daemon startup errors. Integration is with the full daemon command package and platform-specific process lifecycle.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/cmd/dockerd/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/cmd/dockerd/main_windows.go -->
# sources/cloud-native/moby/cmd/dockerd/main_windows.go

## Purpose
Pulls Windows resources into the dockerd binary on Windows builds.

## APIs, Types, And Functions
The file contains a blank import of `github.com/moby/moby/v2/cmd/dockerd/winresources`. It has no functions or runtime logic of its own.

## Control Flow, State, And Integration
The blank import ensures the package and its generated resource objects are linked when building Windows dockerd. State is build/link metadata rather than runtime state.

## Risks And Test Signals
Risks are build-time: removing or renaming the import can drop version info, icons, manifests, or event message resources from Windows binaries. Integration is with go-winres and Windows release packaging.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/cmd/dockerd/main_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/cmd/dockerd/winresources/Dockerfile -->
# sources/cloud-native/moby/cmd/dockerd/winresources/Dockerfile

## Purpose
Builds generated Windows event message resources for dockerd in a containerized cross-compilation environment.

## APIs, Types, And Functions
The Dockerfile uses `tonistiigi/xx` for cross tooling, Debian slim as the build stage, `xx-apt-get` to install binutils, and `x86_64-w64-mingw32-windmc` to compile `event_messages.mc` into `event_messages.bin`.

## Control Flow, State, And Integration
The build copies xx tooling into the build image, installs required packages, mounts the source resource directory, generates the event-message binary, and exports `/out` from a scratch stage. Build state is isolated to image layers.

## Risks And Test Signals
Risks include dependency tag drift, target platform mismatches, and generated resource incompatibility with Windows event logging. Integration is with Windows dockerd build automation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/cmd/dockerd/winresources/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/cmd/dockerd/winresources/event_messages.h -->
# sources/cloud-native/moby/cmd/dockerd/winresources/event_messages.h

## Purpose
Contains generated Windows message resource constants and documentation for event-message IDs.

## APIs, Types, And Functions
The file is a generated C header from `windmc`. It documents the 32-bit event identifier layout with severity, customer, reserved, facility, and code fields, and defines generated symbolic message IDs elsewhere in the header.

## Control Flow, State, And Integration
There is no runtime control flow; the header participates in Windows resource compilation. Its state is generated source that must match the `.mc` message definition and produced binary resources.

## Risks And Test Signals
Risks include manual edits, stale generated IDs, and mismatch between header and event message binary. Integration is with Windows Event Log resources for dockerd.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/cmd/dockerd/winresources/event_messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/cmd/dockerd/winresources/winresources.go -->
# sources/cloud-native/moby/cmd/dockerd/winresources/winresources.go

## Purpose
Declares the `winresources` package used to embed Windows resources into dockerd.

## APIs, Types, And Functions
The file has package documentation only and no exported functions. It describes resources for version information, icon, Windows manifest, and event message table.

## Control Flow, State, And Integration
The package is linked through blank imports and generated resource object files produced by build automation. It has build-time state rather than runtime behavior.

## Risks And Test Signals
Risks are packaging regressions where generated resource objects are missing or the package is not linked. Integration is with Windows binary metadata, manifest support, and event logging.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/cmd/dockerd/winresources/winresources.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/contrib/apparmor/main.go -->
# sources/cloud-native/moby/contrib/apparmor/main.go

## Purpose
Generates a Docker AppArmor profile file from the embedded template.

## APIs, Types, And Functions
The file defines `profileData` and `main`. It uses `text/template`, filesystem creation through `os.MkdirAll`, `os.OpenFile`, and the `dockerProfileTemplate` constant from `template.go`.

## Control Flow, State, And Integration
The command requires an output path argument, parses the template, creates the destination directory, truncates or creates the profile file, executes the template, and prints the created profile path. Persistent state is the AppArmor profile file under the target directory.

## Risks And Test Signals
Risks include writing to the wrong path, stale template permissions, and fatal exits on template or filesystem errors. Integration is with AppArmor tooling and distribution packaging of Docker profiles.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/contrib/apparmor/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/contrib/apparmor/template.go -->
# sources/cloud-native/moby/contrib/apparmor/template.go

## Purpose
Holds the AppArmor profile template used by the contrib generator.

## APIs, Types, And Functions
`dockerProfileTemplate` is a large raw string defining the `/usr/bin/docker` profile, child profiles for helper binaries, mount rules, signal and ptrace rules, capability permissions, network access, and profile transitions.

## Control Flow, State, And Integration
There is no Go control flow in this file. The string becomes the rendered AppArmor profile written by `contrib/apparmor/main.go` and loaded by system AppArmor tooling.

## Risks And Test Signals
Risks include over-permissive rules, denied legitimate Docker operations, outdated helper paths, and rootless/user-namespace path mismatches. Integration is with Linux AppArmor policy enforcement and Docker daemon/container setup behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/contrib/apparmor/template.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/contrib/busybox/Dockerfile -->
# sources/cloud-native/moby/contrib/busybox/Dockerfile

## Purpose
Builds a minimal BusyBox-based image artifact used by Moby contributors or tests.

## APIs, Types, And Functions
The Dockerfile stages fetch or assemble BusyBox filesystem content and configure the resulting image. Its API surface is Dockerfile instructions rather than code functions.

## Control Flow, State, And Integration
Build steps create image layers containing BusyBox utilities and metadata. State is the generated container image, which can be used as a compact test root filesystem or base image.

## Risks And Test Signals
Risks include upstream BusyBox source/image drift, architecture assumptions, and reproducibility of generated layers. Integration is with Docker build tooling and test fixtures that need a tiny Linux userspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/contrib/busybox/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/contrib/check-config.sh -->
# sources/cloud-native/moby/contrib/check-config.sh

## Purpose
Checks a Linux kernel configuration for Docker-relevant features and reports required, optional, and limit-related support.

## APIs, Types, And Functions
Important shell helpers include `is_set`, `is_set_in_kernel`, `is_set_as_module`, color/wrap helpers, `check_flag`, `check_flags`, `check_command`, `check_device`, `check_sysctl`, and `check_limit_over`.

## Control Flow, State, And Integration
The script chooses a kernel config path, provides `zgrep` fallback behavior, detects terminal color support, derives kernel version pieces, then checks kernel config symbols, commands, devices, sysctls, and cgroup/storage/networking capabilities. It reports to stdout and accumulates an exit code.

## Risks And Test Signals
Risks include stale kernel option lists, distro-specific config paths, false negatives for module support, and shell portability. Integration is with administrator diagnostics for Docker host readiness.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/contrib/check-config.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/contrib/dockerd-rootless-setuptool.sh -->
# sources/cloud-native/moby/contrib/dockerd-rootless-setuptool.sh

## Purpose
Installs, checks, and uninstalls rootless Docker user services and CLI context configuration for non-root users.

## APIs, Types, And Functions
Important functions include `INFO`, `WARNING`, `ERROR`, `init`, `cmd_entrypoint_check`, `cmd_entrypoint_nsenter`, `show_systemd_error`, `install_systemd`, `install_nonsystemd`, `cli_ctx_exists`, `cli_ctx_create`, `cli_ctx_use`, `cli_ctx_rm`, `cmd_entrypoint_install`, `cmd_entrypoint_uninstall`, and `usage`.

## Control Flow, State, And Integration
`init` validates Linux, non-root execution, PATH, HOME, XDG runtime state, subuid/subgid, and optional systemd support. Install paths create systemd user units or non-systemd shell instructions, manage Docker CLI contexts, and respect force/iptables flags. Persistent state includes user systemd units, CLI contexts, runtime dirs, and shell environment guidance.

## Risks And Test Signals
Risks include privilege confusion, bad systemd user environment, stale contexts, iptables limitations, and incomplete cleanup. Integration is with `dockerd-rootless.sh`, RootlessKit, systemd user services, and Docker CLI context management.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/contrib/dockerd-rootless-setuptool.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/contrib/dockerd-rootless.sh -->
# sources/cloud-native/moby/contrib/dockerd-rootless.sh

## Purpose
Launches `dockerd` in rootless mode through RootlessKit with selected network, port, mount, and namespace settings.

## APIs, Types, And Functions
The script exposes environment-driven configuration such as RootlessKit state dir, network driver, MTU, port driver, slirp4netns sandbox/seccomp flags, host loopback policy, and detach-netns mode. `mount_directory` is a key helper for child-context bind mounts.

## Control Flow, State, And Integration
The script validates writable `XDG_RUNTIME_DIR` and `HOME`, prevents setup-tool subcommands from being misrouted, selects available network/port drivers, configures RootlessKit arguments, mounts necessary directories, and execs dockerd in a rootless namespace. Persistent/runtime state lives under the RootlessKit state dir and user Docker data paths.

## Risks And Test Signals
Risks include environment misconfiguration, unavailable helpers, network-driver compatibility, leaked mounts, and security tradeoffs around host loopback or detach-netns. Integration is with RootlessKit, slirp4netns, pasta, vpnkit, gvisor-tap-vsock, and dockerd rootless mode.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/contrib/dockerd-rootless.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/contrib/dockerize-disk.sh -->
# sources/cloud-native/moby/contrib/dockerize-disk.sh

## Purpose
Converts a disk image into a Docker image layer set, optionally diffing against a base image.

## APIs, Types, And Functions
The shell functions are `usage` and `cleanup`. The script depends on `qemu-nbd`, kernel `nbd`, `mount`, `aufs`, Docker CLI operations, `tar`, `diff`, and shell processing of add/update/delete entries.

## Control Flow, State, And Integration
The script parses image name/tag, attaches the disk image read-only via NBD, mounts it, optionally unpacks base image layers, mounts an AUFS workdir, diffs disk and workdir contents, and builds Docker image metadata/layers. Cleanup unmounts and detaches NBD on exit.

## Risks And Test Signals
Risks are high because it requires root, NBD devices, AUFS, and destructive mount cleanup. Integration is with legacy image-format assembly and host kernel storage drivers; failures can leave mounts or NBD devices attached.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/contrib/dockerize-disk.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/contrib/download-frozen-image-v2.sh -->
# sources/cloud-native/moby/contrib/download-frozen-image-v2.sh

## Purpose
Downloads Docker Registry v2 image manifests and blobs into a frozen archive layout for CI and educational use.

## APIs, Types, And Functions
Important helpers include `usage`, `fetch_blob`, `handle_single_manifest_v2`, `get_target_arch`, and `get_target_variant`. The script depends on `curl`, `jq`, registry auth tokens, manifest lists, schema v2 manifests, and Bash arrays.

## Control Flow, State, And Integration
The script validates tools, parses target directory and image references, obtains registry tokens, fetches manifests and blobs, handles architecture/variant selection, writes layer/config files, and assembles repository/tag metadata unless disabled. Persistent state is the frozen image directory tree and temporary tag files.

## Risks And Test Signals
Risks include registry API drift, auth failures, digest mismatch, Bash version portability, platform selection mistakes, and partial downloads. Integration is with Docker Hub registry APIs and CI fixtures that need pre-fetched images.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/contrib/download-frozen-image-v2.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/contrib/init/systemd/docker.service -->
# sources/cloud-native/moby/contrib/init/systemd/docker.service

## Purpose
Defines a systemd service unit for running dockerd.

## APIs, Types, And Functions
The unit declares dependencies on network, Docker socket, firewalld, containerd, and time synchronization. Service settings include `Type=notify`, `ExecStart=/usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock`, reload by HUP, restart policy, resource limits, `Delegate=yes`, `KillMode=process`, and `OOMScoreAdjust=-500`.

## Control Flow, State, And Integration
Systemd starts dockerd through socket activation, expects readiness notification, restarts on failure, and delegates cgroup management so containers are not reset by systemd. Persistent state is systemd unit configuration and dockerd runtime behavior under systemd.

## Risks And Test Signals
Risks include dependency ordering issues, cgroup delegation regressions, socket activation mismatch, and distro systemd compatibility. Integration is with containerd and Docker socket units.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/contrib/init/systemd/docker.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/contrib/init/systemd/docker.socket -->
# sources/cloud-native/moby/contrib/init/systemd/docker.socket

## Purpose
Defines the systemd socket unit for Docker API socket activation.

## APIs, Types, And Functions
The socket listens on `/run/docker.sock`, sets mode `0660`, owner `root`, and group `docker`, and installs into `sockets.target`.

## Control Flow, State, And Integration
Systemd creates and owns the Unix socket before dockerd starts. The service unit consumes it via `-H fd://`. Persistent state is the enabled socket unit and socket filesystem node.

## Risks And Test Signals
Risks include incorrect socket path on systems where `/var/run` is not `/run`, group permission exposure, and service/socket mismatch. Integration is with Docker CLI access and systemd socket activation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/contrib/init/systemd/docker.socket -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/contrib/init/sysvinit-debian/docker -->
# sources/cloud-native/moby/contrib/init/sysvinit-debian/docker

## Purpose
Provides a Debian-style SysV init script for starting, stopping, restarting, and checking dockerd.

## APIs, Types, And Functions
The script defines LSB metadata, configurable variables such as `DOCKERD`, pid files, logfile, and `DOCKER_OPTS`, plus `fail_unless_root` and case handlers for `start`, `stop`, `restart`, `force-reload`, and `status`.

## Control Flow, State, And Integration
On start, it validates root and executable presence, prepares the log file, raises limits, and invokes `start-stop-daemon` with dockerd pidfile arguments. Stop and status use pid files and LSB helper functions. Persistent state includes pid files and `/var/log/docker.log`.

## Risks And Test Signals
Risks include stale pid files, permission issues, shell differences for ulimit behavior, and outdated init assumptions. Integration is with Debian LSB init and `/etc/default/docker`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/contrib/init/sysvinit-debian/docker -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/contrib/init/sysvinit-redhat/docker -->
# sources/cloud-native/moby/contrib/init/sysvinit-redhat/docker

## Purpose
Provides a Red Hat-style SysV init script for dockerd.

## APIs, Types, And Functions
The script defines chkconfig metadata, paths for `unshare`, `dockerd`, pidfile, lockfile, logfile, and optional `/etc/sysconfig/docker` settings. Functions include `prestart`, `start`, `stop`, `restart`, `reload`, `force_reload`, status helpers, and `check_for_cleanup`.

## Control Flow, State, And Integration
Start verifies executability, cleans stale pid files, starts cgconfig if needed, launches dockerd in a new mount namespace via `unshare -m`, waits for the pidfile, and writes lock/log state. Stop uses `killproc` and removes the lock on success.

## Risks And Test Signals
Risks include stale pid handling, cgconfig dependency failures, mount namespace assumptions, fixed paths, and log growth. Integration is with Red Hat service management and `/etc/sysconfig/docker`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/contrib/init/sysvinit-redhat/docker -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/contrib/nnp-test/Dockerfile -->
# sources/cloud-native/moby/contrib/nnp-test/Dockerfile

## Purpose
Builds a small image for testing Linux no-new-privileges behavior.

## APIs, Types, And Functions
The Dockerfile compiles or packages `nnp-test.c` into a container image. Its interface is the resulting test executable image rather than a code API.

## Control Flow, State, And Integration
Build steps create an image containing the no-new-privileges test binary and any minimal runtime dependencies. The produced image is used to verify security-option behavior at container runtime.

## Risks And Test Signals
Risks include compiler/base-image drift and mismatched file capabilities or setuid expectations. Integration is with Docker security option tests around `no-new-privileges`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/contrib/nnp-test/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/contrib/nnp-test/nnp-test.c -->
# sources/cloud-native/moby/contrib/nnp-test/nnp-test.c

## Purpose
Provides a tiny C program used to observe whether privilege elevation is blocked under no-new-privileges.

## APIs, Types, And Functions
The file contains a minimal `main`-style program that reports or exits based on effective identity behavior. It uses standard C and Unix process credential APIs.

## Control Flow, State, And Integration
The program runs inside a container and checks runtime privilege state. It persists no state; its exit code/output is the signal consumed by tests or manual checks.

## Risks And Test Signals
Risks include platform assumptions, setuid/capability setup differences, and too-simple diagnostics. Integration is with Docker runtime security options and the accompanying Dockerfile image.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/contrib/nnp-test/nnp-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/contrib/nuke-graph-directory.sh -->
# sources/cloud-native/moby/contrib/nuke-graph-directory.sh

## Purpose
Safely destroys an old Docker graph directory by unmounting submounts and deleting btrfs subvolumes before removing files.

## APIs, Types, And Functions
The key helper is `dir_in_dir`. The script uses `readlink`, `/proc/self/mountinfo`, `umount -f`, optional `btrfs subvolume delete`, `find`, `stat`, shell globbing, and `rm -rf`.

## Control Flow, State, And Integration
The script requires a directory argument and root privileges, canonicalizes the target, prints a warning with a delay, unmounts nested mount points, deletes nested btrfs subvolumes, then removes all contents of the target directory.

## Risks And Test Signals
Risk is intentionally high because the script is destructive. Its safety controls are root check, canonicalization, delay, mount unrolling, and targeting contents rather than blindly crossing mount boundaries. Integration is with legacy Docker data-root cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/contrib/nuke-graph-directory.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/contrib/otel/compose.yaml -->
# sources/cloud-native/moby/contrib/otel/compose.yaml

## Purpose
Defines a local OpenTelemetry observation stack for Moby development.

## APIs, Types, And Functions
The Compose project `moby-otel` defines services for Jaeger all-in-one, Aspire dashboard, and OpenTelemetry Collector. It exposes Jaeger UI on 16686, Aspire dashboard on 18888, and OTLP HTTP on 4318.

## Control Flow, State, And Integration
Compose starts the tracing backends, makes the collector depend on dashboards, and uses a develop watch rule to sync and restart the collector when `otelcol.yaml` changes. State is service containers and collected trace data.

## Risks And Test Signals
Risks include `latest` image drift, unsecured dashboard access, host port conflicts, and collector config syntax issues. Integration is with Moby OTLP HTTP trace emission.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/contrib/otel/compose.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/contrib/otel/otelcol.yaml -->
# sources/cloud-native/moby/contrib/otel/otelcol.yaml

## Purpose
Configures OpenTelemetry Collector to receive Moby traces and export them to Jaeger and Aspire.

## APIs, Types, And Functions
The config declares an OTLP receiver over gRPC on 4317 and HTTP on 4318, OTLP exporters for `jaeger:4317` and `aspire-dashboard:18889`, and a traces pipeline connecting receiver to both exporters.

## Control Flow, State, And Integration
At runtime the collector accepts trace signals, routes them through the traces pipeline, and forwards them to the configured backends. State is in-memory collector processing and backend storage.

## Risks And Test Signals
Risks include endpoint mismatches, TLS option syntax errors, and backend protocol incompatibility. Integration is with the companion Compose stack and Moby tracing configuration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/contrib/otel/otelcol.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/contrib/syscall-test/Dockerfile -->
# sources/cloud-native/moby/contrib/syscall-test/Dockerfile

## Purpose
Builds small syscall test binaries used for validating seccomp and namespace behavior.

## APIs, Types, And Functions
The Dockerfile compiles C and assembly sources such as `acct.c`, `ns.c`, `raw.c`, `socket.c`, `userns.c`, `setuid.c`, `setgid.c`, and `exit32.s` into runnable test programs.

## Control Flow, State, And Integration
Build steps produce an image containing individual syscall probes. Runtime tests execute those probes under different Docker security profiles and inspect exit codes or syscall denials.

## Risks And Test Signals
Risks include compiler/architecture assumptions, 32-bit assembly support, and kernel syscall availability. Integration is with seccomp profile validation and container security regression tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/contrib/syscall-test/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/contrib/syscall-test/acct.c -->
# sources/cloud-native/moby/contrib/syscall-test/acct.c

## Purpose
Exercises the Linux `acct` syscall for security-profile testing.

## APIs, Types, And Functions
The C program calls the accounting syscall or libc wrapper against a temporary path such as `/tmp/t`. It uses standard Unix headers and returns process exit status as the test signal.

## Control Flow, State, And Integration
At runtime the program attempts process accounting setup from inside a container. It may touch a temporary file path but has no durable intended state. The result indicates whether the syscall is allowed or blocked.

## Risks And Test Signals
Risks include requiring privileges or kernel support and interpreting EPERM correctly. Integration is with Docker seccomp/default profile checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/contrib/syscall-test/acct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/contrib/syscall-test/exit32.s -->
# sources/cloud-native/moby/contrib/syscall-test/exit32.s

## Purpose
Provides a minimal 32-bit assembly program that exits via a raw syscall.

## APIs, Types, And Functions
The assembly defines the entry sequence for a 32-bit Linux exit syscall. It has no C-level functions.

## Control Flow, State, And Integration
Execution enters the assembly entry point, loads syscall registers, invokes the kernel, and exits. It persists no state and is used only for architecture/syscall behavior checks.

## Risks And Test Signals
Risks include architecture incompatibility, assembler/toolchain availability, and host kernels without 32-bit syscall support. Integration is with seccomp and compatibility testing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/contrib/syscall-test/exit32.s -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/contrib/syscall-test/ns.c -->
# sources/cloud-native/moby/contrib/syscall-test/ns.c

## Purpose
Exercises namespace-related syscalls for Docker security profile validation.

## APIs, Types, And Functions
The C file uses Linux namespace APIs such as clone, unshare, or setns style calls through system headers. Its process exit result indicates whether the syscall path was allowed.

## Control Flow, State, And Integration
The program attempts namespace operations from inside a container and exits based on success or failure. Runtime state is limited to attempted namespace changes in the process.

## Risks And Test Signals
Risks include kernel capability requirements, seccomp blocking, and host configuration differences. Integration is with tests for namespace isolation and default syscall policy.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/contrib/syscall-test/ns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/contrib/syscall-test/raw.c -->
# sources/cloud-native/moby/contrib/syscall-test/raw.c

## Purpose
Exercises raw socket creation or related raw networking syscalls for security testing.

## APIs, Types, And Functions
The C program uses socket/syscall headers to attempt a privileged raw operation and returns status for test assertions.

## Control Flow, State, And Integration
At runtime it invokes the raw operation inside the container and exits. It does not persist state, but may require or be denied network capabilities.

## Risks And Test Signals
Risks include host capability differences and expected EPERM/seccomp outcomes. Integration is with Docker networking capability and seccomp default-profile validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/contrib/syscall-test/raw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/contrib/syscall-test/setgid.c -->
# sources/cloud-native/moby/contrib/syscall-test/setgid.c

## Purpose
Tests `setgid` behavior inside a container for security and syscall policy validation.

## APIs, Types, And Functions
The C program calls a group-ID changing API such as `setgid` and reports success or failure through its exit code.

## Control Flow, State, And Integration
Execution attempts to change the process group identity. Any state change is limited to the running process credentials and disappears at exit.

## Risks And Test Signals
Risks include capability-dependent behavior and mismatched expectations across root/rootless containers. Integration is with seccomp, capabilities, and user namespace tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/contrib/syscall-test/setgid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/contrib/syscall-test/setuid.c -->
# sources/cloud-native/moby/contrib/syscall-test/setuid.c

## Purpose
Tests `setuid` behavior inside a container for security and syscall policy validation.

## APIs, Types, And Functions
The C program calls a user-ID changing API such as `setuid` and exposes the result via process exit status.

## Control Flow, State, And Integration
The program attempts to change its process user identity and exits. State is process-local credential state only.

## Risks And Test Signals
Risks include capability and user-namespace differences causing different legitimate results. Integration is with Docker default capabilities and seccomp policy tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/contrib/syscall-test/setuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/contrib/syscall-test/socket.c -->
# sources/cloud-native/moby/contrib/syscall-test/socket.c

## Purpose
Exercises socket syscalls for container security-profile validation.

## APIs, Types, And Functions
The C program uses socket-related system headers and attempts to create or use a socket type selected for policy testing.

## Control Flow, State, And Integration
At runtime it performs the socket operation, exits with status reflecting success or denial, and persists no state beyond any transient descriptor.

## Risks And Test Signals
Risks include kernel/network namespace variation and capability requirements. Integration is with Docker seccomp and network capability policy tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/contrib/syscall-test/socket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/contrib/syscall-test/userns.c -->
# sources/cloud-native/moby/contrib/syscall-test/userns.c

## Purpose
Exercises user-namespace creation or entry behavior for security testing.

## APIs, Types, And Functions
The C program uses Linux namespace syscalls and user namespace constants through system headers, reporting results via exit status.

## Control Flow, State, And Integration
The program attempts user namespace operations inside a container. State is process namespace membership and credential mapping behavior for the lifetime of the process.

## Risks And Test Signals
Risks include host sysctl restrictions, rootless differences, seccomp blocks, and kernel version differences. Integration is with Docker user namespace and default security policy tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/contrib/syscall-test/userns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/contrib/systemd-sysusers/docker.conf -->
# sources/cloud-native/moby/contrib/systemd-sysusers/docker.conf

## Purpose
Defines systemd-sysusers configuration for creating the Docker group.

## APIs, Types, And Functions
The config uses sysusers syntax to declare a `docker` group entry with no fixed numeric ID unless assigned by the system.

## Control Flow, State, And Integration
At package install or boot, `systemd-sysusers` reads the file and ensures the group exists. Persistent state is the system group database entry.

## Risks And Test Signals
Risks include unintended API socket access for members of the docker group and distro-specific group policy. Integration is with Docker socket permissions and packaging.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/contrib/systemd-sysusers/docker.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/contrib/wireshark/memberlist.lua -->
# sources/cloud-native/moby/contrib/wireshark/memberlist.lua

## Purpose
Implements a Wireshark Lua dissector for HashiCorp memberlist protocol traffic used by Moby networking components.

## APIs, Types, And Functions
The script defines `memberlist_protocol`, protocol fields for message type, CRC, label, encryption, compression, compound parts, and user data, preferences for ports, keylog path, and user-data dissector, plus functions such as `dissect_userdata`, `try_decrypt`, and `memberlist_protocol.dissector`. It also inlines msgpack, LZW, and CRC32 helper code.

## Control Flow, State, And Integration
The dissector registers TCP/UDP ports, optionally decrypts AES-GCM messages using keys from a preference file, validates CRC wrappers, decodes labels, compound messages, push/pull msgpack payloads, compression wrappers, and delegates user payloads to another dissector when configured. State is Wireshark preference state and keylog file contents.

## Risks And Test Signals
Risks include malformed packet handling, keylog file trust, crypto API availability, recursive dissector bugs, and protocol drift. Integration is with Wireshark Lua APIs, protobuf/msgpack dissectors, and Moby network gossip analysis.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/contrib/wireshark/memberlist.lua -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/contrib/wireshark/moby-networkdb.lua -->
# sources/cloud-native/moby/contrib/wireshark/moby-networkdb.lua

## Purpose
Adds Wireshark protobuf decode helpers for Moby NetworkDB gossip payloads.

## APIs, Types, And Functions
The script uses the protobuf dissector, `Field.new` accessors for gossip message type/data and table event names, `last_fieldinfo`, `gossip_proto.dissector`, and `tableevent_proto.dissector`. It registers decode hooks in the `protobuf_field` dissector table.

## Control Flow, State, And Integration
The gossip dissector first decodes a generic `networkdb.GossipMessage`, reads the last parsed type/data fields, chooses a concrete protobuf message type from a map, and recursively decodes the data field. Table events similarly decode values based on table name such as overlay peer or endpoint records.

## Risks And Test Signals
Risks include protobuf field-name drift, missing generated protobuf descriptors in Wireshark, recursive decode failures, and malformed field offsets. Integration is with the memberlist user-data dissector path and Moby overlay/networkdb debugging.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/contrib/wireshark/moby-networkdb.lua -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/apparmor_default.go -->
# sources/cloud-native/moby/daemon/apparmor_default.go

## Purpose
Implements Linux default AppArmor profile naming, support checks, and installation for the daemon.

## APIs, Types, And Functions
The file defines `unconfinedAppArmorProfile`, `defaultAppArmorProfile`, `DefaultApparmorProfile`, `loadDefaultAppArmorProfileIfMissing`, `installDefaultAppArmorProfile`, and `defaultAppArmorProfileSupported`. It uses `github.com/moby/profiles/apparmor` and rootless detached-netns detection.

## Control Flow, State, And Integration
`DefaultApparmorProfile` returns `docker-default` only when AppArmor is supported. Loading checks whether the default profile is already present, installs it if missing, and skips support in rootless detached-netns mode because AppArmor sysfs is inaccessible. Persistent state is the loaded kernel AppArmor profile.

## Risks And Test Signals
Risks include false support detection, failure to load profiles on AppArmor-enabled hosts, and rootless detached namespace permission errors. Integration is with container default security profiles and host LSM state.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/apparmor_default.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/apparmor_default_unsupported.go -->
# sources/cloud-native/moby/daemon/apparmor_default_unsupported.go

## Purpose
Provides non-Linux fallback implementations for default AppArmor profile functions.

## APIs, Types, And Functions
The file defines `loadDefaultAppArmorProfileIfMissing`, `DefaultApparmorProfile`, and `installDefaultAppArmorProfile` for `!linux` builds.

## Control Flow, State, And Integration
All functions are no-ops or return an empty profile name. No profile state is loaded or persisted on unsupported platforms.

## Risks And Test Signals
Risks are low but important for cross-platform builds: callers must tolerate an empty default profile. Integration is with shared daemon code that references AppArmor helpers without platform conditionals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/apparmor_default_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/apparmor_linux.go -->
# sources/cloud-native/moby/daemon/apparmor_linux.go

## Purpose
Detects whether AppArmor is supported and accessible on Linux.

## APIs, Types, And Functions
The file defines `appArmorSupported`, using containerd's AppArmor host support probe and Moby rootless detached-netns detection.

## Control Flow, State, And Integration
The function first rejects detached rootless network namespace mode because AppArmor sysfs is netns-scoped and inaccessible, then delegates to `apparmor.HostSupports`. It reads host/kernel state but does not mutate it.

## Risks And Test Signals
Risks include false negatives in rootless configurations and host probe behavior changes. Integration is with default profile selection and daemon security option setup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/apparmor_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/apparmor_unsupported.go -->
# sources/cloud-native/moby/daemon/apparmor_unsupported.go

## Purpose
Provides unsupported-platform fallback for AppArmor support detection.

## APIs, Types, And Functions
The file defines `appArmorSupported` for non-AppArmor build targets, returning false.

## Control Flow, State, And Integration
There is no runtime probing. Shared daemon code can call the function safely and receive an unsupported result.

## Risks And Test Signals
Risk is limited to ensuring build tags select the correct implementation. Integration is with cross-platform daemon security configuration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/apparmor_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/archive.go -->
# sources/cloud-native/moby/daemon/archive.go

## Purpose
Provides public daemon methods for statting, archiving, and extracting paths in container filesystems with consistent error translation.

## APIs, Types, And Functions
The methods are `Daemon.ContainerStatPath`, `Daemon.ContainerArchivePath`, and `Daemon.ContainerExtractToDir`. They use `GetContainer`, platform-specific helpers, container `PathStat`, `io.Reader`/`ReadCloser`, container-file not-found errors, and Moby/containerd errdefs.

## Control Flow, State, And Integration
Each method resolves the container, delegates to lower-level filesystem helpers, maps `os.IsNotExist` to container-aware not-found errors, preserves invalid-argument errors, and wraps other failures as system errors. Extraction can mutate container filesystem state; stat and archive read it.

## Risks And Test Signals
Risks include incorrect error classification, path traversal or symlink behavior in lower helpers, archive stream lifetime, and destructive extraction. Integration is with Docker `cp`, archive API endpoints, event logging, and container filesystem mounts.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/archive.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/archive_tarcopyoptions.go -->
# sources/cloud-native/moby/daemon/archive_tarcopyoptions.go

## Purpose
Provides the default tar extraction options used by container archive copy operations.

## APIs, Types, And Functions
`Daemon.defaultTarCopyOptions` returns an `archive.TarOptions` configured from `allowOverwriteDirWithFile`, primarily controlling `NoOverwriteDirNonDir`.

## Control Flow, State, And Integration
The function creates option structs and persists no state. It is called by extraction paths when user/group ownership copying is not requested or as a base behavior.

## Risks And Test Signals
Risks include changing overwrite semantics and accidentally allowing directory/file replacement in unsafe cases. Integration is with `ContainerExtractToDir` and `go-archive` untar behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/archive_tarcopyoptions.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/archive_tarcopyoptions_unix.go -->
# sources/cloud-native/moby/daemon/archive_tarcopyoptions_unix.go

## Purpose
Adds Unix-specific tar copy options that honor the container configured user and group when extracting archives.

## APIs, Types, And Functions
Important functions are `Daemon.tarCopyOptions`, `getUIDGID`, `getIDOrName`, `lookupUser`, and `lookupGID`. They use `github.com/moby/sys/user`, numeric parsing, and `archive.ChownOpts`.

## Control Flow, State, And Integration
If the container has no configured user, default tar options are used. Otherwise the user string is split into user/group parts, numeric IDs or names are resolved against the container filesystem context, and tar options include chown settings. Empty user or group pieces default to root-aligned behavior.

## Risks And Test Signals
Risks include mismatching `docker run --user` semantics, UID/GID overflow, failed name lookup, and incorrect ownership on copied files. Integration is with Unix container `/etc/passwd`/`group` resolution and archive extraction.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/archive_tarcopyoptions_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/archive_unix.go -->
# sources/cloud-native/moby/daemon/archive_unix.go

## Purpose
Implements Unix container filesystem stat, archive, and extraction helpers for Docker copy APIs.

## APIs, Types, And Functions
Key functions are `containerStatPath`, `containerArchivePath`, `containerExtractToDir`, and `checkWritablePath`. Dependencies include `openContainerFS`, `go-archive`, compression helpers, `ioutils.NewReadCloserWrapper`, container mount parsing, event logging, and Moby errdefs.

## Control Flow, State, And Integration
Stat locks the container, opens its filesystem, and stats the target path. Archive locks the container for the lifetime of the returned reader, rebases tar paths, runs tarball creation inside the container filesystem, and logs an archive event. Extraction decompresses before entering the container filesystem, resolves symlinks, verifies a directory and writability, selects tar options, untars content, and logs an extract event.

## Risks And Test Signals
Risks include lock lifetime tied to stream closure, symlink/path traversal mistakes, executing decompression helpers inside container context, read-only volume/rootfs checks, and archive overwrite semantics. Integration is with Docker `cp`, volume mount metadata, container events, and Unix filesystem isolation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/archive_unix.go -->
