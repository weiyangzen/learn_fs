# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_cex4.h

## Purpose
`zcrypt_cex4.h` is the small local header for the CEX4+ AP driver module. It exposes module lifecycle functions to the rest of the zcrypt build.

## Important APIs, Types, And Functions
The header declares `zcrypt_cex4_init()` and `zcrypt_cex4_exit()`. It has a conventional include guard and no data structures.

## Control Flow
There is no runtime control flow. The declarations correspond to driver registration and unregistration in `zcrypt_cex4.c`.

## State And Persistence
No state is defined in the header. Module state is owned by the source file and zcrypt/AP subsystems.

## Dependencies And Integration Points
Consumers can include this header to call CEX4+ initialization or teardown from aggregate zcrypt initialization paths. In this snapshot, the source also uses `module_init()`/`module_exit()`.

## Risks And Test Signals
Risk is limited to declaration/signature drift relative to `zcrypt_cex4.c`. Build coverage catches mismatches.
