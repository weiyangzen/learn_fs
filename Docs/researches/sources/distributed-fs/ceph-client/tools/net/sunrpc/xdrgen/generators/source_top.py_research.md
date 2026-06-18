# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/source_top.py

Purpose: Emits top-of-file boilerplate for generated client or server XDR C source files.

Important APIs and functions: `XdrSourceTopGenerator.emit_source(filename, root)` finds the program/header name, selects the template named for `peer`, and renders program name, source filename, and source mtime.

Control flow: Program name comes from `find_xdr_program_name`, which prefers a header pragma and otherwise derives from the first RPC program definition. Peer selects `server.j2` or `client.j2`.

State and persistence behavior: Reads source file mtime and prints to stdout.

Dependencies and integration points: Used by `subcmds/source.py` before type-specific encoders/decoders. Depends on boilerplate templates and AST program discovery.

Risks: Output is time-dependent. If no RPC program exists and no header pragma is set, generated name falls back to `noprog`.

Test signals: Generate source for specs with header pragma, with program name suffixes, and with no program; verify selected template and name.
