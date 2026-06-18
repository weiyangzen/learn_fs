# sources/distributed-fs/ceph-client/tools/testing/selftests/wireguard/qemu/Makefile

## Purpose

This Makefile builds and runs the WireGuard QEMU selftest environment. It downloads fixed userspace/toolchain distfiles, builds a minimal cross-compiled userspace and kernel with an initramfs containing `init`, `netns.sh`, and required tools, then boots the result under QEMU and checks for a `success` marker.

## Important APIs, Types, and Functions

The Makefile defines download macros `tar_download` and `file_download`, architecture mapping variables such as `CHOST`, `QEMU_ARCH`, `KERNEL_ARCH`, `KERNEL_BZIMAGE`, `QEMU_MACHINE`, and build variables such as `KERNEL_PATH`, `BUILD_PATH`, `DISTFILES_PATH`, `NR_CPUS`, `CROSS_COMPILE`, `CC`, `CFLAGS`, and `LDFLAGS`. Targets build iperf3, bash, iproute2 `ip`/`ss`, iptables legacy multi-call binary, nmap `ncat`, iputils `ping`, wireguard-tools `wg`, the local `init.c`, the initramfs cpio spec, kernel config, kernel image, and `qemu`.

## Control Flow

The default target is `qemu`. Distfile targets download from `download.wireguard.com` first and upstream mirrors second, then verify SHA-256. Architecture conditionals select the cross toolchain, kernel image path, QEMU machine/cpu options, and special command-line handling. The initramfs spec embeds `/init`, `/init.sh` from `../netns.sh`, tool binaries, libc, symlinks, and device nodes. Kernel config is produced by `allnoconfig` plus merges of `kernel.config`, architecture config, initramfs settings, and optional debug config. The QEMU target boots the image for up to 20 minutes, writes a result virtio/serial chardev to `$(BUILD_PATH)/result`, and greps for `success`.

## State and Persistence Behavior

Persistent build cache lives under `$(BUILD_PATH)`, downloaded archives under `$(DISTFILES_PATH)`, and optional `ccache` under `$(CCACHE_DIR)`. `clean`, `distclean`, and `cacheclean` remove increasingly broad state. The target writes `$(BUILD_PATH)/result` for QEMU success detection.

## Dependencies and Integration Points

It depends on host `make`, `gcc`, `wget`, `flock`, `sha256sum`, `tar`, QEMU for the selected architecture, kernel source tree, and optional `ccache`. It integrates with kernel header installation, cross musl toolchains, autotools/configure-based packages, and QEMU serial/virtio console success reporting.

## Risks and Edge Cases

The Makefile downloads and builds old pinned userspace package versions, so upstream URL changes or checksum mismatch will fail builds. It uses `sed -i` patches on extracted packages. Cross-architecture support is extensive but brittle around host/target matching, KVM availability, QEMU machine support, and architecture-specific config fragments. `qemu` requires the guest to write `success`; otherwise the final grep fails even if boot mostly worked.

## Test Signals

Pass signals are successful verified downloads, installed toolchain, built static userspace tools, generated initramfs spec, merged kernel config, built kernel image, QEMU exiting within timeout, and `success` present in `$(BUILD_PATH)/result`.
