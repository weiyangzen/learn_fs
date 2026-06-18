# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/generators/header_top.py

Purpose: Emits opening boilerplate for generated XDR declaration and definition headers.

Important APIs and functions: `XdrHeaderTopGenerator.emit_declaration` and `.emit_definition` render header templates with guard infix, filename, and source file modification time. `.emit_source` is a no-op.

Control flow: Construction creates a C `header_top` template environment. Emission calls `os.path.getmtime(filename)`, formats it with `time.ctime`, and prints the rendered template.

State and persistence behavior: Reads source file metadata but writes only stdout.

Dependencies and integration points: Used before type-specific emission by declaration and definition subcommands.

Risks: Generated output is time-dependent because it embeds source mtime, which can reduce reproducibility. Guard infix uses only the filename stem.

Test signals: Generate headers for a fixture file with known mtime and verify guard names and comment metadata.
