# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_err.h

Purpose: defines GSS-API status bit fields, flags, and standard major-status constants used by Lustre GSS mechanism code.

Important APIs/types/functions: `OM_uint32` is the status type. Context flags include delegation, mutual auth, replay, sequence, confidentiality, and integrity. Macros split status codes into calling, routine, and supplementary fields (`GSS_CALLING_ERROR`, `GSS_ROUTINE_ERROR`, `GSS_SUPPLEMENTARY_INFO`, `GSS_ERROR`). Routine errors include `GSS_S_BAD_MECH`, `GSS_S_BAD_SIG`, `GSS_S_NO_CONTEXT`, `GSS_S_DEFECTIVE_TOKEN`, `GSS_S_CONTEXT_EXPIRED`, and `GSS_S_FAILURE`; supplementary flags include duplicate, old, unsequenced, and gap tokens.

Control flow: no runtime code. Mechanisms return these constants through the `lgss_*` dispatch wrappers and higher PTLRPC security code maps failures to kernel errno values where needed.

State/persistence: none.

Dependencies/integration: consumed by all GSS implementation files in this set. Values are adapted from standard GSS bindings and should remain ABI-stable within the module's user/kernel negotiation contract.

Risks/test signals: accidental value changes would alter error classification. Tests should verify `GSS_ERROR()` behavior, supplementary bit extraction, and representative mechanism failure mapping to `-EACCES`, `-EPROTO`, or retry behavior in surrounding code.
