# sources/distributed-fs/ceph-client/tools/testing/selftests/kho/arm64.conf

`arm64.conf` provides AArch64-specific settings for the Kexec Handover QEMU selftest. It is sourced by `vmtest.sh`.

It defines `QEMU_CMD="qemu-system-aarch64 -M virt -cpu max"`, serial console Kconfig for PL010 and PL011, `KERNEL_IMAGE="Image"`, and `KERNEL_CMDLINE="console=ttyAMA0"`.

There is no control flow beyond shell variable assignment. Dependencies are `qemu-system-aarch64`, an arm64 kernel build, and working AMBA serial console support. It integrates with `vmtest.sh` build, initrd, and QEMU launch logic.

Risks are unavailable QEMU machine/CPU settings or missing serial console output. Pass signal is QEMU serial output containing the KHO restore success marker under these settings.
