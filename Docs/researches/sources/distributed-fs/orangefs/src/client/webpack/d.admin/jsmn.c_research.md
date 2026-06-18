## sources/distributed-fs/orangefs/src/client/webpack/d.admin/jsmn.c

Purpose: Provides the bundled minimal jsmn JSON tokenizer used by the admin module to parse small request bodies.

Important APIs, types, and functions: Public functions are `jsmn_parse` and `jsmn_init`. Internal helpers are `jsmn_alloc_token`, `jsmn_fill_token`, `jsmn_parse_primitive`, and `jsmn_parse_string`. The parser emits flat `jsmntok_t` tokens with type, start/end offsets, size, and optional parent links.

Control flow: `jsmn_parse` scans the JSON string byte-by-byte, allocating tokens for objects/arrays, strings, and primitives, maintaining `toksuper` as the current parent. Closing delimiters resolve the most recent open object/array. At end, unmatched containers produce `JSMN_ERROR_PART`.

State and persistence: Parser state is in caller-owned `jsmn_parser` and token arrays. No allocations are performed by the parser itself.

Dependencies and integration points: Includes only `<stdlib.h>` and `jsmn.h`. `mod_orangefs_admin.c` uses it for attribute update JSON.

Risks and test signals: This older jsmn copy does not validate `\uXXXX` hex digits and is non-strict by default, accepting broad primitive syntax. Token count limits are caller-enforced. Test valid/invalid objects, arrays, strings with escapes, partial JSON, too few tokens, non-strict primitives, and admin payloads over/under 50 tokens.
