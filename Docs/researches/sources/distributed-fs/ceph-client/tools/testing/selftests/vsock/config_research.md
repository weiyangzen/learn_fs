# sources/distributed-fs/ceph-client/tools/testing/selftests/vsock/config

## Purpose

`config` is the kernel configuration fragment used by the vsock VM test harness when `vmtest.sh -b` asks virtme-ng to generate a test kernel config. It enables VM boot support, tracing/BPF, networking, virtio, multiple vsock transports, filesystems, and the i6300esb watchdog used by the test environment.

## Important APIs, Types, and Functions

This is declarative Kconfig input rather than executable code. Important symbols include `CONFIG_VSOCKETS`, `CONFIG_VSOCKETS_DIAG`, `CONFIG_VSOCKETS_LOOPBACK`, `CONFIG_VMWARE_VMCI_VSOCKETS`, `CONFIG_VIRTIO_VSOCKETS`, `CONFIG_HYPERV_VSOCKETS`, `CONFIG_VHOST_VSOCK`, `CONFIG_VIRTIO_NET`, `CONFIG_NET_9P`, `CONFIG_9P_FS`, `CONFIG_KVM_GUEST`, `CONFIG_KVM_INTEL`, `CONFIG_KVM_AMD`, `CONFIG_FW_CFG_SYSFS`, `CONFIG_DEBUG_FS`, `CONFIG_SECURITYFS`, and `CONFIG_I6300ESB_WDT`.

## Control Flow

The fragment is consumed by `vng --kconfig --config ...` from `vmtest.sh`. virtme-ng merges the requested symbols with architecture defaults and later builds the kernel. Runtime scripts rely on the resulting kernel to expose vsock, network namespace, virtio, SSH/9p support, and diagnostics.

## State and Persistence Behavior

The file has no runtime state. It influences the generated `.config` and built kernel image in the caller's kernel tree.

## Dependencies and Integration Points

It integrates the VM test with virtme-ng, QEMU, virtio devices, vsock transport modules, debug/sysfs interfaces, and ordinary guest networking/storage facilities. The selected symbols are broader than vsock alone because the harness also needs SSH, user networking, 9p/shared directories, and diagnostics.

## Risks and Edge Cases

Some symbols are architecture- or dependency-sensitive and may be ignored if prerequisites are unavailable. Enabling several vsock transports broadens coverage but can also change module probing and warning surface. This fragment is not a minimal production config.

## Test Signals

A useful validation signal is that `vng --kconfig --config tools/testing/selftests/vsock/config` produces a bootable kernel where `vmtest.sh` can load/use virtio-vsock, loopback vsock, net namespaces, SSH, debugfs, and dmesg checks.
