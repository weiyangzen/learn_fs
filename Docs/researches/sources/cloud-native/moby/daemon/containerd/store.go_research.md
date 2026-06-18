<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/store.go -->
# sources/cloud-native/moby/daemon/containerd/store.go

Purpose: wraps a content store so push can pretend selected missing blobs exist for cross-repository mount attempts.

Important APIs and flow: `fakeStoreWithSources` embeds a real `content.Store` and a digest-to-distribution-source map. `wrapWithFakeMountableBlobs` constructs it. All content store methods delegate except `Info`: when the real store returns not-found and the digest has a source, `Info` returns synthetic content metadata with a `containerd.io/distribution.source.<domain>` label. `ReaderAt` still delegates and therefore still fails for missing content.

State and persistence: no durable writes; synthetic metadata exists only through this wrapper during push.

Dependencies and integration: used by `image_push.go` after `findMissingMountable`. It relies on containerd remotes recognizing distribution source labels to mount blobs instead of uploading/reading them.

Risks: this intentionally lies about content existence, so it must be scoped to push mount optimization. If a caller tried to read the synthetic blob, it would fail. Label domain/value formatting must match containerd expectations.

Test signals: no direct tests in this subset; push tests cover descriptor selection but not fake store mount behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/store.go -->
