# sources/distributed-fs/ceph-client/include/crypto/des.h

Purpose: DES and 3DES-EDE constants, contexts, block operations, and key expansion declarations.

Important APIs/types/functions: DES/3DES key/block/expanded-key sizes, `struct des_ctx`, `struct des3_ede_ctx`, encrypt/decrypt functions, `des_expand_key`, and `des3_ede_expand_key`.

Control flow: callers expand a raw key into schedule state, then call encrypt/decrypt for one block. Expansion returns `-EINVAL` for rejected keys and `-ENOKEY` for weak accepted keys, with FIPS changing weak-key handling for 3DES.

State and persistence: expanded key schedules persist in context structs and are sensitive.

Dependencies and integration points: used by legacy DES/3DES crypto providers and modes.

Risks: DES is obsolete and 3DES has limited security margin and block-size constraints. Weak-key and FIPS behavior must be propagated correctly.

Test signals: DES/3DES KATs, weak-key rejection tests, FIPS-mode tests, and mode-level block cipher tests.
