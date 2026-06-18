# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_msgtype6.c

## Purpose
`zcrypt_msgtype6.c` implements message type 6 operations for CEXxC CCA coprocessors and CEXxP EP11 adapters. It handles RSA modexpo/CRT through CCA CPRBX frames, generic CCA `send_cprb`, EP11 `send_ep11_cprb`, hardware RNG requests, reply conversion, speed-index classification, and registration of default and EP11 zcrypt ops variants.

## Important APIs, Types, And Functions
Visible helper APIs are `speed_idx_cca()`, `speed_idx_ep11()`, `prep_cca_ap_msg()`, `prep_ep11_ap_msg()`, `prep_rng_ap_msg()`, `zcrypt_msgtype6_init()`, and `zcrypt_msgtype6_exit()`. Key internal functions convert ICA MEX/CRT to type 6, convert generic XCRB and EP11 URB requests to AP messages, convert type 86 replies for ICA/XCRB/EP11/RNG, receive tasklet callbacks, and send queued requests. Important wire views include `type86x_reply`, `type86_ep11_reply`, and embedded CPRBX/EP11 CPRB payload overlays.

## Control Flow
RSA paths build type 6 CCA messages using static headers, static CPRBX values, and function/rule blocks (`PK`/`MRP` for modexpo, `PD`/`ZERO-PAD` for CRT), copy input data from user space, append encoded keys, queue the AP message, and copy response data back after type 86 conversion. Generic CCA XCRB preparation aligns control/data lengths, checks overflow, copies request CPRB/data from user or kernel address space, extracts function code/domain, and sets AP message flags for usage/admin/special handling. EP11 preparation validates CPRB/payload length formats, extracts the EP11 function ID, marks admin/usage, and later rewrites non-management target domain fields to the queue domain before sending. RNG preparation builds an `RL`/`RANDOM` CPRB and returns copied random data from type 86 count2.

## State And Persistence
The file keeps static registered ops and an atomic PSMID sequence. It can mark queues offline and emit uevents on unknown or firmware-failure replies. It also dynamically lowers `zcard->max_exp_bit_length` on a specific CCA error for large-exponent requests, influencing future dispatch behavior. No on-disk persistence exists.

## Dependencies And Integration Points
It depends on AP queueing, zcrypt queue/card structures, common error conversion, CCA key encoding helpers from `zcrypt_cca_key.h`, architecture zcrypt request structs, and EP11/CCA callers that use `zcrypt_send_cprb()` and `zcrypt_send_ep11_cprb()` through the zcrypt API. CEX4 queue probe selects the default or EP11 variant based on hardware personality.

## Risks And Test Signals
Risks include alignment and integer overflow errors in XCRB sizing, incorrect user/kernel copy mode, reply length/count trust, domain rewrite mistakes for EP11 management vs usage commands, retry semantics for administrative requests, and queue-offline side effects on unexpected responses. Tests should cover CCA and EP11 prepared-message extraction, AP message flags, oversize request rejection, interrupted waits and cancellation, type 82/86/87/88 response mapping, RNG count handling, and speed-index classification for known function codes.
