<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/Kconfig -->
# sources/distributed-fs/ceph-client/virt/kvm/Kconfig

## Purpose

`Kconfig` is part of the common KVM virtualization core. It contributes configuration, helpers, or implementation used by architecture-specific KVM code.

## Important APIs, Types, and Functions

Source size: 120 lines, 2380 bytes. Kconfig symbols: KVM_COMMON, HAVE_KVM_PFNCACHE, HAVE_KVM_IRQCHIP, HAVE_KVM_IRQ_ROUTING, HAVE_KVM_DIRTY_RING, HAVE_KVM_DIRTY_RING_TSO, HAVE_KVM_DIRTY_RING_ACQ_REL, NEED_KVM_DIRTY_RING_WITH_BITMAP, KVM_MMIO, KVM_ASYNC_PF, KVM_ASYNC_PF_SYNC, HAVE_KVM_MSI, HAVE_KVM_READONLY_MEM, HAVE_KVM_CPU_RELAX_INTERCEPT, KVM_VFIO, HAVE_KVM_INVALID_WAKEUPS, KVM_GENERIC_DIRTYLOG_READ_PROTECT, KVM_GENERIC_PRE_FAULT_MEMORY, plus 14 more.

## Control Flow and Data Flow

Key local functions/types include none. Control flow is driven by KVM ioctls, vCPU entry/exit paths, memory-slot updates, or VM teardown depending on the file.

## State and Persistence Behavior

State is held in `struct kvm`, `struct kvm_vcpu`, per-feature lists/rings/locks, and userspace-visible ABI structures.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/virt/kvm`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

KVM code is concurrency-heavy: SRCU, spinlocks, workqueues, MMU locks, userspace ABI offsets, and teardown ordering are common failure points.

## Test Signals

Use KVM selftests, lockdep/KASAN/KCSAN builds, ioctl negative tests, VM teardown races, and architecture-specific enabled/disabled config combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/Kconfig -->
