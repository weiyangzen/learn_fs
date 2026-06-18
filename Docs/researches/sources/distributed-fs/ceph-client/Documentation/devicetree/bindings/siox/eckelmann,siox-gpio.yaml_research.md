# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/siox/eckelmann,siox-gpio.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/siox/eckelmann,siox-gpio.yaml` defines the Devicetree binding contract for Eckelmann SIOX GPIO bus. `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/siox/eckelmann,siox-gpio.yaml` is a Devicetree YAML schema for Eckelmann SIOX GPIO bus. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `eckelmann,siox-gpio`; required properties `compatible`, `din-gpios`, `dout-gpios`, `dclk-gpios`, `dld-gpios`. Maintainers: Frank Li <Frank.Li@nxp.com>. Property contract: `compatible`: const `eckelmann,siox-gpio` Required. `din-gpios`: maxItems 1 Required. `dout-gpios`: maxItems 1 Required. `dclk-gpios`: maxItems 1 Required. `dld-gpios`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are none. It integrates through Devicetree schema validation and the matching Linux platform, bus, or MFD driver. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/siox/eckelmann,siox-gpio.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
