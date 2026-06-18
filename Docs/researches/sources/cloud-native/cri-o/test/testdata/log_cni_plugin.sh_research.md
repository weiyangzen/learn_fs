<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/log_cni_plugin.sh -->
# sources/cloud-native/cri-o/test/testdata/log_cni_plugin.sh

Purpose: minimal CNI plugin fixture that logs ADD input and returns simple CNI responses.

Important flow: reads stdin JSON, switches on `CNI_COMMAND`, and for `ADD` extracts `.config.log_path` using `jq`; if present, appends the full config to that log and emits a `cniVersion` result. `VERSION` emits supported versions, while `DEL` and `GET` are no-ops; unknown commands fail.

State and integration: writes to the configured log path and participates in CRI-O CNI setup during tests. Dependencies include bash and `jq`. Risks include no validation of log path, silent no-op for DEL/GET, and minimal CNI result fields that may not satisfy consumers outside tests. Test signal is captured log content and CNI command behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/log_cni_plugin.sh -->
