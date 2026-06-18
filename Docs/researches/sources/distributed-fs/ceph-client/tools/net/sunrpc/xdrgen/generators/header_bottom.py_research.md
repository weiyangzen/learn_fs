# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/header_bottom.py

Purpose: Emits closing boilerplate for generated XDR declaration and definition headers.

Important APIs and functions: `XdrHeaderBottomGenerator.emit_declaration` and `.emit_definition` render bottom header templates with the header guard infix derived from the source filename. `.emit_source` is intentionally a no-op.

Control flow: Construction creates a C `header_bottom` template environment. Each header method loads the proper template subdirectory and prints rendered guard closure.

State and persistence behavior: Stateless stdout generation.

Dependencies and integration points: Used at the end of `subcmds/declarations.py` and `subcmds/definitions.py` after type-specific emission.

Risks: Header guard infix is based on filename stem only, so two specs with the same stem in different directories could collide in generated headers.

Test signals: Generate declaration and definition headers for sample filenames and verify guard closure matches the top generator.
