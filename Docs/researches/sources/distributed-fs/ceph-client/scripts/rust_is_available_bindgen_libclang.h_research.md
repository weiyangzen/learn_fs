# sources/distributed-fs/ceph-client/scripts/rust_is_available_bindgen_libclang.h

Purpose: this two-line C header is a bindgen probe used by `rust_is_available.sh` to discover the libclang version that bindgen loaded.

Important APIs, types, and functions: it contains only an SPDX header and `#pragma message("clang version " __clang_version__)`. The preprocessor expands `__clang_version__`, and bindgen forwards the compiler diagnostic to stderr.

Control flow: it is not executed directly. Bindgen parses it; successful parsing creates a warning/message containing `clang version x.y.z`, which the shell script extracts with sed.

State and persistence: no persistent state.

Dependencies and integration points: depends on clang/libclang supporting `__clang_version__` and pragma messages. It is tightly coupled to the sed pattern in `rust_is_available.sh` and the fake bindgen output in `rust_is_available_test.py`.

Risks: changes to bindgen diagnostic formatting or libclang pragma output could break version extraction. Non-Clang front ends would not provide the expected macro, but bindgen uses libclang by design.

Test signals: unit tests feed many realistic warning strings, including absolute paths, distro suffixes, and locale noise, and expect the same version extraction behavior.
