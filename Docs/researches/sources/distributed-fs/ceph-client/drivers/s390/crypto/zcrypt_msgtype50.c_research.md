# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_msgtype50.c

## Purpose
`zcrypt_msgtype50.c` implements zcrypt operations for accelerator-style CEXxA message type 50 RSA modular exponentiation and CRT requests. It converts user ICA request structures into fixed type-50 AP messages, waits for AP completion, converts type-80 replies back to user buffers, and registers a `zcrypt_ops` implementation.

## Important APIs, Types, And Functions
Important internal wire types include `type50_hdr`, `type50_meb[1-3]_msg`, `type50_crb[1-3]_msg`, and `type80_hdr`. Exported helper functions `get_rsa_modex_fc()` and `get_rsa_crt_fc()` classify request sizes into dispatcher function codes. Main operation callbacks are `zcrypt_msgtype50_modexpo()` and `zcrypt_msgtype50_modexpo_crt()`. Lifecycle functions register/unregister `zcrypt_msgtype50_ops`.

## Control Flow
For modexpo, `ICAMEX_msg_to_type50MEX_msg()` chooses 128, 256, or 512 byte operand slots based on `inputdatalength`, right-aligns modulus, exponent, and message, and copies user buffers into the AP message. For CRT, `ICACRT_msg_to_type50CRT_msg()` similarly chooses CRB format, derives half-size CRT fields, uses the documented adjustment offset for selected operands, and enforces 4K CRT only when the zcrypt card says it supports 512-byte modulus. Send callbacks set the receive function, generate a PSMID from current PID and an atomic sequence, queue the AP message, wait interruptibly, cancel on signal, and convert the reply. Response conversion dispatches type 82/88 to `convert_error()` and type 80 to `convert_type80()`.

## State And Persistence
The file keeps only the static registered ops object and an atomic PSMID sequence. Queue online state can be changed to offline on impossible short or unknown replies. No persistent storage exists.

## Dependencies And Integration Points
It integrates with AP queueing (`ap_queue_message()`, `ap_cancel_message()`), zcrypt queue/card metadata, user-copy helpers, common error conversion, and zcrypt message-type registration. CEX4+ queue probe selects this ops variant for accelerator hardware.

## Risks And Test Signals
Risks include user pointer copy failures, operand length boundary errors, response length mismatches, queue-offline side effects on malformed replies, and compatibility behavior for 4K CRT support. Tests should cover 0/129/257/513-byte boundaries, CRT short length calculation, type 80 copyback, type 82/88 mapping, interrupt cancellation, and registration lookup by name/variant.
