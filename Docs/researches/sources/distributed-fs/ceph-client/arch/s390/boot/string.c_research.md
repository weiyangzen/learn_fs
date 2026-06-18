<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/string.c -->
# sources/distributed-fs/ceph-client/arch/s390/boot/string.c

Purpose: Provides string and memory helpers for the boot decompressor by including s390 library string code and locally implementing a small set of common helpers needed before the full kernel runtime exists.

Important APIs/types/functions: Includes `../lib/string.c` with sanitizer config macros undefined, and defines `strncmp()`, `sized_strscpy()`, `memset64()`, `skip_spaces()`, `strim()`, `simple_strtoull()`, `simple_strtol()`, and `kstrtobool()`.

Control flow: Numeric parsing uses `simple_guess_base()` for 0/0x prefixes, consumes valid digits until the base is exceeded, and optionally returns the end pointer. `strim()` trims trailing whitespace then returns the first non-space byte. `kstrtobool()` recognizes y/Y/1, n/N/0, on, and off.

State and persistence: No persistent state exists.

Dependencies and integration points: Used by command-line parsing, boot printk formatting, symbol parsing, vmem/linker metadata helpers, and included library routines. Sanitizer macros are explicitly disabled because the decompressor cannot use normal KASAN/KMSAN runtime support.

Risks: These are intentionally small substitutes, not full libc/kernel equivalents. `simple_strtoull()` does not detect overflow. `kstrtobool()` checks only the beginning of accepted strings. Changes in included `../lib/string.c` can affect boot code assumptions.

Test signals: Boot command-line parsing for numeric values and booleans, printk symbol parsing, whitespace trimming, and sanitizer-enabled builds.

Source read size: 168 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/string.c -->
