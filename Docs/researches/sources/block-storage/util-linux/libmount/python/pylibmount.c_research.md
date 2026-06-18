# File Research: sources/block-storage/util-linux/libmount/python/pylibmount.c

Top-level Python module implementation for the libmount bindings.

Key responsibilities:
- Defines the `libmount.Error` exception.
- Provides shared helpers for reference increments, object freeing, exception translation, integer/string result creation, and Python-string-to-C-string conversion.
- Initializes debug masks from `PYLIBMOUNT_DEBUG`.
- Creates the `pylibmount` module and registers `Fs`, `Table`, and Linux-only `Context`.
- Exports mount userspace option constants, Linux `MS_*` constants, and iterator direction constants.

Important behavior:
- `UL_RaiseExc()` maps common `errno` and libmount-specific `MNT_ERR_*` codes to Python exceptions.
- `PyObjectResultStr()` returns `None` for NULL C strings.
- `pystos()` accepts Python 3 Unicode objects and returns their internal one-byte data pointer.
- Python 3 module state supports traversal and clear for the stored error object.
- `mnt_init_debug(0)` is called during module init.

Dependencies:
- Depends on `pylibmount.h`, Python C API, libmount constants/APIs, and the module-object registration functions from `fs.c`, `tab.c`, and Linux `context.c`.

Notable risks:
- `pystos()` assumes a one-byte Unicode representation and does not explicitly encode or verify null-terminated UTF-8/ASCII data.
- `LibmountError` is global while module state also stores an `error` field only used by the sample `error_out()` method.
- Many `PyModule_AddIntConstant()` calls ignore return values.
