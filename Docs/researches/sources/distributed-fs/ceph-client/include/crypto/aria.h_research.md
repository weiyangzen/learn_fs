# sources/distributed-fs/ceph-client/include/crypto/aria.h

Purpose: ARIA block cipher constants, context, S-box tables, inline round transformations, and crypto API key/encrypt/decrypt declarations.

Important APIs/types/functions: ARIA size constants, `struct aria_ctx`, static S-box/precomputed tables, `rotl32`, `rotr32`, `bswap32`, `get_u8`, `make_u32`, `aria_m`, S-box layer helpers, `aria_diff_word`, `aria_diff_byte`, `aria_add_round_key`, odd/even substitution-diffusion helpers, `aria_gsrk`, `aria_encrypt`, `aria_decrypt`, and `aria_set_key`.

Control flow: key setup fills encryption/decryption round keys and round count. Encrypt/decrypt implementations apply add-round-key and alternating S-box/diffusion layers using the inline helpers.

State and persistence: `aria_ctx` persists round keys, round count, and key length. Static lookup tables are read-only implementation data.

Dependencies and integration points: includes crypto algapi/module/init/types/errno and byteorder. Used by ARIA cipher provider and mode wrappers.

Risks: large static tables and inline transforms must match RFC 5794 exactly; byte ordering mistakes break all vectors. Table-based S-boxes may be side-channel sensitive depending on usage context.

Test signals: ARIA known-answer tests for 128/192/256-bit keys, encryption/decryption inverse tests, endian coverage, and crypto API setkey failure tests.
