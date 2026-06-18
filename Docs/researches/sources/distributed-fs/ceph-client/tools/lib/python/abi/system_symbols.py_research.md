<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/abi/system_symbols.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/abi/system_symbols.py

## Purpose
`SystemSymbols` scans a live or alternate sysfs tree, builds a path/alias graph, and compares discovered nodes against ABI documentation regexes to report undocumented system symbols.

## Important APIs, Types, and Functions
- `graph_add_file(path, link=None)` inserts real paths and optional symlink aliases into a nested graph.
- `print_graph` emits a bounded tree visualization.
- `_walk(root)` recursively scans files, directories, and symlinks while applying ignore rules.
- `__init__(abi, sysfs="/sys", hints=False)` stores parser references, ignore regexes, graph state, aliases, and discovered files, then walks sysfs.
- `check_file(refs, found)` checks a chunk of sysfs names against candidate ABI regexes.
- `_ref_interactor` traverses graph leaf references and honors optional ABI search filtering.
- `get_fileref` chunks references.
- `check_undefined_symbols(max_workers=None, chunk_size=50, found=None, dry_run=None)` parses ABI regexes, optionally prints graph/dry-run data, dispatches chunk checks through process or thread executors, prints progress, and reports missing symbols.

## Control Flow and State
Initialization is eager: scanning happens in `__init__`. The graph stores `__name` arrays at leaves, with the first entry as canonical path and later entries as symlink aliases. Undefined checks parse ABI data, collect refs, choose process workers unless limited to one, shuffle work for load balance, poll futures with progress output, and accumulate `not_found`.

## Dependencies and Integration Points
It depends on `AbiRegex`-style parser methods (`parse_abi`, `get_regexes`, `re_string`, debug flags), filesystem APIs, `concurrent.futures`, datetime, random shuffle, and stderr/stdout output. It intentionally skips debugfs, tracing, pstore, bpf, cgroup, firmware, modules, and parameter paths.

## Risks and Test Signals
Scanning `/sys` can be expensive and host-specific. `_walk` uses `return` when an ignored path matches, which stops the current directory traversal branch immediately. Multiprocessing serializes parser state and chunks, so memory/performance can regress with large ABI sets. Tests should use a small fixture sysfs tree with files, symlinks, ignored paths, aliases, filtering, dry-run, and hint output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/abi/system_symbols.py -->
