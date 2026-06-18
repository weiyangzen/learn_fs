# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/kvm_util.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/kvm_util.h

Purpose: central KVM selftest utility API. It defines the in-process model for VMs, vCPUs, memory regions, guest modes, binary stats, ioctl wrappers, memory allocation/mapping, vCPU execution, device attributes, IRQ routing, VM creation, CPU pinning, guest-global synchronization, and architecture hooks.

Important APIs/types/functions: key state types are `struct userspace_mem_region`, `struct kvm_binary_stats`, `struct kvm_vcpu`, `struct userspace_mem_regions`, `struct kvm_mmu`, `struct kvm_vm`, `struct vcpu_reg_sublist`, `struct vcpu_reg_list`, `enum vm_guest_mode`, `struct vm_shape`, and `struct vm_guest_mode_params`. Major APIs include `kvm_check_cap`, `vm_ioctl`/`vcpu_ioctl`, `vm_enable_cap`, `vm_set_memory_attributes`, `vm_guest_mem_fallocate`, dirty-log/ring helpers, `vm_get_stats_fd`, IRQFD helpers, stats descriptor/data readers, `vm_create_irqchip`, guest memfd helpers, memory-region add/move/delete/reload, guest virtual/physical allocators, `virt_map`, address conversion helpers, `vcpu_run`, register/device-attribute wrappers, device creation, IRQ routing, VM creation families, CPU pinning, page-count conversion, `sync_global_to_guest`, `write_guest_global`, `vm_vcpu_add`, arch page-table hooks, `kvm_selftest_arch_init`, and release/finalize hooks.

Control flow and state: tests open `/dev/kvm`, create a VM shape, add memory regions tracked by GPA/HVA trees and slot hash, create vCPUs tracked on the VM, map guest virtual pages using arch hooks, run vCPUs through `KVM_RUN`, and interpret exits through common utilities. State persistence is process-local and fd-backed: VM/vCPU fds, mmaped `kvm_run`, sparsebit allocation maps, dirty-ring buffers, binary stats fds/descriptors, memfd-backed guest memory, and per-VM mode/type fields.

Dependencies and integration: depends on Linux KVM uAPI, local kernel-style list/rbtree/hashtable headers, `test_util.h`, `kvm_syscalls.h`, `kvm_util_arch.h`, `kvm_util_types.h`, and `sparsebit.h`. It is the primary integration point for all architecture headers and almost every KVM selftest.

Risks: ioctl wrappers assert by default, so negative tests must use raw underscore forms. Memory-region state must stay synchronized with KVM memslot ioctls and host mappings. Protected-memory flows currently assert that only private/no attributes are used. VM-killed detection relies on probing `KVM_CAP_USER_MEMORY` after `-EIO`. Architecture hooks must preserve common invariants for page size, address tagging, vCPU init, and IRQ chip support.

Test signals: almost all KVM selftests compile through this header. Direct signals include VM creation tests, memory-mapping tests, dirty-log/ring tests, IRQFD/routing tests, binary stats tests, guest memfd/private memory tests, vCPU state save/restore tests, and arch page-table tests.
