# sources/distributed-fs/coda/coda-src/asr/resolver_lexer.l

Purpose: Flex lexer for the ASR `RESOLVE` rule language.

Important APIs/tokens: Produces tokens such as `COLON`, `SEMI_COLON`, `COMMA`, `BLANK_LINE`, `NEW_LINE`, `INTEGER`, `OBJECT_NAME`, `DEPENDENCY_NAME`, `COMMAND_NAME`, `ARG_NAME`, and `ALL`. Defines `yywrap` and global `context`.

Control flow: Whitespace is mostly skipped. Token classes depend on parser-maintained `context`: object names in file context, dependency names in dependency context, commands in command context, and arguments plus replica selectors in argument context. Brackets are accepted only in argument context. Backslash-newline joins lines, and comment/blank groups can return `BLANK_LINE`.

State and persistence: Maintains global lexer `context` and line numbers; no filesystem writes.

Dependencies and integration: Includes generated `resolver_parser.h` and `asr.h`. Its tokens drive `resolver_parser.y`, which builds `rule_t` objects.

Risks and test signals: Context-sensitive tokenization is fragile after syntax errors. Character classes are restrictive and may reject valid modern paths. The lexer uses older lex compatibility declarations and custom YYERRCODE handling.
