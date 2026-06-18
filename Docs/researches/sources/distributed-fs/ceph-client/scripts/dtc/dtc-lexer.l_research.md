# sources/distributed-fs/ceph-client/scripts/dtc/dtc-lexer.l

## Purpose
`dtc-lexer.l` is the flex lexer for DTS source input. It tokenizes DTS syntax, handles include files and line directives, tracks source positions, and passes typed semantic values to the Bison parser.

## Important APIs, Types, and Functions
Start states include `BYTESTRING`, `PROPNODENAME`, and `V1`. Tokens include strings, labels, references, literals, character literals, bytes, directives, delete/omit keywords, operators, and property/node names. `push_input_file()`, `pop_input_file()`, and `lexical_error()` integrate with `srcfile` and `srcpos`.

## Control Flow and State
`YY_USER_ACTION` updates `yylloc` on every token. `/include/ "file"` pushes a new input buffer. EOF pops include buffers until the root ends. Line directives update source position. Strings and character literals use `data_copy_escape_string()`. The lexer switches to `BYTESTRING` after `[`, to `PROPNODENAME` after `{`, `;`, and delete/omit directives, and to `V1` after `/dts-v1/`. Lexical errors set `treesource_error`.

## Dependencies and Integration
It depends on flex, `dtc-parser.tab.h`, `dtc.h`, `srcpos.h`, srcfile helpers, and parser globals.

## Risks and Test Signals
Lexer state transitions are grammar-coupled. The comment notes buffer behavior assumes no `yyless()` or `yyunput()`. Path/reference regexes are permissive but not full path parsers. Test nested includes, line directives with escaped filenames, literals with suffixes, bad identifiers after `/dts-v1/`, byte strings, labels in property data, delete directives, and lexical errors.
