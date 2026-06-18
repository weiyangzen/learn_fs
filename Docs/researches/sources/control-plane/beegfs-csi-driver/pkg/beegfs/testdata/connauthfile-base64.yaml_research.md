# sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/connauthfile-base64.yaml

Purpose: Secret fixture for `parseConnAuthFromFile` covering base64-encoded BeeGFS connection auth values, including a simple text secret and a multiline binary-like secret.

Important data: Contains two list entries keyed by `sysMgmtdHost`. The first decodes to `secret1\n`. The second uses a YAML block scalar for a longer base64 payload representing binary data and targets `127.0.0.1`.

Control flow: `parseConnAuthFromFile` unmarshals the list, selects `encoding: base64`, decodes the content exactly, and writes decoded strings into matching filesystem-specific configs. It does not append the raw-mode newline in the base64 branch.

State and persistence: Static test fixture. Secrets are sample data but still exercise secret-safe logging paths through API marshal behavior.

Dependencies and integration points: Used by `config_test.go` alongside a binary fixture to assert exact decoded bytes. Represents the recommended secret material flow into `writeClientFiles`.

Risks: Multiline base64 formatting depends on YAML preserving block content in a way accepted by Go's base64 decoder. Bad base64 and invalid encoding are not covered by this fixture.

Test signals: Confirms base64 decoding supports both normal text and binary connAuth files and applies values by `sysMgmtdHost`.
