<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_pull.go -->
# sources/cloud-native/moby/daemon/images/image_pull.go

Purpose: implements legacy-store image pull, progress streaming, and content lease preservation.

Important APIs and control flow: `PullImage` accepts at most one platform, delegates to `pullImageWithReference`, records metrics, and emits a warning for the special single-arch platform mismatch case. `pullImageWithReference` creates buffered progress channels, starts a progress writer goroutine, adds the containerd namespace, creates a temporary lease with `tempLease`, wraps the content store and image config store so committed digests get leased to the final image, builds a distribution pull config, and calls `distribution.Pull`. `tempLease` reuses an existing lease or creates an expiring temporary lease.

State and persistence: writes image configs, references, layers/content, distribution metadata, final image content leases, temporary leases, progress output, metrics, and image events through distribution callbacks.

Dependencies and integration: integrates containerd namespaces/leases/content, Moby distribution pull, progress formatting, registry auth/meta headers, and image-store lease wrappers from `store.go`.

Risks: temporary lease deletion failures are deferred and ignored by callers. Progress writing runs concurrently and cancels the pull context when output fails. Only one platform is supported. The platform mismatch warning relies on `GetImage`'s special non-nil-image plus NotFound behavior.

Test signals: store lease behavior is covered by `store_test.go`; pull integration tests cover registry behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_pull.go -->
