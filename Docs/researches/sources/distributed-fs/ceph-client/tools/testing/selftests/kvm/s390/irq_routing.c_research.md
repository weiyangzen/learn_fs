# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/s390/irq_routing.c

## Purpose
This s390x test verifies validation of adapter IRQ routing summary and indicator offsets passed through `KVM_SET_GSI_ROUTING`.

## Important APIs, Types, And Functions
It uses `KVM_CAP_IRQ_ROUTING`, `kvm_gsi_routing_create()`, `struct kvm_irq_routing_entry` with `KVM_IRQ_ROUTING_S390_ADAPTER`, and `__vm_ioctl(vm, KVM_SET_GSI_ROUTING, routing)`. The guest only issues `diag 0,0,0` and loops; routing validation is the real target.

## Control Flow
`main()` requires IRQ routing and sets a four-test TAP plan. `test()` creates a one-vCPU VM, allocates guest physical pages, constructs one adapter route with summary and indicator addresses, and tries offsets that are outside and then inside the target page for both summary and indicator. It expects `EINVAL` for outside-page offsets and success after subtracting four bytes.

## State, Dependencies, And Integration
State is limited to the dynamically allocated routing table and VM memory. The test integrates with generic KVM routing selftest helpers and s390 adapter-interrupt UAPI.

## Risks And Test Signals
Risks are boundary validation regressions allowing offsets beyond the page or rejecting valid near-end offsets. Signals are four kselftest results named for summary/indicator offset inside/outside page behavior.
