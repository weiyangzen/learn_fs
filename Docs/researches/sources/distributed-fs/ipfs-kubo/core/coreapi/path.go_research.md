# sources/distributed-fs/ipfs-kubo/core/coreapi/path.go

Purpose: implements CoreAPI path and node resolution over namesys plus IPFS/IPLD path resolvers.

Important APIs/types/functions: `CoreAPI.ResolveNode` and `CoreAPI.ResolvePath`.

Control flow: `ResolveNode` calls `ResolvePath` then fetches the resolved root CID from DAG. `ResolvePath` resolves mutable names through `namesys.Resolve`, maps missing namesys to `coreiface.ErrOffline`, selects IPLD or UnixFS resolver by namespace, converts to immutable path, resolves to the last node and remainder, rebuilds a sanitized path from namespace/root/remainder, and returns the immutable path plus unresolved remainder.

State and persistence behavior: read-only. It may fetch blocks through configured online/offline DAG/resolver stack and may consult namesys cache/network.

Dependencies and integration points: central dependency for block, UnixFS, pin, routing, object, and resolve commands. Uses boxo path/namesys/path resolver and Kubo tracing.

Risks: only IPFS and IPLD namespaces are supported after namesys resolution. Resolver behavior depends on whether CoreAPI was created offline or with fetch disabled. Errors from mutable names can become offline errors for callers.

Test signals: `coreapi/test/path_test.go` targets UnixFS HAMT partial-resolution timeout behavior through this API.
