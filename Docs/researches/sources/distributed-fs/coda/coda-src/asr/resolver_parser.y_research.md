# sources/distributed-fs/coda/coda-src/asr/resolver_parser.y

Purpose: Yacc grammar and semantic actions for ASR `RESOLVE` files.

Important APIs/grammar objects: Builds global `olist rules` by allocating `rule_t`, `command_t`, object, dependency, argument, and replica-specifier objects. `yyerror` reports line/token/context.

Control flow: A rule is `object_list : dependency_list` followed by a command list, with blank lines separating rules. Parser actions update lexer `context` before dependency, command, and argument regions. Commands collect arguments and optional `[index]` or `[all]` replica specifiers; command terminators append the current command to the current rule.

State and persistence: All parsed state is heap-allocated C++ objects in the global `rules` list. No persistence beyond reading the rule file.

Dependencies and integration: Requires lexer tokens, `asr.h`, `olist`, and `ruletypes.h`. The generated parser is compiled as C++ by the Makefile.

Risks and test signals: Global `crule` and `ccmd` mean parsing is non-reentrant. Error handling reports but returns 0, so callers need to validate parse outcomes. Empty starts allocate rules; ownership is handled later by `rule_t` destructors only if lists are destroyed.
