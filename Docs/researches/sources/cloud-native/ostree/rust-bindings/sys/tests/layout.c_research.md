# sources/cloud-native/ostree/rust-bindings/sys/tests/layout.c

Purpose: This generated C fixture prints C `sizeof` and `alignof` values for selected libostree types so Rust ABI layout declarations can be checked.

Important APIs, types, and functions: It includes `manual.h`, `<stdalign.h>`, and `<stdio.h>`. `main` prints semicolon-separated rows for classes/interfaces, enum and flag typedefs, boxed structs, option structs, stats structs, vtables, and pointer-vector aliases such as `OstreeCollectionRefv` and `OstreeRepoFinderResultv`.

Control flow: Straight-line `printf` calls produce `<type>;<size>;<alignment>` rows in the order expected by `RUST_LAYOUTS`.

State and persistence behavior: None beyond stdout. No OSTree repository or object state is created.

Dependencies and integration points: Requires a C compiler with `alignof` support, the libostree headers, GLib/GObject type definitions pulled through `ostree.h`, and the ordering contract with `abi.rs`.

Risks: It checks type size and alignment but not field offsets. If Rust fields are reordered in a way that preserves total size and alignment, this test would not detect it unless another assertion is added. Conditional header compatibility in `manual.h` affects what can compile against older libostree.

Test signals: Passing `cross_validate_layout_with_c` confirms the Rust FFI declarations for selected records and typedefs have C-compatible size and alignment on the test platform.
