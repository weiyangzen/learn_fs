# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/readlink.c

Purpose: implements `winutils readlink`, printing the target print-name of a Windows symbolic link with Unix-like success/failure behavior.

Important APIs/types/functions: local `REPARSE_DATA_BUFFER` definition avoids a WDK dependency; `Readlink` opens the reparse point with `FILE_FLAG_OPEN_REPARSE_POINT`, calls `FSCTL_GET_REPARSE_POINT`, validates `IO_REPARSE_TAG_SYMLINK`, extracts `PrintNameOffset`/`PrintNameLength`, null-terminates, and prints; `ReadlinkUsage` documents no-option behavior.

Control flow: only `argc == 2` is accepted. The link path is converted to long-path form, opened with backup semantics, then queried in a growing buffer loop on `ERROR_INSUFFICIENT_BUFFER` or `ERROR_MORE_DATA`. Non-symlink reparse points and all API errors fall through cleanup and return failure without detailed stderr messages.

State and persistence: read-only except for stdout. It allocates a long path, a reparse buffer, and a copied print-name buffer.

Dependencies/integration: depends on `ConvertToLongPath`, Win32 file/device APIs, and `winutils.h`; dispatched by `main.c`; pairs with `symlink.c` for link creation.

Risks and test signals: buffer length is in bytes while the terminator index is in WCHARs, so tests should include long Unicode targets. Test regular files, junctions, missing links, directory symlinks, and exact no-newline stdout formatting.
