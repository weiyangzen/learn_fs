# File Research: sources/block-storage/util-linux/sys-utils/setpriv-landlock.h

This header declares the Landlock option structure and helper functions used by `setpriv.c`. When `HAVE_LINUX_LANDLOCK_H` is available, `struct setpriv_landlock_opts` stores the handled filesystem access mask and a list of parsed rules.

When Landlock headers are unavailable, the header provides empty stubs. Runtime attempts to parse Landlock access or rules fail with “no support for landlock,” while initialization, application, and usage extension become no-ops. This keeps `setpriv.c` buildable without conditional call sites.
