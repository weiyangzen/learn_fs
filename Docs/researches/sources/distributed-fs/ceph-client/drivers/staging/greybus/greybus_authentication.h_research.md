# sources/distributed-fs/ceph-client/drivers/staging/greybus/greybus_authentication.h

## Purpose
User ABI header for Greybus Component Authentication Protocol ioctls. It defines certificate/authentication constants and packed ioctl payloads exchanged with the CAP character-device implementation.

## Important APIs, Types, And Functions
Defines certificate and signature maximum sizes, IMS certificate class constants, IMS certificate result codes, authentication type constants, and authentication result codes. User structs are `cap_ioc_get_endpoint_uid`, `cap_ioc_get_ims_certificate`, and `cap_ioc_authenticate`. Ioctls are `CAP_IOC_GET_ENDPOINT_UID`, `CAP_IOC_GET_IMS_CERTIFICATE`, and `CAP_IOC_AUTHENTICATE`.

## Control Flow
No executable flow. Userspace fills the packed structures and submits ioctls; the CAP driver is expected to populate result codes, certificate data, response data, and signatures.

## State And Persistence
No kernel state. This file freezes ABI sizes and field order, including fixed-size certificate and signature arrays embedded in ioctl payloads.

## Dependencies And Integration Points
Includes Linux ioctl and fixed-width type headers. It is part of the user/kernel ABI for the firmware authentication side of Greybus firmware support.

## Risks
Packed ABI structs cannot be changed without breaking userspace. Large embedded arrays make ioctl copies relatively heavy and require strict bounds checking in the implementation. Endianness expectations are implicit in fixed-width integer fields.

## Test Signals
ABI tests should validate ioctl numbers, struct sizes/offsets, max certificate/signature handling, invalid certificate/auth types, result-code propagation, and 32-bit/64-bit userspace compatibility.
