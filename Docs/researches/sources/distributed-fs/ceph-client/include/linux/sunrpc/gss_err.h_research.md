# sources/distributed-fs/ceph-client/include/linux/sunrpc/gss_err.h

Purpose: provides GSS major status code constants and bitfield helpers adapted from the GSSAPI C bindings for SUNRPC security code.

Important APIs and types: `OM_uint32` is the status type. Constants define context flags, credential usage, status code types, indefinite lifetime, success, calling/routine/supplementary field offsets and masks, error testers such as `GSS_ERROR()`, concrete routine errors such as `GSS_S_BAD_MECH`, `GSS_S_NO_CRED`, `GSS_S_CONTEXT_EXPIRED`, and supplementary values such as `GSS_S_CONTINUE_NEEDED`.

Control flow: mechanism and RPCSEC_GSS code compose and test status words using macros. `GSS_ERROR()` checks calling and routine error fields without treating supplementary bits as fatal.

State and persistence: no state; this is a constants-only compatibility header.

Dependencies and integration points: consumed by GSS mechanism code and Kerberos definitions. It mirrors external GSSAPI semantics inside the kernel.

Risks and test signals: risks are numeric drift from GSSAPI expectations, treating supplementary status as fatal, and signed/unsigned misuse. Test with context continuation, expired credentials, bad token handling, and mechanism error translation.
