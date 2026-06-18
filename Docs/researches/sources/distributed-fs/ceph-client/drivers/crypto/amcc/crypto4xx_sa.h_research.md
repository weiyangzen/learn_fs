# sources/distributed-fs/ceph-client/drivers/crypto/amcc/crypto4xx_sa.h

## Purpose

`crypto4xx_sa.h` defines dynamic Security Association command words, content masks, state records, and SA layouts for AES, CCM, GCM, and HMAC-SHA1 operations on the PPC4xx crypto engine.

## Important APIs, Types, And Functions

Key definitions are `union dynamic_sa_contents`, `union sa_command_0`, `union sa_command_1`, `struct dynamic_sa_ctl`, `struct sa_state_record`, AES/CCM/GCM/hash SA structs, length/content macros such as `SA_AES128_LEN`, `SA_AES_CONTENTS`, `SA_AES_GCM_CONTENTS`, and accessors `get_dynamic_sa_offset_state_ptr_field()`, `get_dynamic_sa_key_field()`, and `get_dynamic_sa_inner_digest()`.

## Control Flow

The header has no standalone execution. Algorithm setkey code fills these command fields and key/digest locations, while `crypto4xx_build_pd()` computes and writes the state-record pointer into the dynamic SA before descriptor submission.

## State And Persistence Behavior

SA buffers persist per TFM in `crypto4xx_ctx` until rekey or exit. Per-packet shadow SAs and state records persist in DMA-coherent pools until descriptor completion. Saved IV and digest fields carry final IV and AEAD tag material back from hardware.

## Dependencies And Integration Points

It is consumed by `crypto4xx_alg.c` and `crypto4xx_core.c`, and its layouts must match the hardware dynamic SA ABI described by the PPC4xx Security Subsystem. It relies on packed structures and little-endian fields inside otherwise PowerPC-oriented code.

## Risks And Test Signals

Risks include state-pointer offset computation errors, incorrect content masks for variable key sizes, bitfield packing differences, GCM inner digest placement mistakes, and confusion between inbound/outbound direction plus opcode. Test every key size, ECB/CBC/CTR/CCM/GCM vectors, saved IV updates, auth tag generation/checking, and structure offset assertions.
