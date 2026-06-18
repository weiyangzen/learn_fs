# sources/distributed-fs/coda/coda-src/asr/Makefile.am

Purpose: Automake build recipe for the legacy ASR resolver/parser client program.

Important APIs/build targets: Conditionally builds `parser` when `BUILD_CLIENT` is enabled. Sources include `resolver_parser.y`, `resolver_lexer.l`, `ruletypes.cc`, `ruletypes.h`, `resolver.cc`, `wildmat.c`, `path.c`, and `asr.h`; `resolve.eg` is distributed as extra data.

Control flow: Yacc is invoked with `-d` to generate headers. A custom rule compiles `resolver_parser.c` as C++ into `resolver_parser.o`, matching its C++ semantic actions and `rule_t` usage. Lexer generation depends on `resolver_parser.h`.

State and persistence: Build-only file; it does not define runtime state.

Dependencies and integration: Includes RPC2, base, util, kerndep, vicedep, and vv include paths. Links util, kerndep, and base libraries.

Risks and test signals: Parser generation depends on generated header order and C++ compilation of yacc output. Build coverage of this target is conditional on client builds.
