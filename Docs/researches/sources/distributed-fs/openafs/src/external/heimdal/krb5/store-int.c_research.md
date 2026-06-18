# sources/distributed-fs/openafs/src/external/heimdal/krb5/store-int.c

Purpose: provides fixed-width big-endian integer serialization helpers for internal krb5 code.

Important APIs/types/functions: `_krb5_put_int()` stores the low `size` bytes of an unsigned long into a buffer in big-endian order. `_krb5_get_int()` reads `size` bytes from a buffer into an unsigned long in big-endian order.

Control flow: put walks from last output byte to first while shifting the value right. Get walks forward, left-shifting the accumulator and adding each input byte.

State and persistence behavior: stateless and purely buffer-local.

Dependencies and integration points: used by crypto key-usage derivation constants and other internal store/load code that needs network-order integer fields.

Risks: no buffer length validation and no overflow reporting if `size` exceeds the meaningful width of `unsigned long`; callers must pass valid sizes. Return type reports bytes processed, not an error channel.

Test signals: round trips for 1 to 5 byte values, truncation behavior for oversized values, and expected key-usage constant encoding in crypto derivation.
