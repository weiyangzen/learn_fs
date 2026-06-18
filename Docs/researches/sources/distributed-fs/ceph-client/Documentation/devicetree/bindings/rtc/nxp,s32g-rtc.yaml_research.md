# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,s32g-rtc.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/rtc/nxp,s32g-rtc.yaml` defines the Devicetree binding contract for NXP S32G2/S32G3 Real Time Clock (RTC). RTC hardware module present on S32G2/S32G3 SoCs is used as a wakeup source. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `nxp,s32g2-rtc`, `nxp,s32g3-rtc`; required properties `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Maintainers: Bogdan Hamciuc <bogdan.hamciuc@nxp.com>, Ciprian Marian Costea <ciprianmarian.costea@nxp.com>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required. `clocks`: ordered items Required. `clock-names`: ordered items Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `rtc.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `rtc.yaml#`. It integrates with the RTC subsystem and the shared `rtc.yaml` common properties for wakeup, trickle charging, oscillator, and time-range metadata when referenced. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: false` rejects undeclared properties at this schema level. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/rtc/nxp,s32g-rtc.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
