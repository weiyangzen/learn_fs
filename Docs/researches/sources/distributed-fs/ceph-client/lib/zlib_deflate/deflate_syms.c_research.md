# sources/distributed-fs/ceph-client/lib/zlib_deflate/deflate_syms.c

Purpose: Provides the module symbol exports and metadata for the kernel deflate implementation.

Important APIs/functions:
- Exports `zlib_deflate_workspacesize`, `zlib_deflate_dfltcc_enabled`, `zlib_deflate`, `zlib_deflateInit2`, `zlib_deflateEnd`, and `zlib_deflateReset`.
- Declares module description and GPL license.

Control flow: There is no runtime control flow beyond module metadata registration. The file makes the deflate API available to other built-in or module code through `EXPORT_SYMBOL()`.

State and persistence: No local state. Export table entries become part of the kernel module symbol namespace.

Dependencies and integration:
- Includes `<linux/module.h>`, `<linux/init.h>`, and `<linux/zlib.h>`.
- Integrates `deflate.c` with kernel consumers such as crypto transforms, firmware/debug compression, and architecture-specific code.

Risks:
- Removing or renaming an export breaks out-of-tree or modular in-kernel users.
- Exporting `zlib_deflate_dfltcc_enabled()` exposes architecture acceleration status; behavior must remain stable across build configs.

Test signals:
- Kernel/module build should resolve all exported deflate symbols.
- `modpost` should report no missing or duplicate symbols.
