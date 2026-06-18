# sources/distributed-fs/ceph/src/rgw/rgw_kms.h

Purpose: Declares the public KMS/SSE-S3 key retrieval interface used by RGW encryption code, backend name constants, Vault/KMIP secret engine constants, and the `SecretEngine` abstraction for backend implementations and tests.

Important APIs and types: Backend constants include `RGW_SSE_KMS_BACKEND_TESTING`, `BARBICAN`, `VAULT`, and `KMIP`. Vault auth constants include `token` and `agent`; Vault secret engine constants include `transit` and `kv`; KMIP currently exposes `kv`. Public functions derive or reconstitute actual object encryption keys from KMS or SSE-S3 metadata, and manage SSE-S3 bucket keys. `SecretEngine::get_key()` provides the minimal polymorphic contract for backend secret retrieval.

Control flow: This header does not implement behavior, but it defines the split between generating a new actual key (`make_actual_key_*`) and reconstructing an existing actual key (`reconstitute_actual_key_*`). The caller supplies object attrs, an optional KMS cache for SSE-KMS, an `optional_yield`, and an output string for the actual key.

State and persistence: Functions operate primarily through the supplied attrs map. Implementations may read or mutate encryption attributes such as key id and wrapped data key. The cache pointer is non-owning and may share secrets across KMS users.

Dependencies and integration points: The declarations rely on Ceph/RGW common types such as `DoutPrefixProvider`, `bufferlist`, `optional_yield`, and `rgw::kms::KMSCache`. It is the narrow interface between RGW encryption code and KMS-specific implementation details in `rgw_kms.cc`.

Risks: The output `actual_key` is a raw string containing cryptographic material; callers are responsible for clearing it when done. The attrs map is mutable in some APIs, which is necessary for wrapped keys but means callers need to persist updated attrs correctly.

Test signals: API-level tests should use a mock `SecretEngine` or test backend to verify make versus reconstitute semantics, error propagation, attribute mutation, and cache-enabled versus uncached behavior.
