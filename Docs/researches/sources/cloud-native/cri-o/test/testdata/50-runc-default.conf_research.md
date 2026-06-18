<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/50-runc-default.conf -->
# sources/cloud-native/cri-o/test/testdata/50-runc-default.conf

Purpose: minimal CRI-O drop-in config fixture that sets `runc` as the default runtime and declares the `runc` runtime path.

Important structure: under `[crio.runtime]`, `default_runtime = "runc"`; under `[crio.runtime.runtimes.runc]`, `runtime_path="/usr/bin/runc"`.

State and integration: static TOML fragment merged into CRI-O config in tests. It does not persist state. Risks are path assumptions on hosts where `runc` is elsewhere and accidental masking of runtime defaults. Test signal is config-loading behavior in runtime selection tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/50-runc-default.conf -->
