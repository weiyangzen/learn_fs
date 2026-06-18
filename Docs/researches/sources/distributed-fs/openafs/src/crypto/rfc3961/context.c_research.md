# sources/distributed-fs/openafs/src/crypto/rfc3961/context.c

This file provides no-op Kerberos context and error-reporting functions required by selected Heimdal crypto code. `krb5_init_context` returns success without storing a context, `krb5_free_context` does nothing, `krb5_set_error_message` ignores formatted errors, and `krb5_abortx` returns 0.

There is no state, persistence, or meaningful control flow. Dependencies are `krb5_locl.h`, which renames these symbols for OpenAFS. Integration is RFC3961 crypto code that accepts a `krb5_context` parameter but does not need a real Kerberos library context in OpenAFS.

Risks are diagnostics and error semantics: callers get numeric errors only and no localized text; a real abort path is suppressed. Test signals are crypto operations that pass NULL/no-op contexts and verify errors are returned numerically without dereferencing context data.
