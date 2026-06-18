# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/subcmds/lint.py

Purpose: Provides a syntax and semantic validation subcommand for XDR specifications without emitting code.

Important APIs and functions: `subcmd(args)` parses `args.filename` with `xdr_parser`, reports parse errors with `make_error_handler`, transforms the tree with `transform_parse_tree`, and reports semantic errors with `handle_transform_error`.

Control flow: The command reads the entire source file, parses with Lark, transforms to AST, returns 0 on success, and returns 1 on parse or transform failure.

State and persistence behavior: Read-only with diagnostics to stderr. AST transformation still mutates global metadata such as constants and pragmas in the current Python process.

Dependencies and integration points: Used as a lightweight gate before declaration/definition/source generation. Sets Lark logger to DEBUG for more parser detail.

Risks: Because transform side effects are global, repeated lint calls in one process can affect later generation unless the caller isolates processes or resets state.

Test signals: Lint valid specs, malformed syntax, undefined types, unsupported directives, and duplicate/global-state-sensitive specs; assert return status.
