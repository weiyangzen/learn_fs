# sources/distributed-fs/ceph-client/include/linux/hugetlb_inline.h

## Purpose
Provides minimal inline predicates for identifying hugetlb VMAs and VMA flag sets without pulling in the full hugetlb header.

## APIs, Control Flow, and State
The enabled path maps `is_vm_hugetlb_flags()` to `VM_HUGETLB` and `is_vma_hugetlb_flags()` to the VMA flag bitset helper `vma_flags_test_any(..., VMA_HUGETLB_BIT)`. `is_vm_hugetlb_page()` applies the raw `vm_flags` test to a `vm_area_struct`. In !`CONFIG_HUGETLB_PAGE` builds, all tests return false. There is no persistent state.

## Dependencies, Integration, Risks, and Tests
Depends only on `linux/mm.h` definitions. It is included by broader MM headers to avoid include cycles while still allowing cheap hugetlb decisions. Risks are mostly config-sensitive: code using this predicate must tolerate all-false results when hugetlb is compiled out. Test signals are compile coverage across hugetlb-enabled and disabled builds and VMA classification checks in mmap/unmap paths.
