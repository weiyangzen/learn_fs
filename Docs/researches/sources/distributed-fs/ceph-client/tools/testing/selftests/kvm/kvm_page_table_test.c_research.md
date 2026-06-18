# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/kvm_page_table_test.c

## Purpose
This test stresses KVM page-table creation, dirty-logging updates, huge-page splitting, and mapping coalescing across guest modes and backing sources. It is aimed at bugs such as stale TLB entries after block mappings are split and later coalesced.

## Important APIs, Types, and Functions
`enum test_stage` defines the guest access phases. `struct test_args` is shared with the guest and stores VM, page sizes, page counts, memory backing, and vCPU pointers. `guest_code()` performs read/write patterns. `vcpu_worker()` runs a vCPU per host thread. `pre_init_before_test()` creates the VM, adds the test memslot, maps GVA to GPA, initializes semaphores, and exports globals. `run_test()` sequences all stages and toggles `KVM_MEM_LOG_DIRTY_PAGES`.

## Control Flow
`main()` parses `-p`, `-m`, `-b`, `-v`, and `-s`, appends supported guest modes, and invokes `run_test()` for each enabled mode. `run_test()` starts vCPU threads at `KVM_BEFORE_MAPPINGS`, then drives `KVM_CREATE_MAPPINGS`, enables dirty logging and drives `KVM_UPDATE_MAPPINGS`, disables dirty logging and drives `KVM_ADJUST_MAPPINGS`, then tears down all threads and semaphores.

## State, Dependencies, and Integration
Host and guest coordinate through shared `guest_test_stage`, exported `test_args`, and two POSIX semaphores. It depends on `guest_modes`, `kvm_util`, `processor`, backing-source helpers, ucall syncs, pthreads, and KVM memslot flag updates.

## Risks and Test Signals
The test is sensitive to memory size alignment, guest physical placement, hugepage availability, vCPU count, and host backing type. Success is each vCPU reporting `UCALL_SYNC` for every stage without unexpected exits; timing logs are diagnostic rather than pass criteria.
