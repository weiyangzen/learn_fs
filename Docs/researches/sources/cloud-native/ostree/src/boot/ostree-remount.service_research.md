# sources/cloud-native/ostree/src/boot/ostree-remount.service

Purpose: This systemd oneshot remounts OSTree OS bind mounts early in the real boot so writable state such as `/etc` and `/var` is ready before core services need it.

Important APIs, types, and functions: It runs only with `ostree` on the kernel command line, has no default dependencies, conflicts with `umount.target`, runs after `-.mount`, `var.mount`, and `systemd-remount-fs.service`, and before `local-fs.target`, `umount.target`, random seed, Plymouth read-write, journal flush, tmpfiles setup, and rfkill units. `ExecStart=/usr/lib/ostree/ostree-remount`; installed as `WantedBy=local-fs.target`.

Control flow: systemd orders it after core mounts but before services that require write access. Failure triggers emergency target.

State and persistence behavior: The OSTree binary performs mount namespace/bind mount changes for deployment state. The service remains active after exit.

Dependencies and integration points: Integrates with systemd local filesystem ordering, OSTree deployment mounts, `/var`, `/etc`, and early services that read/write persistent machine state.

Risks: Incorrect ordering can cause services to see read-only or wrong `/etc`/`/var`. Failure early in boot can isolate emergency mode. It must avoid racing unmount during shutdown.

Test signals: Boot integration tests and systemd ordering analysis are primary validation.
