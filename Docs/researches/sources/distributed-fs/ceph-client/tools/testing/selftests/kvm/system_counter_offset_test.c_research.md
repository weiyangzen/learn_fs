# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/system_counter_offset_test.c

## Purpose
This x86-only test verifies userspace adjustment of the guest-visible system counter by setting the vCPU TSC offset and checking guest `rdtsc()` observations against host-computed ranges.

## Important APIs, Types, And Functions
It uses `KVM_VCPU_TSC_CTRL`, `KVM_VCPU_TSC_OFFSET`, `vcpu_device_attr_set()`, `__vcpu_has_device_attr()`, `rdtsc()`, and `GUEST_SYNC_ARGS`. `struct test_case` contains a `tsc_offset`; test cases cover zero, +180 seconds, and -180 seconds in nanosecond units.

## Control Flow
`main()` creates a one-vCPU VM, checks that the TSC offset device attribute is supported, then enters the guest once per test case. Before each run, the host sets the offset, records a start value as `rdtsc() + offset`, runs the guest, records an end value the same way, and handles the guest sync. The guest loops through test cases and sends its raw `rdtsc()` value; the host asserts it lies within the computed start/end window.

## State, Dependencies, And Integration
State is limited to the static test-case table and vCPU TSC offset attribute. There is no persistent state. The test depends on x86 KVM TSC offset device attributes and stable enough host/guest TSC reads to form an enclosing range.

## Risks And Test Signals
Risks include unit ambiguity in offset values, unsupported attribute handling, and TSC instability on unsuitable hosts. Signals are precondition skip on missing attr, exact range assertions, and printed observed/expected counter ranges.
