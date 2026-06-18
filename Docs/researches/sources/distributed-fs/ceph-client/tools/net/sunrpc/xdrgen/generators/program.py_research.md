# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/program.py

Purpose: Generates C RPC program/procedure constants plus procedure argument/result declarations and peer-specific encoder/decoder wrappers.

Important APIs and functions: Helpers emit version procedure definitions, declarations for unique argument/result types, server argument decoders, client result decoders, client argument encoders, server result encoders, and max-argument-size macros. `XdrProgramGenerator` dispatches by peer.

Control flow: Program names are lowercased with `_program`/`_prog` suffixes removed. Definitions emit procedure numbers for each version and the program number. Declarations deduplicate argument and result type names with dictionaries. Source generation switches on `peer`: server decodes arguments and encodes results; client encodes arguments and decodes results. `emit_maxsize` selects the largest non-void, non-excluded argument width.

State and persistence behavior: Stateless stdout output, reading global `excluded_apis`, `max_widths`, and header name.

Dependencies and integration points: Used for `_RpcProgram` nodes by all generator subcommands. Integrates AST procedure metadata with C template naming conventions.

Risks: Exclusion is by procedure name only and global. Missing `max_widths` entries silently skip max-args consideration. Client source has a TODO for procedure macros.

Test signals: Generate multi-version RPC specs with duplicate argument/result types, excluded procedures, void arguments, and varying max widths; verify server/client output differs correctly.
