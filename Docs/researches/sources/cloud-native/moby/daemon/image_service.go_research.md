<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/image_service.go -->
# sources/cloud-native/moby/daemon/image_service.go

Purpose: defines the daemon-level `ImageService` interface used while Moby supports both legacy graphdriver and containerd image-store implementations.

Important APIs and control flow: the interface groups image operations such as pull, push, create, delete, list, prune, import, tag, inspect, history, commit, squash, attestations, and disk usage; layer operations such as create/release/size/changes; builder support such as image cache and build-step commit; and cross-cutting functions such as distribution service access, storage driver reporting, cleanup, and config update.

State and persistence: the interface has no state itself, but it defines access to persistent image stores, reference stores, layer stores, and distribution metadata.

Dependencies and integration: this is a key contract between `daemon`, `daemon/images`, server backends, legacy builder, BuildKit migration shims, and containerd-backed alternatives. It imports API image/event types, backend option structs, internal image/layer types, and OCI platform values.

Risks: the comment explicitly says the interface is temporary and unstable. Its breadth couples daemon code to many image-store details, including Windows-specific and legacy-builder functions, which makes migration harder.

Test signals: no direct tests for the interface; compile-time conformance and daemon subsystem tests reveal drift.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/image_service.go -->
