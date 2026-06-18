# sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/no-quotes-integer.yaml

Purpose: Negative YAML fixture proving numeric `beegfsClientConf` values must be quoted strings.

Important data: Sets `config.beegfsClientConf.connMgmtdPort: 8000` as an integer instead of `"8000"`.

Control flow: Strict YAML unmarshal fails because the destination type is string. `parseConfigFromFile` adds the missing-quotes hint when the error matches its regex.

State and persistence: Static fixture.

Dependencies and integration points: Documents runtime config contract for values later written into `beegfs-client.conf`, where all BeeGFS client config overrides are string values.

Risks: Same diagnostic-string coupling as the boolean fixture. It does not test quoted numeric strings with leading zeroes or empty values; those are covered elsewhere.

Test signals: Negative parsing path used by `TestParseConfigFromFile`.
