# sources/cloud-native/ostree/rust-bindings/.ci/generate-test-jobs.sh

Purpose: This shell generator emits GitLab CI YAML jobs for every Cargo feature in the Rust bindings except `dox`. It keeps feature test coverage in sync with `Cargo.toml` metadata.

Important functions and commands: `get_features` runs `cargo read-manifest` and pipes JSON to `jq`, extracting feature keys, excluding `dox`, and printing a space-delimited list. The script emits an `include: /.ci/gitlab-ci-base.yml` header, then writes one `test_feature_${feature}` job per feature that extends `.fedora-ostree-devel` and runs `cargo test --verbose --workspace --features ${feature}`.

Control flow and state: The script is deterministic given the Cargo manifest. It produces CI YAML on stdout and writes no files itself. `set -eu` makes missing commands or unset variables fail early.

Dependencies and integration points: Depends on Cargo, `jq`, GitLab CI includes, and base job definitions in `.ci/gitlab-ci-base.yml`. It integrates feature-gated generated bindings with CI so each version feature can be compiled and tested.

Risks: Feature names are interpolated into job names and shell commands without quoting or sanitization; Cargo feature names are usually safe but unusual names could produce invalid YAML. The generated jobs test each feature individually, not all feature combinations. Missing `jq` or `cargo` fails generation.

Test signals: CI should validate the generated YAML and run at least one generated feature job. A local check can compare generated output after feature changes to ensure newly added version gates get test jobs.
