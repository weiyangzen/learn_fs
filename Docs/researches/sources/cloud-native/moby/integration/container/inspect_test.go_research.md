# sources/cloud-native/moby/integration/container/inspect_test.go

Purpose: Container inspect API tests for annotations, network alias defaults, image manifest platform metadata, and raw JSON/size fields.

Important APIs and flow: `TestInspectAnnotations` creates a container with host config annotations and verifies inspect preserves them. `TestNetworkAliasesAreEmpty` creates containers on default network modes and expects nil aliases. `TestInspectImageManifestPlatform` runs only on Linux snapshotter storage, compares inspect `ImageManifestDescriptor.Platform` with image inspect platform, and verifies API v1.47 hides the field. `TestContainerInspectWithRaw` calls inspect with and without `Size`, unmarshals `Raw`, and checks `SizeRw`/`SizeRootFs` presence.

State and dependencies: Creates containers and reads image metadata. Platform tests rely on snapshotter mode and frozen test images.

Risks and signals: It guards versioned inspect fields, raw payload fidelity, platform manifest propagation, and nil-vs-empty network alias semantics. Failures can break API clients relying on stable JSON shape.
