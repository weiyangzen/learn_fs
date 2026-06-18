## sources/cloud-native/moby/daemon/list_windows.go

Purpose: Implements Windows-specific container isolation filtering for `docker ps`.

Important API: `excludeByIsolation(container *container.Snapshot, ctx *listContext)` lowercases `container.HostConfig.Isolation`, defaults empty isolation to `default`, and matches it against the user filter.

Control flow and state: If the filter does not match the normalized isolation value, returns `excludeContainer`; otherwise returns `includeContainer`.

Dependencies and integration points: Called by shared `includeContainerInList`. Depends on Windows `HostConfig.Isolation` semantics and the filters package matching behavior.

Risks: Assumes `HostConfig` is non-nil for snapshots reaching this code. Empty isolation is surfaced as `default`, which is API-visible filtering behavior. Case normalization is one-way and depends on filter matching expectations.

Test signals: No direct Windows-specific tests in this subset.
