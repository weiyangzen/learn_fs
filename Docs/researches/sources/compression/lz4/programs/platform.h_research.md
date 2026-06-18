# sources/compression/lz4/programs/platform.h

Purpose: portability layer for compiler settings, architecture detection, large-file support, POSIX version detection, console checks, binary mode, and sparse-file mode.

Important macros/functions: defines MSVC compatibility macros, `__64BIT__`, `_FILE_OFFSET_BITS` and related large-file macros, `PLATFORM_POSIX_VERSION`, `IS_CONSOLE()`, `SET_BINARY_MODE()`, and `SET_SPARSE_FILE_MODE()`.

Control flow: preprocessor probes choose Unix/POSIX, DOS/OS2/Cygwin, Windows, or fallback behavior. Windows console/sparse handling uses Win32 APIs.

State and persistence: no durable state; macros alter compilation and runtime file/console behavior.

Dependencies/integration: included before `util.h` and used by CLI/I/O code for safe stdio and large files.

Risks: feature macros must be set before relevant system headers; unusual platforms can be misdetected; console detection influences safety refusals.

Test signals: 32-bit/64-bit interop, huge-file, QEMU/platform, and Windows builds exercise this layer.
