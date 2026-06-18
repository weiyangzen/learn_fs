## sources/cloud-native/buildkit/snapshot/localmounter_freebsd.go

Purpose: FreeBSD implementation of local mount/unmount.

Important APIs/types/functions: `Mount` lazily gets mounts, short-circuits writable single `nullfs` mounts unless `forceRemount` is set, otherwise mounts all into a temp dir. `Unmount` calls `mount.Unmount`, removes target, and invokes release.

Control flow: guarded by mutex and idempotent on repeated `Mount`. FreeBSD differs from Linux/Darwin by using `nullfs` as the bind-like shortcut type.

State and persistence: temporary mount target and release callback. No durable state beyond mounted filesystem while active.

Dependencies and integration points: selected on FreeBSD builds for snapshot local access.

Risks and test signals: only single writable nullfs gets shortcut; other bind-like forms require mount support. Release errors are returned after unmount cleanup. No FreeBSD-specific tests in subset.
