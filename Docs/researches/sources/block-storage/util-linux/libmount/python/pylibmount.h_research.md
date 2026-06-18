# File Research: sources/block-storage/util-linux/libmount/python/pylibmount.h

Shared header for pylibmount C-extension source files.

Key responsibilities:
- Includes Python and libmount headers.
- Defines debug masks and debug macros for init, table, filesystem, and context paths.
- Defines common error strings.
- Declares Python wrapper structs for `FsObject`, `TableObject`, and Linux-only `ContextObjext`.
- Declares exported type objects, module registration functions, wrapper conversion helpers, and utility helpers.

Important behavior:
- Debug logging is always compiled because `CONFIG_PYLIBMOUNT_DEBUG` is defined in the header.
- `TableObject` owns a `libmnt_table`, iterator, and parser error callback.
- `FsObject` owns or references a `libmnt_fs` through libmount refcounting.
- `ContextObjext` is guarded by `__linux__`.

Dependencies:
- Depends on `c.h`, generated/public `libmount.h`, Python C API, and util-linux debug conventions.

Notable risks:
- `ContextObjext` appears misspelled, which is harmless if consistently used but awkward for maintainability.
- Header guard closing comment names `UTIL_LINUX_PYLIBMOUNT`, while the actual guard is `UTIL_LINUX_PYLIBMOUNT_H`.
