# Research: sources/compression/xz/src/xz/list.c
## sources/compression/xz/src/xz/list.c

Purpose: Implements `xz --list` metadata inspection for `.xz` files, including basic, verbose, debug, and robot output formats.

Important APIs and functions: Public `list_file()` lists one file and `list_totals()` prints aggregate totals. Internal `xz_file_info` holds combined liblzma index metadata, stream padding, max decoder memory use, header-size completeness, and minimum XZ Utils version. `block_header_info` holds per-block header details. `parse_indexes()` uses `lzma_file_info_decoder()` to build a combined `lzma_index`. `parse_block_header()`, `parse_check_value()`, and `parse_details()` read block-level details through `io_pread()`. Printing helpers include `print_info_basic()`, `print_info_adv()`, `print_info_robot()`, and totals variants.

Control flow: `main.c` selects `list_file()` when `opt_mode == MODE_LIST`. `list_file()` rejects non-xz/non-auto formats and stdin, initializes translated field widths, forces source-open behavior to follow symlinks while rejecting special files, parses indexes, prints according to robot and verbosity mode, updates totals only on successful print, frees the index, and closes the source without removing it. `list_totals()` prints always in robot mode and only for multiple files in human mode.

State and persistence: Static totals accumulate across listed files until process exit. Formatting width state is recomputed per `list_file()` call but stored statically. `check_value` is a static buffer for detailed check output. Listing does not write persistent files and calls `io_close(pair, false)` to avoid source deletion.

Dependencies and integration points: Depends heavily on liblzma index, block, filter-string, check-size, and file-info decoder APIs. Uses `file_io.c` for safe open/seek/read, `message.c` for verbosity and diagnostics, `hardware.c` list-mode memlimit, `args.c` globals for robot/stdout/force, and `tuklib` multibyte width helpers.

Risks: Detailed mode can be slow because it seeks and parses each block header and check value. Totals have TODO overflow checks. `list_file()` mutates global `opt_stdout` and `opt_force`; that is safe in list-only execution but would be risky if reused in a mixed-mode future. Robot output masks filenames but still has a stable tab-delimited schema that tests must preserve. Minimum-version logic must track new filters and decoder quirks.

Test signals: Use empty, too-small, corrupt, multi-stream, stream-padding, no-check, CRC/SHA, unknown-check, blocks with and without size fields, empty LZMA2 block, ARM64/RISC-V filter chains, huge block counts, multi-file totals, robot modes at `-l`, `-lv`, `-lvv`, and memory-limit failures in index parsing.
