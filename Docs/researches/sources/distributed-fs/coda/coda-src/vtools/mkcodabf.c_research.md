# sources/distributed-fs/coda/coda-src/vtools/mkcodabf.c

## Purpose

`mkcodabf.c` converts a large regular file into a Coda "big file" directory containing numbered data hunks and a `_Coda_BigFile_` metadata marker.

## Important APIs, Types, and Functions

Global options include `hunksize`, `hunkbytes`, `filesperdir`, `dirdigits`, and `verbose`. `main()` parses `-f`, `-s`, and `-v`, validates source and destination, creates the target directory, and calls `mkbigfile()`. `mkbigfile()` computes required hunk count and directory levels, creates one or two levels of numbered subdirectories, writes each chunk file as mode `0444`, and writes `_Coda_BigFile_` with `CDBGFL00 <size> <hunksize> <filesperdir> <files>`.

## Control Flow

The converter refuses non-regular files, too-small files, existing destinations, hunk sizes below 1 MB, and files requiring more than two directory levels. It streams the source file sequentially into 8192-byte buffers and writes chunks into deterministic numeric paths.

## State and Persistence Behavior

It creates a directory tree and read-only chunk files at the destination. On failure after destination creation, it exits without cleanup, leaving partial big-file state.

## Dependencies and Integration Points

It depends on POSIX stat/open/read/write/mkdir and Coda's big-file directory convention. Consumers must understand `_Coda_BigFile_`.

## Risks and Test Signals

`hfd` is declared `long` but stores file descriptors. `read()` returning zero before `temp` reaches zero would spin because `temp` is not decremented. Directory creation loops use `<= files / filesperdir`, which can create extra directories at exact boundaries. Existing partial destinations are not rolled back. Tests should cover exact hunk multiples, tiny files, maximum `filesperdir`, two-level layout, read/write short counts, metadata content, and cleanup expectations after failures.
