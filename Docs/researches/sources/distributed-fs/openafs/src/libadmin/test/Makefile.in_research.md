<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/Makefile.in -->
# sources/distributed-fs/openafs/src/libadmin/test/Makefile.in

## Purpose
Builds the `afscp` libadmin test driver and its command modules.

## Important APIs, Types, And Functions
`AFSCPLIBS` links admin utility, client, bos, vos, kas, pts, afsrpc, auth, cmd, kauth, opr, ubik, util, and crypto libraries. `AFSCPOBJS` lists command modules: `bos.o`, `client.o`, `kas.o`, `pts.o`, `util.o`, and `vos.o`. The `afscp` target links those with `afscp.o`.

## Control Flow
`all`, `test`, and `tests` build `afscp`. `CFLAGS_client.o = @CFLAGS_NOERROR@` suppresses warning-as-error for the client test module. `install` and `dest` are no-ops. `clean` removes libtool files, objects, the `afscp` binary, and core files.

## State And Persistence
Build products are generated in the test directory. No runtime state is managed by the makefile.

## Dependencies And Integration Points
It integrates the libadmin subsystem tests into the OpenAFS build and links all major admin libraries because `afscp` exercises BOS, client, KAS, PTS, util, and VOS command families.

## Risks And Test Signals
Risks include library-order fragility, hidden client-module warnings, and no install target for external test packaging. Signals are successful `make tests`, successful static link, and running `afscp` subcommands against a configured test cell.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/Makefile.in -->
