# File Research: sources/block-storage/util-linux/libmount/python/meson.build

Meson build recipe for the Python libmount extension package.

Key responsibilities:
- Skips the subdirectory when `build-python` is disabled.
- Builds `pylibmount` from `pylibmount.c`, `pylibmount.h`, `fs.c`, and `tab.c`.
- Adds `context.c` only on Linux.
- Locates the requested Python installation and builds an extension module installed under `libmount`.
- Installs `__init__.py` into the same package.

Important behavior:
- For Meson older than 1.4.1, explicitly checks for `Python.h` using the Python include path.
- Suppresses `-Wcast-function-type`.
- Suppresses Python 3.12 redundant-declaration warnings as a workaround for util-linux issue 2366.
- Links against `mount_dep` and `python.dependency(embed: true)`.

Dependencies:
- Meson Python module, configured `mount_dep`, `dir_include`, `LINUX`, and project options `build-python`/`python`.

Notable risks:
- Linux-only inclusion means `Context` is absent from non-Linux builds while `Fs` and `Table` remain available.
- The extension build is coupled to generated include directories and libmount availability.
