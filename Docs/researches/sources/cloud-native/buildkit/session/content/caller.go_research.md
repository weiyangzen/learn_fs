<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/content/caller.go -->
# sources/cloud-native/buildkit/session/content/caller.go

Purpose: creates a client-side `content.Store` proxy that routes operations over a BuildKit session to a selected attachable content store.

Important APIs, types, and functions: `callerContentStore` wraps a proxied content store, selected store id, and session caller. `choose(ctx)` merges caller context and outgoing metadata with `GRPCHeaderID`. All content store methods call `choose` and delegate, wrapping errors with stack context. `NewCallerStore(c, storeID)` builds a containerd content client over `c.Conn()` and returns a proxy store.

Control flow and state: state is the caller connection and target store id. Each operation injects metadata before making the proxied content request.

Dependencies and integration: integrates with containerd content proxy, generated containerd content service client, and session caller lifecycle.

Risks and test signals: outgoing metadata key overwrite order matters; the newest store id is intentionally first. Errors are stack-wrapped, which can affect equality tests. `content_test.go` validates read flow through a real session.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/content/caller.go -->
