# sources/distributed-fs/openafs/src/aklog/aklog.h

## Purpose
`aklog.h` is the small public/local header for the `aklog` family. It declares `aklog(int, char *[])`, includes Kerberos 5 and the local linked-list header, and supplies a Kerberos 4 `CREDENTIALS` compatibility definition when the system lacks `<kerberosIV/krb.h>`.

## Important APIs, types, and functions
The exported function declaration is `void aklog(int, char *[])`, although this source tree's `aklog.c` provides a `main` entry point. The fallback `struct ktext` and `struct credentials` mirror the K4 fields needed by 524 conversion code: service, instance, realm, session key, lifetime, kvno, ticket, issue date, principal name, and principal instance. `CREDENTIALS` aliases `struct credentials`.

## Control flow
There is no runtime control flow. The header conditionally selects either the platform Kerberos IV definition or the local compatibility layout.

## State and persistence
No state is stored here. The fallback struct definitions describe in-memory ticket conversion data used by `aklog.c`.

## Dependencies and integration points
It depends on `afsconfig.h`, `<krb5.h>`, and `linked_list.h`. It is included by `aklog.c`, `krb_util.c`, and `skipwrap.c`, giving those files the Kerberos compatibility constants such as `REALM_SZ` when native K4 headers are absent.

## Risks
The compatibility layout must match the expectations of the Kerberos 524 APIs closely enough for builds without Kerberos IV headers. The local `u_int32_t` macro fallback is invasive if a platform has unusual typedef behavior. Since fixed sizes such as `ANAME_SZ` and `REALM_SZ` are legacy K4 limits, callers must still avoid assuming modern unbounded Kerberos principal lengths.

## Test signals
Build coverage should include platforms with and without `HAVE_KERBEROSIV_KRB_H`, MIT and Heimdal Kerberos headers, and code paths that compile 524 conversion support.
