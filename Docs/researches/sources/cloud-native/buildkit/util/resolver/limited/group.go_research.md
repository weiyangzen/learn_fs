<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/limited/group.go -->
# sources/cloud-native/buildkit/util/resolver/limited/group.go

Purpose: limits concurrent registry fetch and push operations per registry domain, while giving JSON metadata requests one extra high-priority slot.

Important APIs and types: `Group`, `Default`, `DefaultMaxConcurrency`, `SetMaxConcurrency`, `WrapFetcher`, `PushHandler`, package-level `FetchHandler` and `PushHandler`, and internal `req`/`readCloser`.

Control flow: `req.acquire` skips limiting if the context already has the package marker, derives high priority from media type suffix `+json`, acquires semaphores, and returns a release function. Fetch wrappers hold slots until the returned reader closes and attach a finalizer warning/release path if not closed. Push wrappers acquire around each descriptor handler call.

State and persistence: `Group` stores per-domain semaphore pairs in memory. The default group is replaceable via `SetMaxConcurrency`.

Dependencies and integration: wraps containerd remotes fetch/push handlers, content providers/ingesters, OCI descriptors, BuildKit logging, and distribution reference parsing for domain extraction.

Risks: leaked readers delay semaphore release until finalizer execution and log a warning. The default group is mutable global state. High-priority JSON requests still acquire the total semaphore, allowing at most one extra metadata connection per domain.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/limited/group.go -->
