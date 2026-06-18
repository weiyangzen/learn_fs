# sources/distributed-fs/ceph-client/include/crypto/dh.h

Purpose: Diffie-Hellman private key parameter encoding helpers for the KPP API.

Important APIs/types/functions: `struct dh`, `crypto_dh_key_len`, `crypto_dh_encode_key`, `crypto_dh_decode_key`, and `__crypto_dh_decode_key`.

Control flow: callers package key/p/g buffers and sizes into a packet representation for `crypto_kpp_set_secret`, or decode a packet into borrowed pointers inside the original buffer.

State and persistence: decoded fields point into the packet buffer; the packet must outlive the decoded `struct dh` use.

Dependencies and integration points: used by DH KPP implementations and callers preparing DH secrets.

Risks: invalid sizes or truncated buffers must be rejected. Borrowed pointer lifetime is easy to misuse. Parameter validation beyond packet structure belongs to algorithm implementations.

Test signals: encode/decode round-trip tests, truncated buffer tests, invalid size tests, and KPP DH shared-secret vectors.
