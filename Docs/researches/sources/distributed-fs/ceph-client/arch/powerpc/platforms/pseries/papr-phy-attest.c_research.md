# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-phy-attest.c

## Purpose
Implements `/dev/papr-physical-attestation`, allowing userspace to submit a physical attestation command and read the complete RTAS response through an fd-backed blob.

## Important APIs, Types, And Functions
Key pieces are `struct rtas_phy_attest_params`, `rtas_physical_attestation`, `phy_attest_sequence_begin`, `phy_attest_sequence_end`, `phy_attest_sequence_fill_work_area`, `papr_phy_attest_create_handle`, `papr_phy_attest_dev_ioctl`, and the common read/seek/release handlers from `papr-rtas-common.c`.

## Control Flow
The ioctl copies a `papr_phy_attest_io_block` from userspace, derives the command length, and constructs a `papr_rtas_sequence`. The begin callback locks the physical-attestation RTAS lock, allocates a 4K work area, copies the command into it, and initializes sequence state. The work callback calls RTAS until more-data or complete states stop, appending only the reported bytes. The common setup helper returns an anonymous fd containing the immutable response blob.

## State And Persistence
State is per ioctl: allocated params, RTAS work area, sequence number, bytes written, and a blob attached to the returned fd. No durable storage is written. Firmware attestation state is accessed transiently.

## Dependencies And Integration Points
Depends on RTAS `ibm,physical-attestation`, RTAS work areas, `rtas_ibm_physical_attestation_lock`, uapi `papr-physical-attestation`, miscdevice/ioctl, and common PAPR RTAS sequence helpers.

## Risks And Edge Cases
The command length comes from a big-endian user-provided field and is copied into a 4K work area; bounds depend on the uapi structure size and firmware behavior. The code warns and aborts if firmware reports more bytes than the work area. A copy-from-user failure leaks the allocated params in this source as written because the early return occurs before sequence cleanup.

## Test Signals
Test missing RTAS token, valid multi-part attestation responses, invalid parameters, hardware errors, reported length exceeding work area, fatal signal interruption during common retries, copy-from-user failure, read/seek/release behavior, and repeated concurrent ioctls serialized by the RTAS lock.
