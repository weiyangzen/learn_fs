# sources/distributed-fs/lizardfs/doc/CMakeLists.txt

## Purpose
This CMake file builds and installs LizardFS manual pages from AsciiDoc sources using `a2x`.

## Important APIs, Types, and Functions
It checks `A2X_BINARY`, defines the `MANPAGES` list, creates custom commands for each existing `<manpage>.txt`, installs generated manpages into `${MAN_SUBDIR}/man<section>`, synthesizes `mfsmount3.1.txt` by replacing `mfsmount` with `mfsmount3`, and creates an `ALL` custom target `manpages`.

## Control Flow and State
If `a2x` is unavailable, it warns and returns early. For each listed manpage, it builds a symlink to the source text in the binary dir and runs `a2x -L -f manpage`, optionally with verbose/keep-artifacts flags. It installs each generated manpage even though generation only occurs for source files that exist. The special `mfsmount3.1` output is always generated from `mfsmount.1.txt`.

## Dependencies and Integration Points
Top-level `CMakeLists.txt` adds `doc` when `ENABLE_DOCS` is on. This file depends on `a2x`, source `.txt` files, CMake install paths, and `ENABLE_VERBOSE_ASCIIDOC`.

## Risks and Edge Cases
The loop calls `install(FILES ${GENERATED_MANPAGE_PATH} ...)` for every listed page, even entries without source files and without generated output, which can cause install-time issues depending on CMake behavior. The `mfsmount3` text replacement is global and may alter more than command names. `ln -s` is Unix-specific.

## Test Signals
The `manpages` target and installed man files are the signals. Missing `a2x` disables generation with a warning.
