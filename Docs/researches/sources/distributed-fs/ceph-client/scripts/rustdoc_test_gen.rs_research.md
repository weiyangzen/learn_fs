# sources/distributed-fs/ceph-client/scripts/rustdoc_test_gen.rs

Purpose: `rustdoc_test_gen.rs` aggregates saved rustdoc doctest bodies into generated Rust and C KUnit glue: `rust/doctests_kernel_generated.rs` and `rust/doctests_kernel_generated_kunit.c`.

Important APIs, types, and functions: `find_real_path()` reconstructs the source path represented by rustdoc's flattened file name by recursively trying underscore-as-path-separator combinations under `rust/kernel`. It panics on zero or multiple candidates. `main()` reads and sorts saved doctest files, groups tests by original file to assign stable per-file numbers, builds Rust extern test functions with KUnit-aware `assert!` and `assert_eq!` macro overrides, emits KTAP-style location diagnostics, and writes matching C `KUNIT_CASE` declarations.

Control flow: the script gets `srctree` from the environment, scans `rust/test/doctests/kernel`, sorts paths for deterministic output, parses each filename as `{file}_{line}_{number}`, resolves the real source path once per file, computes body line offsets for diagnostics, and appends generated code fragments before writing both output files.

State and persistence: it writes two generated files in `rust/`. It reads all saved doctest bodies and maintains only transient string buffers and path-candidate vectors.

Dependencies and integration points: depends on the builder output naming convention, `srctree`, KUnit C APIs, Rust kernel prelude, and `kernel::kunit_assert*` macros. It is part of the Rust documentation-test Kbuild path.

Risks: ambiguous underscore/path mappings cause a panic and require source renaming. Doctest failures from spawned threads may only log and not fail the owning KUnit test, as documented. Generated C/Rust must stay synchronized with KUnit and Rust kernel APIs.

Test signals: doctest suites with multiple tests per file, files/directories containing underscores, ambiguous candidates, and Result-returning bodies. Generated files should compile and report original locations accurately.
