# sources/distributed-fs/ceph-client/arch/xtensa/lib/strncpy_user.S

Purpose: Copies a NUL-terminated string from userspace into kernel memory with bounded length and fault handling.

Important APIs, types, and functions: `__strncpy_user`, endian byte masks, aligned and unaligned copy paths, exception fixup labels `10`/`11`, and `EXPORT_SYMBOL`.

Control flow: Handles zero length, aligns source with initial byte copies, chooses fast word path when destination is word-aligned, scans each word for zero bytes while storing only up to the terminator, and falls back to byte copy for unaligned destinations. On fault, returns `-EFAULT`.

State and persistence: Writes destination bytes until NUL, length exhaustion, or fault. Returns copied string length excluding NUL per code comments, `len` when full, or `-EFAULT`.

Dependencies and integration: Used by `strncpy_from_user` architecture support; depends on exception table macros, endian masks, and user access fault fixups.

Risks: Partial destination contents remain on fault; zero-byte detection is endian-specific; destination unaligned path is simpler but slower; comments mention possible future clearing behavior not implemented.

Test signals: Usercopy string tests with aligned/unaligned source and destination, NUL at each byte position, exact-length truncation, zero length, and faulting user pages.
