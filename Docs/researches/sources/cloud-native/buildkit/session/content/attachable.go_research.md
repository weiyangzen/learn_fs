<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/content/attachable.go -->
# sources/cloud-native/buildkit/session/content/attachable.go

Purpose: exposes one or more containerd content stores over a BuildKit session as an attachable gRPC content service.

Important APIs, types, and functions: `GRPCHeaderID` names the metadata key selecting a store. `attachableContentStore` implements content store methods by calling `choose(ctx)`. `choose` reads incoming metadata, validates store id, and returns the selected store. `NewAttachable(stores)` wraps the store selector in containerd's `contentserver.New`. `(*attachable).Register` registers the content server.

Control flow and state: persistent state is the in-memory map of store ids to `content.Store`. Every content API call chooses a store from request metadata and delegates.

Dependencies and integration: uses containerd content API/server, errdefs, BuildKit session attachables, gRPC metadata, OCI descriptors, and digest types. Paired with `content/caller.go`.

Risks and test signals: missing metadata returns invalid argument; unknown store returns not found. Store ids are trusted metadata over the authenticated session. `content_test.go` verifies two stores can be selected and read through a session.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/content/attachable.go -->
