# sources/cloud-native/containers-storage/pkg/mount/flags_unsupported.go

Purpose: defines zero-valued mount constants for platforms without Linux or FreeBSD support.

Important APIs, types, and functions: zero constants for all package mount flags and `mntDetach`.

Control flow: none; constants only.

State and persistence: none.

Dependencies and integration points: selected for `!linux && !freebsd`. It lets packages compile even though mount operations are unsupported.

Risks and edge cases: parsing known option names with zero-valued flags treats them as data or no-ops. Actual mount/unmount implementations panic on unsupported platforms.

Test signals: no direct tests; compile coverage on unsupported platforms is the main signal.
