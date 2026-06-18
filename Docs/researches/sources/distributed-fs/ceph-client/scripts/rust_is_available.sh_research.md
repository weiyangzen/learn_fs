# sources/distributed-fs/ceph-client/scripts/rust_is_available.sh

Purpose: `rust_is_available.sh` validates that Kbuild has a usable Rust toolchain. It checks required environment variables, command availability, `rustc`, `bindgen`, and libclang versions, Clang/libclang consistency warnings, and the availability of Rust `core` source.

Important APIs, types, and functions: `get_canonical_version()` converts `x.y.z` into a comparable integer with extra major/minor room for Rust 1.100+. `print_docs_reference()` and `print_kbuild_explanation()` centralize diagnostics. The script uses `scripts/min-tool-version.sh` for minimum `rustc`, `bindgen`, and LLVM versions, `scripts/cc-version.sh` to identify Clang, and `rust_is_available_bindgen_libclang.h` to force bindgen to print libclang version.

Control flow: after `set -e`, an EXIT trap prints the Rust quick-start reference on failure or warning. It validates `RUSTC`, `BINDGEN`, and `CC` are set and executable, parses version output with sed, compares canonical versions, invokes bindgen on the probe header, warns if Clang and libclang versions differ, then checks `$RUST_LIB_SRC` or the rustc sysroot for `core/src/lib.rs`.

State and persistence: it writes diagnostics to stderr and produces no stdout on success. It does not modify files. `warning=1` preserves successful exit while still causing the docs reference to print.

Dependencies and integration points: called by Kbuild's `rustavailable` target and Rust build checks. It depends on POSIX shell, `sed`, `cut`, rustc, bindgen, a C compiler, libclang, and the in-tree helper scripts.

Risks: version parsing accepts only full numeric `x.y.z` prefixes and may reject unusual tool wrappers. The `CC` invocation is intentionally loose to handle ccache/multiple arguments, but shell word splitting is involved. Missing Rust source is a common packaging issue.

Test signals: `rust_is_available_test.py` provides extensive fake-tool coverage. Integration tests should include real GCC/Clang, mismatched Clang/libclang, version suffixes, missing executables, and sysroot/RUST_LIB_SRC failure cases.
