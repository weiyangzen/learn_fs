# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/json-bignum.js

## Purpose
This file provides `window.JSONParseBigNum`, a JSON parser based on Douglas Crockford's recursive-descent reference parser with Hadoop-specific handling for large numeric values. Its main purpose in the HDFS web UI is to parse WebHDFS JSON responses without losing precision for block IDs, generation stamps, file lengths, or other integer-like values that may exceed JavaScript's safe integer range.

## Important APIs, Types, and Functions
- `BigNumber(number)` is a small wrapper type that stores the original numeric token as `numberStr`. Its constructor validates the token with `parseFloat`/`isFinite`, and `toString()` returns the preserved string.
- `exports.JSONParseBigNum` is exported from an IIFE invoked with `window`, so the public API is a global browser function.
- Parser state variables are closure-scoped: `text` holds the source string, `at` is the current index, and `ch` is the current character.
- `error(m)` throws an object with `name: 'SyntaxError'`, `message`, `at`, and `text`.
- `next(c)`, `white()`, `word()`, `string()`, `number()`, `array()`, `object()`, and `value()` implement recursive-descent JSON parsing.
- The returned parse function accepts `(source, reviver)` and mirrors `JSON.parse` reviver traversal semantics, including deletion when the reviver returns `undefined`.

## Control Flow
Parsing starts by assigning the source to the closure state, setting `at = 0`, priming `ch = ' '`, and calling `value()`. `value()` skips whitespace and dispatches by the current character to object, array, string, number, or literal parsing. Objects reject duplicate keys with an explicit `Duplicate key` syntax error. Arrays and objects recursively call `value()` until their closing delimiter is reached.

The key Hadoop-specific path is `number()`. It builds the number token as a string, converts it with unary `+`, rejects non-finite results, then compares `number.toString()` with the original token. If JavaScript changed the textual representation, the parser attempts to return `new BigNumber(string)` instead of the rounded numeric value. If the wrapper cannot be constructed, it falls back to the normal numeric value.

After parsing, the function skips trailing whitespace and rejects any remaining characters. If a reviver is provided, it walks the resulting object graph depth-first using a temporary root holder and calls the reviver for every key/value pair.

## State and Persistence Behavior
All parser state is transient and closure-local to the parse invocation, but the variables are shared by the exported parser closure. Calls are synchronous and not reentrant; a reviver that calls `JSONParseBigNum` recursively would overwrite the shared parser state. Parsed results are normal JavaScript arrays/objects/numbers/strings/booleans/null plus `BigNumber` wrapper instances for precision-sensitive numeric tokens.

The file does not persist data, does not touch browser storage, and does not make network requests.

## Dependencies and Integration Points
The file depends only on standard browser JavaScript and `window`. It is loaded by `hdfs/explorer.html` before `rest-csrf.js`, `moment.min.js`, `dfs-dust.js`, and `explorer.js`.

The observed consumer is `hdfs/explorer.js`, which calls `JSONParseBigNum(data_text)` for a `/webhdfs/v1... ?op=GET_BLOCK_LOCATIONS` AJAX response declared as `dataType: 'text'`. That flow then passes the parsed `LocatedBlocks` data into Dust templates and UI controls. The custom parser prevents precision loss before block metadata is displayed or selected.

## Risks and Edge Cases
- The big-number detection compares `number.toString()` with the source token. Numerically equivalent alternate spellings such as exponent notation, leading zeros rejected/accepted by parser behavior, or decimal formatting can influence whether a value is wrapped.
- `BigNumber` is local to the closure and not exported directly. Consumers can stringify wrapper values, but cannot use `instanceof BigNumber` outside the closure.
- The parser uses a plain object for JSON objects. It rejects duplicate keys, which is stricter than some parsers and could reject inputs accepted by native `JSON.parse`.
- The parser does not use native `JSON.parse`, so it has its own syntax, performance, and maintenance risks. Large WebHDFS responses can parse more slowly than native JSON.
- Shared closure state means recursive use through a reviver is unsafe.
- Error throws are plain objects rather than `SyntaxError` instances, so consumers expecting `err instanceof SyntaxError` would not match.

## Test Signals
No direct tests for this file were found in the listed set. Useful regression tests would parse large block IDs above JavaScript's safe integer range, ordinary integers, decimals, exponent notation, duplicate keys, invalid strings, arrays/objects with whitespace, and reviver transformations. Browser-level testing should verify that the file explorer block-location modal displays large numeric identifiers without rounding.
