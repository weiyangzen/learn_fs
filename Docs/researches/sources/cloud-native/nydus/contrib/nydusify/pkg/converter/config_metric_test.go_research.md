# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/config_metric_test.go

Purpose: tests converter driver config mapping and metric dumping.

Important APIs and flow: `TestGetConfig` populates an `Opt` with representative values and asserts every generated config key. `TestDumpMetric` writes an acceleration-service `Metric` to JSON, checks expected fields, and verifies path creation failure is wrapped.

State and persistence: writes metric JSON to a temporary file.

Dependencies and integration: protects `getConfig` compatibility with the `nydus` driver and `dumpMetric` output used by `Convert` when `OutputJSON` is set.

Risks and test signals: comprehensive for current config keys. It does not validate downstream driver interpretation or metric schema evolution beyond field presence.
