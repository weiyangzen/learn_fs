# sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/no-quotes-boolean.yaml

Purpose: Negative YAML fixture proving `beegfsClientConf` values must be strings even when they look like booleans.

Important data: Sets `config.beegfsClientConf.connUseRDMA: true` without quotes.

Control flow: `yaml.UnmarshalStrict` attempts to decode this boolean into a `map[string]string` value and fails. `parseConfigFromFile` recognizes the resulting error pattern and wraps it with a specific likely-missing-quotes diagnostic.

State and persistence: Static test fixture.

Dependencies and integration points: Protects user-facing config validation in `config.go` and documents the schema expected by the operator API type.

Risks: The enhanced diagnostic depends on matching the unmarshalling error string. If the YAML library changes wording, the parser may still fail correctly but lose the tailored hint.

Test signals: `TestParseConfigFromFile` expects an error containing "likely missing quotes around an integer or boolean beegfsClientConf value".
