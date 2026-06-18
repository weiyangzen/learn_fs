# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/passthru.py

Purpose: Emits pass-through content from XDR specifications into generated headers or source files.

Important APIs and functions: `XdrPassthruGenerator.emit_definition` renders a header definition template, while `emit_decoder` renders a source template. Both pass `node.content` verbatim through the relevant template.

Control flow: Construction creates a C `passthru` environment. Source subcommands use `emit_decoder` for pass-through blocks because pass-through content is inserted before generated decode/encode functions.

State and persistence behavior: Stateless stdout output.

Dependencies and integration points: `_XdrPassthru` nodes are produced by `xdr_ast` from grammar pass-through lines and consecutive pass-through nodes are merged before generation.

Risks: Pass-through content is intentionally raw; invalid C or unsafe declarations are not validated by the generator.

Test signals: Parse adjacent pass-through lines and verify they are merged and emitted with newlines preserved in definitions and source output.
