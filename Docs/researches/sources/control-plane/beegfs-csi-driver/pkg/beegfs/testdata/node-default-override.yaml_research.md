# sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/node-default-override.yaml

Purpose: Fixture for node-specific default config override behavior.

Important data: Top-level `config` sets `grpcPort`, interface/filter values, and `connMgmtdPort` with `0` variants. A single `nodeSpecificConfigs` entry for `testnode` supplies `1` variants for the same fields.

Control flow: When `nodeID` is `testnode`, `parseConfigFromFile` overlays the node config onto `DefaultConfig`. When the node ID does not match, top-level defaults remain unchanged.

State and persistence: Static fixture.

Dependencies and integration points: Demonstrates how a single config file can adjust driver behavior per node, affecting later BeeGFS client file generation and mount behavior.

Risks: Node matching is exact string equality against `nodeList`. Missing or differently-cased node IDs prevent override application.

Test signals: Positive and negative node match cases in `TestParseConfigFromFile`.
