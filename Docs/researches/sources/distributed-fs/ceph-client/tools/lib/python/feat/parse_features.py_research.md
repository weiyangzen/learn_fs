<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/feat/parse_features.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/feat/parse_features.py

## Purpose
`ParseFeature` parses Linux `Documentation/features/**/arch-support.txt` files and generates ReST feature matrices, per-architecture summaries, per-feature summaries, or plain list output.

## Important APIs, Types, and Functions
- Header constants define table labels such as `Feature`, `Kconfig`, `Description`, `Subsystem`, `Status`, and `Architecture`.
- `status_map` orders `ok`, `TODO`, `N/A`, and other statuses.
- `__init__` initializes output width tracking, parse data, debug flags, and message buffer.
- `emit` appends to the output buffer.
- `parse_error` prints warning messages with file/line context.
- `parse_feat_file(fname)` parses one `arch-support.txt`, extracting feature metadata and architecture status rows.
- `parse()` recursively finds feature files under a prefix and populates `data`.
- `output_arch_table`, `output_feature`, `output_matrix`, and `list_arch_features` render different views.
- `matrix_lines` helps render grid-style ReST tables.

## Control Flow and State
Parsing iterates all files under the prefix, ignores anything not named `arch-support.txt`, derives subsystem from the parent directory, updates maximum column widths, and stores records keyed by feature name. Rendering functions reuse `self.msg`; callers should use fresh instances or manage accumulated output carefully.

## Dependencies and Integration Points
It depends on `os`, `re`, `sys`, and recursive `glob.iglob`. Kernel documentation build scripts can use it to turn feature support text files into generated ReST.

## Risks and Test Signals
The parser is strict about expected comment headers and table row syntax. It normalizes `..` status to `---` to avoid special ReST cell meaning. `re.search(r"^\\s*$", line)` appears to match a literal backslash-s rather than whitespace, so blank-line handling mostly relies on other paths. Tests should cover valid files, missing headers, status sorting, long descriptions, list/matrix rendering, and filename-emission mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/feat/parse_features.py -->
