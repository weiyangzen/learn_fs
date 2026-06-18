<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/trivial-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/trivial-gpio.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/trivial-gpio.yaml` defines the GPIO controller binding titled `Trivial 2-cell GPIO controllers`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. This file delegates most chip identity to `Documentation/devicetree/bindings/trivial-devices.yaml`; its local API is the shared GPIO-controller shape for simple I2C/SPI expander-like chips. Top-level properties are `compatible`, `reg`, `#gpio-cells`, `gpio-controller`, `gpio-line-names`, `ngpios`. Required top-level properties are `compatible`, `#gpio-cells`, `gpio-controller`. Pattern properties are `^(hog-[0-9]+|.+-hog(-[0-9]+)?)$`. The highest-risk API details are GPIO line count, `#gpio-cells`, interrupt-cell shape, parent interrupt wiring, and vendor-specific pin control flags.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including gpiochip registration, line direction/value state, optional IRQ domain setup, and consumer GPIO descriptor lookup.

## Dependencies and Integration Points
Maintainers listed: Bartosz Golaszewski <brgl@bgdev.pl>. Dependencies include dt-schema core/meta schemas only. Integration points include gpiolib, pin consumers, optional interrupt-controller registration, and board DTS GPIO specifiers. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to GPIO line count, `#gpio-cells`, interrupt-cell shape, parent interrupt wiring, and vendor-specific pin control flags, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; pattern property regexes can over-match or under-match child nodes; large compatible catalogues are prone to missing fallback ordering; examples can drift from the schema and give false confidence if not validated; the split between this schema and `trivial-devices.yaml` can leave simple expanders incompletely described.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/trivial-gpio.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/gpio/trivial-gpio.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/gpio/trivial-gpio.yaml -->
