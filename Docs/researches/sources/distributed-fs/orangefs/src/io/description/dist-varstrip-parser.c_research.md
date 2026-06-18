# sources/distributed-fs/orangefs/src/io/description/dist-varstrip-parser.c

## Purpose
Parses variable-stripe distribution parameter strings into an ordered array of strip descriptors.

## Important APIs, Types, And Functions
Exports `PINT_dist_strips_parse` and `PINT_dist_strips_free_mem`. Private helpers are `strips_parse_elem` and `strips_alloc_mem`.

## Control Flow
The parser copies the input into a bounded local buffer, allocates one descriptor per colon in the string, then repeatedly parses `<server>:<size>[K|M|G]` elements using `strtok_r`. Each strip offset is the previous offset plus previous size. Size suffixes scale by powers of 1024. Parsing stops when no next server token exists and returns the count.

## State And Persistence
Allocates an array that callers must release with `PINT_dist_strips_free_mem`. No global state or persistence exists.

## Dependencies And Integration Points
Used by `dist-varstrip.c` to interpret `PVFS_varstrip_params.strips`. Depends on PVFS size/offset types and varstrip max string length.

## Risks And Test Signals
Risks include `atoi/atoll` accepting malformed prefixes, no overflow checks for suffix multiplication, repeated `strlen` scans, and comment typo around counting separators. Tests should parse valid multi-strip strings, invalid/missing/too-long inputs, zero/negative sizes, suffixes, malformed tokens, and free behavior.
