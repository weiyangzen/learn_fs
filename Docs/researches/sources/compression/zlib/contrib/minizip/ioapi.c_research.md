# sources/compression/zlib/contrib/minizip/ioapi.c

Purpose: implements minizip's portable file-function callbacks for stdio and bridges 32-bit and 64-bit file APIs.

Important APIs/types/functions: `call_zopen64`, `call_zseek64`, `call_ztell64`, `fill_zlib_filefunc64_32_def_from_filefunc32`, stdio callbacks `fopen_file_func`, `fopen64_file_func`, `fread_file_func`, `fwrite_file_func`, `ftell_file_func`, `ftell64_file_func`, `fseek_file_func`, `fseek64_file_func`, `fclose_file_func`, `ferror_file_func`, and fillers `fill_fopen_filefunc`, `fill_fopen64_filefunc`.

Control flow: bridge calls prefer 64-bit callbacks when present, otherwise fall back to 32-bit callbacks and reject offsets that truncate. Stdio open callbacks map minizip mode flags to `"rb"`, `"r+b"`, or `"wb"`. Read/write/tell/seek/close/error callbacks wrap standard C library calls. Filler functions populate callback tables with these wrappers.

State and persistence: no global mutable state. Each file stream is a `FILE *` returned through the callback interface.

Dependencies/integration: depends on `ioapi.h`, platform macros selecting `fopen64`/`ftello64`/`fseeko64`, zlib types, and minizip `zip.c`/`unzip.c`.

Risks: 32-bit fallback cannot handle offsets above `MAXU32`. Mode translation ignores append semantics. `call_ztell64()` tests `zseek64_file` rather than `ztell64_file`, which assumes they are set together. Large-file macro behavior varies by platform.

Test signals: exercised by minizip/miniunz operations and any Zip64 tests using large offsets.
