# sources/distributed-fs/openafs/src/budb/Makefile.in

## Purpose
Defines the Autoconf make rules for building and installing the OpenAFS backup database client library, generated BUDB RPC/error headers, generated RX stubs, and the `budb_server`/`buserver` binary.

## Important APIs, Types, And Functions
Key variables are `INCLS`, `LIBS`, `COMMON_OBJS`, and `SERVER_OBJS`. Major targets are `all`, `generated`, `${TOP_LIBDIR}/libbudb.a`, installed headers under `${TOP_INCDIR}/afs`, `budb_errs.[ch]`, generated `budb.cs.c`, `budb.ss.c`, `budb.xdr.c`, `budb.h`, `libbudb.a`, `budb_server`, `install`, `dest`, and `clean`.

## Control Flow
The default target builds the static client library, installs generated headers into the object include tree, and links `budb_server`. Error table sources come from `budb_errs.et` via `COMPILE_ET_*`. RPC sources and headers come from `budb.rg` via `RXGEN` in client, server, xdr, and header modes. `libbudb.a` archives the error object, client stub, XDR object, struct operations, and component version object. `budb_server` links server/common objects with OpenAFS libraries in top-level-defined order. Install and dest targets copy libraries, headers, and the server binary to packaging/staging locations.

## State And Persistence
Build outputs are generated `.c/.h`, object files, `libbudb.a`, and `budb_server`. Installation persists artifacts under configured lib/include/server-libexec directories or legacy `${DEST}` staging paths. `clean` removes generated stubs, generated headers, archive, objects, core, server binary, and component version file.

## Dependencies And Integration Points
Depends on top object configuration includes, `Makefile.lwp`, RXGEN, compile_et, top-level library layout, generated `AFS_component_version_number.c`, BUDB source files, and many OpenAFS libraries (`libbubasics`, audit, prot, kauth, ubik, auth, rxkad, sys, rx, lwp, cmd, com_err, util, opr, crypto helpers). The generated headers are consumed by `bucoord` and other backup components.

## Risks And Test Signals
Library ordering is manually encoded and can break link resolution. Generated-file dependencies must be correct for parallel builds. The `all` target expects generated headers and library installation into `${TOP_INCDIR}`/`${TOP_LIBDIR}` before downstream consumers build. Test signals include clean-tree parallel `make generated`, `make all`, relink after touching `budb.rg` and `budb_errs.et`, install/dest staging, and `make clean` removing generated outputs without removing source files.
