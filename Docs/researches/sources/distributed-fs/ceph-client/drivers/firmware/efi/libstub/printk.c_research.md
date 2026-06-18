
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/printk.c

Purpose: implements EFI stub console logging with UTF-8 to UCS-2 conversion, loglevel filtering, kernel-style prefixes, and bounded formatting.

Important APIs/types/functions: exports `efi_char16_puts()`, `efi_puts()`, and `efi_printk()`. Internal `utf8_to_utf32()` decodes UTF-8 and validates surrogate/range rules.

Control flow: `efi_puts()` chunks UTF-8 text into a 128-character EFI CHAR16 buffer, inserts carriage returns before newlines, encodes non-BMP characters as surrogate pairs, and calls ConOut. `efi_printk()` reads the leading kernel loglevel, filters by global `efi_loglevel`, formats with the stub `vsnprintf()` into 256 bytes, prints an EFI stub prefix for numbered levels, and emits a truncation notice if needed.

State and persistence behavior: global `efi_loglevel` defaults to notice and is changed by `quiet` or `efi=debug`. No persistent state exists.

Dependencies and integration points: depends on EFI Simple Text Output Protocol, local `vsnprintf()`, kernel loglevel helpers, and command-line parsing. Used by all stub diagnostics.

Risks and test signals: output is truncated at 255 bytes, invalid UTF-8 falls back to byte output, and firmware consoles can be slow or missing. Test signals include quiet/debug options, multi-byte UTF-8 output, newline CRLF conversion, truncation path, and calls before/after console availability.
