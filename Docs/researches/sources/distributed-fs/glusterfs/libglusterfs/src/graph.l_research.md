# sources/distributed-fs/glusterfs/libglusterfs/src/graph.l

Purpose: `graph.l` is the flex lexer for GlusterFS volfile syntax.

Important APIs and types: it returns tokens for `volume`, `type`, `end-volume`, `subvolumes`, `option`, unquoted IDs, and quoted strings. It defines a `STRING` start condition and accumulates quoted string text in static `text`/`text_size` using `append_string`.

Control flow and state: comments beginning with `#` and whitespace are skipped. Keywords are lowercase regexes. A quote enters `STRING` mode; normal string chunks and escaped characters append to the static buffer; a closing quote returns `STRING_TOK` with `graphyylval = text`. Unquoted words are duplicated and returned as `ID`.

Dependencies and integration: includes `xlator.h` for allocation helpers and `y.tab.h` for parser tokens. The parser in `graph.y` consumes these tokens while holding a graph-construction mutex.

Risks: keyword matching is case-sensitive except for `subvolume[s]` final `s/S`. Unterminated strings are not explicitly reported in the lexer. `append_string` can lose the previous buffer if `GF_REALLOC` fails because it assigns directly to `text`. Static string state is non-reentrant.

Test signals: lexer/parser tests should cover quoted values with escapes, whitespace, comments, uppercase/lowercase keywords, unterminated quotes, allocation failure, and repeated parse invocations.
