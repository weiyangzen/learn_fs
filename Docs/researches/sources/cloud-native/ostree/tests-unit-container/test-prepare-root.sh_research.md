# sources/cloud-native/ostree/tests-unit-container/test-prepare-root.sh

Purpose: privileged container test for `ostree-prepare-root`, treating a podman container as an initramfs.

Important operations: asserts `TEST_CONTAINER=1`, defines cleanup for `/target-sysroot` and `/sysroot.tmp`, creates a bind-mounted target sysroot, initializes OSTree admin fs/stateroot, fakes a deployment, binds a temporary `/proc/cmdline`, runs `/usr/lib/ostree/ostree-prepare-root /target-sysroot`, and validates mount/layout behavior.

Control flow: first run disables composefs on the kernel cmdline and checks `/run/ostree-booted`, `/etc` and `/usr` mountpoints, no transient `/etc`, no `/boot` mount, and default read-only `/sysroot`. It then removes prepare-root config to test writable default fallback. Next it enables `[etc] transient = true` and checks overlay upperdir. Finally it creates a traditional `/boot/loader` symlink and verifies prepare-root still does not mount `/boot`.

State/persistence: creates and tears down target sysroot, fake deployment files, bind mounts, `/run/ostree-booted`, `/run/ostree`, and temporary edits to `/usr/lib/ostree/prepare-root.conf`.

Dependencies/integration: requires podman/privileged container capabilities, mount/umount/findmnt, `ostree admin`, and installed `/usr/lib/ostree/ostree-prepare-root`.

Risks: modifies installed prepare-root config in-place with backup/restore; cleanup must run to avoid leaked mounts. The test disables composefs for unprivileged container compatibility, so composefs path is not covered here.

Test signals: strong direct coverage for nonstatic prepare-root legacy bind path, readonly sysroot config defaulting, transient `/etc`, and generator-owned `/boot` behavior.
