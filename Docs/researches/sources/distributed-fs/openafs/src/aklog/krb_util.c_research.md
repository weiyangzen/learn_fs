# sources/distributed-fs/openafs/src/aklog/krb_util.c

## Purpose
`krb_util.c` provides `afs_realm_of_cell`, a small Kerberos realm inference helper used by `aklog` when deciding where to request AFS service tickets.

## Important APIs, types, and functions
The only function is `char *afs_realm_of_cell(krb5_context context, struct afsconf_cell *cellconfig, int fallback)`. It returns a pointer to a static `REALM_SZ + 1` buffer.

## Control flow
If `cellconfig` is null, it returns null. In fallback mode, it takes the domain portion of the first cell DB server hostname, or the cell name if no dot exists, and uppercases it. In normal mode it calls `krb5_get_host_realm` for `cellconfig->hostName[0]`, copies the first returned realm into the static buffer, frees the realm list, and returns the buffer.

## State and persistence
The function has no persistent external effects. It stores the result in a static buffer, so each call overwrites the previous value and the function is not thread-safe or reentrant.

## Dependencies and integration points
It depends on Kerberos realm lookup, `struct afsconf_cell`, K4 realm-size constants from `aklog.h`, and C character classification. `aklog.c` uses it in its ticket-acquisition fallback sequence.

## Risks
The static fixed-size buffer is copied into with `strcpy`, so unusually long host realms from Kerberos could overflow if not bounded by the Kerberos library or configuration. Returning null without freeing `hrealms` when `hrealms[0]` is null is a small leak. Fallback realm derivation is heuristic and can produce wrong realms for non-DNS-style deployments.

## Test signals
Test host-realm success, empty host-realm result, fallback from dotted hostname, fallback from undotted hostname, lowercase-to-uppercase conversion, null cell input, and repeated-call overwrite behavior.
