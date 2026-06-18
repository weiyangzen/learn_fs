# sources/compression/zstd/tests/regression/levels.h

Purpose: This macro include file centralizes the compression levels used by the regression matrix. It is included by `config.c` with `FAST_LEVEL`, `LEVEL`, and `ROW_LEVEL` defined to generate both objects and the config pointer list.

Important APIs and macros: The file requires callers to define `LEVEL(x)`, `FAST_LEVEL(x)`, and `ROW_LEVEL(x, y)`. It lists fast levels 5, 3, and 1; normal levels including 0, 1, 3 through 7, 9, 13, 16, and 19; and row-match variants at selected levels with `y` values representing force enabled and disabled.

Control flow: There is no runtime flow. The compile-time flow is macro expansion: each entry expands according to the including context. The comments explain that selected levels aim to trigger every strategy across source sizes, fast levels, default level, and row hash entries of different widths.

State and persistence: None. This is a generated-code driver for static configuration.

Dependencies and integration points: It is tightly coupled to `config.c` and must be included only after the three macros are defined. It assumes zstd's level-to-strategy mapping and row hash behavior, so it should be updated when compression strategy thresholds change.

Risks and test signals: Because it is macro-only, compile errors can be cryptic if a required macro is missing or has a mismatched expansion. Level selection can become stale as zstd internals evolve, reducing regression coverage without obvious build failures. Useful signals are the number and names of generated config rows in the regression output.
