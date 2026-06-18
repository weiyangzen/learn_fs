# sources/control-plane/rook/pkg/operator/k8sutil/endpoint.go

Purpose: create-or-update helper for Kubernetes `EndpointSlice` resources.

Important APIs/types/functions: `CreateOrUpdateEndpointSlice`.

Control flow: attempts to create the given EndpointSlice in the target namespace. On AlreadyExists, updates the full provided definition. Non-AlreadyExists create errors and update errors are wrapped with endpoint slice name context.

State and persistence behavior: writes EndpointSlice objects through the discovery v1 client.

Dependencies/integration: client-go DiscoveryV1 EndpointSlices, Kubernetes API error helpers, and k8sutil logger.

Risks: update uses the provided object directly, so callers must ensure resourceVersion and desired metadata are valid for updates. No conflict retry. Namespace is a separate parameter even though the object also has a namespace field; mismatches could be confusing.

Test signals: no direct tests in this subset.
