# sources/distributed-fs/openafs/src/external/heimdal/krb5/data.c

Purpose: implements allocation, copying, freeing, and comparison helpers for `krb5_data` buffers.

Important APIs/types/functions: `krb5_data_zero()`, `krb5_data_free()`, `krb5_free_data()`, `krb5_data_alloc()`, `krb5_data_realloc()`, `krb5_data_copy()`, `krb5_copy_data()`, `krb5_data_cmp()`, and `krb5_data_ct_cmp()`.

Control flow: allocation helpers set `data` and `length`, accepting zero-length allocations as successful even with null pointers. Copy helpers allocate then `memmove()` input. Free helpers free content and zero the structure. Compare helpers first compare lengths, then use `memcmp()` or `ct_memcmp()`.

State and persistence behavior: no global state. Ownership is caller-managed; allocated buffers persist until the matching free helper.

Dependencies and integration points: used across krb5 crypto, encoding, and ASN.1 copy paths. `krb5_copy_data()` delegates to `der_copy_octet_string()`. Constant-time compare integrates with roken `ct_memcmp()`.

Risks: length parameters are `int` for allocation/reallocation but `size_t` for copy, so oversized lengths need caller discipline. `krb5_data_cmp()` subtracts lengths and may truncate on unusual size ranges. Secrets freed through `krb5_data_free()` are not wiped unless caller does it first.

Test signals: zero-length allocation/copy, realloc growth/shrink, copy failure cleanup, constant-time compare equality/inequality, and ownership of `krb5_copy_data()` results.
