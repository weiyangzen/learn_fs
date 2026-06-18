# sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/virtio-ccw.h

## Purpose
Provides the small s390 virtio-ccw UAPI shared by KVM, guest kernels, and userspace tooling. It fixes the virtqueue ring alignment and the diagnose 0x500 subcode used to notify virtio-ccw devices.

## Important APIs, Types, And Functions
The exported constants are `KVM_VIRTIO_CCW_RING_ALIGN`, set to 4096 bytes, and `KVM_S390_VIRTIO_CCW_NOTIFY`, set to subcode 3. There are no functions or structs.

## Control Flow
There is no control flow. Guest or userspace virtio setup code allocates vrings with the required alignment and uses the notify subcode when issuing the s390 virtio diagnose hypercall.

## State And Persistence
No runtime state is owned here. The constants are persistent ABI and must not change without breaking existing guests or hypervisors.

## Dependencies And Integration Points
Integrates the virtio-ccw transport with KVM s390 diagnose 0x500 handling and vring layout assumptions. The permissive dual license supports both Linux and non-Linux consumers.

## Risks And Edge Cases
Changing alignment or subcode values would break device notification and shared-memory layout. Tests should also catch accidental include-guard or license regressions because this header is consumed outside the kernel tree.

## Test Signals
Signals include virtio-ccw guest boot, KVM unit tests for diagnose 0x500 notify, vring alignment assertions, and UAPI header install/build checks.
