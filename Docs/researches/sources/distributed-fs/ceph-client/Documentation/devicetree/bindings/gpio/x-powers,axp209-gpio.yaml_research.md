<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/x-powers,axp209-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/x-powers,axp209-gpio.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/x-powers,axp209-gpio.yaml` defines the GPIO controller binding titled `X-Powers AXP209 GPIO`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 3 branches with 6 tokens: `x-powers,axp209-gpio`, `x-powers,axp221-gpio`, `x-powers,axp813-gpio`, `x-powers,axp223-gpio`, `x-powers,axp809-gpio`, `x-powers,axp803-gpio`. Top-level properties are `#gpio-cells`, `compatible`, `gpio-controller`. Required top-level properties are `compatible`, `#gpio-cells`, `gpio-controller`. Pattern properties are `^.*-pins?$`. The highest-risk API details are GPIO line count, `#gpio-cells`, interrupt-cell shape, parent interrupt wiring, and vendor-specific pin control flags.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including gpiochip registration, line direction/value state, optional IRQ domain setup, and consumer GPIO descriptor lookup.

## Dependencies and Integration Points
Maintainers listed: Chen-Yu Tsai <wens@csie.org>. Dependencies include `/schemas/pinctrl/pinmux-node.yaml#`. Integration points include gpiolib, pin consumers, optional interrupt-controller registration, and board DTS GPIO specifiers. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to GPIO line count, `#gpio-cells`, interrupt-cell shape, parent interrupt wiring, and vendor-specific pin control flags, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: pattern property regexes can over-match or under-match child nodes.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/x-powers,axp209-gpio.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/x-powers,axp209-gpio.yaml` against representative board DTBs. There are no embedded examples, so coverage must come from DTS users and schema-only validation. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/x-powers,axp209-gpio.yaml -->
