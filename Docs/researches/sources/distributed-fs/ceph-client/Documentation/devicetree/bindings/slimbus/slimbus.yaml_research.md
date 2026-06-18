# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/slimbus/slimbus.yaml

Purpose: `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/slimbus/slimbus.yaml` defines the Devicetree binding contract for SLIM (Serial Low Power Interchip Media) bus. SLIMbus is a 2-wire bus, and is used to communicate with peripheral components like audio-codec. The binding is documentation plus machine-checkable validation used by `dtbs_check`, not executable runtime code.

Important APIs/types/functions: the externally visible API is the node shape: `compatible` values none extracted from `compatible`; required properties `#address-cells`, `#size-cells`. Maintainers: Srinivas Kandagatla <srinivas.kandagatla@linaro.org>. Property contract: `#address-cells`: const `2` Required. `#size-cells`: const `0` Required.

Control flow: dt-schema loads this YAML through its `$id`, applies the core meta-schema, resolves `$ref` links, checks required properties first, validates property cardinality and value enums/consts, then evaluates composition, child patterns, and extra-property policy. Validation is mostly direct property checking with no top-level schema composition. Pattern `^.*@[0-9a-f]+,[0-9a-f]+$` accepts child objects with properties `compatible`, `reg`; required child fields: `compatible`, `reg`.

State and persistence behavior: the file has no mutable runtime state. Its persistent effect is the accepted ABI for board DTS files: once a compatible string, register layout, interrupt name, clock name, child-node form, or phandle cell format is documented here, kernel DTS users and boot firmware tend to rely on it long term.

Dependencies and integration points: schema references are none. It integrates with SLIMbus controller/device enumeration and, for Qualcomm NGD, with clocks, DMA or interconnect-like SoC resources. The examples act as integration fixtures for the binding and are compiled by Devicetree validation tooling. Example blocks present: 1.

Risks: the main risks are ABI drift between the YAML and Linux drivers, incorrect compatible fallback ordering, too-loose validation that lets broken DTS files pass, or too-strict validation that rejects deployed boards. `additionalProperties: true` intentionally leaves extension room, usually because this is a common/shared schema. Array ordering is especially sensitive for `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, DMA names, phandle-array cells, and child-node `reg` values.

Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/slimbus/slimbus.yaml` and relevant `make dtbs_check` targets. Good tests should include the example node, at least one in-tree DTS user for each compatible family, negative checks for missing required properties, and edge cases for conditional branches, child node patterns, and deprecated properties.
