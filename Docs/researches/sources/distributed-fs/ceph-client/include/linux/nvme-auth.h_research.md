
# sources/distributed-fs/ceph-client/include/linux/nvme-auth.h

Purpose: declares NVMe DH-HMAC-CHAP authentication and TLS PSK derivation helpers used by NVMe fabrics host and target code.

Important APIs/types/functions: `struct nvme_dhchap_key` stores a counted key plus hash ID. Mapping helpers convert DH group and HMAC IDs to names, crypto KPP names, lengths, and IDs. `struct nvme_auth_hmac_ctx` wraps SHA-256/SHA-384/SHA-512 HMAC contexts. APIs initialize/update/finalize HMACs, allocate/extract/parse/free/transform keys, compute augmented challenges, generate DH private/public/session keys, generate PSKs, generate digest strings, and derive TLS PSKs.

Control flow: authentication negotiation selects a hash and DH group, parses host/subsystem secrets, optionally transforms them by NQN, generates challenges and DH material, derives a session key/PSK, and finally produces digests or TLS PSKs for fabrics security.

State and persistence: key objects and HMAC/DH contexts are in-memory sensitive material. Persistent secrets live outside this header in configuration or keyrings; callers must free and avoid leaking derived material.

Dependencies and integration points: depends on kernel crypto KPP and SHA2 HMAC implementations plus NVMe auth constants in `nvme.h`. It integrates NVMe fabrics authentication, NVMe keyring/TLS setup, and host/subsystem NQN identity.

Risks and test signals: risks include unsupported hash/group negotiation, incorrect key parsing or NQN transformation, insufficient zeroization in implementation, challenge concatenation mismatch, and digest/PSK length errors. Test signals include DH-HMAC-CHAP positive/negative handshake tests, invalid secret parsing, all hash/group combinations, TLS PSK derivation vectors, and memory-sanitizer checks for freed key paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvme-auth.h -->
