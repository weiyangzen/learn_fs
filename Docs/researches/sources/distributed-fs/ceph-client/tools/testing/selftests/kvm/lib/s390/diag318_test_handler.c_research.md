# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/s390/diag318_test_handler.c

## Purpose
This s390x helper obtains DIAGNOSE 0x0318 information through an ad-hoc KVM VM so tests can verify or use the userspace-handled instruction payload.

## Important APIs, Types, and Functions
`guest_code()` executes `diag 0,0,0x318` with a known info value. `diag318_handler()` creates a one-vCPU VM, runs it, validates `KVM_EXIT_S390_SIEIC`, extracts the register encoded in IPA, reads the GPR value, and frees the VM. `get_diag318_info()` caches and returns the value, or returns zero if `KVM_CAP_S390_DIAG318` is unsupported.

## Control Flow
The first successful caller probes KVM capability, runs the temporary VM until the diagnose intercept, validates intercept code and IPA, reads the info register, asserts nonzero, caches it, and returns it. Later calls reuse the cached value.

## State, Dependencies, and Integration
Persistent state is static cached `diag318_info` and `printed_skip`. It depends on s390 KVM exit layout, generic VM creation, and kselftest skip-style messaging.

## Risks and Test Signals
If KVM lacks the capability, tests receive zero and a single skip message. Incorrect intercept decoding or zero payload causes assertions, which protects callers from silently using invalid diagnostic data.
