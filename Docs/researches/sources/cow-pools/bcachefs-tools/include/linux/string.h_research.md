# File Research: sources/cow-pools/bcachefs-tools/include/linux/string.h

Wraps libc string APIs and declares Linux helpers implemented in `linux/string.c`: `strlcpy`, `strscpy`, `strim`, `memzero_explicit`, `match_string`, and `memscan`. It maps `kstrdup/kstrndup` to libc duplication and defines `strtomem_pad()` using `memcpy_and_pad()`.
