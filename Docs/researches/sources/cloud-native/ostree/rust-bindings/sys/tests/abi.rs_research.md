# sources/cloud-native/ostree/rust-bindings/sys/tests/abi.rs

Purpose: This generated Unix-only Rust test validates the `ostree_sys` raw ABI against the installed C libostree headers by comparing exported constant values and type layouts with small compiled C programs.

Important APIs, types, and functions: `Compiler` builds commands from `CC`, `CFLAGS`, `CPPFLAGS`, and `pkg-config --cflags ostree-1`, always adding `-Wno-deprecated-declarations`, `-std=c11`, and a MinGW printf define. `cross_validate_constants_with_c` compares `RUST_CONSTANTS` to output from `tests/constant.c`. `cross_validate_layout_with_c` compares `RUST_LAYOUTS` to output from `tests/layout.c`. `get_c_output` compiles the C fixture into a temporary executable and captures stdout. `Results` accumulates pass/fail counts and panics if any mismatch occurs.

Control flow: Each test runs the corresponding C fixture, parses semicolon-separated lines, zips C rows with the Rust manifest arrays in order, checks names first, then values or layouts, and records detailed stderr diagnostics before the final summary assertion. The compiler setup fails early if environment variables cannot be shell-split or pkg-config cannot locate `ostree-1`.

State and persistence behavior: State is limited to temporary directories from `tempfile::Builder`, process environment variables, and child compiler/executable processes. No repository state is modified. The test does depend on the system-installed libostree development files visible to pkg-config.

Dependencies and integration points: Depends on `ostree_sys::*`, Rust `std::process::Command`, `shell_words`, `tempfile`, C compiler tooling, pkg-config, `tests/constant.c`, `tests/layout.c`, and `tests/manual.h`. It is the bridge between generated Rust declarations and the authoritative C headers.

Risks: The test assumes identical ordering between `RUST_CONSTANTS`/`RUST_LAYOUTS` and C fixture output; a missing row can cascade into many name mismatches. It only checks selected constants and selected layouts, not every function signature or ownership rule. Local compiler/pkg-config differences can make failures environmental rather than source regressions.

Test signals: This file is itself the ABI test signal. Passing output means selected constants, struct sizes, and alignments match the installed libostree headers for the active feature set and target.
