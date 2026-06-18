# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/ostweaks_unsupported.go

Purpose: Provides a non-Linux no-op implementation of overlay OS tuning.

Important APIs and functions: `applyOStweaks` is an empty function under `!linux`.

Control flow: allows cross-platform builds of overlay package components without Linux sysctl dependencies.

State and persistence: none.

Dependencies and integration points: selected by build tags as the counterpart to `ostweaks_linux.go`.

Risks: non-Linux platforms do not receive equivalent tuning; this is intentional.

Test signals: no direct tests.
