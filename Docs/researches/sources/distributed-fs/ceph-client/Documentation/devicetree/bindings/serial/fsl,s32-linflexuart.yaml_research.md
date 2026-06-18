# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/fsl,s32-linflexuart.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/serial/fsl,s32-linflexuart.yaml` defines the Devicetree binding contract for Freescale LINFlexD UART. The LINFlexD controller implements several LIN protocol versions, as well as support for full-duplex UART communication through 8-bit and 9-bit frames. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values `fsl,s32v234-linflexuart`, `nxp,s32g2-linflexuart`, `nxp,s32g3-linflexuart`; required properties `compatible`, `reg`, `interrupts`. Maintainers: Chester Lin <chester62515@gmail.com>. Property contract: `compatible`: schema keys oneOf Required. `reg`: maxItems 1 Required. `interrupts`: maxItems 1 Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation uses `allOf` imports `serial.yaml#`. No child-node patternProperties are defined.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are `serial.yaml#`. It integrates with the Linux serial/TTY binding stack and usually feeds console, earlycon, DMA, wakeup, and RS-485 validation through common serial schemas. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `unevaluatedProperties: false` closes the schema after referenced/common properties are accounted for. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/serial/fsl,s32-linflexuart.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
