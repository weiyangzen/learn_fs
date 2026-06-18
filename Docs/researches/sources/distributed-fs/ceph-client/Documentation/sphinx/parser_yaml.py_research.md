<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/sphinx/parser_yaml.py -->
# sources/distributed-fs/ceph-client/Documentation/sphinx/parser_yaml.py

## Purpose
Sphinx source parser for selected YAML files in the kernel tree. Its current concrete use is rendering netlink YAML specs under `netlink/specs` into ReST using the YNL documentation generator.

## Important APIs, Types, And Functions
- `YamlParser` subclasses `sphinx.parsers.Parser` and declares `supported = ('yaml',)`.
- `netlink_parser` is an instance of `YnlDocGenerator`.
- `rst_parse()` parses generated ReST into the current docutils document and honors `.. LINENO` source markers.
- `parse()` dispatches by `document.current_source`; only paths containing `/netlink/specs/` are handled.
- `setup()` registers `.yaml` as a Sphinx source suffix handled by this parser.

## Control Flow
Sphinx passes YAML source text to `parse()`. If the file path matches netlink specs, `YnlDocGenerator.parse_yaml_file()` produces ReST. `rst_parse()` builds a docutils `ViewList`, adjusts line offsets from `.. LINENO` markers, and runs an `RSTStateMachine` against the current document. Non-netlink YAML files are intentionally ignored.

## State And Persistence
No files are written. The parser keeps a class-level generator instance and a compiled line-number regex. It mutates `sys.path` based on the `srctree` environment variable to import YNL generator code.

## Dependencies And Integration Points
Integrates Sphinx source suffix handling with `tools/net/ynl/pyynl/lib/doc_generator.py`. It depends on docutils parser internals and on the kernel documentation build environment supplying `srctree`.

## Risks And Edge Cases
Any YAML outside `/netlink/specs/` yields an empty document without warning. Import failure or missing `srctree` breaks parser loading. Error handling reports generated-ReST parse failures but does not fail hard, so some malformed YAML conversions may become documentation warnings rather than build-stopping errors.

## Test Signals
Build docs containing netlink specs and check generated sections, source-line attribution, and absence of output for unrelated YAML. A useful regression test is a YAML spec with deliberate malformed generated ReST to confirm `document.reporter.error()` attribution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/sphinx/parser_yaml.py -->
