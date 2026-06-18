# sources/cloud-native/nydus/contrib/nydusify/pkg/remote/remote.go

Purpose: wraps containerd remote resolver operations for resolving, pulling, and pushing OCI descriptors with reference normalization and plain HTTP retry state.

Important APIs/types/functions: `Remote`, `New`, `MaybeWithHTTP`, `WithHTTP`, `IsWithHTTP`, `namedReference`, `requestRef`, `Push`, `Pull`, and `Resolve`.

Control flow: `New` parses a normalized Docker reference. `requestRef` returns repository name for digest-addressed blob operations or tag-normalized reference for manifest operations. Each operation creates a fresh resolver from `resolverFunc` to avoid stale auth tokens. `Push` serializes concurrent pushes by containerd ref key using a sync.Map of mutexes, creates a pusher, treats already-exists as success, and streams content through `content.Copy`. `Pull` fetches descriptors, and `Resolve` resolves the tag reference.

State and persistence: `Remote` stores parsed reference, resolver factory, pushed mutex map, and `withHTTP` flag. Remote registry persistence happens through pusher/fetcher.

Dependencies and integration points: distribution/reference, containerd remotes/content, errdefs, OCI descriptors, provider remote constructors, parser, optimizer, and modctl.

Risks and test signals: `MaybeWithHTTP` relies on error-string host matching. The mutex map can grow with unique ref keys. Resolver factory must be safe to call repeatedly.
