# sources/distributed-fs/openafs/src/rxkad/sboxes.h

Purpose: Supplies four 256-byte substitution tables for the fcrypt block cipher.

Important APIs/data: `sbox0`, `sbox1`, `sbox2`, and `sbox3` are `static const unsigned char` arrays indexed by bytes of the fcrypt round input. They are arranged so `fc_ecb_encrypt` can combine substitution and byte permutation.

Control flow and state: No flow or mutable state. Inclusion creates private static table copies in translation units that include it; this group uses it in `fcrypt.c`.

Dependencies and integration: Direct dependency of `fcrypt.c`; indirectly affects every rxkad encrypted packet, packet checksum, and challenge response.

Risks: Table edits silently change the cipher and break interoperability. The static-header pattern can duplicate data if included elsewhere.

Test signals: Known-vector and round-trip behavior in `fc_test`/`tcrypt` would catch accidental table changes.
