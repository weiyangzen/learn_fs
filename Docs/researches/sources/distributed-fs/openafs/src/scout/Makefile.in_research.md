<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/scout/Makefile.in -->
# sources/distributed-fs/openafs/src/scout/Makefile.in

## Purpose

This makefile builds and installs the `scout` monitoring command. `scout` is linked as a static OpenAFS tool using fsprobe, gtx UI, rxkad authentication, fsint, cmd, util, opr, LWP compatibility, and volser libraries, plus roken, curses, and optional X11 libraries.

## Important Targets and Variables

`INCLS` lists installed headers required by `scout.o`, mostly GTX UI headers plus keys, cell config, and command parsing headers. `LIBS` lists libtool library dependencies from other OpenAFS source directories:

- `liboafs_fsprobe.la`
- `liboafs_gtx.la`
- `liboafs_rxkad.la`
- `liboafs_fsint.la`
- `liboafs_cmd.la`
- `liboafs_util.la`
- `liboafs_opr.la`
- `liboafs_lwpcompat.la`
- `liboafs_volser.la`

The default `all` target builds `scout`. `scout.o` depends on `scout.c`, the installed headers, and `AFS_component_version_number.c`. `scout` links with `$(LT_LDRULE_static)`.

## Control Flow

Build flow is simple: compile `scout.o`, then statically link it with the library list, roken, curses, and X libraries. The `install` target creates `${DESTDIR}${bindir}` and installs the program there. The `dest` target installs into legacy `${DEST}/bin`. `clean` removes the object, executable, core file, and generated component version source.

## State and Persistence Behavior

The makefile persists only build artifacts and installed binaries. It has no runtime state. Runtime monitoring behavior belongs to `scout.c` and its linked libraries, not this makefile.

## Dependencies and Integration Points

`scout` integrates filesystem probing (`fsprobe`), text/window UI via `gtx` and curses/X11, rxkad security, file-server interface stubs, command parsing, utility/opr helpers, LWP compatibility, and volume-server support. The include dependencies require top-level header installation to have happened before this tool is built.

## Risks and Edge Cases

The `INCLS` list contains `gtxobjects.h` twice, which is harmless but indicates manual maintenance drift. Because `scout` links statically against many internal libraries, dependency ordering can matter; link failures may surface when any library changes its transitive dependencies. Curses and X11 availability are platform-sensitive, so configure substitutions must provide the right `LIB_curses` and `XLIBS`.

## Test Signals

Run `make scout`, `make install DESTDIR=/tmp/stage`, and `make clean`. Link tests should cover builds with and without X11 support as configured. Packaging should verify the final binary lands in `${bindir}` or `${DEST}/bin` as appropriate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/scout/Makefile.in -->
