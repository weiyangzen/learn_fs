# sources/control-plane/external-snapshotter/pkg/utils/util.go

Purpose: shared utility surface for snapshot controllers: constants for annotations/finalizers/CSI parameter keys, cache version handling, name/key helpers, secret template resolution, credential loading, deletion/finalizer predicates, parameter filtering, logging status helpers, readiness predicates, and content update enqueue filtering.

Important APIs/types/functions: `secretParamsMap`; secret parameter maps for snapshot, group snapshot, list, and get operations; finalizer and annotation constants; `StoreObjectUpdate`; `GetSecretReference`; `GetGroupSnapshotSecretReference`; `GetCredentials`; `RemovePrefixedParameters`; finalizer predicates; ready/bound/created predicates; dynamic content-name functions; and `ShouldEnqueueContentChange`.

Control flow: cache updates compare numeric `ResourceVersion` values and reject older objects. Secret reference resolution requires name and namespace templates as a pair, expands whitelisted tokens, validates DNS names, and returns nil when no secret is configured. Credential loading reads Kubernetes secrets into string maps. Parameter filtering strips known reserved `csi.storage.k8s.io/*` keys and rejects unknown reserved keys. Enqueue filtering normalizes status, finalizers, managed fields, resource version, and sidecar-owned annotations before deep equality, while always allowing resyncs and ready transitions.

State and persistence: stateless except for reading Kubernetes secrets and returning data for callers to persist. Constants define durable API annotations/finalizers used across controllers.

Dependencies and integration: integrates core Kubernetes API types, snapshot/group snapshot CRDs, client-go caches and clients, validation helpers, semantic equality, klog, and set utilities. The sidecar and common controllers rely on these helpers for safe event filtering and CRD metadata conventions.

Risks and test signals: risks include token-template restrictions surprising users, reserved parameter drift, string-based credential conversion, resource-version parse assumptions, and enqueue filtering hiding meaningful changes if sanitization expands too far. Tests cover slice removal, secret template success/failure, prefixed parameter filtering, default-class annotations, and many enqueue-filter cases.
