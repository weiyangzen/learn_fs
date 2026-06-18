# sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_uv.c

Purpose: provides a pkey handler for Ultravisor secret tokens in protected-virtualization guests. It maps UV secret IDs to retrievable protected-key material and verifies that referenced UV secrets exist with the expected secret type.

Important APIs and functions: `struct uvsecrettoken` defines the non-CCA token layout with version `TOKVER_UV_SECRET`, secret type, length, and UV secret ID. `is_uv_key()` validates token type/version and supported UV secret types. `get_secret_metadata()` serializes access to the preallocated `uv_secret_list` and calls `uv_find_secret()`. `retrieve_secret()` fetches metadata, checks caller buffer length, and calls `uv_retrieve_secret()`. `uv_get_size_and_type()` maps UV secret type to protected-key byte size and pkey key type. `uv_key2protkey()` retrieves the secret and fills pkey output. `uv_verifykey()` checks metadata and reports pkey type, bit size, and underlying pkey type in `flags`.

Control flow: module init only succeeds in protected-virtualization guests with UV retrieve-secret support. Handler calls validate the token, compute expected size/type, retrieve metadata, then retrieve or verify the secret ID. Exit unregisters the handler and frees the preallocated list under the mutex.

State and persistence: `uv_list` is a module-lifetime scratch buffer shared by `uv_find_secret()` and protected by `uv_list_mutex`. Actual secrets persist in UV-managed storage, not in this driver. Retrieved protected key bytes are returned to the caller buffer only.

Dependencies and integration: depends on `asm/uv.h`, CPU feature `S390_CPU_FEATURE_UV`, `is_prot_virt_guest()`, `uv_info.inst_calls_list`, and the pkey handler interface. It integrates UV secret retrieval with the normal pkey protected-key conversion API.

Risks: `uv_key2protkey()` assumes callers passed a valid token; incorrect dispatch could read fields before full validation. The shared `uv_list` must remain serialized to avoid metadata races. Size/type mapping is security-relevant because it controls output buffer requirements and algorithm identification.

Test signals: run init gating for non-PV guests, PV guests without retrieve-secret, and allocation failure; verify every supported UV secret type maps to expected protected-key size/type; test missing secret ID, mismatched metadata type, short output buffer, and concurrent verify/retrieve calls.
