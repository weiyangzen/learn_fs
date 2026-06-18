# sources/distributed-fs/ceph-client/tools/perf/tests/demangle-rust-v0-test.c

Purpose: `demangle-rust-v0-test.c` validates Rust v0 symbol demangling across functions, impls, traits, closures, const generics, arrays, and statics.

Important APIs and state: it calls `dso__demangle_sym(NULL, 0, mangled)` for a table of v0 mangled names and expected readable symbols. The suite is `"Demangle Rust"`.

Control flow: the test iterates all cases, requires a non-null demangled buffer, compares it with expected text, logs detailed mismatches, frees the buffer, and returns aggregate success/failure.

State and persistence: no persistent state; heap outputs are freed.

Dependencies, integration, risks, and tests: it depends on perf's Rust v0 demangler. Risks include strict string expectations for Rust demangling syntax and missing coverage for newer mangling features. Test signals are exact demangling for standard path impls, trait-qualified methods, closures, higher-ranked function types, numeric consts, arrays, and nested statics.
