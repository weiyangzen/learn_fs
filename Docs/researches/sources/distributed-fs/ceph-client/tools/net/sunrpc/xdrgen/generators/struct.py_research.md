# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/struct.py

Purpose: Generates C declarations, definitions, encoders, decoders, and maxsize macros for XDR struct types.

Important APIs and functions: Helper functions emit struct-level and field-level code for `_XdrBasic`, strings, fixed/variable opaque data, fixed/variable arrays, and optional data. `XdrStructGenerator` exposes the standard `SourceGenerator` methods.

Control flow: Public structs get declaration close templates. Definitions emit open, every field, and close templates. Decoders and encoders emit open templates, per-field code in source order, and close templates. Maxsize joins each field's symbolic width into `<HEADER>_<struct>_sz`.

State and persistence behavior: Stateless stdout output, reading global public/header state.

Dependencies and integration points: Called for `_XdrStruct` nodes by declaration, definition, and source subcommands. Shares much field handling logic with pointer and typedef generators.

Risks: Field support is duplicated across definition/decoder/encoder helpers, so adding a new declaration kind can leave one path incomplete. Template selection depends on each AST field's `template` string.

Test signals: Generate structs containing every supported field kind, public/nonpublic structs, optional data members, and arrays of defined types; compile and inspect maxsize macros.
