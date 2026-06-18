# sources/compression/zlib/contrib/crc32vx/crc32_vx_hooks.h

Purpose: internal declaration for the s390x CRC-32 hook pointer.

Important APIs/types: include guard `CRC32_VX_HOOKS_H`; declares `ZLIB_INTERNAL extern unsigned long (*crc32_z_hook)(unsigned long crc, const unsigned char FAR *buf, z_size_t len);`.

Control flow: header-only declaration; no runtime behavior.

State and persistence: exposes process-global hook state defined in `crc32_vx.c`.

Dependencies and integration: included by `crc32_vx.c` and referenced by Makefile dependencies. Requires zlib internal macros/types from `zutil.h` or equivalent prior includes.

Risks: because it declares a mutable function pointer, all users must respect one-time initialization semantics. It is internal and should not be installed as public API.

Test signals: compile/link success verifies the hook definition and declaration match.
