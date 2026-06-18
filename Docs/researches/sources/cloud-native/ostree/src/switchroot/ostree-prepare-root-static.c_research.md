# sources/cloud-native/ostree/src/switchroot/ostree-prepare-root-static.c

Purpose: static, pid-1 variant of prepare-root for systems without an initramfs. It resolves the OSTree deployment from the kernel command line, constructs the deployment root, pivots or moves mounts, prepares `/boot`, `/etc`, `/usr`, `/var`, and execs `/sbin/init`.

Important APIs/functions: `sysroot_is_configured_ro()` manually scans `ostree/repo/config` for `[sysroot] readonly=true` without GLib. `resolve_deploy_path()` reads `ostree=` from `/proc/cmdline`, validates it is a symlink, resolves it, and optionally logs to systemd journal. `pivot_root()` wraps the syscall. `main()` asserts pid 1 and performs the mount choreography.

Control flow: ensure `/proc/cmdline` is readable, mounting proc temporarily if needed; resolve `/` and deployment path; inspect readonly config; make mounts private; create `/sysroot.tmp`; bind the deployment there; optionally stamp read-only sysroot; bind `/boot` if needed; make `/etc` writable for readonly sysroot; mount `/usr` overlay or read-only bind; prepare `/var`; pivot to deployment or move mounts; make `/sysroot` private; exec init.

State/persistence: mutates the live mount namespace, may create `_OSTREE_SYSROOT_READONLY_STAMP`, bind/overlay mounts directories, and changes process cwd/root. It does not write `/run/ostree-booted` metadata like the nonstatic path.

Dependencies/integration: minimal libc/syscall implementation plus optional systemd journal. Shares macros/helpers from `ostree-mount-util.h`.

Risks: asserts pid 1, so it aborts outside the intended boot mode. Manual config parsing is fragile. Missing `ostree=` is not explicitly checked before path formatting. Mount ordering errors can leave an unusable boot. Static path lacks newer composefs/transient-root logic from `ostree-prepare-root.c`.

Test signals: `tests-unit-container/test-prepare-root.sh` targets the nonstatic initramfs path, not this static path. Static behavior needs boot/integration tests on embedded/no-initramfs systems.
