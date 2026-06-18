## sources/distributed-fs/ceph-client/tools/lib/perf/Documentation/asciidoc.conf

Purpose: Customizes asciidoc conversion for libperf documentation.

Important sections: Defines `linktep` inline macro, special character attributes, docbook link rendering, listing/verse block workarounds for roff/docbook XSL behavior, manpage header template, and XHTML link rendering.

Control flow: Asciidoc conditionals select docbook vs XHTML output and compatibility behavior based on attributes like `tep-asciidoc-no-roff` and `doctype-manpage`.

State/persistence: No runtime state; affects generated documentation output.

Dependencies/integration: Consumed by `Documentation/Makefile` through `ASCIIDOC_EXTRA`. Integrates with docbook manpage generation and libperf manual metadata.

Risks: The macro name/comments mention TEP in a libperf file, suggesting copied configuration and possible stale naming. The header enumerates many `mannameN` fields and depends on asciidoc filling them correctly. Incorrect conditionals can produce malformed man XML.

Test signals: Generate docbook and XHTML outputs, validate manpage headers, link macro rendering, listing blocks, and no-roff variants across supported asciidoc/docbook versions.
