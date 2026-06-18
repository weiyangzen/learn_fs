# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serio/arm,pl050.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serio/arm,pl050.yaml` defines the Devicetree binding contract for Arm Ltd. PrimeCell PL050 PS/2 Keyboard/Mouse Interface. The Arm PrimeCell PS2 Keyboard/Mouse Interface (KMI) is an AMBA compliant peripheral that can be used to implement a keyboard or mouse interface that is IBM PS2 or AT compatible. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `arm,pl050`, `arm,primecell`; required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Maintainers: Andre Przywara <andre.przywara@arm.com>. Property contract: `compatible`: ordered items Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: ordered items Required. `clock-names`: ordered items Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are none. It integrates with serio input drivers and interrupt/clock/reset providers used by keyboard or PS/2 controller nodes. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serio/arm,pl050.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
