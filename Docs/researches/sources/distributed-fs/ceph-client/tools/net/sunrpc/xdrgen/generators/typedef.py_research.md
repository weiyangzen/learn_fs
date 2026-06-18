# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/typedef.py

Purpose: Generates C typedef definitions plus optional public declarations, encoders, decoders, and maxsize macros for XDR typedefs.

Important APIs and functions: `emit_typedef_declaration`, `emit_type_definition`, `emit_typedef_decoder`, `emit_typedef_encoder`, and `emit_typedef_maxsize` handle declaration variants. `XdrTypedefGenerator` invokes them for `_XdrTypedef.declaration`.

Control flow: Public declarations are emitted only for names in `public_apis`. Definitions support basic, string, fixed/variable opaque, fixed/variable array declarations. Encoders and decoders parallel those variants. Optional-data typedefs raise `NotImplementedError`, and void typedefs raise `ValueError`.

State and persistence behavior: Stateless stdout generation, using header/public global state.

Dependencies and integration points: Used by definitions, declarations, and source subcommands after `xdr_ast` computes widths and pass-by-reference metadata.

Risks: Some template renders use `node.spec.type_name` while declarations use `kernel_c_type`, so generated C type spelling differs by context intentionally but must match templates. Optional-data typedef support is absent.

Test signals: Generate typedefs for all supported forms, public and nonpublic, arrays of defined types, and unsupported optional/void cases; verify errors and generated maxsize macros.
