
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/vsprintf.c

Purpose: implements a compact `vsnprintf()`/`snprintf()` for EFI stub diagnostics without relying on the full kernel formatter.

Important APIs/types/functions: exports `vsnprintf()` and `snprintf()`. Internal helpers parse flags/width/precision/qualifiers, format 64-bit decimal without division-heavy operations, handle octal/hex/pointers, and convert UTF-16 wide strings/chars to UTF-8.

Control flow: the formatter copies literal characters, parses `%` conversions, obtains field widths and precision from digits or `*`, supports `h/hh/l/ll`, handles `%c`, `%lc`, `%s`, `%ls`, `%o`, `%p`, `%x`, `%X`, `%d`, `%i`, and `%u`, applies sign/prefix/padding rules, writes bounded output through `PUTC`, and stops on invalid specifiers.

State and persistence behavior: no persistent state. It operates on caller buffers and returns the untruncated output length.

Dependencies and integration points: depends on local string helpers and is used by `efi_printk()` and other stub formatting.

Risks and test signals: unsupported format specifiers abort remaining formatting, wide-string length accounting must avoid partial UTF-8 writes, and return type is `int` despite `size_t` internal position. Test signals include integer formats with flags/precision, pointers, width from `*`, UTF-16 BMP and surrogate pairs, NULL strings, buffer size 0/1, and invalid specifiers.
