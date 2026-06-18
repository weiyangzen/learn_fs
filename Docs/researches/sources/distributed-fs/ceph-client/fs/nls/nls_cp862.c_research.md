# sources/distributed-fs/ceph-client/fs/nls/nls_cp862.c

Purpose: Implements the Linux NLS module for DOS codepage 862, a Hebrew single-byte codepage. It enables exact conversion between CP862 filesystem bytes and Unicode Hebrew/Latin/symbol characters.

Important APIs/types/functions: Defines `charset2uni[256]`, reverse pages `page00`, `page01`, `page03`, `page05`, `page20`, `page22`, `page23`, and `page25`, `page_uni2charset[256]`, byte case tables, `uni2char()`, `char2uni()`, and `struct nls_table table` with `.charset = "cp862"`. `init_nls_cp862()` and `exit_nls_cp862()` manage registration.

Control flow: `uni2char()` maps Unicode page 05 Hebrew entries and other covered pages back to one CP862 byte after checking output capacity. Missing pages or zero entries return `-EINVAL`. `char2uni()` maps one input byte to Unicode and rejects zero. Module init/exit only register and unregister.

State and persistence behavior: The module stores only static generated tables and has no persistence. Runtime state is the registered NLS table while loaded.

Dependencies and integration points: Uses Linux NLS and module infrastructure. Filesystems selecting `cp862` use these callbacks for names; Latin case folding is present, while Hebrew letters themselves do not have simple upper/lower byte pairs in this DOS codepage.

Risks: Right-to-left display ordering is outside this module; it only converts code points. Applications may misinterpret successful conversion as bidi handling. Exact mapping rejects Hebrew presentation variants and other Unicode forms not represented in CP862.

Test signals: Verify `cp862` lookup, round-trip Hebrew letters in Unicode page 05, and test shared box-drawing/symbol entries. Check that unsupported Hebrew marks or presentation forms fail with `-EINVAL` and that case tables do not unexpectedly alter Hebrew bytes.
