# sources/distributed-fs/openafs/src/ubik/Makefile.in

## Purpose
Builds the core ubik replicated database library, authenticated ubik client subset, generated ubik RPC interfaces, error headers, debug/test utilities, and libtool libraries.

## Important APIs, Types, And Functions
Important target groups are `LT_authent_objs`, `LT_objs`, `LT_deps`, `libubik.a`, `liboafs_ubik.la`, `libauthent_ubik.la`, `udebug`, `utst_server`, and `utst_client`. Generated outputs include `ubik_int.cs/ss/xdr.c`, `ubik_int.h`, kernel `Kubik_int.*`, `utst_int.*`, `uerrors.c`, and `ubik.h`.

## Control Flow
`all` performs dependency install, builds static and libtool libraries, and builds debug/test tools. RXGEN produces user and kernel ubik interfaces; compile_et produces ubik errors and public `ubik.h`. Installation copies `libubik.a`, `ubik.h`, `ubik_int.h`, and `udebug` to configured library/include/bindir paths. Clean removes objects, generated interfaces, error outputs, libraries, tools, and version files.

## State And Persistence
Persistent build/install artifacts are ubik libraries, public headers, generated RPC files, and `udebug`. Runtime database state is not affected by the makefile.

## Dependencies And Integration Points
The makefile is central to ubik consumers: ptserver, vlserver, volser, auth clients, and test tools. It integrates LWP build rules, rxgen, compile_et, libtool static/shared rules, auth/comerr/lwp/rx/util/opr dependencies, and public include/library install locations.

## Risks And Test Signals
Risks include ABI drift in generated RPC headers, mismatch between static and libtool object sets, generated kernel/user interface confusion, and public header install ordering. Test signals are full `make all`, generated-file determinism, `libubik.a` and `liboafs_ubik.la` link success, `udebug` smoke execution, and downstream rebuilds of pt/vl/volser targets.
