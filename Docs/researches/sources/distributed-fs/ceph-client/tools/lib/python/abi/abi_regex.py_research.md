<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/abi/abi_regex.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/abi/abi_regex.py

## Purpose
`AbiRegex` extends `AbiParser` by converting ABI `What:` sysfs paths into grouped regular expressions for fast matching against live system symbols.

## Important APIs, Types, and Functions
- `escape_symbols`, `leave_others`, and `re_whats` define the transformation pipeline from ABI wildcard syntax to Python regex syntax.
- `regex_append(what, new)` selects a search subgroup from path components and stores a compiled regex.
- `get_regexes(what)` returns candidate regexes for a live sysfs path by checking reversed path components plus the `others` bucket.
- `__init__` accepts optional `search_string`, validates it, and delegates parser initialization.
- `parse_abi` first parses ABI files, then builds `regex_group` from `/sys` `What:` entries and optionally emits debug/subgroup diagnostics.

## Control Flow and State
After base parsing, each ABI symbol is transformed through ordered regex substitutions. The transformed regex is stored in the symbol record and inserted into a subgroup chosen from the most specific usable path component. This reduces live symbol checking from a full scan to a smaller candidate set.

## Dependencies and Integration Points
It imports `AbiParser` and `AbiDebug`. `SystemSymbols` calls `get_regexes` while scanning sysfs. Debug flags from helpers control conversion and subgroup reporting.

## Risks and Test Signals
The substitution order is fragile: temporary marker bytes are used to protect dots, numeric ranges, and wildcard forms before final escaping. Incorrect transforms can overmatch, undermatch, or produce invalid regexes. Group selection skips common names like `devices` and `hwmon`, which improves performance but can affect candidate size. Tests should feed representative ABI wildcards, numeric ranges, alternatives, and invalid patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/abi/abi_regex.py -->
