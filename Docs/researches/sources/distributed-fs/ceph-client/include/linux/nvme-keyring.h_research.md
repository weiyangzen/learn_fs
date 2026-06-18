
# sources/distributed-fs/ceph-client/include/linux/nvme-keyring.h

Purpose: declares NVMe TLS PSK keyring integration for storing, refreshing, selecting, and looking up keys used by secure NVMe/TCP or fabrics connections.

Important APIs/types/functions: when `CONFIG_NVME_KEYRING` is enabled, `nvme_tls_psk_refresh()` creates or updates a PSK entry for host NQN, subsystem NQN, HMAC ID, key data, and digest; `nvme_tls_psk_default()` finds a default key serial; `nvme_keyring_id()` returns the NVMe keyring serial; and `nvme_tls_key_lookup()` resolves a serial to a key. Disabled builds return `-ENOTSUPP` or zero.

Control flow: authentication or connection setup derives/obtains key material, refreshes the keyring entry, then stores or passes key serials to TLS setup. Lookup converts a configured serial into a live `struct key`.

State and persistence: key material lives in the kernel key retention service and follows keyring lifetime/permissions. This header owns no state but gates whether callers can use keyring-backed PSKs.

Dependencies and integration points: depends on `linux/key.h`, key serial types, errno pointers, NVMe authentication helpers, and kernel TLS consumers. It integrates NVMe DH-HMAC-CHAP PSK derivation with Linux keyrings.

Risks and test signals: risks include disabled-config fallback handling, key permission/ownership failures, stale digest-to-key mapping, serial reuse, and leaking PSK material. Test signals include keyring-enabled and disabled builds, PSK refresh/default lookup tests, permission-negative tests, TLS connection setup using selected keys, and key lifetime cleanup checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvme-keyring.h -->
