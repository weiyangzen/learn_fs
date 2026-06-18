# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/loongarch/processor.c

## Purpose
This is the LoongArch processor backend for KVM selftests. It implements page-table setup, address translation, vCPU register/CSR initialization, exception routing, and argument passing.

## Important APIs, Types, and Functions
Page-table functions include `virt_arch_pgd_alloc()`, `virt_populate_pte()`, `virt_arch_pg_map()`, `addr_arch_gva2gpa()`, and `virt_arch_dump()`. vCPU functions include `loongarch_vcpu_setup()`, `vm_arch_vcpu_add()`, `vcpu_arch_set_entry_point()`, and `vcpu_args_set()`. Exception APIs include `route_exception()`, `vm_init_descriptor_tables()`, `vm_install_exception_handler()`, and `assert_on_unhandled_exception()`.

## Control Flow
PGD allocation prebuilds invalid page-table pages for each level. Mapping lazily allocates child tables and writes present/read/write/cache/user PTEs. vCPU setup validates guest mode, mirrors CPUCFG6, programs CRMD/PRMD/EUEN/ASID/page-walk CSRs, installs refill and general exception entries, allocates exception and runtime stacks, and assigns CPUID/TMID.

## State, Dependencies, and Integration
Static state includes `invalid_pgtable[]` and guest `exception_handlers`. It depends on LoongArch KVM register IDs, CSR helpers, `exception.S` symbols, generic VM allocation, and ucall handling.

## Risks and Test Signals
Risks include invalid table sentinel misuse, recursive dump level decrement behavior, mode assumptions limited to 16K LoongArch modes, and CSR misprogramming. Failures surface through `UCALL_UNHANDLED`, TEST_ASSERTs, or inability to translate/map guest addresses.
