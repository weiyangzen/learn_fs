# sources/distributed-fs/coda/coda-src/util/Makefile.am

## Purpose
This Automake fragment builds the private Coda utility library `libutil.la`, collecting generic containers, recoverable/RVM containers, logging, daemonization, paths, secrets, histograms, and small testsupport utilities used by Coda server and client programs.

## Important APIs, Types, And Functions
`noinst_LTLIBRARIES = libutil.la` makes the library internal to the build. `libutil_la_SOURCES` lists every source and public header in this subset, including `arrlist`, `bitmap`, `bitvect`, `bstree`, `dhash`, `dict`, `dlist`, `ohash`, `olist`, `rec_*`, `rvmlib`, `util`, `vice_file`, `vmindex`, and `bitmap7`. `AM_CPPFLAGS` pulls RVM/RPC2 flags and the base include directory.

## Control Flow
Automake expands this source list into compile and archive rules. Downstream `coda-src` programs link against `libutil.la` instead of rebuilding these primitives independently.

## State And Persistence
The file has no runtime state. Its build state is the membership of `libutil.la`, which controls which utility APIs are available to Coda components.

## Dependencies And Integration Points
It depends on configured `$(RVM_RPC2_CFLAGS)` and `lib-src/base` headers. Integration points include update server, volume/server code, RVM-backed metadata structures, and utility tests.

## Risks
Because headers and implementations are explicitly enumerated, adding a new utility file without updating this list will compile locally only if included elsewhere. RVM/RPC2 include flags are shared by many sources, so configuration drift can break unrelated utility builds.

## Test Signals
Run Automake/configure builds, verify `libutil.la` contains each listed object, build clients such as `updatesrv` and tests such as `proctest`, and test with RVM enabled/disabled configuration matrices.
