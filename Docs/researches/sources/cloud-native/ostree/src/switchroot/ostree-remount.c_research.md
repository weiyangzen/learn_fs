# sources/cloud-native/ostree/src/switchroot/ostree-remount.c

Purpose: post-switchroot remount helper that restores intended writability for `/sysroot`, `/etc`, and `/var`, and relabels transient `/etc` overlay contents for SELinux.

Important APIs/functions: `do_remount()` checks target existence, skips symlinks/nonmounts, compares current `ST_RDONLY` state, and remounts rw/ro. `relabel_dir_for_upper()` recursively restorecons overlay upperdir entries when SELinux is enabled. `main()` reads `OTCORE_RUN_BOOTED` metadata, handles legacy stamp fallback, relabels transient `/etc`, detects composefs, and remounts selected paths.

Control flow: read `/run/ostree-booted` variant dict if present; if transient `/etc` metadata exists, optionally unshare mount namespace to expose the real `/etc/machine-id`, relabel upperdir-backed files, then restore namespace. If `/` is read-only and not composefs, exit without remounts. Otherwise remount `/sysroot` according to readonly metadata, `/etc` writable when it is a bind mount, and `/var` writable.

State/persistence: mutates mount flags and, under SELinux, filesystem labels. It may create `/run/ostree-booted` as an empty compatibility stamp if missing.

Dependencies/integration: depends on `ostree-mount-util.h`, `otcore.h` metadata keys, libglnx variant/dir iterators, mount namespace syscalls, and optional SELinux restorecon.

Risks: relabeling recursively mirrors upperdir paths into `/etc`; races with systemd-sysusers are partly tolerated for ENOENT. Namespace unshare/setns failures are fatal. Incorrect metadata can leave `/sysroot` writable or read-only contrary to policy.

Test signals: prepare-root container tests validate metadata creation and mount state before remount; full boot/admin tests are needed to exercise `ostree-remount` behavior and SELinux relabeling.
