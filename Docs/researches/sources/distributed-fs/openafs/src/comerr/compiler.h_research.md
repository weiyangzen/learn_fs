# sources/distributed-fs/openafs/src/comerr/compiler.h

Purpose: shared declarations for the error table compiler and parser sources.

Important APIs and state: defines `enum lang` values `lang_C`, `lang_KRC`, and unfinished `lang_CPP`; declares global parser/compiler state `debug`, `filename`, `language`, and `whoami`; declares `yyparse`.

Control flow and dependencies: no executable logic. It couples `compile_et.c` and yacc/lex generated code through global variables.

Risks and tests: global state makes the compiler non-reentrant. C++ support is represented in the enum but rejected by `compile_et.c`. Build coverage comes from compiling `compile_et`.
