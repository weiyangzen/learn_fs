# File Research: sources/block-storage/util-linux/libmount/python/Makemodule.am

## Scope

Autotools build definition for pylibmount.

## Behavior

- Gated by `BUILD_PYLIBMOUNT`.
- Installs the binary module and `__init__.py` into `$(pyexecdir)/libmount` so architecture-specific binary and Python files stay together.
- Builds `pylibmount.la` from shared Python binding sources and adds `context.c` only on Linux.
- Links against `libmount.la` and Python libraries.
- Adds Python binding tests to `dist_check_SCRIPTS`.

## Dependencies And Risks

- Uses `-avoid-version -module -shared -export-dynamic` for Python extension semantics.
- Linux gating controls whether context mount/umount APIs are available.
