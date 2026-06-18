<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/c_lex.py -->
# sources/distributed-fs/ceph-client/tools/lib/python/kdoc/c_lex.py

## Purpose
This module provides C tokenization and delimiter-aware matching/substitution helpers for the Python kernel-doc implementation. It supports macro transforms, visibility filtering, nested argument extraction, and replacements that are difficult with Python's regular expressions alone.

## Important APIs, Types, and Functions
- `tokenizer_set_log(logger, prefix="")` installs a prefixed logger adapter.
- `CToken` defines enum-like token kinds and stores token value, source position, and bracket/paren/brace nesting levels.
- `RE_SCANNER_LIST`, `fill_re_scanner`, `RE_CONT`, `RE_COMMENT_START`, and `RE_SCANNER` define tokenization regexes.
- `CTokenizer` converts source strings or token lists to token streams; `__str__` reconstructs visible code while honoring `/* private: */` and `/* public: */` comments.
- `CTokenArgs` parses replacement backrefs like `\0`, `\1`, and greedy `\4+`, extracts grouped macro arguments, and generates replacement tokens.
- `CMatch` finds balanced nested delimiter blocks after a name regex and supports `search` and `sub` operations over strings or tokenizers.

## Control Flow and State
Tokenization strips line continuations, emits tokens while tracking nesting levels, and logs mismatches. Reconstruction keeps a stack of visibility booleans by nesting depth. `CMatch` scans tokens until a target name is found, waits for the expected opening delimiter, then yields only balanced ranges; substitutions splice token slices and replacement tokens into a new tokenizer.

## Dependencies and Integration Points
It depends on logging, regex, copy, and `KernRe`. It is consumed by kdoc parser/transform modules that need to normalize complex C declarations and macros before documentation extraction.

## Risks and Test Signals
Regex tokenization is intentionally approximate and can mis-handle unusual C extensions. Visibility filtering depends on comment text and nesting. `CTokenArgs.groups` references `sub_str` in one error path where only `self.sub_str` is in scope, which could mask an intended diagnostic. Tests should cover strings/chars/comments, nested macro arguments, greedy replacements, private/public sections, unmatched delimiters, and token-level substitution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/python/kdoc/c_lex.py -->
