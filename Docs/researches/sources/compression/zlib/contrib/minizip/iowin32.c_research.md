# sources/compression/zlib/contrib/minizip/iowin32.c

Purpose: implements minizip file-function callbacks using Win32 file handles, including ANSI, wide, and WinRT-aware open paths.

Important APIs/types/functions: `WIN32FILE_IOWIN`, `win32_translate_open_mode`, `win32_build_iowin`, open callbacks `win32_open64_file_func`, `win32_open64_file_funcA`, `win32_open64_file_funcW`, `win32_open_file_func`, read/write callbacks, `MySetFilePointerEx`, tell/seek callbacks for 32-bit and 64-bit offsets, close/error callbacks, and filler functions `fill_win32_filefunc*`.

Control flow: open callbacks translate minizip mode flags to desired access and creation disposition, call `CreateFile`, `CreateFileA/W`, or `CreateFile2`, wrap the handle in allocated `WIN32FILE_IOWIN`, and return it as `voidpf`. Read/write use `ReadFile`/`WriteFile` and store `GetLastError()` on failure. Tell/seek use `SetFilePointerEx` or a compatibility wrapper. Close closes the handle and frees the wrapper.

State and persistence: each open file has heap state containing `HANDLE hf` and last error code. No global state is used.

Dependencies/integration: includes Windows APIs through `iowin32.h`, zlib, and `ioapi.h`. `miniunz.c` uses `fill_win32_filefunc64A()` on Windows.

Risks: ANSI to wide conversion uses a fixed stack buffer and does not check truncation. Share mode is read-only for read opens and zero for write/create, which can be restrictive. The custom `INVALID_HANDLE_VALUE` fallback casts to integer. Error state is overwritten only on failed calls.

Test signals: Windows minizip/miniunz open, read, write, seek, and Zip64 behavior should exercise this; no local tests are shown here.
