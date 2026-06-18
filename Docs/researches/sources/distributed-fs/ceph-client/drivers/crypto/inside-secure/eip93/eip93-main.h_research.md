# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-main.h

## Purpose
Defines EIP93 core constants, algorithm/mode/descriptor flags, device/ring structures, and algorithm template type shared by all EIP93 driver files.

## Important APIs, Types, and Functions
Key constants include `EIP93_RING_NUM`, `EIP93_RING_BUSY`, `EIP93_CRA_PRIORITY`, algorithm flags (`EIP93_ALG_*`, `EIP93_HASH_*`), mode flags (`EIP93_MODE_*`), direction flags, and descriptor flags (`EIP93_DESC_*`). Helper macros classify flags, such as `IS_AES()`, `IS_HMAC()`, `IS_CTR()`, and `IS_ENCRYPT()`.

Types include `struct eip93_device`, `struct eip93_desc_ring`, `struct eip93_ring`, `enum eip93_alg_type`, and `struct eip93_alg_template`.

## Control Flow
The flags defined here are set by algorithm templates and per-request frontends, then consumed by common SA record generation, descriptor submission, result dispatch, and algorithm support filtering.

## State and Persistence
`struct eip93_device` is the driver instance. `struct eip93_ring` owns command/result rings, lock state, a tasklet, and the async IDR. Template objects are global descriptors patched with the active device pointer during registration.

## Dependencies and Integration Points
Includes Linux crypto internal headers for AEAD/hash/skcipher algorithm structures and interrupt support. It is the central include for EIP93 sibling files.

## Risks
Macros encode overlapping bit ranges and must stay synchronized with `eip93-regs.h` and template flags. The 16-bit crypto IDR field limits active tracked requests to `EIP93_RING_NUM - 1` in current code. `EIP93_RING_SA_STATE_DMA()` casts DMA addresses to 32-bit, reflecting descriptor limitations.

## Test Signals
Compile-time coverage of all templates, sparse checks for bitfield usage, and runtime tests that combine every algorithm/mode/direction flag path.
