# sources/distributed-fs/ceph-client/tools/perf/util/demangle-java.c

## Purpose

`demangle-java.c` demangles OpenJDK-style Java method descriptors into human-readable return type, class, method, and argument strings for perf symbol display.

## Important APIs, Types, and Functions

The exported API is `java_demangle_sym(const char *str, int flags)`. The internal parser `__demangle_java_sym()` walks descriptor text in modes `MODE_PREFIX`, `MODE_CLASS`, `MODE_FUNC`, `MODE_TYPE`, and `MODE_CTYPE`. `base_types` maps Java descriptor letters to type names. `JAVA_DEMANGLE_NORET` suppresses return-type output.

## Control Flow

`java_demangle_sym()` finds the closing `)` separating arguments from return type, allocates a buffer with an estimated expansion factor, optionally demangles the return type first, then demangles the class/function/argument prefix. The parser handles object descriptors starting with `L`, package separators `/`, arrays `[`, primitive descriptors, void, argument delimiters, and class terminators `;`.

## State and Persistence Behavior

No persistent state exists. The demangled string is heap allocated and owned by the caller. Parser state is local: output length, array depth, argument count, and mode.

## Dependencies and Integration Points

It depends on perf string formatting (`scnprintf`), Linux ctype/kernel helpers, and `demangle-java.h`. It integrates with symbol display paths for Java/JIT symbol names.

## Risks and Edge Cases

Malformed descriptors return `NULL`. The parser is intentionally OpenJDK-focused and not GCJ-compatible. Buffer truncation can stop output early if the expansion estimate is insufficient. Array state must be reset after each type. Object class parsing depends on descriptor grammar and can reject unusual or partial names.

## Test Signals

Tests should cover primitive returns, object returns, void, arrays of primitives and objects, multiple arguments, nested package names, `JAVA_DEMANGLE_NORET`, malformed missing parentheses, bad array placement, truncated/partial descriptors, and null input.
