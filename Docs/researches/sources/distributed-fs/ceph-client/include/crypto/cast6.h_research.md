# sources/distributed-fs/ceph-client/include/crypto/cast6.h

Purpose: CAST6 cipher constants, context, and primitive operation declarations.

Important APIs/types/functions: `CAST6_BLOCK_SIZE`, key size bounds, `struct cast6_ctx`, `__cast6_setkey`, `cast6_setkey`, `__cast6_encrypt`, and `__cast6_decrypt`.

Control flow: setkey expands key into 12 rounds of masking and rotation subkeys; encrypt/decrypt operate on a block using the context.

State and persistence: context stores 12x4 masking words and 12x4 rotation bytes.

Dependencies and integration points: uses CAST common S-boxes and crypto API setkey wrapper.

Risks: key schedule dimensions must match CAST6 spec; mode users must account for 16-byte block size and alignment.

Test signals: CAST6 KATs, key length validation, and crypto API provider tests.
