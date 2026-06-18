# sources/cloud-native/containers-storage/types/options_bsd.go

Purpose: FreeBSD/NetBSD platform defaults for storage configuration.

Important APIs and control flow: defines `defaultRunRoot` as `/var/run/containers/storage`, `defaultGraphRoot` as `/var/db/containers/storage`, `SystemConfigFile` as `/usr/local/share/containers/storage.conf`, and `defaultOverrideConfigFile` as `/usr/local/etc/containers/storage.conf`. `canUseRootlessOverlay` always returns false.

State and persistence: no runtime state beyond constants and package variable used by `options.go`.

Dependencies and integration: selected by `//go:build freebsd || netbsd`. Feeds `DefaultConfigFile`, `loadDefaultStoreOptions`, and rootless driver selection.

Risks: rootless users on BSD always fall back away from overlay unless an explicit driver is supplied, which may affect feature parity. Defaults must track OS packaging conventions.

Test signals: platform-specific compile and config tests would catch missing symbols; functional overlay behavior is intentionally disabled here.
