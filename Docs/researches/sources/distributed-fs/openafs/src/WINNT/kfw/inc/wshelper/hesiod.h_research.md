# sources/distributed-fs/openafs/src/WINNT/kfw/inc/wshelper/hesiod.h

## Purpose

`hesiod.h` declares the Windows wshelper Hesiod API. Hesiod maps names and types to DNS TXT-style records, historically used at MIT for user, mail, service, and password data.

## Important APIs, types, and functions

Configuration constants are `HESIOD_CONF`, `DEF_RHS`, and `DEF_LHS`. Error codes are `HES_ER_UNINIT`, `HES_ER_OK`, `HES_ER_NOTFOUND`, `HES_ER_CONFIG`, and `HES_ER_NET`. Query APIs are `hes_to_bind`, `hes_resolve`, `hes_error`, and `hes_free`. Higher-level accessors are `hes_getmailhost`, `hes_getservbyname`, `hes_getpwnam`, and `hes_getpwuid`. `struct hes_postoffice` stores `po_type`, `po_host`, and `po_name`.

## Control flow

The documented flow is `hes_to_bind` combines the caller's name/type with LHS/RHS suffixes, `hes_resolve` performs the DNS lookup and returns a null-terminated vector, callers inspect errors through `hes_error`, and `hes_free` releases vector results. Higher-level APIs perform specific Hesiod lookups and return thread-local/static structures that callers must copy before the next call.

## State and persistence behavior

The library can read `c:\net\tcp\hesiod.cfg` for site-specific LHS/RHS suffixes, falling back to `.ns` and `.Athena.MIT.EDU`. Returned structures are owned by the library and reused per call per thread, making them transient state rather than caller-owned allocations except for `hes_resolve` vectors.

## Dependencies and integration points

The header includes `windows.h` and uses `LPSTR` plus `WINAPI`. It integrates with `resolv.h` DNS search behavior and with wshelper's Unix-compatible network lookup surface.

## Risks and edge cases

The hard-coded default file path and MIT defaults are site-specific. Callers can accidentally keep stale pointers returned by thread-local/static APIs. Error state is likely global or thread-local, so mixed concurrent calls need implementation review. Returned strings are narrow `LPSTR`, so code-page assumptions matter.

## Test signals

Tests should cover config-file parsing versus default suffixes, DNS not-found and network errors, freeing `hes_resolve` vectors, repeated calls overwriting static structures, and integration with service/passwd/mailhost record formats.
