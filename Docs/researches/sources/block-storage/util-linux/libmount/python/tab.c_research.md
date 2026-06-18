# File Research: sources/block-storage/util-linux/libmount/python/tab.c

Python C-extension binding for `struct libmnt_table`, exposed as `libmount.Table`.

Key responsibilities:
- Creates and initializes table objects from nothing, a file, or a directory.
- Supports parser error callbacks from Python.
- Exposes table comments, entry count, parsing functions, find functions, add/remove FS, iteration, write, and atomic file replacement.
- Attaches a libmount cache to each initialized table.
- Converts libmount table pointers back into Python wrappers via `PyObjectResultTab()`.

Important behavior:
- `Table_init()` resets prior table state, handles optional path parsing, sets parser callback/userdata, and always installs a cache.
- `next_fs()` uses a built-in forward iterator and resets it at end-of-list.
- `Table_unref()` walks contained filesystems and decrefs Python userdata wrappers before unrefing the table.
- Parser callback calls the Python callable with `(table_object, filename, line)` and expects an integer return code.

Dependencies:
- Depends on `pylibmount.h`, Python C API, `stat(2)`, libmount table/parser/cache APIs, and `FsType`/`PyObjectResultFs()`.

Notable risks:
- `Table_add_fs()` increments the Python FS object before `mnt_table_add_fs()` but does not roll back the Python ref on failure.
- `Table_remove_fs()` decrefs the Python FS after removal regardless of whether removal succeeded.
- `Table_repr()` calls `PyObject_Repr(self->errcb)` and converts it through `pystos()` without decrefing the repr object.
- Path initialization leaves `self->tab` NULL if `path` exists but is neither regular file nor directory, then unconditionally uses it.
