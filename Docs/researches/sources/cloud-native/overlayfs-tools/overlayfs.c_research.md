# sources/cloud-native/overlayfs-tools/overlayfs.c

Purpose: userspace copies of Linux overlayfs option splitting helpers.

Important APIs/types/functions: `ovl_split_lowerdirs` splits lowerdir lists on unescaped `:` and mutates separators to NUL; `ovl_next_opt` splits mount option strings on unescaped `,`.

Control flow: both helpers scan in place, skip escaped characters, terminate current token at separators, and return count or next token pointer.

State and persistence: mutates caller-provided strings only; no allocation.

Dependencies/integration: used by `mount.c` to parse user-supplied and `/proc/mounts` overlay options consistently with kernel syntax.

Risks: input strings are destroyed during parsing, so callers must duplicate if original text is needed. Escaping behavior must track kernel overlayfs semantics.

Test signals: unit cases for escaped separators, trailing escapes, empty options, and multi-layer lowerdir strings.
