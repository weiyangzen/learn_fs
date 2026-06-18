# sources/distributed-fs/openafs/src/comerr/internal.h

Purpose: private include for the AFS com_err package.

Important APIs/types/functions: includes the MIT SIPB copyright header plus `errno.h`, `stdlib.h`, and `stdio.h`, and declares `yyerror(const char *s)` plus `xmalloc(unsigned int size)` for parser/compiler support.

Control flow: this header has no executable control flow; it standardizes private declarations shared by generated parser/scanner and comerr tooling.

State and persistence: no state is defined. The declarations imply error-reporting and allocation behavior implemented elsewhere.

Dependencies and integration: bridges lexer/parser code with local comerr helpers and libc error/allocation/stdio APIs. It is included by comerr implementation files such as `et_name.c` and generated grammar support.

Risks and test signals: risks are prototype drift, especially around old K&R-era generated C and `unsigned int` allocation sizes. Compile coverage of the comerr tools and parser error paths is the main signal.
