<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/abi/abi_parser.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/abi/abi_parser.py

## Purpose
`AbiParser` parses Linux `Documentation/ABI` files into structured symbol/file records and can emit text or ReST documentation, cross-reference ABI paths, check duplicates, and search symbols.

## Important APIs, Types, and Functions
- Class constants `TAGS` and `XREF` define valid ABI tags and path-like references.
- `__init__` prepares regexes, logger, output options, and mutable indexes: `data`, `what_symbols`, `file_refs`, and `what_refs`.
- `warn` emits line-aware parser warnings.
- `add_symbol` tracks where each `What:` symbol is defined and optional xrefs.
- `_parse_line` is the main tag/state parser for `What`, `Date`, `KernelVersion`, `Contact`, `Description`, and `Users`.
- `parse_readme`, `parse_file`, `_parse_abi`, and `parse_abi` traverse files and populate the database.
- `desc_txt`, `desc_rst`, `xref`, and `doc` emit plain text or ReST with generated cross references.
- `check_issues` warns on duplicate ABI entries.
- `search_symbols` prints matching ABI symbols and metadata.

## Control Flow and State
Parsing is stateful per file through a `Namespace` object (`fdata`) tracking current tag, key, label, indentation, line number, file reference, and active `what` list. New `What:` tags create stable-ish keys from sanitized content; duplicate keys append deterministic pseudo-random letters after seeding with 42. Descriptions preserve indentation and are post-processed for ReST links.

## Dependencies and Integration Points
It depends on `abi.helpers.AbiDebug` and `ABI_DIR`, `argparse.Namespace`, logging, regex, filesystem traversal, and pprint/random helpers. `AbiRegex` subclasses it to add regex generation for sysfs symbol matching. Documentation scripts use `doc()` output.

## Risks and Test Signals
Parsing relies on permissive regular expressions and a mutable class-level `Namespace` pattern, so malformed ABI files can lead to warnings or surprising state carryover if fields are missed. Key generation for duplicates is deterministic only relative to current parsed data order. ReST enrichment must avoid code-block false positives. Tests should cover malformed tags, multi-`What` entries, README handling, duplicate symbols, xref generation, and search output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/abi/abi_parser.py -->
