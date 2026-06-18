# sources/distributed-fs/openafs/src/util/krb5_nt.h

Purpose: Declares Windows-only Kerberos helper functions.

Important APIs: Under `AFS_NT40_ENV`, declares `initialize_krb5(void)` and `fetch_krb5_error_message(afs_uint32)`.

Control flow and state: Header-only declarations; all state lives in `krb5_nt.c`.

Dependencies and integration: Assumes `afs_uint32` is already defined by included OpenAFS platform headers. Included by Windows code that needs optional Kerberos initialization or error translation.

Risks and test signals: The header has no include guard, so repeated inclusion relies on declarations being identical. It is effectively inert on non-Windows platforms. Compile coverage in Windows builds is the main signal.
