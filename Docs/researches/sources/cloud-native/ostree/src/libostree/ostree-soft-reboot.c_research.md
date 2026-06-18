# sources/cloud-native/ostree/src/libostree/ostree-soft-reboot.c

Purpose: prepares a soft reboot target root at `/run/nextroot` for composefs-based OSTree systems, enabling systemd soft reboot into a new root without a full kernel reboot when supported.

Important APIs/types/functions: `_ostree_prepare_soft_reboot` is the sole function. Under `HAVE_SOFT_REBOOT` it uses prepare-root config, `read_proc_cmdline`, `otcore_load_rootfs_config`, `otcore_mount_rootfs`, `otcore_mount_boot`, `otcore_mount_etc`, `OTCORE_RUN_NEXTROOT`, `OTCORE_RUN_NEXTROOT_BOOTED`, and mount syscalls `open_tree`, `mount_setattr`, and `move_mount`. Without support it returns "soft reboot not supported".

Control flow: load config and kernel cmdline, derive rootfs config, reject non-composefs deployments, create `/run/nextroot`, bind-mount `/sysroot` onto itself, refresh cwd, mount composefs root, boot, and etc into nextroot, detach temporary sysroot bind mount, clone `/sysroot`, mark the clone read-only, move it into `/run/nextroot/sysroot`, write booted metadata, and return success.

State/persistence: mutates live mount namespace state, creates `/run/nextroot`, mounts root/boot/etc/sysroot into it, writes serialized booted metadata, and temporarily bind-mounts/detaches `/sysroot`. It does not alter repository objects or bootloader config.

Dependencies/integration: depends on Linux mount APIs, libglnx, OSTree core/sysroot private headers, mount utilities, keyfile utilities, and otcore prepare-root helpers. Integrates with rpm-ostree/OSTree soft reboot orchestration and systemd `/run/nextroot` handoff.

Risks: privileged Linux-only code with modern syscall requirements. Some mount/cwd failures call `err(EXIT_FAILURE, ...)`, terminating the process instead of returning `GError`. It hard-requires composefs and read-only sysroot assumptions. Mount namespace and cwd manipulation are delicate.

Test signals: `tests/kolainst/destructive/soft-reboot.sh` exercises soft reboot into staged/non-staged deployments, default soft reboot when `/run/nextroot` is mounted, and failures for kernel/kernel-arg changes. Composefs integration tests cover related prerequisites.
