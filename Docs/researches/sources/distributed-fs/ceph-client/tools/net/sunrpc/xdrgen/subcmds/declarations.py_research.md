# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/subcmds/declarations.py

Purpose: Implements the XDR generator subcommand that emits declaration headers for public XDR APIs and RPC procedure argument/result helpers.

Important APIs and functions: `emit_header_declarations(root, language, peer)` dispatches AST definitions to enum, pointer, typedef, struct, union, and program generators. `subcmd(args)` is the command entry point.

Control flow: The subcommand sets annotation mode, parses the input file with `xdr_parser` and `make_error_handler`, transforms the parse tree into an AST, emits header-top boilerplate, emits declarations for supported AST nodes in source order, emits header-bottom boilerplate, and returns 0 or 1 on parse/semantic errors.

State and persistence behavior: Reads one XDR file and writes generated header text to stdout. It mutates parser global `annotate` and AST globals through transformation.

Dependencies and integration points: Depends on Lark, generator modules, `xdr_ast`, and `xdr_parse`. Intended to be called by a higher-level CLI with `filename`, `language`, `peer`, and `annotate`.

Risks: The dispatch creates a new generator for each definition. Global AST side effects are not reset between invocations in the same process. Unsupported node types are silently skipped.

Test signals: Run on valid specs with public and nonpublic types, RPC programs, parse errors, and undefined types; verify output and return status.
