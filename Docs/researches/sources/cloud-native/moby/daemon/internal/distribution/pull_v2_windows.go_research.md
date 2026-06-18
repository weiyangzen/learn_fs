# sources/cloud-native/moby/daemon/internal/distribution/pull_v2_windows.go

## Purpose
Implements Windows-specific v2 pull behavior for foreign layers and Windows image compatibility.

## APIs, Control Flow, and Integration
`Descriptor` exposes foreign layer descriptors when URL-backed. `open` tries registry blob access first, then foreign URLs via HTTP read seeker. `filterManifests` filters by architecture, requested/host OS validity, Windows compatibility, logs skipped/matched entries, and sorts compatible Windows versions before others. `versionMatch` matches version prefix up to build. `checkImageCompatibility` rejects Windows images with build numbers newer than the host.

## State, Dependencies, and Risks
State is host OS version and network access to foreign URLs. Risks include foreign URL trust/availability, version parsing leniency, only architecture matching host GOARCH, and sorting that prefers compatible versions without full numeric ordering. Tests are indirect; Windows behavior is hard to cover cross-platform.
