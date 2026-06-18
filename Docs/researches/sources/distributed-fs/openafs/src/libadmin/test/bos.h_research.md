<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/bos.h -->
# sources/distributed-fs/openafs/src/libadmin/test/bos.h

## Purpose
Declares the BOS command registration function for the `afscp` test driver and pulls in the headers needed by BOS command implementations.

## Important APIs, Types, And Functions
The only explicit declaration is `SetupBosAdminCmd(void)`. The header includes OpenAFS standards, stdlib/stdio/string/errno, pthread, RX/rxstat, BOS/util/client admin headers, cellconfig, cmd, and `common.h`.

## Control Flow
`afscp.c` calls `SetupBosAdminCmd` during startup so `bos.c` can register all BOS subcommands with the command parser.

## State And Persistence
The header stores no state. It exposes access to global handles from `common.h` and the admin APIs that can mutate BOS server state.

## Dependencies And Integration Points
It is shared between `afscp.c` and `bos.c`, coupling the BOS command module to the common auth setup and OpenAFS command-parser environment.

## Risks And Test Signals
The broad include set can hide missing includes in `bos.c`, but compile success of both the module and `afscp` is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/bos.h -->
