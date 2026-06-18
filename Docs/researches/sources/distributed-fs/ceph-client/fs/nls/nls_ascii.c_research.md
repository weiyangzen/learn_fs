# sources/distributed-fs/ceph-client/fs/nls/nls_ascii.c

## Purpose
`nls_ascii.c` implements the `ascii` NLS charset. It provides exact one-byte conversion for 7-bit ASCII plus control bytes, with no mappings for bytes `0x80` through `0xff`. This is the simplest loadable NLS table and serves filesystems that explicitly request ASCII conversion.

## Important APIs, types, and functions
`charset2uni[256]` contains entries only through `0x7f`; uninitialized trailing entries are zero and therefore invalid. `page00[256]` provides reverse mappings for Unicode page 0 values through `0x7f`, while `page_uni2charset[256]` points only to `page00`. `charset2lower` and `charset2upper` implement ASCII case folding for `A-Z` and `a-z`.

`uni2char()` and `char2uni()` implement the standard single-byte NLS callbacks. `table` registers `.charset = "ascii"` with conversion and case tables. `init_nls_ascii()` and `exit_nls_ascii()` register and unregister the table with the NLS core.

## Control flow
The module initialization path calls `register_nls(&table)`. Consumers loading `"ascii"` then use the table callbacks. `char2uni()` indexes directly by input byte; because bytes above `0x7f` map to zero, they fail with `-EINVAL`. `uni2char()` accepts only Unicode values whose high byte points at `page00` and whose low byte maps to a nonzero output byte. A zero output buffer fails with `-ENAMETOOLONG`.

## State and persistence behavior
The file has no mutable state except its registration with the global NLS list. Translation tables are static constants and conversions are deterministic. No persistent filesystem metadata is changed here.

## Dependencies and integration points
The module depends on kernel module/NLS headers and the registry in `nls_base.c`. Filesystem clients use it by charset name and then call callbacks through `struct nls_table`, especially for filename conversion and byte case operations.

## Risks and test signals
The notable semantic detail is that `char2uni()` rejects byte `0x00`, and `uni2char()` rejects Unicode NUL, because zero also marks unmapped entries. Another risk is callers expecting ISO-8859-1 behavior for bytes above `0x7f`; this table intentionally rejects them. Tests should cover ASCII printable round trips, control-byte conversion except NUL behavior, rejection of high bytes, upper/lower ASCII case folding, `boundlen` errors, and module load/unload.
