## sources/cloud-native/soci-snapshotter/config/resolver.go

Purpose: TOML model for registry resolver mirrors and per-host settings.

Important APIs/types/functions: `ResolverConfig`, `HostConfig`, and `MirrorConfig`.

Control flow: no parsing logic in this file; TOML decoder fills maps/slices based on tags.

State and persistence: none directly; values influence registry resolution elsewhere.

Dependencies and integration: embedded in `ServiceConfig` and used by service/resolver code outside this subset.

Risks and test signals: no validation here for hostnames, mirror schemes, or timeout ranges. No direct tests in this subset.
