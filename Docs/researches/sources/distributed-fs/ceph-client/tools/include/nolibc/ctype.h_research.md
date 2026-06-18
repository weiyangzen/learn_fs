# sources/distributed-fs/ceph-client/tools/include/nolibc/ctype.h

## Purpose
Provides minimal ASCII character classification for nolibc programs.

## APIs, Types, and Functions
Defines inline-style functions `isascii`, `isblank`, `iscntrl`, `isdigit`, `isgraph`, `islower`, `isprint`, `isspace`, `isupper`, `isxdigit`, `isalpha`, `isalnum`, and `ispunct`.

## Control Flow, State, and Persistence
Control flow is simple integer range and equality checks. There is no locale state, no tables, and no persistence; behavior is ASCII-only and deterministic.

## Dependencies and Integration
Depends only on the nolibc include umbrella. It integrates with parsers in `getopt`, `stdio` scanning, and `stdlib` numeric conversion that need libc-like classification without libc.

## Risks and Test Signals
Risks are callers expecting locale-aware classification or undefined behavior for negative `char` values to match glibc exactly. Test signals are exhaustive 0-127 classification checks, negative and >127 inputs, and parser tests that consume whitespace, digits, and hex prefixes.
