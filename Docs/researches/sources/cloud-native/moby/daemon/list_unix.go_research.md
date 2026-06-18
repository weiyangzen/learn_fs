## sources/cloud-native/moby/daemon/list_unix.go

Purpose: Provides the Unix implementation of isolation filtering for container listing.

Important API: `excludeByIsolation(container *container.Snapshot, ctx *listContext) iterationAction` always returns `includeContainer`.

Control flow and state: No state is read. The function is a platform stub because container isolation is a Windows-only concept in this daemon path.

Dependencies and integration points: Built for Linux and FreeBSD. Called from `includeContainerInList` after label checks.

Risks: Minimal; the main risk is expectation mismatch if an isolation filter is accepted on Unix but effectively ignored by this stub. The accepted filter set includes `isolation`, so behavior differs by platform.

Test signals: No direct Unix-specific test in this subset.
