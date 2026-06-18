## sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/platform.go

Purpose: shared platform flag parsing for CLI commands.

Important APIs/types/functions: `PlatformFlags`, `GetPlatforms`, `PlatformFlag`, and `AllPlatformsFlag`.

Control flow: if `--all-platforms` is set, return platforms from image manifest/index using content store. Otherwise parse each `--platform` string. If neither is set, return an empty slice and let callers choose defaults.

State and persistence: read-only content store access when all platforms are requested.

Dependencies and integration: containerd images/content and `containerd/platforms`.

Risks and test signals: comments contain a typo in `all-plaforms`; no tests cover precedence or invalid platform parsing in this subset.
