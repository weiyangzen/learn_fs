# sources/distributed-fs/ceph-client/drivers/nvme/common/auth.c

Purpose: Provides common NVMe DH-HMAC-CHAP and TLS PSK cryptographic helpers shared by host authentication and tests.

Important APIs and flow: Exports sequence number generation, DH group name/KPP mapping, HMAC algorithm mapping, key allocation/free/parse/extract, HMAC init/update/final wrappers, key transformation by NQN, augmented challenge generation, DH private/public/session key generation, TLS generated PSK generation, PSK digest generation, and TLS PSK derivation. `nvme_auth_extract_key()` decodes base64 DHHC keys and verifies CRC. `nvme_auth_gen_session_key()` computes DH shared secret and hashes it. TLS helpers implement generated PSK, Base64 digest, and HKDF-Expand-Label-style derivation for SHA-256/SHA-384.

State and persistence behavior: Maintains a mutex-protected global DH-HMAC-CHAP sequence number seeded from random on first use. Key material is dynamically allocated and freed with sensitive zeroing. No persistent storage is written.

Dependencies and integration points: Uses Linux crypto KPP/DH, SHA/HMAC library helpers, base64, CRC32, NVMe auth UAPI constants, and exported symbols consumed by `host/auth.c`, target auth, and KUnit tests.

Risks and test signals: Cryptographic ABI must match NVMe specs. SHA-512 has a hash id and HMAC support but TLS digest/derive intentionally reject it. Tests should cover key CRC failures, unsupported hashes/groups, sequence wraparound, DH KPP errors, transformed keys, augmented challenge vectors, TLS PSK derivation vectors, and sensitive buffer cleanup on errors.
