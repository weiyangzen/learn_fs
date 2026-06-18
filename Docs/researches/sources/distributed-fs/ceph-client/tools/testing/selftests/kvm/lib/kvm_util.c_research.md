# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/kvm_util.c

## Purpose
This is the central KVM selftest utility implementation. It handles `/dev/kvm` access, capability probing, VM and vCPU lifecycle, guest memory registration, virtual/physical allocation, address translation, device attributes, IRQ routing, dirty-ring mapping, stats, signal handling, and architecture hook dispatch.

## Important APIs, Types, and Functions
Creation flows through `____vm_create()`, `__vm_create()`, `__vm_create_with_vcpus()`, and `__vm_vcpu_add()`. Memory APIs include `vm_mem_add()`, `vm_userspace_mem_region_add()`, `memslot2region()`, `vm_mem_region_set_flags()`, `vm_mem_region_delete()`, `__vm_phy_pages_alloc()`, `virt_map()`, `addr_gpa2hva()`, `addr_hva2gpa()`, and `addr_gva2hva()`. Other major APIs include `kvm_check_cap()`, `kvm_set_files_rlimit()`, `_vcpu_run()`, `vcpu_run()`, device attribute wrappers, IRQ routing helpers, `vm_dump()`, and binary stats readers.

## Control Flow
VM creation initializes mode-derived address properties, opens KVM, sets up valid GVA bitmaps, creates slot 0 with `KVM_SET_USER_MEMORY_REGION2`, loads the ELF image, initializes ucall MMIO, seeds guest RNG state, and invokes architecture post-create hooks. VCPU creation creates the KVM vCPU fd, maps `struct kvm_run`, attaches stats, and links into the VM list. Memory creation allocates host backing, optional memfd/guest_memfd, registers a memslot, and indexes it by GPA, HVA, and slot.

## State, Dependencies, and Integration
`struct kvm_vm` owns file descriptors, memslot hash/tree indexes, sparsebit allocators, vCPU list, stats cache, and architecture fields. `struct userspace_mem_region` persists backing mappings, aliases, guest_memfd state, and allocation bitmaps. The file depends on Linux KVM ioctls, sparsebit/rbtree/list/hash helpers, architecture weak hooks, ucall, ELF loading, and kselftest utilities.

## Risks and Test Signals
The biggest risks are stale region indexes, overlapping memslots, incorrect page-count adjustment across host/guest page sizes, guest_memfd ownership mistakes, and architecture hook assumptions. Assertions and VM dumps provide strong failure signals; constructor signal handlers turn unexpected SIGBUS/SIGSEGV/SIGILL/SIGFPE into test failures.
