
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/string.c

Purpose: supplies a compact subset of string and numeric parsing routines needed by EFI stub code without the full kernel library.

Important APIs/types/functions: conditionally exports `strlen()`, `strnlen()`, `strcmp()`, `strrchr()`, and `memchr()`, and always provides `strstr()`, `strncmp()`, `simple_strtoull()`, and `simple_strtol()`.

Control flow: string routines perform straightforward byte scans. `simple_strtoull()` guesses base from `0`/`0x` prefixes when base is zero, accepts digits/letters valid for the base, and returns the end pointer. `simple_strtol()` handles a leading minus by negating the unsigned conversion.

State and persistence behavior: no state.

Dependencies and integration points: depends on ctype helpers and is used by command-line, graphics, and x86 option parsing. Optional definitions are controlled by EFI_HAVE_* and FDT parameter configs.

Risks and test signals: no overflow reporting is provided, and numeric parsing accepts only simple prefixes. Test signals include decimal/octal/hex inputs, invalid digits, negative values, substring matching, and config combinations that use arch-provided string functions.
