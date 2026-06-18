## sources/cloud-native/buildkit/snapshot/localmounter.go

Purpose: defines a small cross-platform helper abstraction for mounting BuildKit mountables or raw mount lists onto local paths.

Important APIs/types/functions: `Mounter` has `Mount` and `Unmount`. `LocalMounter(mountable, opts...)` and `LocalMounterWithMounts(mounts, opts...)` create `localMounter`. `ForceRemount` sets `forceRemount`, preventing writable bind/nullfs short-circuit behavior on platforms that support it.

Control flow: this file only constructs state. Platform files implement `Mount`/`Unmount`.

State and persistence: `localMounter` stores mounts, mountable, target path, release function, and force flag under a mutex. It persists nothing beyond temporary mount directories created by platform implementations.

Dependencies and integration points: used by snapshot differ, tests, and code needing a local filesystem view of `Mountable`.

Risks and test signals: correct release behavior depends on platform files setting `target` and `release` consistently. `ForceRemount` is important when callers need an actual mount path even for writable binds.
