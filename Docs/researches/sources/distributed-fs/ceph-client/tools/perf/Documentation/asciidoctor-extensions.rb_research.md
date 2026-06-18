# sources/distributed-fs/ceph-client/tools/perf/Documentation/asciidoctor-extensions.rb

Purpose: Supports building perf manual pages and HTML documentation from asciidoc/asciidoctor sources.

Important APIs/types/functions: the file-local declarations and build entries.

Control flow: The Makefile selects asciidoc/asciidoctor/xmlto/docbook pipelines, while config/extension files translate perf link macros and manpage references.

State and persistence behavior: Persists generated docs only through make targets; configs are declarative.

Dependencies and integration points: Depends on make, asciidoc or asciidoctor, ruby extensions, xmlto/docbook toolchain, and perf documentation sources.

Risks: Toolchain version differences can break manpage links, macro expansion, or generated filenames.

Test signals: Build man/html targets with asciidoc and asciidoctor paths and inspect cross-reference output.

Source coverage: researched from the complete local file (30 lines, 816 bytes).
