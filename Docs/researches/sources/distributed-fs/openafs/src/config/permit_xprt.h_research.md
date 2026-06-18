# sources/distributed-fs/openafs/src/config/permit_xprt.h

This tiny compatibility header unconditionally enables old export-permission macros. It defines `xprt_CoerceLevel`, makes `xprt_CryptOK(x)` always return `1`, and defines `AFS_HIDE`.

There are no functions, control flow, or persistent data. Its API is intentionally macro-only and is included by code that expects transport/export-layer authorization toggles to exist. The security-relevant behavior is that any caller using `xprt_CryptOK` receives success regardless of the argument.

Dependencies are only the C preprocessor. Integration points are legacy OpenAFS export/transport consumers that need these symbols to compile. The main risk is semantic: a macro named `CryptOK` returning true can hide missing encryption enforcement if used outside the historical context. Test signals are compile coverage of modules that include it and targeted audits of all `xprt_CryptOK` uses to confirm the macro is not relied on as a real policy decision.
