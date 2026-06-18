<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_push.go -->
# sources/cloud-native/moby/daemon/images/image_push.go

Purpose: implements legacy-store image push with progress streaming and optional platform validation.

Important APIs and control flow: `PushImage` rejects multiple platforms, validates the requested platform by resolving the local image when provided, starts a buffered progress writer goroutine, constructs a distribution push config with schema2 config media type, layer providers from the layer store, upload manager, registry/auth metadata, and calls `distribution.Push`. It waits for progress output and records push metrics.

State and persistence: reads image, reference, distribution metadata, and layer stores; writes progress, registry upload state, metrics, and image events through callbacks.

Dependencies and integration: used by API push paths and depends on Moby distribution push, upload concurrency manager, registry resolver, and progress utilities.

Risks: only one platform is supported. Progress output cancellation can cancel the push context. Platform validation depends on legacy image-store platform semantics.

Test signals: no direct tests here; push integration tests cover registry upload behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_push.go -->
