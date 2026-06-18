# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/s390/processor.c

## Purpose
This is the s390x processor backend for KVM selftests. It implements s390 page tables, address translation, vCPU setup, argument passing, dumps, and default IRQ-chip reporting.

## Important APIs, Types, and Functions
`virt_arch_pgd_alloc()` allocates and invalidates the top region table. `virt_alloc_region()` allocates region/segment/page-table levels. `virt_arch_pg_map()` walks and populates region tables and leaf PTEs. `addr_arch_gva2gpa()` translates GVAs. `virt_arch_dump()` prints region/PTE state. `vm_arch_vcpu_add()`, `vcpu_arch_set_entry_point()`, `vcpu_args_set()`, and `vcpu_arch_dump()` implement vCPU integration.

## Control Flow
PGD allocation reserves four pages and fills them with invalid entries. Mapping walks four region/segment levels using 11-bit indexes, allocating invalidated child tables when needed, then writes the page table entry. VCPU setup allocates a stack, creates the vCPU, sets GPR15 stack pointer, enables floating point in CR0, points CR1 to the primary region table, and sets PSW mask for DAT and 64-bit mode.

## State, Dependencies, and Integration
State lives in the generic VM MMU fields, guest page tables, KVM regs/sregs, and `kvm_run` PSW fields. It depends on s390 page-table constants, generic allocation, and KVM register ioctls.

## Risks and Test Signals
Only 4K pages are supported. `virt_alloc_region()` clears `PAGES_PER_REGION * page_size` even for page tables, so table allocation assumptions must remain aligned with available memory. Failures assert on unsupported page size, missing mappings, or KVM register errors.
