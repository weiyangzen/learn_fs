# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_internal.h

Purpose: central internal header for PTLRPC GSS implementation. It defines raw object helpers, GSS wire constants, client/server context structures, keyring-specific state, inline conversions, and cross-file prototypes.

Important APIs/types/functions: raw object API includes allocation, duplication, serialization, extraction, and netobj conversion. `gss_round_ctx_expiry()` subtracts a timeout delta for forward contexts. GSS enums define interface versions, PTLRPC GSS procedures, target services, and packing flags. `struct gss_svc_reqctx`, `struct gss_cli_ctx`, `struct gss_cli_ctx_keyring`, `struct gss_sec`, and `struct gss_sec_keyring` carry service request state, client context handles, keyring bindings/timers, security mechanism pointers, reverse handles, cache lists, and root-context locks. Inline helpers convert base PTLRPC security/context pointers to GSS-specific structs.

Control flow: no primary flow, but prototypes expose the file-level integration map: common signing/sealing in `sec_gss.c`, keyring lifecycle, bulk wrapping, client/server upcalls, lproc stats, and mechanism init/cleanup. Conditional inline stubs make keyring and SSK support compile out cleanly.

State/persistence: defines in-memory security context and cache state. Persistence, if any, is through kernel keyrings and user-space tokens handled elsewhere.

Dependencies/integration: includes keyring, keyctl, crypto hash, LNet crypto, Lustre security, and upcall cache headers. It binds this work item to unlisted companions such as `sec_gss.c`, `gss_svc_upcall.c`, and `lproc_gss.c`.

Risks/test signals: structure layout and flag definitions are cross-file contracts. Tests should build all configuration combinations, validate context expiry rounding, handle conversion helpers, bulk descriptor pointer storage, reverse-context sequence updates, and upcall cache interactions.
