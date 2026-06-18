## sources/cloud-native/moby/daemon/internal/image/cache/compare.go

Purpose: Supplies cache matching helpers for platform and container config comparison.

Important APIs: `comparePlatform(builderPlatform, imagePlatform)` wraps `containerd/platforms.Only(...).Match` but special-cases Windows OS version matching. `compare(a, b *container.Config)` compares relevant container config fields while intentionally ignoring container-specific fields such as Image, Hostname, Domainname, and MacAddress.

Control flow: For Windows, if both OS values are windows and both versions have at least three dot-separated parts, it rewrites the image platform version to share the builder major/minor and builder build/revision before invoking the platform matcher; this effectively ignores build/revision compatibility. Config comparison checks nil, slice/map lengths, ordered slice entries, map key/value presence, booleans, strings, stop timeout pointer/value equality, and detailed healthcheck fields.

State and persistence: Pure functions. No persistence.

Dependencies and integration: Used by `getLocalCachedImage` to decide whether a locally built child can satisfy a builder cache request.

Risks: Slice order is significant for Env, Cmd, Entrypoint, Shell, OnBuild, and healthcheck test. The Windows version rewrite is subtle and only meaningful under the platform matcher behavior active on Windows. New fields added to `container.Config` must be considered manually.

Test signals: `compare_test.go` exercises many same/different config cases and platform matching including Windows version behavior.
