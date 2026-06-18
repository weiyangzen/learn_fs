# sources/cloud-native/containerd/core/images/converter/converter.go

Purpose: top-level image conversion entry point and option wiring.

Important APIs/types: `Opt`, `WithLayerConvertFunc`, `WithDockerToOCI`, `WithPlatform`, `WithIndexConvertFunc`, `WithUpdateManifest`, `Client`, and `Convert`.

Control flow and state: `Convert` applies options, defaults platform matcher to `platforms.All`, builds a default index conversion function unless supplied, opens a lease through the client, fetches source image, converts its target descriptor tree, builds destination image metadata, deletes any existing destination when `dstRef != srcRef`, then creates or updates image service entry.

Dependencies and integration: content store, image store, leases, platforms, digest map in default converter when update callback is used.

Risks: `WithDockerToOCI(v bool)` ignores its parameter and always enables conversion. Destination delete ignores errors before create. Conversion occurs under a lease, but deletion/create semantics can still race with external image operations. Caller-supplied convert functions must preserve content and labels correctly.

Test signals: no direct tests here. Conversion integration tests should cover same-ref update, different-ref create, lease release, option wiring, and the `WithDockerToOCI(false)` behavior if intentional.
