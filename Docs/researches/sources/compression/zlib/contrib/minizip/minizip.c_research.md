# sources/compression/zlib/contrib/minizip/minizip.c

## Purpose
`minizip.c` is the command-line sample program for creating ZIP archives with the MiniZip writer API. It demonstrates how to parse archive options, open or append a ZIP file, collect file metadata, optionally encrypt entries, stream each input file through `zipWriteInFileInZip()`, and close the archive cleanly.

## Important APIs, Types, and Functions
- Uses MiniZip writer APIs from `zip.h`: `zipOpen64()`, `zipOpen2_64()`, `zipOpenNewFileInZip3_64()`, `zipWriteInFileInZip()`, `zipCloseFileInZip()`, and `zipClose()`.
- `filetime()` is platform-specific. Windows uses `FindFirstFileA()` plus DOS date conversion. Unix-like platforms use `stat()` and `localtime()` to fill `tm_zip`; other platforms return no timestamp.
- `check_exist_file()` probes with `FOPEN_FUNC(..., "rb")`.
- `getFileCrc()` computes a source file CRC before encrypted writing, because classic ZIP encryption needs the CRC in advance.
- `isLargeFile()` seeks to end and marks entries needing Zip64 if size is at least `0xffffffff`.
- `main()` owns option parsing, archive open mode selection, entry path normalization, file streaming, and cleanup.

## Control Flow
`main()` prints the banner, parses flags (`-o`, `-a`, compression level `-0` to `-9`, `-p`, `-j`), allocates a 16 KiB buffer, derives the archive name, and prompts before overwriting when needed. It opens the archive in create or append mode, then iterates positional arguments after the ZIP filename. For each input it fills `zip_fileinfo`, strips leading slashes, optionally reduces the stored name to a basename, opens a ZIP entry with `zipOpenNewFileInZip3_64()`, copies source bytes in a loop, and closes the entry. The archive is closed once all entries finish or an error stops the loop.

## State and Persistence
Persistent effects are the output ZIP archive and any append-mode mutation of an existing archive. Runtime state is local: parsed flags, a shared heap buffer, CRC accumulator for encryption, per-entry `zip_fileinfo`, and file handles. No configuration or global state is stored by the program.

## Dependencies and Integration Points
Depends on the MiniZip writer library (`zip.h`), zlib CRC helpers, standard C file APIs, POSIX `stat()`/`utime` headers on Unix-like systems, and Win32 file APIs when built on Windows. On Windows it uses `iowin32.h` with `zipOpen2_64()` to supply Win32 IO callbacks.

## Risks and Edge Cases
The fixed `MAXFILENAME` buffer truncates long archive names before appending `.zip`. `filetime()` on Unix calls `localtime()` even when `stat()` fails, using epoch time. Interactive overwrite prompting makes unattended runs hang unless `-o` or `-a` is supplied. The argument filter for skipped option-like entries is narrow and can treat some filenames beginning with `-` or `/` unexpectedly. Password mode reads the whole source once for CRC and again for compression.

## Test Signals
The MiniZip CMake tests invoke the built `minizip` executable to create test archives, then invoke `miniunzip` and compare extracted content. No direct unit tests target the prompt path, encrypted path, very long path truncation, or Zip64 boundary behavior.
