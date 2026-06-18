# sources/distributed-fs/ceph-client/lib/zlib_inflate/inflate_syms.c

Purpose: Exports the kernel inflate API symbols and declares module metadata.

Important APIs/functions:
- Exports `zlib_inflate_workspacesize`, `zlib_inflate`, `zlib_inflateInit2`, `zlib_inflateEnd`, `zlib_inflateReset`, `zlib_inflateIncomp`, and `zlib_inflate_blob`.
- Provides module description and GPL license.

Control flow: No runtime logic beyond symbol export metadata.

State and persistence: No local state. Exported symbols become available to in-kernel modular users.

Dependencies and integration:
- Includes `<linux/module.h>`, `<linux/init.h>`, and `<linux/zlib.h>`.
- Connects inflate implementation to crypto, firmware, boot helpers, and other subsystems.

Risks:
- Export ABI stability matters for modular consumers.
- `zlib_inflateIncomp` and `zlib_inflate_blob` are specialized helpers; removing exports can break less obvious users.

Test signals:
- Kernel/module link with `CONFIG_ZLIB_INFLATE`.
- `modpost` symbol validation.
