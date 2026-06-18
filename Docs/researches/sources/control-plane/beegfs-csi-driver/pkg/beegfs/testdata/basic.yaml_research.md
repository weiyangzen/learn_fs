# sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/basic.yaml

Purpose: Positive configuration fixture for `parseConfigFromFile`. It defines a complete default BeeGFS config and one filesystem-specific config with the same values.

Important data: Top-level `config` sets `grpcPort`, `connInterfaces`, `connNetFilter`, `connTcpOnlyFilter`, and string-valued `beegfsClientConf` keys `connMgmtdPort` and `connUseRDMA`. `fileSystemSpecificConfigs` contains `sysMgmtdHost: 127.0.0.0` with equivalent nested config.

Control flow: Consumed by `TestParseConfigFromFile`, `TestValidateConfig`, and strip tests to establish a valid baseline. The parser should strictly unmarshal it, validate IP/CIDR values, and preserve all supported config entries.

State and persistence: Static test fixture, no runtime writes.

Dependencies and integration points: Mirrors the operator API YAML schema consumed by `config.go`. It feeds expected runtime config used by `writeClientFiles`.

Risks: Because it duplicates default and filesystem-specific config, fixture changes must be reflected in expected structs in tests. It only covers IPv4-style filters, not IPv6 or DNS host cases.

Test signals: Baseline passing config for parsing, validation, stripping no-effect options, stripping clean configs, and retaining unsupported options when tests inject them.
