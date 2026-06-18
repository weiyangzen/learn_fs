<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_import.go -->
# sources/cloud-native/moby/daemon/images/image_import.go

Purpose: implements `docker import` for the legacy image store.

Important APIs and control flow: `ImportImage` defaults nil platforms to `platforms.DefaultSpec`, validates OS support, applies Dockerfile-style `changes` to an empty container config, decompresses the input layer stream, registers it as a root layer, constructs a minimal image config with one diff ID and history entry, creates the image, optionally tags it, and logs an import event.

State and persistence: writes a new layer, image config record, optional reference tag, last-updated metadata through tagging, and image event.

Dependencies and integration: depends on archive compression, Dockerfile config mutation, image/layer stores, OCI platforms, and daemon event logging.

Risks: a failure after `imageStore.Create` but before tag/event leaves an untagged imported image. OS validation is based on the requested platform, not stream content. Layer release after registration is critical to avoid reference leaks.

Test signals: import integration tests cover this path; no direct unit test is in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image_import.go -->
