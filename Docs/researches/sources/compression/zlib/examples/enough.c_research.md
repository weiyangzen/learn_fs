# sources/compression/zlib/examples/enough.c

## Purpose
Command-line analysis tool that exhaustively determines the maximum number of inflate Huffman table entries required for all valid complete prefix codes under a symbol count, root table width, and maximum code length. Defaults model the deflate literal/length code (`286`, root `9`, max `15`); `enough 30 6` models deflate distance codes.

## APIs, Types, And Functions
The program is standalone C using standard I/O and allocation. Core types are `big_t` for code counts, `code_t` for bit-pattern counts, `struct tab` for visited-state bit vectors, and `string_t` for accumulating printed maximum cases. Global `g` holds max/root/large/total, arrays for current code counts, memoized `num` counts, visited `done` states, and output text. Main helpers are `map()`, `cleanup()`, `count()`, `been_here()`, `examine()`, `enough()`, and the small `string_*` allocation helpers.

## Control Flow
`main()` parses optional numeric arguments, clamps unconstrained max length to `syms - 1`, validates integer-capacity limits, allocates memo tables, counts valid prefix codes for all symbol counts from two through `syms`, allocates visited-state tables, and runs `enough()`. `count()` recursively enumerates possible distributions of code lengths with memoization. `enough()` starts examination from reachable `root + 1` states, and `examine()` recursively tracks table memory (`mem`) and remaining entries (`rem`) to find and print all sub-codes that reach a new maximum.

## State And Persistence
All state is process-local heap memory referenced from the global `g`. `cleanup()` frees variable-size bit vectors, memo arrays, current code vectors, and output strings before exit. The tool persists no files and only writes human-readable counts and maximum cases to stdout; invalid arguments or impossible code spaces write diagnostics to stderr.

## Dependencies And Integration
Uses only libc headers and `assert()`. Its integration point with zlib is conceptual: it validates the table-size constants used by inflate's Huffman decode table builder, rather than linking against zlib. Results are used as engineering evidence for safe static table limits in the inflater.

## Risks And Test Signals
The main risks are combinatorial blow-up, unsigned overflow, and incorrect pruning. The code intentionally aborts on arithmetic or allocation failure via assertions and explicit checks. Test signals include running defaults, running `30 6`, comparing printed maxima to documented inflate table limits, testing boundary arguments (`2`, root greater than max, impossible symbol/max pairs), and compiling with sanitizers to catch `va_list`, allocation, and shift-bound issues.
