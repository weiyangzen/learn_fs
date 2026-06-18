<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/ocf_env_headers.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/ocf_env_headers.h

Purpose: Minimal OCF environment version/header constants.

APIs and types: Includes stdint/stddef/stdbool and defines `OCF_LOGO`, short/long prefixes, and OCF version numbers `20.3.0`.

State and persistence: Stateless constants.

Dependencies and integration: Included by `ocf_env.h` and OCF code for logging/version compatibility.

Risks and test signals: Version constants must match vendored OCF expectations. Compile and OCF cache startup validate compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/ocf_env_headers.h -->
