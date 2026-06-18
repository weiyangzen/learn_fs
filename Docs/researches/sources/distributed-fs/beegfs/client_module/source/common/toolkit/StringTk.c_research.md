# sources/distributed-fs/beegfs/client_module/source/common/toolkit/StringTk.c

## Purpose
Implements kernel-safe string utilities for splitting, boolean parsing, trimming, and formatted allocation.

## Important APIs and control flow
`StringTk_explode` splits a delimiter-separated string into a `StrCpyList`, skipping empty elements. It creates temporary substrings with `StringTk_subStr`, appends copies to the output, and frees temporaries. `StringTk_strToBool` treats empty strings and common truthy strings as `true`, and everything else as `false`. `StringTk_trimCopy` trims spaces, newlines, carriage returns, and tabs into a newly allocated string. `StringTk_kasprintf` emulates `kasprintf` by first measuring with `vsnprintf`, allocating, then formatting.

## State, dependencies, integration
No persistent state is kept. It depends on BeeGFS allocation wrappers and `StrCpyList`. Metadata, filters, and component queues use these helpers for copied IDs and configuration strings.

## Risks and test signals
`StringTk_strToBool` returning true for empty strings is intentional but easy to misuse for explicit false parsing. Allocation failures are not consistently checked by callers. Test delimiter edge cases, all-whitespace trim, truthy/falsy config values, and long format strings.
