# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/s390/ucall.c

## Purpose
This s390x ucall backend decodes selftest ucalls from DIAGNOSE instruction intercepts delivered as `KVM_EXIT_S390_SIEIC`.

## Important APIs, Types, and Functions
`ucall_arch_get_ucall()` checks for intercept code 4, DIAGNOSE IPA class `0x83`, and IPB function `0x501`. It extracts the register number from IPA and returns the guest pointer stored in that GPR.

## Control Flow
On each KVM exit, generic ucall handling delegates here. Matching DIAGNOSE exits produce a payload pointer; all other exits return NULL for higher-level handling.

## State, Dependencies, and Integration
There is no persistent state. The backend depends on s390 KVM run-structure fields and the guest-side ucall convention of placing the pointer in the IPA-selected GPR.

## Risks and Test Signals
The decoder is tightly coupled to the DIAGNOSE encoding. Encoding drift or wrong register selection causes missing ucalls, usually observed as unexpected exit reasons or failed guest synchronization.
