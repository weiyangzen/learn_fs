# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/env.go

## Purpose

This file centralizes Kubernetes environment variable definitions that expose monitor namespace, monitor endpoint data, and Ceph username credentials to Rook sidecars and daemons.

## Important APIs and Behavior

`PodNamespaceEnvVar(namespace)` returns `ROOK_POD_NAMESPACE` with a literal namespace value. `EndpointEnvVar()` returns `ROOK_MON_ENDPOINTS` sourced from the `rook-ceph-mon-endpoints` ConfigMap `data` key. `CephUsernameEnvVar()` returns `ROOK_CEPH_USERNAME` sourced from the `rook-ceph-mon` Secret key identified by `controller.CephUsernameKey`.

## State, Persistence, and Dependencies

The file does not persist state. Its env var definitions depend on persisted ConfigMap and Secret objects created by monitor reconciliation and cluster access-secret management. Consumers include the mgr active watcher sidecar and other components that need live mon endpoint and username values without embedding them into pod specs.

## Risks and Test Signals

Incorrect object names or keys would cause pods to start with missing env vars or fail admission depending on Kubernetes behavior. The helpers reduce duplication, but coverage is indirect through pod spec tests that assert these env vars are present in sidecar containers.
