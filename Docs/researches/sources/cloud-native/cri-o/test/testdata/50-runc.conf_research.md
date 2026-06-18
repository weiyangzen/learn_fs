<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/50-runc.conf -->
# sources/cloud-native/cri-o/test/testdata/50-runc.conf

Purpose: minimal CRI-O runtime definition fixture that declares `runc` without setting it as `default_runtime`.

Important structure: contains only the runtime tables and `runtime_path="/usr/bin/runc"`. It is useful for testing runtime table merging or default selection from other config sources.

State and integration: static TOML drop-in consumed by CRI-O config loading tests. It stores no state. Risks are host path assumptions and ambiguity when combined with other runtime fragments. Test signal comes from config merge/runtime selection tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/50-runc.conf -->
