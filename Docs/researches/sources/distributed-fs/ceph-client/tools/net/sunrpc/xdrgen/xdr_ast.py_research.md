# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/xdr_ast.py

Purpose: Defines the XDR abstract syntax tree, semantic side-channel tables, width calculation, pragma handling, and Lark parse-tree transformer for the SunRPC XDR generator.

Important APIs and types: Dataclasses model identifiers, values, constants, built-in/defined type specifiers, declarations, constants, enums, structs, pointer-like recursive structs, typedefs, union cases/defaults, RPC procedures/versions/programs, pragmas, pass-through lines, definitions, and specifications. Global tables include `big_endian`, `excluded_apis`, `header_name`, `public_apis`, `structs`, `pass_by_reference`, `constants`, `symbolic_widths`, and `max_widths`. `ParseToAst` transforms grammar productions. `transform_parse_tree` merges adjacent pass-through blocks.

Control flow: During transformation, constructors compute numeric and symbolic XDR widths and update global tables. Defined types consult `structs` to choose C classifiers. Structs ending in optional data of their own type become `_XdrPointer`. Pragmas mutate global code-generation controls. RPC productions collect procedures into versions/programs.

State and persistence behavior: Semantic state is process-global and persists across parses in one Python interpreter. No files are written.

Dependencies and integration points: Used by all subcommands and generators. Depends on Lark `ast_utils`, dataclasses, and the grammar's production names.

Risks: Global state is not reset per parse, which is risky for long-lived command drivers. Forward references depend on transformation order and `max_widths` entries. Some union width paths assume at least one arm initializes `width`. Unsupported optional typedefs and arm types surface later in generators.

Test signals: Transform specs with constants, arrays using symbolic constants, recursive optional structs, pragmas, pass-through merging, unions with defaults, RPC programs, undefined types, and repeated parses in one process.
