# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/s390x/uvdevice/test_uvdevice.c

## Purpose
Validates Ultravisor UAPI device input validation for attestation ioctls. It focuses on bad user pointers, invalid ioctl control blocks, invalid command encodings, invalid attestation sizes, reserved fields, and invalid attestation buffer addresses.

## Important APIs, Types, And Functions
Uses `/dev/uv`, `UVIO_IOCTL_ATT`, `struct uvio_ioctl_cb`, `struct uvio_attest`, `mmap(PROT_NONE)` fault pages, and kselftest fixtures. Fixtures are `uvio_fixture` with variant `att`, and `attest_fixture`. Helpers `att_inval_sizes_test()` and `att_inval_addr_test()` mutate size/address fields and assert errno.

## Control Flow
`main()` opens `/dev/uv` and skips if unavailable. Fixture tests call the attestation ioctl with null/faulting outer pointers, null/faulting argument pointers, invalid lengths/flags/reserved fields, and malformed ioctl command numbers/types/directions. Attestation-specific tests check zero and too-large ARCB/measurement/additional-data sizes and bad addresses for all attestation buffers.

## State And Persistence
State is fixture-local descriptors, buffers, and one PROT_NONE fault page. No persistent state is modified.

## Dependencies And Integration Points
Requires s390x UV UAPI, `/dev/uv` access, `asm/uvdevice.h`, and kselftest harness.

## Risks
The test mostly validates negative paths, not successful attestation. Fixture teardown closes `uv_fd` only if nonzero, so fd 0 would not be closed, though opening `/dev/uv` should normally return a higher fd.

## Test Signals
Expected signals are `EFAULT`, `EINVAL`, and `ENOTTY` for specific invalid inputs, plus skip message when `/dev/uv` is absent or inaccessible.
