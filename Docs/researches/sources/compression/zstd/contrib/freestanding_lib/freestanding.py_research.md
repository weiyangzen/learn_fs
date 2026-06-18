# sources/compression/zstd/contrib/freestanding_lib/freestanding.py

Purpose: generator that copies and rewrites zstd library sources into a freestanding/embedded-friendly output tree, especially for the Linux kernel import path.

Important APIs and control flow: constants choose included subdirs, skipped threading/pool/dependency files, and optional xxhash omission. `FileLines` reads/writes files. `PartialPreprocessor` repeatedly simplifies simple `#if/#ifdef/#ifndef/#elif defined(...)` blocks using supplied defines, replaces, and undefs, with partial handling for `&&`/`||` and integer comparisons. `Freestanding.go()` copies selected source files, substitutes `zstd_deps.h` and `mem.h`, hardwires macros, removes marked excluded sections, rewrites includes, optionally renames external `XXH64` symbols/types, applies Python-regex sed replacements, and inserts SPDX identifiers. CLI parsing supports `-D`, `-U`, `-R`, `-E`, `--rewrite-include`, `--xxhash`, `--xxh64-state`, `--xxh64-prefix`, `--sed`, and `--spdx`; it always undefines multithreading and disables tracing by default.

State, dependencies, and integration: persistent state is the generated output directory. It depends on Python stdlib, source zstd layout, replacement dependency headers, and predictable preprocessor patterns. Linux-kernel `Makefile` is a major consumer.

Risks and test signals: the partial preprocessor is intentionally incomplete and can mis-handle complex/multiline preprocessor logic. Regex include/sed rewrites are powerful but fragile. Kernel import tests and generated library builds are the main validation signals.
