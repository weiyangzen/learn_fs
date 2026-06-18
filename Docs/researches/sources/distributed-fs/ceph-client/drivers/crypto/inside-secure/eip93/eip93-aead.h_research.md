# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-aead.h

## Purpose
Declares the EIP93 AEAD/authenc algorithm templates and the AEAD result callback used by the EIP93 core.

## Important APIs, Types, and Functions
The header exports `eip93_aead_handle_result(struct crypto_async_request *async, int err)` and many `extern struct eip93_alg_template` declarations. The declared templates cover HMAC-MD5/SHA1/SHA224/SHA256 with CBC AES, CTR/RFC3686 AES, CBC DES, CBC 3DES, and null-cipher authenc variants.

## Control Flow
`eip93-main.c` includes this header to populate its algorithm array and to dispatch result descriptors with AEAD flags. The concrete template definitions for most listed combinations are in `eip93-aead.c`; consumers do not allocate or mutate these declarations directly outside registration.

## State and Persistence
The header owns no runtime state. It exposes global algorithm templates that become bound to an `eip93_device` during registration.

## Dependencies and Integration Points
Requires `struct eip93_alg_template` from `eip93-main.h`, indirectly available through the include graph in the C files. It integrates AEAD definitions into the common EIP93 registration and interrupt completion path.

## Risks
Some extern declarations are broader than the definitions in the listed `eip93-aead.c` view, especially CTR/null authenc names. Build coverage must ensure every declared symbol is either defined in the compilation unit or intentionally excluded by Kconfig/source selection.

## Test Signals
Build/link the EIP93 driver with all declared AEAD templates enabled, then check `/proc/crypto` for expected driver names and run AEAD self-tests for registered algorithms.
