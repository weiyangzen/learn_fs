# Research: sources/compression/xz/src/xz/coder.h
## sources/compression/xz/src/xz/coder.h

Purpose: Defines the public coder interface and shared compression-mode globals for the xz command-line front end.

Important APIs and types: `enum operation_mode` distinguishes compress, decompress, test, and list. `enum format_type` distinguishes auto, xz, lzma, optional lzip, and raw. `block_list_entry` pairs an uncompressed block size with a filter chain number. The header exports mode/format flags, auto-adjust and single-stream flags, block-list state, and coder setup/run functions.

Control flow and integration: `args.c` sets almost every exported variable or invokes the setters. `main.c` ultimately calls `coder_run()` for non-list operations. `file_io.c`, `message.c`, `hardware.c`, `suffix.c`, and `list.c` read the mode/format globals to select I/O safety, progress formatting, memlimit class, suffixes, and list-mode behavior.

State and persistence: This header intentionally exposes process-global mutable state. The block-list pointer is allocated by `args.c`, validated and consumed by `coder.c`, and freed only by debug cleanup.

Risks: Since the globals are not encapsulated, new call sites can observe partially initialized state if added before `args_parse()` completes. The enum ordering for `format_type` is significant to `suffix.c`, so reordering is a compatibility risk.

Test signals: Build all optional macro combinations (`HAVE_LZIP_DECODER`, `HAVE_ENCODERS`, `HAVE_DECODERS`, `MYTHREAD_ENABLED`) and run mode/format combinations through `args_parse()` and `coder_run()`.
