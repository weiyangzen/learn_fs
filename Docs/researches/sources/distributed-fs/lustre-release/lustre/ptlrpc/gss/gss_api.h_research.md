# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_api.h

Purpose: defines the simplified mechanism-independent GSS API used by Lustre PTLRPC security. It is the dispatch contract between common security code and concrete mechanisms such as Kerberos, shared-key, and null.

Important APIs/types/functions: `struct gss_ctx` stores the selected `gss_api_mech`, an opaque mechanism context, and a `digest_hash` callback. `struct gss_api_mech` describes a registered mechanism, module owner, OID, refcount, operations, and supported subflavors. `struct gss_api_ops` provides import/copy/inquire, MIC, wrap/unwrap, bulk prep/wrap/unwrap, delete, and display hooks. Public wrappers include `lgss_import_sec_context()`, `lgss_get_mic()`, `lgss_verify_mic()`, `lgss_wrap()`, `lgss_unwrap()`, `lgss_prep_bulk()`, `lgss_wrap_bulk()`, `lgss_unwrap_bulk()`, `lgss_delete_sec_context()`, and mechanism lookup/registration helpers.

Control flow: common code creates or receives a `gss_api_mech`, imports an opaque token into a `gss_ctx`, then invokes wrapper functions that assert the mechanism operations and dispatch to mechanism-specific implementations. Mechanism lookup can be by name or security subflavor.

State/persistence: only declares in-memory structures. The runtime registry and context ownership are implemented in `gss_mech_switch.c`; persistent credentials normally come from user-space upcalls or kernel keyrings.

Dependencies/integration: includes `uapi/linux/lustre/lgss.h` for `rawobj_t` and interoperates with `bio_vec` bulk buffers and `ptlrpc_bulk_desc`. It is consumed by `sec_gss.c`, `gss_bulk.c`, keyring/upcall code, and all mechanisms.

Risks/test signals: every mechanism must implement all operation slots expected by the wrappers. Tests should register fake mechanisms, validate module ref get/put behavior, verify subflavor dispatch, exercise MIC/wrap/bulk forwarding, and ensure failed imports clean up partially allocated contexts.
