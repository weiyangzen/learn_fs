# sources/compression/zlib/contrib/minizip/iowin32.h

Purpose: declares the Win32 callback-table fillers for minizip's I/O abstraction.

Important APIs/types/functions: `fill_win32_filefunc`, `fill_win32_filefunc64`, `fill_win32_filefunc64A`, and `fill_win32_filefunc64W`.

Control flow: Windows callers include this header, allocate a `zlib_filefunc_def` or `zlib_filefunc64_def`, call the desired filler, then pass that table to minizip open functions such as `unzOpen2_64`.

State and persistence: no state in the header. Implementations allocate per-open handle wrappers in `iowin32.c`.

Dependencies/integration: includes `<windows.h>` and uses callback struct types from `ioapi.h`, which must be visible to callers before or through the include chain.

Risks: no include guard is present in the visible file, so repeated inclusion can duplicate declarations but should remain benign in C. Including `<windows.h>` from a public contrib header can affect macro namespace and build settings.

Test signals: compile coverage on Windows and runtime miniunz/minizip operations with Win32 I/O callbacks.
