## sources/distributed-fs/ceph-client/tools/lib/perf/Documentation/Makefile

Purpose: Builds and installs libperf documentation, man pages, HTML pages, and example sources.

Important targets/variables: `MAN3_TXT`, `MAN7_TXT`, generated XML/HTML/man variables, `ASCIIDOC`, `XMLTO`, `install-man`, `install-html`, `install-examples`, `clean`, and pattern rules from `.txt` to `.xml`, `.3`, `.7`, and `.html`.

Control flow: `all` depends on man and HTML outputs. XML is generated with asciidoc using `asciidoc.conf`; man pages are generated with `xmlto` and selected XSL customizations. Install targets create destination directories under `DESTDIR`/`prefix` and copy artifacts.

State/persistence: Generated docs live under `$(OUTPUT)`. Install copies into man/doc/example directories.

Dependencies/integration: Includes tools make helpers and supports legacy asciidoc/docbook XSL conditionals such as `ASCIIDOC8`, `DOCBOOK_XSL_172`, and `ASCIIDOC_NO_ROFF`.

Risks: Toolchain-version compatibility is fragile. `EVENT_PARSE_VERSION` is referenced for document attributes and may need to be defined by the parent build. Output path handling depends on `OUTPUT` and DESTDIR quoting.

Test signals: Run `make -C tools/lib/perf/Documentation` with and without `OUTPUT`, install into a temporary `DESTDIR`, and test asciidoc/xmlto version conditionals.
