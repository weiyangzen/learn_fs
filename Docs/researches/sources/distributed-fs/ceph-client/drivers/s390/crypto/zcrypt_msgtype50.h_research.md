# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_msgtype50.h

## Purpose
`zcrypt_msgtype50.h` declares the public local contract for the message type 50 accelerator operations.

## Important APIs, Types, And Functions
It defines `MSGTYPE50_NAME`, `MSGTYPE50_VARIANT_DEFAULT`, `MSGTYPE50_CRB3_MAX_MSG_SIZE`, and `MSGTYPE_ADJUSTMENT`. It declares `get_rsa_modex_fc()`, `get_rsa_crt_fc()`, `zcrypt_msgtype50_init()`, and `zcrypt_msgtype50_exit()`.

## Control Flow
No runtime control flow is present. The constants guide buffer sizing, operation lookup, and user-request classification performed by `zcrypt_msgtype50.c` and the broader dispatcher.

## State And Persistence
No state is defined.

## Dependencies And Integration Points
The prototypes depend on `struct ica_rsa_modexpo` and `struct ica_rsa_modexpo_crt` from architecture zcrypt headers included by consumers. CEX4 accelerator queues use the name and variant to select these operations.

## Risks And Test Signals
Risks are signature drift and incorrect maximum message size if wire structures change. Build coverage and boundary tests around 4K CRB3 requests are the main signals.
