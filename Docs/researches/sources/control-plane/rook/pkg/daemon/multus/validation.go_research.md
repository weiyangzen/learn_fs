# sources/control-plane/rook/pkg/daemon/multus/validation.go

Purpose: implements the public Multus validation test orchestration and all concrete validation state-machine states.

Important APIs/types/functions: `ValidationTest` combines a Kubernetes client, logger, and `ValidationTestConfig`. `ValidationTestResults` stores debugging suggestions and renders `SuggestedDebuggingReport()`. States include `getExpectedNumberOfImagePullPodsState`, `ensureNodeTypesDoNotOverlapState`, reusable `verifyAllPodsRunningState`, `deleteImagePullersState`, `getWebServerInfoState`, `startHostCheckersState`, `verifyAllHostCheckersReadyState`, `deleteHostCheckersState`, `startClientsState`, and `verifyAllClientsReadyState`. Public methods are `Run()` and `CleanUp()`.

Control flow: `Run()` validates config, short-circuits host-check-only mode when no public network is configured, creates the owner ConfigMap, starts the web server and image pullers, then starts the state machine. The state machine stabilizes expected image-puller counts, verifies non-overlapping node types, waits for image pullers, deletes them, discovers web server Multus addresses, optionally starts host checkers, validates host reachability, starts Multus clients, waits for Running then Ready, and exits. Client readiness timing is tracked to flag flaky networks when readiness spreads beyond `FlakyThreshold`.

State and persistence behavior: Kubernetes resources are persisted during a run via helpers in `resources.go`, and in-memory state carries expected counts, web server network info, and suggestion history. Cleanup delegates to owner ConfigMap deletion. Suggestions describe likely root causes and are returned whether the test fails or succeeds with flakiness.

Dependencies and integration points: depends on Kubernetes client-go, `types.NamespacedName`, templates/resources helpers, network parsing helpers, and config validation. Intended callers can use the library with their own logger or default stderr logger.

Risks: the workflow is sensitive to accurate DaemonSet scheduled counts and timing thresholds. Fixed owner resource names prevent concurrent tests in one namespace. Some errors call `Exit()` immediately while others keep polling; incorrect classification can either fail too early or wait until timeout. `podSchedulerDebounceTime` must remain below state timeout. Flakiness detection starts when ready count first increases and may warn even when slow scheduling, not network, is the cause.

Test signals: this subset has no direct tests for the full state machine. Related tests cover config, count helpers, and templates indirectly, leaving resource orchestration and suggestion paths mostly integration-tested.
