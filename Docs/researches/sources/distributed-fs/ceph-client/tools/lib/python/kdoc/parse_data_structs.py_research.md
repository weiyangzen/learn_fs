# sources/distributed-fs/ceph-client/tools/lib/python/kdoc/parse_data_structs.py

Purpose: Parses C/uAPI headers and produces ReStructuredText with Sphinx cross-references for defines, ioctl macros, enum values, typedefs, enums, and structs, optionally applying exception rules.

Important APIs/types/functions: `ParseDataStructs` owns `symbols`, `namespace`, `ignore`, `replace`, and accumulated source text. `read_exceptions()` parses `ignore`, `replace`, and `namespace` rules. `parse_file()` reads the input, strips comments/continuations, stores symbol references through `store_type()`, and applies exceptions. `gen_output()` escapes source text and substitutes references. `gen_toc()` builds a categorized TOC. `write_output()` writes the final rst file.

Control flow: `parse_file()` stores each original line indented in `self.data`, folds backslash continuations and multi-line comments, then detects ioctl defines, generic defines, typedefs, enum starts/member values, and struct starts. `apply_exceptions()` removes ignored symbols and rewrites replacements to explicit Sphinx references. `gen_output()` escapes special ReST characters before replacing escaped symbol occurrences using delimiter-aware regexes.

State and persistence: All parse state is in memory until `write_output()` writes the ReST output. `self.symbols` maps each type category to `symbol -> (replacement, line)`. `self.data` contains the indented source body. Exception rules persist only on the parser instance.

Dependencies/integration: Uses only Python stdlib (`os`, `re`, `sys`) and emits Sphinx C-domain/ref markup consumed by kernel documentation builds. The exception file syntax is part of its integration contract with media/uAPI docs.

Risks: `apply_exceptions()` references `name` in error/warning messages but `name` is local to `read_exceptions()`, causing a `NameError` on invalid type or missing replacement target. C parsing is regex-based and will miss complex typedefs, declarations split in unexpected ways, or macros hiding types. `line.endswith(r"\\")` checks for two backslashes, which may not match intended single continuation handling. Replacement after global escaping can still create false positives/negatives around unusual delimiters.

Test signals: Use header fixtures with ioctl macros, guarded comments, multiline macros, enums with explicit assignments, typedefs, anonymous and named structs, namespaces, ignore/replace rules, invalid exception lines, and TOC generation.
