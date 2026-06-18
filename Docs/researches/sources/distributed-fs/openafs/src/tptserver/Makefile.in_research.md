# sources/distributed-fs/openafs/src/tptserver/Makefile.in

## Purpose
Builds pthreaded variants of the Protection Server tools from sources in `src/ptserver`. It produces server, client, utility, consistency checker, and test binaries when pthreaded ubik support is enabled.

## Important APIs, Types, And Functions
Targets include `ptserver`, `pts`, `pt_util`, `prdb_check`, `readgroup`, `readpwd`, `testpt`, generated `pterror.c/.h`, `ptint.ss.c`, `ptint.xdr.c`, and `ptint.h`. It defines common, server, and client library groups around pthreaded ubik, Rx, rxkad, rxstat, cmd, util, audit, prot, sys, lwpcompat, and opr libraries. Build flags include `CFLAGS_NOSTRICT` for selected ptserver files.

## Control Flow
The makefile compiles ptserver source files from `$(PTSERVER)`, generates the pt RPC interface with `RXGEN`, builds binaries with static libtool link rules, and conditionally installs/dests outputs only when `ENABLE_PTHREADED_UBIK` is `yes`. Error table generation also creates `prerror.h` as a compatibility header aliasing PT error-table base.

## State And Persistence
Build outputs include generated RPC/error files, objects, and binaries. Install/dest targets persist server tools into configured server/client bindirs when pthreaded ubik is enabled. No runtime database state is touched by the makefile.

## Dependencies And Integration Points
This makefile is a bridge from `src/tptserver` to the canonical `src/ptserver` source tree, using pthread config and pthreaded ubik libraries. It integrates rxgen, compile_et, libtool, version generation, and install paths for OpenAFS server packaging.

## Risks And Test Signals
Risks are drift between ptserver sources and this wrapper, missing generated headers before dependent objects compile, and silent non-installation when `ENABLE_PTHREADED_UBIK` is not set. Useful signals are `make all`, generated-file rebuilds from `.xg`/`.et`, conditional install tests with the flag both enabled and disabled, and linking against the pthreaded ubik library set.
