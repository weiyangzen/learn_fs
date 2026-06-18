# sources/distributed-fs/openafs/src/tbudb/Makefile.in

## Purpose
`src/tbudb/Makefile.in` builds the pthread/libtool backup database server (`budb_server` installed as `buserver`) and associated `libbudb.a` artifacts from sources in `src/budb`.

## Important APIs, types, and functions
Key targets are `all`, `budb_server`, `libbudb.a`, generated `budb_errs.[ch]`, `budb.cs.c`, `budb.ss.c`, `budb.xdr.c`, and `budb.h`, plus `install`, `dest`, and `clean`.

## Control flow
The makefile generates error and RX files from `budb_errs.et` and `budb.rg`, compiles common database objects and server objects from `../budb`, links `budb_server` against bubasics, ubik, sys, rxkad, LWP compatibility, cmd, opr, and util libraries, and installs only when `ENABLE_PTHREADED_UBIK` is yes.

## State and persistence behavior
It creates generated RPC/error files, object files, static archives, the `budb_server` binary, installed headers, and install/dest server binaries. `clean` removes generated files and products.

## Dependencies and integration points
It integrates backup database sources, UBIK, RX/RXKAD, OpenAFS command/util libraries, compile_et, RXGEN, and top-level configured install paths.

## Risks
The makefile contains a likely typo `${LT_INSTALl_PROGRAM}` with a lowercase `l`, which can break install. It must stay synchronized with budb source dependencies and generated headers. Conditional install can hide packaging issues in normal builds.

## Test signals
Run generation, build `libbudb.a` and `budb_server`, exercise `make install` with `ENABLE_PTHREADED_UBIK=yes`, and verify generated headers are consumed by all listed objects.
