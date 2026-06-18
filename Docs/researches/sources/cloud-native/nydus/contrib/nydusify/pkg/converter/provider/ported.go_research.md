# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/provider/ported.go

Purpose: ports selected containerd pull/push/import helpers so the custom provider can fetch, push, and load images against its content store.

Important APIs and flow: `importOpts` mirrors containerd archive import settings. `fetch` resolves a ref, creates a fetcher, rejects Docker schema1 manifests, builds handler chains for fetching children, platform filtering, legacy config conversion detection, distribution source labels, optional wrappers, concurrency limiting, and stream-store default refs; it dispatches descriptors and converts legacy manifests when needed. `push` normalizes platform matcher, annotates refs with digest, creates a pusher, wraps handlers, applies upload concurrency, and calls `remotes.PushContent`. `load` imports an OCI/docker archive index, walks descriptors with platform filtering and optional layer discard/missing skip, and produces image records from annotations or digest refs. `imageName` prefers containerd image-name annotation then OCI ref-name with optional cleanup.

State and persistence: reads/writes the supplied content store, pulls from remote fetchers, pushes to remote pushers, and imports archive streams.

Dependencies and integration: used by `Provider.remotePull`, `remotePush`, and `Import`. It bridges containerd v2 APIs with acceleration-service content and Nydus streaming content.

Risks and test signals: ported code must track containerd API semantics. Label handling assumes stream content can support Info/Update. Schema1 is explicitly unsupported. Platform filtering can drop manifests if matcher is wrong.
