# sources/cloud-native/moby/daemon/internal/distribution/pull_v2_unix.go

## Purpose
Provides non-Windows pull helpers for blob opening, manifest-list platform filtering, and compatibility checks.

## APIs, Control Flow, and Integration
`layerDescriptor.open` reads blobs from the registry blob store. `filterManifests` defaults the requested platform, normalizes it, includes descriptors with nil platform or matching platforms, logs matches, and stable-sorts matches by platform preference. `checkImageCompatibility` is a no-op. `withDefault` fills missing OS/architecture/variant from `maximumSpec`.

## State, Dependencies, and Risks
No persistence. Risks include accepting nil-platform descriptors broadly and platform defaulting choosing host maximum compatibility. This file's behavior controls which manifest-list entry is pulled on Linux/Unix. Coverage is indirect; no dedicated tests in this subset validate sorting.
