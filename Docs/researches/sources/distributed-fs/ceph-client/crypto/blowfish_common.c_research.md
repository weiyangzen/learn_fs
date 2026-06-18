<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/blowfish_common.c -->
# sources/distributed-fs/ceph-client/crypto/blowfish_common.c

## Purpose

`blowfish_common.c` provides Blowfish constants and key schedule code shared by C and assembly implementations. It exports `blowfish_setkey()` so algorithm frontends can populate `struct bf_ctx` with derived P-box and S-box material.

## Important APIs, Types, and Flow

The file defines the initial Blowfish P-box and S-box tables, an endian-neutral internal `encrypt_block()` used only during subkey generation, and `blowfish_setkey()`. The key schedule copies initial tables into the context, XORs key words through the P-box cycling across key bytes, repeatedly encrypts a zero block to replace P-box entries, then continues encrypting to fill all S-box entries.

`encrypt_block()` uses the Blowfish F function and 16 unrolled Feistel rounds over two 32-bit words, deliberately ignoring external byte order because the key schedule operates on internal words.

## State, Dependencies, and Integration

State is the caller-provided `bf_ctx` inside a Crypto API transform. The file exports only key setup; block encryption/decryption frontends live in `blowfish_generic.c` or architecture-specific modules. It depends on `crypto/blowfish.h`, module exports, and kernel integer types.

## Risks and Test Signals

Risks include accepting invalid key lengths if callers bypass algorithm min/max checks, byte-order mismatches between common key schedule and frontend block functions, and sensitive key material remaining in transform contexts until freed. Test signals are Blowfish known-answer vectors across minimum, maximum, and odd key lengths, plus cross-checks between generic and assembly frontends sharing this schedule.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/blowfish_common.c -->
