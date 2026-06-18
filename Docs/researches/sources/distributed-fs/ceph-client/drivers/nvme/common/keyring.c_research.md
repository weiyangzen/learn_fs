# sources/distributed-fs/ceph-client/drivers/nvme/common/keyring.c

Purpose: Implements the NVMe global keyring and `psk` key type for NVMe/TCP TLS pre-shared keys, including generated TLS PSK refresh and default-key selection.

Important APIs and flow: `nvme_keyring_id()` exposes the global `.nvme` keyring serial. `nvme_tls_key_lookup()` validates a key id and rejects revoked/invalidated keys. A custom `psk` key type uses user payload parsing plus NVMe-specific description matching. `nvme_tls_psk_refresh()` creates or updates a generated v1 PSK identity of the form `NVMe1G<hmac> <hostnqn> <subnqn> <digest>`, sets permissions, and applies a one-hour timeout. `nvme_tls_psk_default()` searches retained/generated, v1/v0, SHA-384/SHA-256 identities in priority order.

State and persistence behavior: Runtime state is the process-global `nvme_keyring` and keys linked into it or caller-provided keyrings. Key payloads persist in kernel key retention until timeout/revoke/invalidate; generated keys receive a 3600 second timeout.

Dependencies and integration points: Depends on Linux key retention, user key payload helpers, NVMe TCP TLS cipher constants, host/subsystem NQNs, and generated PSKs from common auth or host secure concatenation.

Risks and test signals: `nvme_tls_key_lookup()` returns `-EKEYREVOKED` without putting the revoked key reference, which deserves lifetime scrutiny. Prefix-style description matching can match shorter identities. Tests should cover priority ordering, generated key refresh/update, key timeouts, revoked/invalidated keys, custom keyrings, and identity collisions.
