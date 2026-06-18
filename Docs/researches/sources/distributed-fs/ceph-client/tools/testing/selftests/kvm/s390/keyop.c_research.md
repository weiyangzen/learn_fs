# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/s390/keyop.c

## Purpose
This s390x test validates `KVM_S390_KEYOP` behavior for storage-key operations and interaction with faulted-in versus lazy guest pages.

## Important APIs, Types, And Functions
The test uses `KVM_S390_GET_SKEYS`, `KVM_S390_SET_SKEYS`, `KVM_S390_KEYOP`, `KVM_S390_VCPU_FAULT`, and capabilities `KVM_CAP_S390_KEYOP` and `KVM_CAP_S390_UCONTROL`. Local operations include `_get_skeys()`, `set_skeys()`, `do_keyop()`, `fault_in_buffer()`, and tests for RRBE, ISKE, SSKE, and initialization. Key bit masks cover access, fetch, reference, and change bits.

## Control Flow
`main()` computes a plan across all test functions and five fault-in locations per test. `run_test()` creates a barebones VM, adds anonymous memory, creates a vCPU, confirms storage keys are initially disabled, clears scratch arrays, and runs the selected test. The test cases set predictable key patterns, optionally fault pages in before, during, or after operations, invoke `KVM_S390_KEYOP` per page, compare old and new key arrays, and dump mismatches on failure.

## State, Dependencies, And Integration
The static arrays `tmp`, `old`, and `expected` are the comparison state. VM state includes a 256-page guest memory region and key state on the final 128 pages. The test depends on ucontrol storage-key support and page fault-in behavior.

## Risks And Test Signals
Risks include incorrect return of old key bits, failure to clear only RRBE's reference bit, accepting or setting the low ignored key bit, and lazy page handling bugs. Signals are per-operation pass lines for every fault-in location plus exact byte-for-byte key comparisons.
