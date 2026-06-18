# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5.h

## Purpose
Declares low-level Wave5 backend operations and hardware-facing constants used by the higher-level API. It bridges frontend/API code to register/firmware command implementation.

## Important APIs, Types, and Functions
Defines sub-sampled buffer sizing macros, bitstream option bits, endian configuration constants, WTL constants, rotation/mirror mode encodings, and prototypes for VPU init, sleep/wake, reset, version, decoder commands, interrupt clear, read/write pointer operations, encoder build/init/register/encode/result/finish/check operations.

## Control Flow
No implementation here. The declared backend calls form the firmware command sequence used by `wave5-vpuapi.c`: initialize, build instance parameters, issue sequence init, register framebuffers, submit pictures, collect results, and finish sequences.

## State and Persistence
No state. It defines constants that affect how backend code programs hardware registers and firmware command memory.

## Dependencies and Integration Points
Depends on `struct vpu_device`, `struct vpu_instance`, and codec structs from `wave5-vpuapi.h`. Called by platform initialization and encoder/decoder API wrappers.

## Risks
Backend prototypes are central coupling points; signature changes ripple widely. Hard-coded big-endian register write constants are a hardware assumption that should be validated on any new integration. Rotation/mirror constants must match firmware PRP encodings.

## Test Signals
Compile/link coverage with backend implementation, firmware init/sleep/wake/reset smoke tests, encode/decode command submission, bitstream EOS behavior, and rotation/mirror encode tests.
