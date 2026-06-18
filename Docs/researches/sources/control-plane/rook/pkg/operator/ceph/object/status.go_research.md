# sources/control-plane/rook/pkg/operator/ceph/object/status.go

Purpose: this file manages `CephObjectStore` status updates and endpoint status-info construction. It turns reconcile outcomes into CR status phase, endpoint lists, selector strings, observed generation, replica counts, optional CephX daemon status, and user-facing endpoint info.

Important APIs and functions: `replicaCountNotAvailable` is a sentinel used to avoid overwriting replica count. `setFailedStatus` updates the object store to `ConditionFailure` and returns the original reconcile error wrapped with context. `updateStatus` performs the status write. `buildStatusInfo` builds the legacy/status `Info` map, primarily `endpoint` and sometimes `secureEndpoint`.

Control flow: `updateStatus` uses `retry.RetryOnConflict` to refetch the `CephObjectStore`, initialize status if absent, skip status mutation if the current phase is `Deleting`, set phase/info/replicas/selector/observed generation, recompute insecure and secure DNS endpoints from gateway ports, copy supplied CephX daemon status, and call `reporting.UpdateStatus`. Not-found resources are ignored because deletion is assumed. `buildStatusInfo` asks the CR for its advertise endpoint URL; an explicitly configured advertise endpoint takes precedence over service DNS endpoints and is the only endpoint reported.

State and persistence behavior: this code persists only the CR status subresource through the controller-runtime client and Rook reporting helper. It derives status endpoints from the current spec at update time, so gateway port changes are reflected whenever status is refreshed. It intentionally avoids changing status after a delete phase begins.

Dependencies and integration points: it integrates with `cephv1.ObjectStoreStatus`, Rook status reporting, controller labels via `getLabels`, endpoint builders such as `getAllDNSEndpoints`, `BuildDNSEndpoint`, and `GetStableDomainName`, Kubernetes conflict retry helpers, and `k8sutil.ObservedGenerationNotAvailable`.

Risks: status updates are best-effort but return errors after retries. If status is nil, endpoint slices are initialized empty; if ports are zero, endpoint slices are cleared. `buildStatusInfo` logs and continues if advertise endpoint URL construction fails, which can hide a validation gap but avoids breaking reconcile late. The delete-phase guard can leave stale status fields by design.

Test signals: `status_test.go` covers `buildStatusInfo` for HTTP, HTTPS, dual-port, and advertiseEndpoint cases. `updateStatus` and `setFailedStatus` do not have direct tests in this subset, so conflict handling, delete-phase preservation, CephX status copying, and endpoint slice recomputation rely on broader controller coverage or are residual risk.
