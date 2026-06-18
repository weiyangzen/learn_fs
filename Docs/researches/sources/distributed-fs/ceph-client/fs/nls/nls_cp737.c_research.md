# sources/distributed-fs/ceph-client/fs/nls/nls_cp737.c

Purpose: Implements the Linux NLS translation module for DOS codepage 737, a Greek single-byte character set. It lets filesystem name conversion code translate between on-disk CP737 bytes and Unicode `wchar_t` values using exact mapping tables generated from Unicode charset data.

Important APIs/types/functions: The module contains `charset2uni[256]`, reverse pages `page00`, `page03`, `page20`, `page22`, and `page25`, `page_uni2charset[256]`, `charset2lower[256]`, `charset2upper[256]`, `uni2char()`, `char2uni()`, and `struct nls_table table` with `.charset = "cp737"`. Lifecycle hooks are `init_nls_cp737()` and `exit_nls_cp737()`, wired through `module_init` and `module_exit`.

Control flow: Conversion is a direct table lookup. `uni2char()` validates output capacity, derives `ch` and `cl` from the Unicode value, selects the reverse page by high byte, and returns one byte on a nonzero table hit or `-EINVAL` otherwise. `char2uni()` maps one input byte through `charset2uni` and rejects zero mappings. Module initialization registers the table; unload unregisters it.

State and persistence behavior: The file has only static const mapping data plus the registered NLS table. The only runtime state is the presence of the table in the kernel NLS registry while the module is loaded. It does not allocate memory, write storage, or persist configuration.

Dependencies and integration points: Uses the standard kernel module and NLS APIs from `<linux/module.h>`, `<linux/nls.h>`, and `<linux/errno.h>`. Filesystems that request `cp737` receive these callbacks for filename conversion and byte-level case folding. Greek uppercase/lowercase byte folds are encoded in the case tables, alongside ASCII folding.

Risks: `0x00` is both a byte value and the reverse-table sentinel, so NUL and holes in CP737 cannot be represented as successful conversions. `char2uni()` assumes a valid one-byte input buffer and ignores `boundlen`. Greek sigma and accented Greek mappings are exact table entries only; no normalization-aware or context-sensitive case behavior is attempted.

Test signals: Validate that the module registers as `cp737`, then round-trip all mapped Greek, ASCII, box-drawing, and symbol bytes through `char2uni()` and `uni2char()`. Negative tests should cover unmapped Unicode pages and zero output length. Case tests should exercise Greek alpha/Alpha ranges and ASCII.
