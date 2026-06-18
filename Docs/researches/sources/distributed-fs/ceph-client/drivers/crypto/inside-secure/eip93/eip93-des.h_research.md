# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-des.h

## Purpose
Declares EIP93 DES and 3DES skcipher algorithm templates.

## Important APIs, Types, and Functions
Exports `eip93_alg_ecb_des`, `eip93_alg_cbc_des`, `eip93_alg_ecb_des3_ede`, and `eip93_alg_cbc_des3_ede` as `struct eip93_alg_template` globals. Definitions live in `eip93-cipher.c`.

## Control Flow
`eip93-main.c` includes the header to register DES/3DES templates when the EIP93 option register advertises TDES support. Requests then run through the common skcipher callbacks.

## State and Persistence
No state is held in this header. Template objects become bound to a device pointer during registration.

## Dependencies and Integration Points
Relies on `struct eip93_alg_template` from the EIP93 core. Integrates legacy DES modes into the EIP93 algorithm list.

## Risks
DES/3DES are legacy algorithms and may be disabled or policy-restricted in some deployments. Runtime behavior depends on key validation in `eip93-cipher.c`.

## Test Signals
Compile/link with TDES-capable hardware flags, run DES/3DES KATs, and verify weak-key rejection behavior through crypto self-tests.
