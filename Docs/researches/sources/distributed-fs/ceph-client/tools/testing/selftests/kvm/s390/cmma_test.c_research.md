# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/s390/cmma_test.c

## Purpose
This s390x selftest validates CMMA migration support, especially `KVM_S390_GET_CMMA_BITS`, CMMA enablement, migration mode, dirty tracking interactions, memslot holes, and initial dirty CMMA state.

## Important APIs, Types, And Functions
Important KVM interfaces are `KVM_S390_VM_MEM_ENABLE_CMMA`, `KVM_S390_VM_MIGRATION_START`, `KVM_S390_VM_MIGRATION_STATUS`, `KVM_S390_GET_CMMA_BITS`, dirty-log memslot flags, and s390 guest ESSA plus `diag 0,0,0x501` exits. Helpers create a barebones VM with a main slot and sparse test-data slot, run ESSA code, enable CMMA and migration mode, and query `struct kvm_s390_cmma_log`.

## Control Flow
`main()` requires sync regs, CMMA migration capability, and machine CMMA support, then runs four tests. `test_get_cmma_basic()` checks expected errors before CMMA or migration mode and successful peeking. `test_migration_mode()` verifies migration mode requires memory and dirty tracking and is disabled by adding or changing non-dirty-tracked memslots. `test_get_initial_dirty()` confirms all pages in both slots are initially dirty and then cleared. `test_get_skip_holes()` dirties only the sparse data slot, queries ranges across holes and gaps, and confirms KVM skips to dirty CMMA ranges correctly.

## State, Dependencies, And Integration
The main persistent-in-process buffer is `cmma_value_buf`, filled by GET_CMMA_BITS. VM state includes memslot layout, dirty logging flags, migration mode, and guest-modified CMMA attributes. The test depends on s390 CMMA hardware availability, KVM CMMA migration capability, and correct selftest barebones VM setup.

## Risks And Test Signals
Risks include machine-level CMMA absence despite kernel support, stale CMMA dirty state between queries, and off-by-one behavior across memslot holes. Test signals are exact errno expectations (`ENXIO`, `EINVAL`), migration status assertions, SIE intercept validation for `diag 0x501`, and detailed checks of `start_gfn`, `count`, `remaining`, and returned stable-state values.
