# sources/cloud-native/containers-storage/types/options_windows.go

Purpose: Windows build defaults for the storage options package.

Important APIs and control flow: provides the same default path symbols as Linux and a `canUseRootlessOverlay` stub returning false.

State and persistence: no persistence; only constants and one package variable.

Dependencies and integration: selected by Windows builds to satisfy shared `options.go` references.

Risks: POSIX-style paths are unlikely to be usable as native Windows storage roots without higher-level adaptation. Overlay rootless support is disabled.

Test signals: Windows compile coverage validates symbol availability; functional tests would need platform-specific expectations.
