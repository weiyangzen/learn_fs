# sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/uvdevice.h

## Purpose
Defines the user ABI for the s390 Ultravisor character device `/dev/uv`. It describes the common ioctl control block, attestation argument layout, device capability query result, ioctl numbers, supported-call bit definitions, and intentionally generous maximum buffer sizes for attestation and secret-management requests.

## Important APIs, Types, And Functions
The central ABI type is `struct uvio_ioctl_cb`, an `_IOWR` wrapper carrying flags, returned Ultravisor rc/rrc values, a userspace argument pointer, and argument length. `struct uvio_attest` describes attestation input and output buffers. `struct uvio_uvdev_info` returns the device and Ultravisor support masks. `UVIO_IOCTL_*` macros encode the ioctl commands, while `UVIO_SUPP_*` exposes bit positions for capability reporting.

## Control Flow
This header has no executable control flow. Userspace issues one of the `UVIO_IOCTL_*` commands with a `uvio_ioctl_cb`; the kernel uvdevice driver validates the wrapper, copies the command-specific argument from `argument_addr`, executes the matching UV call when supported, and reports UV return information in `uv_rc` and `uv_rrc`.

## State And Persistence
No state is stored in the header. Runtime state lives in the uvdevice driver and firmware. The ABI is persistent because field sizes, ioctl numbers, and bit positions are user-visible and must remain stable.

## Dependencies And Integration Points
Depends on Linux UAPI integer types and ioctl encoding. It integrates userspace confidential-computing tools with the s390 Ultravisor, especially attestation and protected-secret workflows.

## Risks And Edge Cases
`UVIO_SUPP_UDEV_INFO` uses `UVIO_IOCTL_UDEV_INFO_NR`, while the enum spells `UVIO_IOCTL_UVDEV_INFO_NR`; this is a typo-like ABI risk unless hidden by another definition. Buffer limit changes are ABI-sensitive. User pointers are 64-bit integer fields, so compat handling and zeroed reserved bytes matter.

## Test Signals
Useful signals are UAPI compile tests, ioctl number stability checks, uvdevice selftests for unsupported commands, reserved-field rejection, oversized buffers, UV rc/rrc propagation, and attestation/secret commands on supported hardware or firmware simulators.
