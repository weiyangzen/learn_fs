# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/containerwalker.go

Purpose: resolves container ID prefixes by walking containerd containers, ported from nerdctl.

Important APIs and flow: `Found` describes each match with raw request, index, and total match count. `NewContainerWalker` stores a containerd client and callback. `Walk` rejects `k8s://` form, builds a regex ID filter `id~=^<quoted req>.*$`, lists containers, and calls `OnFound` for each result with match metadata.

State and persistence: no persistence. Reads containerd metadata through the client.

Dependencies and integration: used by `Committer.resolveContainerID` to expand short IDs and detect ambiguity before inspecting/committing containers.

Risks and test signals: only ID prefix matching is supported; names are mentioned in comments but not implemented. Callback errors abort the walk. A nil `OnFound` would panic if matches exist.
