# sources/cloud-native/composefs-rs/crates/composefs/tests/test.sh

Purpose: shell integration test for `composefs-setup-root`, emulating initramfs/sysroot layout and verifying the root pivot creates read-only root plus writable `/etc` and `/var` overlays.

Important APIs/types/functions: helper functions `mkd` and `assert_fail`; invokes `composefs-setup-root --config --cmdline --root-fs --sysroot`.

Control flow: requires root/unshare context, creates a fake block-device tree with composefs repo/state/deployment directories, bind-mounts a fake read-only root, bind-mounts the block tree as `/sysroot`, runs setup with a fixed image id, validates mount effects, writes into `/etc` and `/var`, unmounts recursively, and checks no test mounts remain.

State/persistence: creates persistent test directories under the provided top directory and expects writes to land in deployment upper/state paths. Mount namespace state is mutated and then reversed with `umount -R`.

Dependencies/integration: depends on Linux mount, user/mount namespaces, `composefs-setup-root`, `/proc/mounts`, and overlay/writeable sysroot semantics.

Risks/test signals: catches pivot/mount regressions and persistence placement bugs. Risks include requiring root privileges, bind-mount support, and fake EROFS content that cannot fully validate real kernel EROFS behavior.
