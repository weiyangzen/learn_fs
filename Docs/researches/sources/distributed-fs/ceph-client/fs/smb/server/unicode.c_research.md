## sources/distributed-fs/ceph-client/fs/smb/server/unicode.c

Purpose: converts SMB wire UTF-16LE strings to/from local kernel/NLS strings, including selected Windows/POSIX character remapping and UTF-8 surrogate-pair handling.

Important APIs and functions: exported functions are `smb_strtoUTF16`, `smb_strndup_from_utf16`, and `smbConvertToUTF16`. Internal helpers include `cifs_mapchar`, `smb_utf16_bytes`, and `smb_from_utf16`. Character mapping covers colon, asterisk, question mark, pipe, greater-than, and less-than when mapchars behavior is requested.

Control flow: UTF-16-to-local conversion first computes output byte length, allocates a destination, then walks 16-bit little-endian words with unaligned reads, converting through NLS `uni2char` or UTF-8 fallback for surrogate pairs/variation selectors. Local-to-UTF16 conversion uses direct UTF-8-to-UTF16 for UTF-8 codepages when possible, falls back through NLS `char2uni`, and optionally maps reserved POSIX characters to private Unicode values used by SMB clients.

State and persistence behavior: no persistent state is owned. Functions allocate returned strings for callers and write converted output into caller-provided buffers. Conversion behavior depends on the connection's loaded NLS table and unicode map state held elsewhere.

Dependencies and integration points: uses Linux NLS and Unicode helpers, unaligned endian access, ksmbd default allocation flags, and SMB Unicode constants from the shared NLS utility header. It is used by path, tree-name/share-name, directory entry, short-name, and request parsing code.

Risks: conversion is buffer-bound but caller-supplied lengths must be correct in bytes versus UTF-16 words. UTF-8 fallback advances source indexes for surrogate pairs and IVS sequences; off-by-one bugs can truncate or overrun converted names. Slash/backslash remapping is intentionally not handled because path building uses separators. Unknown characters become `?`, which may interact with wildcard behavior.

Test signals: UTF-16LE path conversion with unaligned source buffers, non-Unicode SMB1 strings, UTF-8 astral-plane characters, variation selectors, mapchars on reserved characters, destination buffer boundary truncation, invalid UTF-8 fallback to `?`, and NLS codepages other than UTF-8.
