
# sources/distributed-fs/openafs/src/uss/grammar.y

`grammar.y` defines the yacc grammar for `uss` bulk/template commands. It maps parsed command lines into provisioning actions such as directory creation, file copy, echo, command execution, link creation, volume creation, directory-pool group declaration, and authentication field updates.

Tokens include command tokens (`DIR_TKN`, `FILE_TKN`, `ECHO_TKN`, `EXEC_TKN`, `LINK_TKN`, `SYMLINK_TKN`, `VOL_TKN`, `GROUP_TKN`, `AUTH_TKN`, `VOL1_TKN`), `STRING_TKN`, and `EOL_TKN`. The `entry` rule calls implementation functions directly: `uss_procs_BuildDir`, `uss_procs_CpFile`, `uss_procs_EchoToFile`, `uss_procs_Exec`, `uss_procs_SetLink`, `uss_vol_CreateVol`, `uss_procs_AddToDirPool`, and `uss_kauth_SetFields`. Return values are assigned to global `uss_perr`.

The `accesslist` rule recursively consumes pairs of strings and builds a space-separated ACL string in a fixed 1000-byte semantic value buffer, defaulting to a single space when absent. Error handling prints line-relative context through `uss_procs_PrintErr`, and `yyerror` writes a short parse error to stderr.

There is no direct persistence here, but parser actions immediately call routines that modify filesystem, AFS volumes, ACLs, and authentication state. Dependencies include lexer token values from `y.tab.h`, global `line`, `uss_perr`, and the uss procedure/volume/kauth modules.

Risks include immediate side effects during parsing, fixed-size semantic buffers, recursive ACL string concatenation truncation/error behavior, and a grammar that only validates command shape while deeper validation lives in action functions. Test signals include parsing each command type, optional and multi-entry ACLs, syntax error line reporting, long token/ACL rejection, and `VOL`/`VOL1` compatibility.
