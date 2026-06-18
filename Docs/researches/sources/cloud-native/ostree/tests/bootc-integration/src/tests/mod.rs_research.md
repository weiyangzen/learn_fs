<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/bootc-integration/src/tests/mod.rs -->
## sources/cloud-native/ostree/tests/bootc-integration/src/tests/mod.rs

Purpose: declares the test module namespace for bootc integration tests.

Important APIs/types/functions: exports `pub mod privileged;`, making privileged test registration statics reachable by the binary.

Control flow/state: no runtime control flow or persistence. Its only state effect is compile-time module inclusion.

Dependencies/integration: connects `main.rs`'s `mod tests;` with `tests/privileged.rs`.

Risks/test signals: if future test files are not added here, their distributed-slice statics will not be linked into the binary.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/bootc-integration/src/tests/mod.rs -->
