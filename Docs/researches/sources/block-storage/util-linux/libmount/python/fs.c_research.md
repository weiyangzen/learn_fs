# File Research: sources/block-storage/util-linux/libmount/python/fs.c

Python C-extension binding for `struct libmnt_fs`, exposed as `libmount.Fs`.

Key responsibilities:
- Defines `Fs` construction with optional `source`, `root`, `target`, `fstype`, `options`, `attributes`, `freq`, and `passno`.
- Exposes libmount filesystem fields as Python properties: mountinfo IDs, source/source path, root, target, fstype, options classes, attributes, fstab dump/fsck fields, swap metadata, tag, TID, and comments.
- Implements mutating helpers for appending/prepending options and attributes.
- Implements matching/comparison helpers for filesystem type, options, source path, and target.
- Provides `copy_fs()` and `print_debug()`.
- Bridges libmount FS pointers back to Python objects via `mnt_fs_set_userdata()` in `PyObjectResultFs()`.

Important behavior:
- String getters map missing C strings to Python `None`.
- `print_debug()` works around Python stdout truncation by chunking long strings.
- `Fs_init()` replaces any existing `self->fs` with a new `mnt_new_fs()` and stores the Python object as libmount userdata.
- `PyObjectResultFs()` reuses an existing wrapper from `fs->userdata`; otherwise it creates a wrapper, refs the libmount FS, and stores the wrapper in userdata.

Dependencies:
- Depends on `pylibmount.h`, Python C API, and libmount `mnt_fs_*` APIs.
- Uses common helper functions from `pylibmount.c`: `PyObjectResultInt`, `PyObjectResultStr`, `pystos`, `UL_RaiseExc`, and `UL_IncRef`.

Notable risks:
- Existing-object `copy_fs(dest)` returns `dest` without `Py_INCREF()`, which is not normal for a Python C API return value.
- `Fs_set_freq()` and `Fs_set_passno()` return raw libmount status and do not translate errors into Python exceptions.
- `PyObjectResultFs()` uses extra Python references to keep userdata wrappers alive; correctness depends on matching cleanup in table/context owners.
- TODO comments note missing source/target matching and per-attribute/per-option accessors.
