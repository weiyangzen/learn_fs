# sources/distributed-fs/ceph-client/arch/x86/boot/string.c

Purpose: implements small string, memory, and integer parsing helpers for x86 boot/setup code.

Important APIs and state: defines `memcmp()`, `bcmp()`, `strcmp()`, `strncmp()`, `strnlen()`, `simple_strtoull()`, `simple_strtol()`, `strlen()`, `strstr()`, `strchr()`, `kstrtoull()`, and `boot_kstrtoul()`. Helpers implement radix guessing, 64-bit division by 32-bit divisor, overflow-aware integer parsing, and simple ASCII lowercase.

Control flow: simple string routines iterate byte-wise or use `repe cmpsb`. `simple_strtoull()` parses permissively and returns end pointer. `kstrtoull()` accepts optional plus, auto-detects base 0, detects overflow with `KSTRTOX_OVERFLOW`, permits one trailing newline, and returns `-EINVAL`/`-ERANGE` on errors.

Dependencies and integration: used by command-line parsers, early serial, video options, and compressed string support. It undefines compiler macros for memory primitives so real symbols exist, then `string.h` redefines default calls to builtins where safe.

Risks and test signals: `memcmp()` returns only nonzero/zero rather than ordered difference, which is acceptable for current uses but not a full libc semantic. Test numeric parsing boundaries, hex/octal autodetect, overflow, command-line option parsing, and Clang lowering of memcmp to bcmp.
