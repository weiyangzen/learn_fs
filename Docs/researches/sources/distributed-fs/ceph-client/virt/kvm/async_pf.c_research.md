<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/async_pf.c -->
# sources/distributed-fs/ceph-client/virt/kvm/async_pf.c

## Purpose

Provides common KVM asynchronous page fault support. It queues background work to fault in guest memory and later notifies the vCPU that the page is present or that it should retry synchronously.

## Important APIs, Types, and Functions

Source size: 241 lines, 6335 bytes. Functions/classes: kvm_async_pf_init, kvm_async_pf_deinit, kvm_async_pf_vcpu_init, async_pf_execute, kvm_destroy_vm, kvm_flush_and_free_async_pf_work, kvm_clear_async_pf_completion_queue, kvm_check_async_pf_completion, while, kvm_setup_async_pf, kvm_async_pf_wakeup_all. Includes: linux/kvm_host.h, linux/slab.h, linux/module.h, linux/mmu_context.h, linux/sched/mm.h, async_pf.h, trace/events/kvm.h.

## Control Flow and Data Flow

Setup bounds the per-vCPU queue, rejects error HVAs, allocates a work item, injects arch-specific not-present state, queues work, and increments counters. The work item pins the VM mm if possible, calls `get_user_pages_remote()`, moves itself to the done list, notifies/kicks the vCPU, and completion dequeue runs arch ready/present hooks before freeing.

## State and Persistence Behavior

Each vCPU owns async PF queue/done lists, lock, and queued count. A global kmem cache stores `struct kvm_async_pf` work items. Wake-all entries skip normal work execution.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/virt/kvm`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Lifetime spans workqueue execution, VM teardown, module unload, and vCPU completion. Queue entries must be flushed even when already done. `CONFIG_KVM_ASYNC_PF_SYNC` changes present-notification ordering.

## Test Signals

Exercise successful async faults, GUP failure, queue-full fallback, VM teardown with queued/done work, wake-all, sync and async configs, and arch dequeue blocking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/async_pf.c -->
