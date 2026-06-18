## sources/cloud-native/soci-snapshotter/config/pull_modes.go

Purpose: defines pull mode switches for SOCI v1, SOCI v2, and parallel pull/unpack.

Important APIs/types/functions: `PullModes`, `V1`, `V2`, `Parallel`, `defaultPullModes`, and `DefaultPullModes`.

Control flow: defaulting creates SOCI v1 disabled, SOCI v2 enabled, parallel disabled, and default parallel config embedded.

State and persistence: no direct state; controls snapshotter runtime strategy for lazy loading, v2 manifest annotation discovery, and parallel fallback.

Dependencies and integration: consumed by daemon service creation and adaptive fetch job setup.

Risks and test signals: fallback mode is marked experimental and tied to containerd content-store GC concerns. Config tests assert defaults and a fallback TOML scenario.
