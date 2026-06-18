# sources/distributed-fs/openafs/src/aklog/skipwrap.c

## Purpose
`skipwrap.c` extracts the encrypted ticket portion from a DER-encoded Kerberos 5 ticket by manually walking the expected ASN.1 wrapper. `klog` uses it for encrypted-part-only rxkad token compatibility.

## Important APIs, types, and functions
The exported function is `afs_krb5_skip_ticket_wrapper(char *tix, size_t tixlen, char **enc, size_t *enclen)`. Internal `skip_get_number` reads ASN.1 short or long-form lengths and advances a pointer/remaining-length pair. Tag constants define SEQUENCE, CONSTRUCTED, APPLICATION, and CONTEXT_SPECIFIC bits.

## Control flow
`afs_krb5_skip_ticket_wrapper` validates the outer application ticket tag, outer length, sequence tag, and context-specific fields 0, 1, and 2, skipping their contents. It then requires context-specific field 3 to consume the remaining data and returns a pointer/length to that encrypted ticket data. Any malformed tag, length mismatch, or truncation returns `-1` or the helper error.

## State and persistence
No persistent state exists. Returned pointers alias the caller-provided ticket buffer; no allocation is performed.

## Dependencies and integration points
It includes `aklog.h`, Kerberos headers, and `skipwrap.h`. The main integration is `klog.c` when constructing `RXKAD_TKT_TYPE_KERBEROS_V5_ENCPART_ONLY` tokens.

## Risks
This is intentionally a narrow parser, not a general ASN.1 decoder. It assumes definite lengths and exact field order. Lengths are read into `int`, so extremely large encodings are not meaningful. Because returned memory aliases input, callers must keep the original credential buffer alive.

## Test signals
Use known-good Kerberos tickets, truncated buffers at every boundary, wrong tags, long-form lengths, mismatched lengths, missing field 3, and caller lifetime checks.
