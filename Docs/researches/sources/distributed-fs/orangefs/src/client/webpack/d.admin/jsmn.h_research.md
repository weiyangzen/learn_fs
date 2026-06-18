## sources/distributed-fs/orangefs/src/client/webpack/d.admin/jsmn.h

Purpose: Declares the bundled jsmn JSON token types, parser state, error codes, and parse/init APIs.

Important APIs, types, and functions: Defines `jsmntype_t` (`PRIMITIVE`, `OBJECT`, `ARRAY`, `STRING`), `jsmnerr_t` (`NOMEM`, `INVAL`, `PART`, `SUCCESS`), `jsmntok_t`, `jsmn_parser`, `jsmn_init`, and `jsmn_parse`.

Control flow: No runtime logic; callers initialize a parser, supply JSON text and a token array, then inspect returned token spans in the original string.

State and persistence: No global state. Parser progress and token output are caller-owned.

Dependencies and integration points: Used by the admin Apache module; optional `JSMN_PARENT_LINKS` changes token layout ABI by adding a parent field.

Risks and test signals: Header ABI must match `jsmn.c` compile flags, especially `JSMN_PARENT_LINKS`. Tokens are not NUL-terminated strings, so callers must honor spans instead of using unbounded string functions. Test compilation with/without parent links and caller parsing of adjacent keys with shared prefixes.
