# sources/distributed-fs/openafs/src/cmd/test/ctest.c

Purpose: sample/test program for subcommand mode in the `cmd` library. It registers two commands and aliases, then dispatches command-line arguments.

Important APIs: uses `cmd_CreateSyntax`, `cmd_CreateAlias`, `cmd_AddParm`, `cmd_Seek`, and `cmd_Dispatch`. `apple` has no arguments; `pear` demonstrates required list, optional flag, expanding list, sparse parameter offset, and optional single string.

Control flow and state: callbacks print parsed option values from `as->parms`. Parser definitions persist globally until process exit; parsed `cmd_item` lists are reset by `cmd_Dispatch`.

Dependencies and integration: includes `<afs/cmd.h>` and therefore uses the generated command error table header. It is built by the cmd test Makefile.

Risks and tests: callbacks assume required items exist and do no defensive checks. It is primarily a manual parser behavior example for aliases, positional/list parsing, and help generation.
