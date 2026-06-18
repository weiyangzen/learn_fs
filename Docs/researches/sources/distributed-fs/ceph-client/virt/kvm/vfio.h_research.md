# sources/distributed-fs/ceph-client/virt/kvm/vfio.h

## Purpose
This header exposes KVM VFIO device registration to common KVM initialization while allowing builds without `CONFIG_KVM_VFIO` to compile cleanly.

## Important APIs, Types, And Functions
When `CONFIG_KVM_VFIO` is enabled, it declares `kvm_vfio_ops_init()` and `kvm_vfio_ops_exit()`. Otherwise, inline stubs return success and perform no cleanup.

## Control Flow And State
The header owns no state. It defines whether `kvm_main.c` really registers `KVM_DEV_TYPE_VFIO` during `kvm_init()` and unregisters it during `kvm_exit()`, or treats the feature as absent.

## Dependencies And Integration Points
It integrates `vfio.c` with `kvm_main.c` and Kconfig. Its include guard prevents duplicate declarations.

## Risks And Test Signals
The main risk is silent feature absence: callers must use KVM capability/device checks rather than assuming VFIO device creation is available. Build tests should include `CONFIG_KVM_VFIO=y/m` and disabled configurations.
