# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-aes.h

## Purpose
Declares EIP93 AES skcipher algorithm templates.

## Important APIs, Types, and Functions
Exports `eip93_alg_ecb_aes`, `eip93_alg_cbc_aes`, `eip93_alg_ctr_aes`, and `eip93_alg_rfc3686_aes` as `struct eip93_alg_template` globals. These templates are defined in `eip93-cipher.c`.

## Control Flow
The EIP93 platform driver includes this header and registers the AES templates if hardware option bits advertise AES and compatible AES key sizes. Per-request behavior is implemented by common skcipher callbacks in `eip93-cipher.c`.

## State and Persistence
No runtime state is owned here. The declared template objects are global descriptors whose `eip93` pointer is set during registration.

## Dependencies and Integration Points
Depends on `struct eip93_alg_template` from `eip93-main.h` through including C files. Integrates AES modes into the driver-wide algorithm list.

## Risks
The header is intentionally declaration-only; missing or mismatched definitions would surface as link failures. Runtime risk comes from registration-time key-size adjustment for hardware AES capabilities in `eip93-main.c`.

## Test Signals
Compile/link EIP93 with AES enabled, verify ECB/CBC/CTR/RFC3686 AES driver names, and run aligned and unaligned skcipher test vectors.
