# sources/distributed-fs/openafs/src/util/krb5_nt.c

Purpose: Windows Kerberos helper for initializing delayed Kerberos support and fetching Kerberos error messages.

Important APIs and state: `initialize_krb5()` attempts `DelayLoadHeimdal()` and sets static `krb5_initialized` on success. `fetch_krb5_error_message(afs_uint32 code)` returns a pointer to a static buffer containing the Kerberos error text when initialization and context creation succeed.

Control flow: Initialization prints to stderr if neither Kerberos for Windows nor Heimdal is available. Error-message lookup creates a `krb5_context`, calls `krb5_get_error_message()`, copies into `errorText[1024]`, frees the Kerberos message and context, and returns the static buffer pointer. If not initialized or context creation fails, returns NULL.

Dependencies and integration: Windows-only code includes `windows.h`, `krb5_nt.h`, MIT/Heimdal Kerberos headers, and com_err. Used by Windows command and auth code to present better Kerberos diagnostics.

Risks and test signals: The static error buffer is not thread-safe and can be overwritten by concurrent calls. `strncpy()` truncates long messages. Initialization state is process-global and not synchronized. Test signals are Windows Kerberos availability and command error-display behavior.
