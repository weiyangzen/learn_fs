# sources/compression/lz4/programs/lz4-exe.rc.in

Purpose: Windows executable resource template for embedding LZ4 version/product metadata.

Important fields: `FILEVERSION`, `PRODUCTVERSION`, company, description, internal/original filename, product name/version, and translation data. Build-time placeholders include `@LIBVER_MAJOR@`, `@LIBVER_MINOR@`, `@LIBVER_PATCH@`, `@PROGNAME@`, and `@EXT@`.

Control flow/state: declarative only; the build system substitutes tokens before compiling the resource.

Dependencies/integration: used by Windows build/package paths for the CLI executable.

Risks: bad substitution yields incorrect metadata; language/codepage and copyright years are hard-coded.

Test signals: validated by successful Windows resource builds and release/version packaging checks.
