# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/s390/cpumodel_subfuncs_test.c

## Purpose
This s390x test compares KVM-reported CPU subfunction data with data obtained by executing matching query instructions on the host CPU. It verifies the CPU model ioctl exposes unmasked machine subfunction information consistently with hardware.

## Important APIs, Types, And Functions
The central ioctl is `KVM_S390_VM_CPU_MACHINE_SUBFUNC` under `KVM_S390_VM_CPU_MODEL`, filling `struct kvm_s390_vm_cpu_subfunc`. The file uses inline assembly query blocks for PLO, KMAC, KMC, KM, KIMD, KLMD, KMCTR, KMF, KMO, PCC, PRNO/PPNO, KMA, KDSA, SORTL, DFLTCC, and PFCR. `test_facility()` gates each case by facility bit.

## Control Flow
`main()` creates a VM, retrieves `cpu_subfunc`, and iterates `testlist`. For installed facilities, it allocates a scratch array of the same size as the reported subfunction array, executes the instruction-specific query block, compares the result with `memcmp()`, and reports pass. If the required facility bit is unavailable, the case is skipped.

## State, Dependencies, And Integration
The global `cpu_subfunc` stores KVM's CPU-model view. Scratch arrays are transient per test. The test depends on s390 facility-bit detection, correct inline instruction encodings, and the fact that KVM currently does not mask the queried instruction data in the CPU model.

## Risks And Test Signals
Risks include future KVM CPU-model masking policy changes, facility-bit mismatches, or wrong inline assembly constraints corrupting query buffers. Signals are exact byte-for-byte equality between ioctl data and hardware query output, with kselftest skip/pass lines per subfunction.
