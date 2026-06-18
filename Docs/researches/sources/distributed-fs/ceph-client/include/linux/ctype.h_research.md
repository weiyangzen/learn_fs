<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ctype.h -->
# sources/distributed-fs/ceph-client/include/linux/ctype.h

## Purpose

`ctype.h` defines the kernel's byte-oriented character classification and case-conversion helpers. Unlike libc ctype, it does not handle EOF specially. The source was read as a complete 81-line file.

## Important APIs, Types, and Functions

Classification mask bits include `_U`, `_L`, `_D`, `_C`, `_P`, `_S`, `_X`, and `_SP`. `_ctype[]` is the lookup table, and `__ismask(x)` indexes it after casting to unsigned char. Macros include `isalnum`, `isalpha`, `iscntrl`, `isgraph`, `islower`, `isprint`, `ispunct`, `isspace`, `isupper`, `isxdigit`, `isascii`, and `toascii`. `isdigit()` uses `__builtin_isdigit` if available or an inline range check. Case helpers include `__tolower()`, `__toupper()`, `tolower`, `toupper`, fast internal `_tolower()`, and `isodigit()`.

## Control Flow

Classification macros look up `_ctype` masks for a byte. Case conversion checks classification before subtracting ASCII offsets. `_tolower()` is a fast internal helper that blindly ORs bit `0x20`.

## State and Persistence Behavior

The only shared state is the constant `_ctype` table. There is no mutable state.

## Dependencies and Integration Points

It depends on `linux/compiler.h` and is used throughout string parsing, sysfs/procfs input handling, command-line parsing, filesystems, and drivers.

## Risks and Edge Cases

Inputs are byte/ASCII-oriented and not locale-aware. EOF is not special. `_tolower()` must only be used when the caller knows the input is uppercase ASCII or can tolerate bit modification. `isspace()` intentionally returns false for NUL.

## Test Signals

Signals include table-driven classification tests for all 256 byte values, case conversion tests, NUL whitespace behavior, `isodigit()` range tests, and parser tests that depend on ASCII classification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ctype.h -->
