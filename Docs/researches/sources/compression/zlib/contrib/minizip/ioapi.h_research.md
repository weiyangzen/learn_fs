# sources/compression/zlib/contrib/minizip/ioapi.h

Purpose: declares minizip's abstract I/O callback API and large-file compatibility types/macros.

Important APIs/types/functions: file mode and seek constants, callback typedefs for open/read/write/tell/seek/close/error, structs `zlib_filefunc_def`, `zlib_filefunc64_def`, and `zlib_filefunc64_32_def`, `ZPOS64_T`, `MAXU32`, macros `ZREAD64`, `ZWRITE64`, `ZCLOSE64`, `ZERROR64`, `ZOPEN64`, `ZTELL64`, `ZSEEK64`, and filler/bridge prototypes.

Control flow: zip/unzip code receives a callback table, opens streams through `ZOPEN64`, performs reads/writes through macros, seeks/tells through bridge helpers, and closes/errors through macros.

State and persistence: callback structs carry function pointers and opaque user data. No state is allocated by the header itself.

Dependencies/integration: includes `stdio.h`, `stdlib.h`, `zlib.h`, and `ints.h`. It configures large-file macros for Linux-like systems and aliases 64-bit stdio functions on platforms where normal functions are already 64-bit.

Risks: macro condition `(!(defined(__ANDROID_API__) || __ANDROID_API__ >= 24))` is easy to misread and may behave oddly when `__ANDROID_API__` is undefined. `ZPOS64_T` is custom rather than standard. Callback implementers must obey exact return conventions.

Test signals: compile coverage across platforms plus minizip operations through default stdio and Win32 callback implementations.
