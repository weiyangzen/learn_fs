# sources/control-plane/beegfs-csi-driver/pkg/beegfs/testdata/node-default-override-double.yaml

Purpose: Fixture documenting sequential node-specific override precedence when more than one node-specific config applies to the same node.

Important data: Top-level default config sets base networking and management port values. Two `nodeSpecificConfigs` entries both list `testnode`; the first overrides values to the `1` variants and the second overrides them again to the `2` variants. Top-level `grpcPort` is intentionally absent to show node-specific config can add it.

Control flow: `parseConfigFromFile` loops through node-specific configs in file order. Both matching entries apply, so later values win. `overWriteBeegfsConfig` copies only non-empty fields and map keys from each override.

State and persistence: Static fixture.

Dependencies and integration points: Tests the precedence semantics that node-local driver config depends on when multiple node selectors overlap.

Risks: Ordering becomes meaningful in YAML. Overlapping node entries can be powerful but may be confusing operationally because the last matching entry wins without warning.

Test signals: `TestParseConfigFromFile` expects final values from the second override and confirms a missing default `grpcPort` can be supplied by node override.
