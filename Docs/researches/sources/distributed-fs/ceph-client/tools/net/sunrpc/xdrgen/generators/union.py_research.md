# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/union.py

Purpose: Generates C structures and XDR encode/decode/maxsize logic for XDR discriminated unions.

Important APIs and functions: Helpers emit declarations, discriminant definitions, case/default arm definitions, decoders, encoders, and maxsize macros. `XdrUnionGenerator` implements the `SourceGenerator` interface. It consults `public_apis`, `big_endian`, and `get_header_name`.

Control flow: Definitions emit an open union wrapper, discriminant field, non-void case/default arms, and close. Decoders and encoders special-case boolean discriminants by emitting an `if` path for the TRUE case; otherwise they emit switch discriminants, all cases, a default block, and close. Big-endian discriminants select alternate case templates.

State and persistence behavior: Stateless stdout output with global pragma inputs.

Dependencies and integration points: Used for `_XdrUnion` AST nodes by subcommands. Supports only basic and string arm payloads in several paths, with assertions enforcing expected AST shapes.

Risks: Boolean union handling only emits the TRUE arm and relies on templates for the false/no-data path. Default handling asserts basic arms in some paths, so richer arm types are unsupported. `symbolic_width` in the AST must define a widest arm.

Test signals: Generate unions with enum, integer, big-endian, and bool discriminants; include void/default/string arms; compile generated code and verify decode switch cases.
