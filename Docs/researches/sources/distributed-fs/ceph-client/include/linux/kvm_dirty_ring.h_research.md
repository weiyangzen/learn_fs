# sources/distributed-fs/ceph-client/include/linux/kvm_dirty_ring.h

## Purpose

`kvm_dirty_ring.h` declares KVM's per-VM or per-vCPU dirty page ring interface. It supports dirty logging through a compact ring of `struct kvm_dirty_gfn` entries, with bitmap fallback stubs when the architecture does not support dirty rings. The source was read as a complete 94-line file.

## Important APIs, Types, and Functions

`struct kvm_dirty_ring` stores `dirty_index`, `reset_index`, ring `size`, `soft_limit`, pointer to `dirty_gfns`, and ring `index`. APIs include `kvm_cpu_dirty_log_size()`, `kvm_use_dirty_bitmap()`, `kvm_arch_allow_write_without_running_vcpu()`, `kvm_dirty_ring_get_rsvd_entries()`, `kvm_dirty_ring_alloc()`, `kvm_dirty_ring_reset()`, `kvm_dirty_ring_push()`, `kvm_dirty_ring_check_request()`, `kvm_dirty_ring_get_page()`, and `kvm_dirty_ring_free()`, with no-op or fallback stubs under `!CONFIG_HAVE_KVM_DIRTY_RING`.

## Control Flow

KVM allocates a ring, pushes dirty GFNs as guest pages become dirty, exits to userspace when the soft limit is reached, and userspace harvests entries. Reset paths re-enable dirty trapping for consumed entries and advance `reset_index`.

## State and Persistence Behavior

Ring indices are free-running counters and the `dirty_gfns` buffer persists while the VM/vCPU dirty ring is allocated. Dirty information is transient migration/logging state, not durable storage.

## Dependencies and Integration Points

It depends on `linux/kvm.h`, KVM VM/vCPU structs, architecture dirty-ring support, vm_operations page lookup, and dirty logging/migration userspace ABI.

## Risks and Edge Cases

Reserved entries and soft limits must prevent producer overrun. Unsupported architectures must fall back to dirty bitmaps. Reset must match userspace harvest order to avoid losing dirty information or re-enabling writes too early.

## Test Signals

KVM dirty-ring selftests, live migration dirty logging tests, ring full/soft-limit tests, reset/retrap tests, mmap page lookup tests, and dirty-bitmap fallback builds are useful.
