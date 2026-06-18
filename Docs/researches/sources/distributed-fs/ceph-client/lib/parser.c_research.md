# sources/distributed-fs/ceph-client/lib/parser.c

## Purpose
Implements simple token, number, substring, and wildcard parsing helpers historically used by mount option and kernel option parsers.

## APIs, Control Flow, and State
Exports `match_token()`, `match_int()`, `match_uint()`, `match_u64()`, `match_octal()`, `match_hex()`, `match_wildcard()`, `match_strlcpy()`, and `match_strdup()`. `match_token()` scans a null-terminated pattern table and uses `match_one()` to match literal text plus `%s`, `%d`, `%u`, `%o`, `%x`, fixed-length numeric/string modifiers, and escaped `%%`, filling `substring_t` arguments. Number helpers copy bounded substrings into a 24-byte stack buffer and convert with `simple_strtol()` or `kstrto*()`. `match_wildcard()` implements iterative `*` and `?` matching with backtracking to the last star. State is stack-local except for caller-provided substring output.

## Dependencies, Integration, Risks, and Tests
Depends on ctype, kstrtox, slab, string helpers, and `linux/parser.h`. Risks include simplistic grammar, table termination requirements, overflow/truncation of long numeric substrings, wildcard worst-case backtracking, and callers assuming stronger validation than provided. Test signals include mount option parser tests, numeric boundary tests, wildcard matching matrices, malformed `%` pattern coverage, and `match_strdup()` allocation failure handling.
