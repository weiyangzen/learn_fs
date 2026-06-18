<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/string.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/string.h

## Purpose
`string.h` bridges libc string functions with kernel-style string helper declarations used by tools.

## APIs And Flow
It includes libc `<string.h>`, declares `memdup()`, `argv_split()`, `argv_free()`, `strtobool()`, `strlcpy()` for glibc builds, `str_error_r()`, `strreplace()`, `skip_spaces()`, `strim()`, `remove_spaces()`, `memchr_inv()`, and `memparse()`, and defines inline `strstarts()` and `str_ends_with()`. `strscpy` is aliased to unsafe libc `strcpy` in this tools copy.

## State, Dependencies, Risks, Tests
State is caller-owned strings and allocated argv/memdup buffers. Dependencies are `linux/types.h`, libc, compiler diagnostic pragmas, and external implementations of declared helpers. Risks include `strscpy` losing kernel truncation safety, redundant `strlcpy` declarations across libcs, ownership leaks from `argv_split`, and in-place mutation by trim/remove helpers. Tests should cover prefix/suffix helpers, bool parsing, argv split/free, memparse units, `str_error_r` variants, and overflow/truncation call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/string.h -->
