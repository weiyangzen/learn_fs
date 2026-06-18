# sources/distributed-fs/beegfs/client_module/source/common/toolkit/StringTk.h

## Purpose
Declares and implements inline string conversion, duplication, substring, and numeric helpers for the client module.

## Important APIs and types
Exports `StringTk_explode`, `StringTk_strToBool`, `StringTk_trimCopy`, and `StringTk_kasprintf`. Inline helpers include `StringTk_hasLength`, `StringTk_strncpyTerminated` via `strscpy`, numeric conversions using `simple_strto*`, `StringTk_strDup`, `StringTk_subStr`, `StringTk_intToStr`, and `StringTk_uintToStr`.

## State, dependencies, integration
The header depends on BeeGFS common allocation wrappers and `StrCpyList`. Returned strings from duplicate/substr/format helpers are heap-owned by callers.

## Risks and test signals
`StringTk_subStr` does not check allocation before writing the terminator. Numeric conversions ignore parse errors and trailing data. Tests should cover allocation failure paths where practical, non-numeric strings, zero-length substrings, and safe truncation behavior.
