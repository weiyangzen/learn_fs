# sources/distributed-fs/ceph-client/include/crypto/ecdh.h

Purpose: ECDH private key packet helpers and curve ID definitions for the KPP API.

Important APIs/types/functions: curve ID macros for NIST P-192/P-256/P-384/P-521, `struct ecdh`, `crypto_ecdh_key_len`, `crypto_ecdh_encode_key`, and `crypto_ecdh_decode_key`.

Control flow: callers encode a private key packet before `crypto_kpp_set_secret`, or decode packet data into an `ecdh` struct whose key pointer references the packet buffer.

State and persistence: decoded key memory is borrowed from the input buffer.

Dependencies and integration points: used by ECDH KPP implementations and callers; curve metadata links to `ecc_curve.h`.

Risks: only key bytes are represented here; curve selection is handled by algorithm context/ID elsewhere. Borrowed pointer lifetime and length validation are key correctness risks.

Test signals: encode/decode round trips, truncated packet tests, KPP ECDH vectors, and unsupported curve handling.
