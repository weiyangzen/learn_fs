# sources/distributed-fs/openafs/src/WINNT/afsd/test/stricmptest.c

## Purpose
Diagnostic test program for UTF-8 case-insensitive comparison, UTF-8 character navigation, and uppercase conversion helpers.

## Important APIs, Types, And Functions
Exercises `cm_stricmp_utf8`, `char_next_utf8`, `char_prev_utf8`, and `strupr_utf8`. Fixture arrays include ASCII and non-ASCII pairs with expected comparison results.

## Control Flow
`wmain` prints comparisons using `strcmp`, CRT `stricmp`, and `cm_stricmp_utf8`; walks a mixed ASCII/non-ASCII UTF-8 string forward and backward printing offsets; then uppercases fixture strings in fixed buffers.

## State And Persistence
No persistent state. Work is limited to local buffers and string literals.

## Dependencies And Integration Points
Includes Windows headers, `strsafe.h`, and `cm_nls.h`. These helpers support Windows afsd filename comparison, normalization, and directory search.

## Risks
The program is observational and does not fail on mismatches. Fixed `MAX_PATH` buffers do not test long strings. Invalid UTF-8 is not covered.

## Test Signals
Automation should assert expected comparison values, navigation counts/offsets, and uppercase outputs. Current signal is manual inspection of printed output.
