# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/enum.py

Purpose: Generates C definitions, optional public declarations, XDR encoders/decoders, and maxsize macros for XDR enum types.

Important APIs and functions: `XdrEnumGenerator` implements `emit_declaration`, `emit_definition`, `emit_decoder`, `emit_encoder`, and `emit_maxsize`. It consults `public_apis`, `big_endian`, `get_header_name`, and `get_xdr_enum_validation`.

Control flow: Public enums get declaration templates. Definitions emit open, one enumerator per AST enumerator, and either normal or big-endian close templates. Decoder and encoder templates switch for big-endian enums. Maxsize emits a macro named `<HEADER>_<enum>_sz` with symbolic width.

State and persistence behavior: Stateless output to stdout, reading global pragma state.

Dependencies and integration points: Called by declaration, definition, and source subcommands for `_XdrEnum` nodes. Template selection ties directly to C kernel XDR support routines.

Risks: Global `big_endian` and `public_apis` are process-wide. Header name defaults to `none`, which affects macro names if the pragma is absent. Enum validation can be disabled by source subcommand options.

Test signals: Generate normal, public, big-endian, and validation-disabled enum specs; compile generated C snippets where possible.
