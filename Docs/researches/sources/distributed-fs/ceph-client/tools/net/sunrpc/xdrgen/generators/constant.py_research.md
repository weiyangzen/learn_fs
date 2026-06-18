# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/constant.py

Purpose: Emits C header definitions for XDR constants.

Important APIs and functions: `XdrConstantGenerator` extends `SourceGenerator`. Its `emit_definition(node)` renders the `constants/definition.j2` template with `node.name` and `node.value`.

Control flow: Construction creates a C constants template environment and stores peer. Only definition emission is implemented; declarations, encoders, decoders, and maxsize are inherited unsupported operations.

State and persistence behavior: Stateless apart from the template environment. Output is printed to stdout.

Dependencies and integration points: Used by `subcmds/definitions.py` for `_XdrConstant` AST nodes. Relies on constants parsed and stored by `xdr_ast`.

Risks: No validation is performed at emit time; malformed values must be rejected by parsing/AST transformation. Peer is stored but unused.

Test signals: Parse a specification with `const FOO = 3;` and verify generated header definition matches the template.
