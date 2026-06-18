# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-common.h

## Purpose
Declares shared EIP93 helper APIs for descriptor rings, SA record programming, hardware error parsing, and HMAC precomputation.

## Important APIs, Types, and Functions
Exports `eip93_get_descriptor()`, `eip93_put_descriptor()`, `eip93_set_sa_record()`, `eip93_parse_ctrl_stat_err()`, and `eip93_hmac_setkey()`. These form the public surface of `eip93-common.c`.

## Control Flow
Frontend files use `eip93_set_sa_record()` during key setup. The main result path uses `eip93_get_descriptor()` while draining RDR/CDR. AEAD and hash key setup call `eip93_hmac_setkey()`. Hardware status parsing is centralized through `eip93_parse_ctrl_stat_err()`.

## State and Persistence
The header owns no state. Its functions operate on caller-provided `struct eip93_device`, `struct eip93_descriptor`, and `struct sa_record` objects.

## Dependencies and Integration Points
Assumes the including translation unit has EIP93 core and register structures visible. It is the API boundary between common EIP93 mechanics and the algorithm-specific frontends.

## Risks
Because prototypes use low-level device/descriptor pointers, misuse can corrupt ring state or misprogram hardware. There are no compile-time annotations for lock ownership around descriptor get/put; callers must hold the appropriate locks.

## Test Signals
Build with sparse/lockdep where possible and run descriptor submission/completion tests under concurrent crypto requests.
