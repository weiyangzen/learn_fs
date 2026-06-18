# sources/distributed-fs/openafs/src/WINNT/afsapplib/regexp.h

## Purpose
Declares the `REGEXP` class and documents its simplified pattern language. The API is intentionally small: compile an expression into an object, match strings repeatedly, or use static one-shot helpers.

## Important APIs and Types
`cchCOMPILED_BUFFER_MAX` fixes the internal compiled pattern size at 512 TCHARs. `nCOMPILED_PARENS_MAX` limits backreference-capable capture groups to nine. Public methods are the default and expression constructors, destructor, `SetExpression`, instance/static `Matches`, and instance/static `fIsRegExp`.

Private helpers expose the implementation shape: `Compile` produces the internal marker stream, `MatchSubset` interprets it against a candidate string, `CompareParen` implements backreferences, and `fIsInCharSet` handles inclusive and exclusive sets. State is `m_fMatchFromStart` plus `m_achCompiled`.

## State, Dependencies, and Integration
The class is exported through the same `EXPORTED` convention as the rest of afsapplib and depends on Win32/TCHAR types. It is not a POSIX or PCRE-compatible interface; consumers must use the documented subset (`^`, `$`, `.`, `?`, `*`, `[]`, `[^]`, escaped groups and numeric references). Objects are reusable via `SetExpression`.

## Risks and Test Signals
Because the header exposes no error retrieval, callers must inspect the Boolean return from `SetExpression` and use `GetLastError` if they need details. The static `Matches` helper does not surface compile failure separately from no-match. Test signals should include API-level tests for expression reuse, no-expression defaults, static helper behavior, and `fIsRegExp` distinguishing literal strings from true patterns.
