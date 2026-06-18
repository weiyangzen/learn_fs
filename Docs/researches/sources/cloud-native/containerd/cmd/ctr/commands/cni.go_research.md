# sources/cloud-native/containerd/cmd/ctr/commands/cni.go

Purpose: defines metadata used when `ctr run` integrates with CNI and helper naming for namespaced container IDs.

Important APIs/types/functions: `CtrCniMetadataExtension` extension name; `NetworkMetaData` with `EnableCni`; `init()` registers the typeurl; `FullID()` returns `<namespace>-<containerID>` when namespace is present.

Control flow: type registration happens at init. `FullID()` reads namespace from context and formats accordingly.

State and persistence: no persistent state; typeurl registration is process-global.

Dependencies/integration: containerd client `Container`, namespace package, and typeurl registry.

Risks: full ID formatting can collide if namespaces/container IDs contain separator-like content, but matches existing ctr convention.

Test signals: no local tests.
