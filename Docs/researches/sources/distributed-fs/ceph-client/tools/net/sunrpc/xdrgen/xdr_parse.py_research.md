# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/xdr_parse.py

Purpose: Provides parser construction, parser/decoder option globals, and user-friendly parse/semantic error reporting for XDR generator subcommands.

Important APIs and functions: `set_xdr_annotate`, `get_xdr_annotate`, `set_xdr_enum_validation`, and `get_xdr_enum_validation` manage generation flags. `make_error_handler(source, filename)` returns a Lark `on_error` callback that prints filename/line/column, unexpected token, expected tokens, source line, and caret. `handle_transform_error` reports semantic transform failures. `xdr_parser()` opens `grammars/xdr.lark`.

Control flow: Subcommands set globals, call `xdr_parser`, parse with the error handler, and transform with `xdr_ast`. Parse errors raise `XdrParseError` to abort after the first formatted diagnostic. Transform errors unwrap `VisitError` and special-case undefined-type `KeyError`.

State and persistence behavior: `annotate` and `enum_validation` are process-global booleans. No persistent files are written.

Dependencies and integration points: Depends on Lark, `grammars/xdr.lark`, and subcommands/generators that read the option globals.

Risks: Global flags can leak across invocations. Error token mapping is partial and grammar changes may produce raw token names. Strict LALR parser construction may fail early if grammar conflicts appear.

Test signals: Parse valid files, unexpected identifiers/numbers/punctuation, EOF errors, undefined types, annotation on/off, enum validation on/off, and grammar path resolution from different working directories.
