<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/content.go -->
# sources/cloud-native/moby/daemon/content.go

Purpose: configures a local containerd content store for the daemon and wraps content/lease services so a default namespace is always applied.

Important APIs and flow: `configureLocalContentStore` creates `<daemon.root>/content`, opens `metadata.db` with bbolt, creates a local content store under `content/data`, wraps it in containerd metadata DB, stores the bbolt handle on the daemon, and returns `namespacedContent` and `namespacedLeases`. `withDefaultNamespace` preserves an existing namespace or injects the configured default. `namespacedContent` implements content store methods by applying the namespace before delegating. `namespacedLeases` does the same for lease manager methods.

State and persistence: creates persistent daemon content metadata DB and blob data directories. Stores `daemon.mdDB` for later lifecycle management. All content and lease operations are namespaced in containerd metadata.

Dependencies and integration: used when the daemon needs a local content store outside a full external containerd setup. Depends on containerd local content plugin, metadata DB, namespaces, leases, bbolt, and daemon root configuration.

Risks: bbolt open uses default options and must be closed elsewhere through `daemon.mdDB`. Namespace wrapping is easy to bypass if callers retain the underlying provider. Directory permissions are restrictive for metadata/data roots, which is appropriate but can surface deployment permission issues.

Test signals: no direct tests in this subset; namespace wrapper behavior and persistence lifecycle need integration coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/content.go -->
