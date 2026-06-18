# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/memstress.c

## Purpose
This file implements reusable memory-stress VM setup and vCPU-thread orchestration for KVM selftests that dirty, read, and fault large guest memory regions.

## Important APIs, Types, and Functions
`memstress_guest_code()` performs guest memory accesses. `memstress_create_vm()` creates the VM, extra memslots, mappings, vCPU args, optional nested setup, and guest globals. `memstress_setup_vcpus()` partitions or shares test memory. Thread helpers include `memstress_start_vcpu_threads()` and `memstress_join_vcpu_threads()`. Dirty-log helpers enable/disable logging, get/clear bitmaps, and allocate/free bitmap arrays.

## Control Flow
VM creation computes guest pages from vCPU memory size and guest mode, reserves nested overhead if needed, creates vCPUs, places test memory near the top of GPA space, adds one or more test memslots, maps them at `DEFAULT_GUEST_TEST_MEM`, sets per-vCPU GVA/GPA/page ranges, and syncs `memstress_args`. Guest code repeatedly touches args pages, then iterates assigned pages randomly or sequentially with read/write probability, ending each pass with `GUEST_SYNC(1)`.

## State, Dependencies, and Integration
Global `memstress_args`, static vCPU thread records, a test vCPU array, and callback pointer store runtime state. It depends on `kvm_util`, `processor`, guest RNG, backing-source helpers, pthreads, bitmap helpers, and weak nested-virtualization hooks.

## Risks and Test Signals
Risks include invalid alignment, uneven slot division, excessive requested GPA space, busy-wait thread synchronization, and architecture gaps for nested support. Test signals are ucall syncs, dirty bitmap contents, and assertions during VM setup.
