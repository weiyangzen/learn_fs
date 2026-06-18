<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/dirty_ring.c -->
# sources/distributed-fs/ceph-client/virt/kvm/dirty_ring.c

## Purpose

Implements common KVM dirty-ring tracking, where vCPU threads append dirtied GFNs to a ring and userspace harvests and resets entries for migration/logging.

## Important APIs, Types, and Functions

Source size: 272 lines, 7344 bytes. Functions/classes: kvm_cpu_dirty_log_size, kvm_dirty_ring_get_rsvd_entries, kvm_use_dirty_bitmap, kvm_arch_allow_write_without_running_vcpu, kvm_dirty_ring_used, kvm_dirty_ring_soft_full, kvm_dirty_ring_full, kvm_reset_dirty_gfn, kvm_dirty_ring_alloc, kvm_dirty_gfn_set_invalid, kvm_dirty_gfn_set_dirtied, kvm_dirty_gfn_harvested, kvm_dirty_ring_reset, while, if, if, if, if, plus 3 more. Includes: linux/kvm_host.h, linux/kvm.h, linux/vmalloc.h, linux/kvm_dirty_ring.h, trace/events/kvm.h, kvm_mm.h.

## Control Flow and Data Flow

Allocation vzallocs a ring and computes the soft limit. `kvm_dirty_ring_push()` writes slot/offset, publishes dirty flags with ordering, advances `dirty_index`, and requests a soft-full exit. `kvm_dirty_ring_reset()` scans harvested entries, invalidates them, batches nearby GFNs per memslot into bitmasks, and re-enables dirty logging in the MMU.

## State and Persistence Behavior

Per-ring state includes `dirty_gfns`, size, soft limit, dirty/reset indices, and vCPU ring index. Userspace observes flags and marks entries reset; kernel reset runs under `slots_lock`.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/virt/kvm`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Reset batching must handle forward/backward offsets without overflow. Ring-full conditions should be prevented by soft limits and reserved entries. Memory ordering on flags is the userspace ABI.

## Test Signals

Test wraparound, soft-full exits, reset batching in one slot and across slots, invalid slot/offset handling, signal interruption, bitmap fallback modes, and userspace harvest/reset ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/dirty_ring.c -->
