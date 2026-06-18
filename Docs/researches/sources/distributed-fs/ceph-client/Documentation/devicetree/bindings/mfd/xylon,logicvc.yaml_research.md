<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/xylon,logicvc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/xylon,logicvc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/xylon,logicvc.yaml` defines the MFD parent or mixed-function device binding titled `Xylon LogiCVC multi-function device`. The LogiCVC is a display controller that also contains a GPIO controller. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an ordered fallback `items` sequence with 3 tokens: `xylon,logicvc-3.02.a`, `syscon`, `simple-mfd`. Top-level properties are `compatible`, `reg`, `#address-cells`, `#size-cells`. Required top-level properties are `compatible`, `reg`. Pattern properties are `^gpio@[0-9a-f]+$`, `^display@[0-9a-f]+$`. Nested required-property signals include `compatible`, `reg`. The highest-risk API details are child-node naming, address-cell layout, interrupt-controller cells, child compatible strings, regmap range boundaries, and whether unknown children are rejected.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including MFD runtime state such as regmap access, IRQ chip registration, child-device population, and parent-controlled power/reset sequencing.

## Dependencies and Integration Points
Maintainers listed: Paul Kocialkowski <paul.kocialkowski@bootlin.com>. Direct schema dependencies include `/schemas/display/xylon,logicvc-display.yaml#`, `/schemas/gpio/xylon,logicvc-gpio.yaml#`. Integration points include the MFD core, regmap-backed child devices, IRQ domains, I2C/SPI/platform probing, regulators, RTC, GPIO, pinctrl, codec, display, or power-management child nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to child-node naming, address-cell layout, interrupt-controller cells, child compatible strings, regmap range boundaries, and whether unknown children are rejected, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: pattern-property regexes can over-match or under-match child nodes; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/xylon,logicvc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/xylon,logicvc.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/xylon,logicvc.yaml -->
