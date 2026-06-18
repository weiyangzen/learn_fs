# sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/lib/doc_generator.py

Purpose: Converts Linux netlink YAML specs into generated RST documentation with line-number comments, references, operation sections, definition sections, attribute set sections, multicast groups, and sub-message descriptions.

Important APIs and state: `NumberedSafeLoader` extends PyYAML safe loading by adding `__lineno__` to mappings. `RstFormatters` provides formatting helpers for fields, definitions, bullets, sections, labels, refs, titles, and line-number comments. `YnlDocGenerator` exposes `parse_yaml_file()` and parsing helpers for multicast groups, do/dump blocks, operation attributes, operations, definitions, attribute sets, sub-messages, and whole YAML documents.

Control flow: `parse_yaml_file()` loads YAML with line numbers, then `parse_yaml()` emits a document header, label, title, contents directive, optional summary, operations, multicast groups, definitions, attribute sets, and sub-messages. Nested helpers skip preprocessed/internal keys and convert recognized references to RST `:ref:` links.

Dependencies and integration: Depends on PyYAML and the netlink spec schema conventions. It is likely invoked by `ynl_gen_rst.py` and the generated Makefile's `%.rst` rule.

State and persistence: No persistent state. Output is a generated RST string; writing is handled by callers.

Risks: Formatting assumes many YAML keys exist, such as operation docs and attribute list names. `rst_ref()` uses fixed prefix mappings, so new spec sections need updates for correct cross-linking. The line-number loader mutates every mapping with `__lineno__`, requiring all parsers to skip that key consistently.

Test signals: Generate RST for specs with operations, do/dump replies, events, multicast groups, enums, structs, nested attribute sets, sub-messages, missing optional docs, multi-line docs, and check Sphinx reference validity.
