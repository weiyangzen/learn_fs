# sources/distributed-fs/openafs/src/ptserver/Makefile.in

## Purpose
Builds the OpenAFS protection server, client tools, database utilities, generated Rx interfaces, and protection client libraries.

## Important APIs, Types, And Functions
Major targets are `ptserver`, `pts`, `pt_util`, `prdb_check`, `ptclient`, `readgroup`, `readpwd`, `testpt`, `liboafs_prot.la`, `libprot_pic.la`, and `libprot.a`. Generated interface files come from `ptint.xg` via `RXGEN` (`ptint.cs.c`, `ptint.ss.c`, `ptint.xdr.c`, `ptint.h`, plus kernel variants). Error files are generated from `pterror.et`. Installed headers include `prclient.h`, `prerror.h`, `print.h`, `prserver.h`, `ptclient.h`, `ptuser.h`, `pterror.h`, `ptint.h`, and `ptserver.h`.

## Control Flow
`all` builds server/tools/libraries and runs `depinstall`. Object dependencies enforce generated headers and version source. The server links ptserver core, utility, RPC server stub, xdr, map, and OpenAFS auth/rx/ubik/cmd/audit libraries. Install/dest skip installing LWP server tools when pthreaded ubik is enabled but still install libraries/headers.

## State And Persistence
Build state includes generated C/header/error files, archives, libtool libraries, executables, objects, and component version source. Install/dest persist server binaries, user tools, libraries, and headers.

## Dependencies And Integration Points
This makefile is the central build integration point for the protection service, Rx RPC generation, Ubik replication, authentication, audit, and command-line tooling.

## Risks And Test Signals
Risks include generated-file ordering, strict-aliasing exceptions for supergroups, library-order sensitivity, and pthreaded-Ubik install conditionals. Test signals are successful generation, all binaries/libraries linked, installed headers present, and functional `pts`, `ptclient`, `pt_util`, and `prdb_check` tools.
