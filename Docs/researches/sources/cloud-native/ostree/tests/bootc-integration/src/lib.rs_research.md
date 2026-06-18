<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/bootc-integration/src/lib.rs -->
## sources/cloud-native/ostree/tests/bootc-integration/src/lib.rs

Purpose: provides the registration infrastructure for bootc integration tests. Test functions return `anyhow::Result<()>` and are registered into a `linkme` distributed slice.

Important APIs/types/functions: `TestFn` aliases the fallible test function signature; `IntegrationTest` stores `name` and function pointer; `INTEGRATION_TESTS` is the distributed slice; `integration_test!` creates a static entry named from the function using `paste`.

Control flow/state: this file has no mutable runtime state. Registration happens at link time through `linkme`, and `main.rs` later enumerates the distributed slice.

Dependencies/integration: depends on `anyhow`, `linkme`, and `paste`, and exports the macro for submodules such as `tests/privileged.rs`. Unsafe code is allowed only because `linkme` requires it.

Risks/test signals: distributed-slice registration can silently miss tests if modules are not referenced by `main.rs`. The main signal is that registered tests appear in the custom harness listing.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/bootc-integration/src/lib.rs -->
