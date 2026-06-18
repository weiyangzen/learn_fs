# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/subcmds/definitions.py

Purpose: Implements the XDR generator subcommand that emits definition headers containing constants, type definitions, RPC program numbers, pass-through blocks, and maxsize macros.

Important APIs and functions: `emit_header_definitions` dispatches concrete definitions for constants, enums, pointers, programs, typedefs, structs, unions, and pass-through nodes. `emit_header_maxsize` emits size macros for type/program nodes. `subcmd(args)` handles parsing and output orchestration.

Control flow: The subcommand sets annotation mode, parses and transforms the XDR file, emits top header boilerplate, emits definitions in source order, prints a blank line then maxsize macros, and emits bottom boilerplate. Parse and transform errors return 1 after formatted diagnostics.

State and persistence behavior: Reads the XDR source and prints generated header content to stdout. It updates parser/AST global side-channel state during parsing.

Dependencies and integration points: Complements `declarations.py`; both must agree on header guards and public API handling. Uses pass-through generator only in definition headers.

Risks: Maxsize emission order is a second pass and skips constants/pass-through. Process-global AST state can leak across multiple invocations. Template or unsupported AST failures propagate as exceptions.

Test signals: Generate a mixed spec with constants, typedefs, structs, unions, enums, programs, pragmas, and pass-through text; verify definitions and maxsize macros.
