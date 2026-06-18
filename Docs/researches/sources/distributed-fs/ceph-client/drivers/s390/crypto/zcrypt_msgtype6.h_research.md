# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_msgtype6.h

## Purpose
`zcrypt_msgtype6.h` defines the local public interface and wire headers for zcrypt message type 6 CCA/EP11 handling.

## Important APIs, Types, And Functions
It defines message type names and variants (`MSGTYPE06_NAME`, default, no-RNG, EP11), `struct type6_hdr`, `struct type86_hdr`, `struct type86_fmt2_ext`, response constants `TYPE86_RSP_CODE`, `TYPE87_RSP_CODE`, `TYPE86_FMT2`, speed classes `LOW`, `MEDIUM`, `HIGH`, and prototypes for CCA, EP11, and RNG AP message preparation, speed indexing, and lifecycle registration.

## Control Flow
No executable logic exists in the header, but the wire structs define how the implementation interprets AP request/reply offsets, lengths, function codes, AP final status, and payload counts. Callers prepare AP messages through the declared helpers before dispatching through selected `zcrypt_ops`.

## State And Persistence
No state is owned by the header.

## Dependencies And Integration Points
It includes `asm/zcrypt.h` for CPRB/URB request types. The header is shared by error conversion, CCA/EP11 misc helpers, and queue/message dispatch code.

## Risks And Test Signals
Risks are packed-wire-layout drift and response constant misuse. Compile-time consumers plus integration tests with real or synthetic type 6/type 86 frames are the primary signals.
