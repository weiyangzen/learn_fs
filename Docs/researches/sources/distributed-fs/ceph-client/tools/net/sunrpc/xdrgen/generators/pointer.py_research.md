# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/pointer.py

Purpose: Generates C structures and XDR encode/decode/maxsize logic for self-referential optional-data structs represented as pointer-like XDR types.

Important APIs and functions: Helper functions emit declarations, member definitions, decoders, encoders, and maxsize macros. `XdrPointerGenerator` wraps those helpers for `_XdrPointer` AST nodes. Member emitters handle basic types, opaque data, strings, fixed/variable arrays, and optional data.

Control flow: Definitions open a struct-like template, emit all fields except the final optional self-reference sentinel, then close. Decoders and encoders similarly skip the final optional-data field after emitting a leading presence bool through pointer templates. Public declarations are emitted only when the pointer type is in `public_apis`.

State and persistence behavior: Stateless stdout generation, reading global header/public state.

Dependencies and integration points: `_XdrPointer` nodes are created by `xdr_ast.ParseToAst.struct` when the last field is optional data of the same type. Templates use `kernel_c_type`, `classifier`, `maxsize`, and `symbolic_width` values.

Risks: Skipping `node.fields[0:-1]` assumes the AST pointer invariant is correct. Optional-data typedefs are not generally implemented elsewhere. Template coverage is type-specific and new declaration variants require updates in multiple helper branches.

Test signals: Generate a recursive linked-list-like XDR struct, verify no final self field is emitted as a normal member, and compile generated encoder/decoder stubs.
