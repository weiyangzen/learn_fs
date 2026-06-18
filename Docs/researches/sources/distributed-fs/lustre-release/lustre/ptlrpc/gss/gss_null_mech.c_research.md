# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_null_mech.c

Purpose: implements a minimal `gssnull` mechanism for null-service GSS contexts, primarily for testing and protocol plumbing without cryptographic protection.

Important APIs/types/functions: `struct null_ctx` stores a 64-bit token. `gss_import_sec_context_null()` validates and copies the token from the input buffer. `gss_copy_reverse_context_null()` duplicates the token for reverse contexts. `gss_inquire_context_null()` returns a short expiry. All MIC, wrap, unwrap, prep bulk, wrap bulk, and unwrap bulk functions return success without modifying data. `gss_display_null()` reports `null`. `init_null_module()` registers the `SPTLRPC_SUBFLVR_GSSNULL` subflavor.

Control flow: import requires exactly one `struct null_ctx` worth of input. Once imported, every security operation is a no-op success, allowing common PTLRPC GSS paths to execute with `SPTLRPC_SVC_NULL`.

State/persistence: stores only the copied 64-bit token and a synthetic expiry of current time plus 60 seconds. No persistent credentials.

Dependencies/integration: registers through `gss_mech_switch.c`, uses OBD allocation macros, and integrates with the subflavor table consumed by security flavor lookup.

Risks/test signals: this mechanism provides no authentication, integrity, or privacy and must only be selected where `gssnull` is intended. Tests should verify invalid input rejection, reverse-copy independence, short expiry behavior, no-op operations, display string, and register/unregister behavior.
