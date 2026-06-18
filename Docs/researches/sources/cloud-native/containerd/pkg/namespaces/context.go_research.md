# sources/cloud-native/containerd/pkg/namespaces/context.go

Purpose: carries containerd namespace identity through contexts, environment defaults, and RPC metadata.

Important APIs/types/functions: constants `NamespaceEnvVar = "CONTAINERD_NAMESPACE"` and `Default = "default"`; private `namespaceKey`; `WithNamespace` stores the namespace in context and also attaches gRPC and ttrpc outgoing metadata; `NamespaceFromEnv` uses the env var or default; `Namespace` reads from context value, then incoming gRPC metadata, then ttrpc metadata; `NamespaceRequired` requires a nonempty namespace and validates it with `identifiers.Validate`.

Control flow: namespace lookup prefers local context value over RPC metadata. Required lookup wraps missing namespace as `errdefs.ErrFailedPrecondition` and invalid names with validation context.

State/persistence: context-only transient state; environment read is process state.

Dependencies/integration: used by clients, services, and spec options such as namespaced cgroups. Bridges gRPC and ttrpc header helpers.

Risks: `Namespace` may return an unvalidated value; only `NamespaceRequired` validates. Environment fallback can make behavior implicit.

Test signals: `context_test.go` validates set/get, required errors, invalid namespace handling, and env default behavior.
