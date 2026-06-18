# sources/distributed-fs/coda/coda-src/asr/wildmat.c

Purpose: Shell-style wildcard matcher used by ASR object-name matching.

Important APIs/functions: Public `wildmat(char *text, char *p)` and internal recursive `DoMatch` and `Star`. Supports `?`, `*`, backslash literals, bracket classes, ranges, and `^` negation.

Control flow: `DoMatch` walks pattern and text, returning TRUE, FALSE, or ABORT. `*` delegates to `Star`, which retries the remaining pattern at successive text offsets until match or abort. Bracket classes scan until `]` and check ranges/literals.

State and persistence: Pure computation; no persistent or heap state.

Dependencies and integration: Called by `objname_t::match` in `ruletypes.cc`. Optional `TEST` main provides interactive matching.

Risks and test signals: The file itself notes malformed patterns may segfault. The optional test uses `gets` under `#ifdef TEST`, so it should not be enabled in production builds. Matching is byte-oriented and not locale/UTF aware.
