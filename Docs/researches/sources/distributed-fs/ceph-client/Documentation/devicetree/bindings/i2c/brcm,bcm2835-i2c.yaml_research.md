<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/brcm,bcm2835-i2c.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/brcm,bcm2835-i2c.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/brcm,bcm2835-i2c.yaml` defines the I2C controller binding titled `Broadcom BCM2835 I2C controller`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 2 branches with 2 tokens: `brcm,bcm2835-i2c`, `brcm,bcm2711-i2c`. Top-level properties are `compatible`, `reg`, `interrupts`, `clock-names`, `clocks`, `clock-frequency`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`. Pattern properties are none. The highest-risk API details are bus child-address cells, register and interrupt ordering, clock-frequency limits, DMA/reset naming, and SoC fallback compatible ordering.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including I2C adapter registration, bus speed programming, clock/reset enablement, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Stephen Warren <swarren@wwwdotorg.org>. Dependencies include `/schemas/i2c/i2c-controller.yaml#`. Integration points include the Linux I2C core, platform bus probing, clock/reset/interrupt providers, pinctrl, DMA where supported, and child I2C device nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to bus child-address cells, register and interrupt ordering, clock-frequency limits, DMA/reset naming, and SoC fallback compatible ordering, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/brcm,bcm2835-i2c.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/i2c/brcm,bcm2835-i2c.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/i2c/brcm,bcm2835-i2c.yaml -->
