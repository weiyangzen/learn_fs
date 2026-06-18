# Research: sources/cloud-native/buildkit/cmd/buildctl/build_test.go

Purpose: provides integration coverage for `buildctl build` behavior across local inputs, exporters, metadata files, containerd image unpacking, registry push progress, and LLB stdin marshaling. The tests run through BuildKit integration sandboxes rather than isolated mocks.

Important functions and flow: `testBuildWithLocalFiles` builds an LLB graph that compares a local file mount against generated output. `testBuildLocalExporter` exports a generated file to a local directory and normalizes Windows CRLF. `testBuildContainerdExporter` exports an image with unpacking and verifies the image in containerd namespace `buildkit`. `testBuildMetadataFile` writes image exporter metadata and checks image name, digest, descriptor shape, and optional containerd digest match. `testBuildPushProgress` starts a registry and asserts push progress text. `marshal` serializes an LLB state to the protobuf stream consumed by `buildctl build`.

State and dependencies: tests create temporary filesystem inputs/outputs, containerd clients, registry sandboxes, and image records. They depend on integration helpers, LLB, containerd namespaces, OCI descriptors, and official base images mirrored by the suite.

Risks and test signals: these tests exercise high-value paths but are environment dependent, with Windows skips or behavior normalization. They validate that CLI arguments are wired into real daemon state, but they do not directly cover every parser failure branch or tracing/cache metrics behavior.
