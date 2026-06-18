# sources/distributed-fs/ceph-client/scripts/rust_is_available_test.py

Purpose: `rust_is_available_test.py` is a unittest suite for `rust_is_available.sh`. It uses generated executable stubs to simulate rustc, bindgen, and clang behavior across success, warning, and failure cases.

Important APIs, types, and functions: `TestRustIsAvailable.Expected` models expected outcome classes. `generate_executable()`, `generate_clang()`, `generate_rustc()`, and `generate_bindgen()` create temporary executable scripts with controlled stdout/stderr/exit behavior. `setUpClass()` discovers default minimum versions through `scripts/min-tool-version.sh` and rust sysroot from real rustc. `run_script()` executes `scripts/rust_is_available.sh`, asserts stdout is empty, checks return code and docs-reference behavior, and returns decoded stderr.

Control flow: individual tests override environment entries to cover unset variables, missing/non-executable tools, unexpected version output, old versions, libclang failures, version mismatch warnings, missing core sources, supported version suffixes, and real-program smoke tests for GCC and Clang.

State and persistence: it creates a temporary directory for fake executables and one non-executable file. It does not write into the source tree.

Dependencies and integration points: depends on Python 3, unittest, executable permission support, the real helper scripts, and, for some tests, real `rustc`, `bindgen`, `gcc`, and `clang` in PATH. It is a test companion to the shell script and probe header.

Risks: the "real programs" test can fail in minimal build environments without bindgen or compilers. The generated stubs are Python scripts, so the test environment needs Python executable support. Because defaults are read from the current tree, min-version changes automatically affect expectations.

Test signals: the file is itself the main signal. Useful additions would include malformed `CC` values, libclang messages without file prefixes, and shell metacharacter safety around generated tool paths.
