## sources/distributed-fs/openafs/src/rxgen/rpc_scan.c

### Purpose
`rpc_scan.c` is rxgen's lexical scanner. It converts the input stream into `token` values, handles comments, preprocessor line directives, rxgen `%` passthrough directives, and verbatim `@{ ... @}` blocks.

### Important APIs, Types, And Functions
Public scanner routines are `scan`, `scan2`, `scan3`, `scan4`, `scan_num`, `peek`, `peekscan`, `get_token`, `unget_token`, `findkind`, and `printdirective`. Static helpers parse string constants and numeric constants, detect `#line`/preprocessor directives, and update logical source file/line information.

### Control Flow
`get_token()` first returns a pushed token if present. Otherwise it reads lines into global `curline`, advances `linenum`, skips whitespace and C comments, copies `%` directives to output without the leading percent, adjusts `infilename`/line number for preprocessor directives, and recognizes punctuation, strings, decimal/hex constants, identifiers, and reserved words.

### State, Persistence, And Dependencies
Global scanner state is `pushed`, `lasttok`, `scan_print`, and the `curline`/`where`/`linenum`/`infilename` globals defined in `rpc_util.c`. String and identifier token values are heap-allocated through `alloc`. Output directives persist as generated text in `fout`.

### Integration Points
The parser consumes tokens through the `scan*` helpers and relies on `expected*` functions in `rpc_util.c` for diagnostics. The symbol table includes rxgen extensions such as `package`, `prefix`, `statindex`, `startingopcode`, `splitprefix`, `multi`, and `afsUUID`.

### Risks
Only one-token pushback is supported. Comments and verbatim blocks are tracked locally inside `get_token()`, so unterminated multi-line constructs can create confusing behavior. Token buffers and line buffers are fixed size; strings are scanned only to the next quote without escape processing. Numeric constants with a leading `-` are scanned, but later validation accepts only decimal digits in some contexts.

### Test Signals
Scanner tests should cover every reserved word, illegal characters, string and hex constants, comments across lines, `%` passthrough output, preprocessor file/line changes, one-token pushback, verbatim blocks, and expected-token diagnostics.
