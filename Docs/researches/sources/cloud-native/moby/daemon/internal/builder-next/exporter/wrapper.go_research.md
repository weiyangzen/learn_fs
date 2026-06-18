# sources/cloud-native/moby/daemon/internal/builder-next/exporter/wrapper.go

## Purpose
Wraps BuildKit's image exporter to apply Moby defaults, label exported content with build-reference metadata, and invoke daemon callbacks for exported/named images.

## APIs, Control Flow, and Integration
`BuildkitCallbacks` exposes `Exported` and `Named`. `NewWrapper` stores the wrapped exporter and content store. `Resolve` sanitizes `name`, defaults `unpack=true`, sets dangling image prefix, forces dangling-empty-only, and wraps the resolved instance. `Export` delegates to the inner exporter, reads the descriptor and image digest, writes a `moby/build.ref.<ref>` content label containing `createdAt`, invokes `Exported`, then parses output `image.name` and calls `Named` for valid tagged refs.

## State, Dependencies, and Risks
Persistence is containerd content label updates. Risks include mutating the caller's attr map, relying on legacy `image.name` until newer BuildKit constants are vendored, and export failure if label update fails after the inner exporter already wrote content. Integration is with containerd image store and Moby callbacks.
