# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/vmtest.sh

## Purpose

`vmtest.sh` builds a kernel and BPF selftests, prepares a Debian-based rootfs image, injects the selftests and an init script, launches QEMU, and retrieves test logs. It is the local/CI runner for executing BPF selftests in a controlled VM across supported platforms.

## Important APIs, Types, and Functions

The script defines platform-specific `QEMU_BINARY`, console, host/cross QEMU flags, `BZIMAGE`, and `ARCH` for `s390x`, `x86_64`, `aarch64`, `riscv64`, and `ppc64el`. Important functions are `usage`, `populate_url_map`, `newest_rootfs_version`, `download_rootfs`, `load_rootfs`, `recompile_kernel`, `mount_image`, `unmount_image`, `update_selftests`, `update_init_script`, `create_vm_image`, `run_vm`, `copy_logs`, `is_rel_path`, `do_update_kconfig`, `update_kconfig`, `catch`, and `main`.

## Control Flow

`main` resolves the kernel checkout, parses options for local rootfs, image update, output directory, job count, and debug shell, validates cross-compile requirements, builds a make command including `O`/`KBUILD_OUTPUT`, refreshes a cached config from BPF selftest config fragments, recompiles the kernel, creates or reuses a 2GB ext4 rootfs, rebuilds and copies selftests into `/root/bpf`, writes `/etc/rcS.d/S50-startup` to run the requested command or shell, starts QEMU, then mounts the image again to copy logs and exit status back.

## State and Persistence Behavior

Persistent state lives in `$HOME/.bpf_selftests` by default: `root.img`, `latest.config`, mounted `mnt`, timestamped logs, and exit-status files. The script mutates the rootfs image and cached kernel config. Trap cleanup unmounts the image and returns the in-VM exit status when available.

## Dependencies and Integration Points

Dependencies include QEMU for the selected platform, curl, zstd, tar, sudo mount/umount, mkfs.ext4, chattr, make, kernel build prerequisites, and libbpf CI rootfs index URLs. It integrates with the kernel tree at `tools/testing/selftests/bpf`, BPF CI rootfs artifacts, and kselftest command execution.

## Risks and Test Signals

Risks include privileged mount operations, stale rootfs indexes, missing QEMU/zstd, cross-compile mismatches, unquoted command injection in init-script generation, failed unmounts, and rootfs corruption after interrupted runs. Signals are successful kernel build, image creation/update, selftest copy, VM boot to the selected console, copied log plus exit-status file, and correct propagation of the VM command exit code.
