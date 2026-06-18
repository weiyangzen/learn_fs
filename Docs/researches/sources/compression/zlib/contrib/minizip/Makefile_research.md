# sources/compression/zlib/contrib/minizip/Makefile

Purpose: provides a simple legacy make build for the minizip and miniunz demo tools against the top-level static zlib library.

Important APIs/types/functions: variables `CPPFLAGS`, `UNZ_OBJS`, `ZIP_OBJS`; targets `all`, `miniunz`, `minizip`, `test`, and `clean`; dependency rules for object files.

Control flow: `all` builds both tools. Link rules compile object lists plus `../../libz.a`. The `test` target creates `test.txt`, zips it, lists the archive, renames the original, extracts it, compares extracted content, and deletes temporary files.

State and persistence: creates local object files, executables, and temporary `test.*` files; `clean` removes them.

Dependencies/integration: assumes a built `../../libz.a`, POSIX shell utilities, `CC`, `LDFLAGS`, and local minizip sources.

Risks: no compiler warnings, large-file flags, BZip2 support, Windows-specific `iowin32.o`, or install rules. The test covers only a tiny stored/deflated text case and not Zip64, paths, encryption, or overwrite prompts.

Test signals: `make test` gives a basic zip/list/unzip/cmp smoke signal.
