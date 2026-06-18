# sources/distributed-fs/openafs/src/WINNT/afsapplib/regexp.cpp

## Purpose
Implements a compact custom regular-expression matcher for TCHAR strings. It supports a small historical expression language: anchors, single-character wildcards, star repetition, character sets and negated sets, escaped capture groups, and numeric backreferences.

## Important APIs and Control Flow
`SetExpression` calls `Compile`, which translates source text into `m_achCompiled`. Marker bytes encode token type, repetition, parenthesis boundaries, references, end-of-line, and end-of-pattern. A leading `^` sets `m_fMatchFromStart`; a terminal `$` becomes `markENDLINE`; `.` and `?` become any-character tokens; `[...]` expands ranges into explicit character lists; `\(`, `\)`, and `\1` through `\9` become capture and reference tokens.

`Matches` initializes capture start/end arrays. Anchored expressions call `MatchSubset` once, character-led unanchored expressions scan for the first literal before trying subsets, and other unanchored expressions try every position. `MatchSubset` is a recursive backtracking interpreter. Starred tokens consume greedily, then backtrack by recursively testing the remainder. Capture tokens record string positions; references compare current text with the captured substring through `CompareParen`. `fIsRegExp` inspects compiled tokens and treats anything except a pure literal sequence as a regexp.

## State, Dependencies, and Integration
The object stores only the compiled buffer and anchor flag. Static helpers create temporary `REGEXP` instances. It depends on Win32 error codes (`ERROR_INVALID_PARAMETER`, `ERROR_BAD_FORMAT`, `ERROR_META_EXPANSION_TOO_LONG`) and TCHAR APIs. No external regex library is used, so callers get deterministic but limited syntax.

## Risks and Test Signals
The compiled buffer is fixed at 512 TCHARs and range expansion can overflow if size checks are off by one. Character-set length is stored in a character slot and iterated with byte casts, so non-ASCII or Unicode ranges are suspect. `CompareParen` assumes valid captured bounds and simple character equality. Recursive backtracking can be expensive on adversarial expressions. Tests should cover invalid empty expressions, unmatched parentheses and brackets, literal `*` handling, anchors, terminal `$`, positive and negative sets, expanded ranges, repeated backreferences, Unicode builds, and maximum-length compiled expressions.
