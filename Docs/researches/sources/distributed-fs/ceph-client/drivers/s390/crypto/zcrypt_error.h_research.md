# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_error.h

## Purpose
`zcrypt_error.h` defines common AP error reply structures and maps firmware reply codes from type 82/type 88/type 86 contexts into Linux errno values for zcrypt message handlers.

## Important APIs, Types, And Functions
The central type is `struct error_hdr`, containing response type and reply code. The file defines response-type constants `TYPE82_RSP_CODE` and `TYPE88_RSP_CODE`, many `REP82_*` and `REP88_*` reply-code constants, and the inline `convert_error()` helper.

## Control Flow
`convert_error()` reads the error header from `reply->msg`, obtains card and queue numbers for diagnostics, and switches on `reply_code`. Request formatting, operand, malformed-message, invalid-domain-pending, hypervisor-filtered, and similar client-side errors map to `-EINVAL`. Machine failure, message-type mismatch, transport failure, and unknown retry-worthy errors map to `-EAGAIN`. Type 86 transport/filter cases include AP final status in debug output when available.

## State And Persistence
The header mutates no state directly. It emits debug events and returns errno values that may cause higher layers to retry, rescan, or mark queues offline depending on caller logic.

## Dependencies And Integration Points
It includes `zcrypt_debug.h`, `zcrypt_api.h`, and `zcrypt_msgtype6.h`. It is used by message type 50 and type 6 response conversion paths to keep error mapping consistent.

## Risks And Test Signals
Risks include firmware reply-code changes not reflected in the mapping, over-broad `-EAGAIN` causing retries for permanent failures, and incorrect type 86 overlay assumptions when logging APFS. Test signals include synthetic type 82/88 replies through both message handlers, debug output for hypervisor filtering and transport failures, and retry behavior at the zcrypt dispatcher.
